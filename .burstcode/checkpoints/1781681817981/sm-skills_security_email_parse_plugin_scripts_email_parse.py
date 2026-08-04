#!/usr/bin/env python3
"""
邮件上传与解析脚本

对接邮件威胁检测系统，Agent 按 SOP 分步调用。

Action:
    upload_email     — 上传邮件并创建检测任务，返回 taskId
    get_task_report  — 获取指定类型的检测报告
    list_emails      — 查询邮件检测结果列表
    list_attachments — 查询附件列表

输出协议:
    所有 action:      processData:<json> / errorData:<json>

环境变量:
    EMAIL_PARSE_BASE_URL              邮件检测系统地址（默认 https://192.168.180.129:8323）

用法:
    python email_parse.py upload_email --file-path <path> [--task-name <name>] [--detection-mode 5]
    python email_parse.py get_task_report --task-id <id> [--report-name ...]
    python email_parse.py list_emails --task-id <id> [--current 1] [--count 20]
    python email_parse.py list_attachments --task-id <id> [--current 1] [--count 20]
"""

import argparse
import json
import logging
import mimetypes
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any, Optional


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://192.168.180.129:8323"

# 忽略 SSL 证书校验（自签证书 / 内网环境）
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE
DEFAULT_POLL_INTERVAL = 5
DEFAULT_POLL_TIMEOUT = 1800  # 30 分钟
REQUEST_TIMEOUT = 30
AUTH_KEY = "805618fffebcdca8f4c3928b764d999b952a84191259b76cf16d63c118848d22"

DETECTION_MODES = {
    "0": "敏感邮件检测",
    "1": "邮件安全检测",
    "2": "综合检测",
    "3": "邮件翻译",
    "4": "邮件总结",
    "5": "自定义",
}

# LLM 常见英文/别名 → 标准 detection_mode 数值映射
DETECTION_MODE_ALIASES = {
    "sensitive": "0", "敏感": "0", "敏感邮件": "0", "敏感检测": "0", "敏感词": "0",
    "safe": "1", "safety": "1", "security": "1", "phishing": "1", "threat": "1",
    "安全": "1", "钓鱼": "1", "威胁检测": "1", "邮件安全": "1",
    "comprehensive": "2", "full": "2", "all": "2", "default": "2", "综合": "2",
    "综合检测": "2", "全面": "2",
    "translate": "3", "translation": "3", "翻译": "3",
    "summary": "4", "summarize": "4", "总结": "4",
    "custom": "5", "自定义": "5",
}
DETECTION_MODE_DEFAULT = "5"

REPORT_NAMES = [
    "邮件内容解读报告",
    "邮件安全分析报告",
    "邮件敏感检测报告",
    "邮件威胁综合分析报告",
]

# LLM 常见英文/缩写 → 标准中文 report_name 映射
REPORT_NAME_ALIASES = {
    "summary": "邮件威胁综合分析报告",
    "comprehensive": "邮件威胁综合分析报告",
    "threat": "邮件威胁综合分析报告",
    "threat_analysis": "邮件威胁综合分析报告",
    "full": "邮件威胁综合分析报告",
    "default": "邮件威胁综合分析报告",
    "content": "邮件内容解读报告",
    "content_analysis": "邮件内容解读报告",
    "解读": "邮件内容解读报告",
    "内容": "邮件内容解读报告",
    "security": "邮件安全分析报告",
    "safety": "邮件安全分析报告",
    "phishing": "邮件安全分析报告",
    "安全": "邮件安全分析报告",
    "钓鱼": "邮件安全分析报告",
    "sensitive": "邮件敏感检测报告",
    "sensitivity": "邮件敏感检测报告",
    "敏感": "邮件敏感检测报告",
}
REPORT_NAME_DEFAULT = "邮件威胁综合分析报告"

TASK_TERMINAL_SUCCESS_TOKENS = (
    "succeeded", "success", "completed", "complete", "finished", "done",
    "已完成", "完成", "成功", "结束"
)
TASK_TERMINAL_FAILURE_TOKENS = (
    "failed", "fail", "error", "cancelled", "canceled", "cancel", "stopped", "stop",
    "异常", "失败", "取消", "终止", "停止"
)
TASK_ACTIVE_TOKENS = (
    "submitted", "pending", "queued", "queue", "running", "processing", "progress", "waiting",
    "已提交", "排队", "处理中", "检测中", "解析中", "执行中", "进行中", "等待"
)

# ---------------------------------------------------------------------------
# ProcessOutputPrefix 协议
# ---------------------------------------------------------------------------

PROCESS_DATA_PREFIX = "processData:"
ERROR_DATA_PREFIX = "errorData:"


# ---------------------------------------------------------------------------
# 文件日志
# ---------------------------------------------------------------------------

logger = logging.getLogger("email_parse")


def _get_run_id() -> str:
    """获取 runId（即 sessionId 去掉连字符）。

    优先级：
    1. 环境变量 ``sessionId``（由 Java 侧 PackagedSkillCommandToolExecutor 注入）
    2. 环境变量 ``LOG_DIR`` 推导的工作目录
    3. 随机生成，避免不同文件复用同一 runId 触发后端幂等逻辑返回旧任务
    """
    session_id = os.environ.get("sessionId", "")
    if session_id:
        run_id = session_id.replace("-", "")
        logger.info("resolved runId=%s from env sessionId=%s", run_id, session_id)
        return run_id
    log_dir = os.environ.get("LOG_DIR")
    if log_dir:
        run_dir = os.path.normpath(os.path.join(log_dir, "..", ".."))
        run_id = os.path.basename(run_dir).replace("-", "")
        logger.info("resolved runId=%s from LOG_DIR=%s", run_id, log_dir)
        return run_id
    run_id = f"hermes{uuid.uuid4().hex[:20]}"
    logger.info("resolved runId=%s (random fallback, no sessionId/LOG_DIR)", run_id)
    return run_id


def _setup_file_logging():
    """
    初始化文件日志。

    日志目录: {workspace}/../../log/  (workspace 由环境变量传入)
    优先读取 SANDBOX_SKILL_STATE_DIR，其次 os.getcwd()。
    """
    workspace = os.environ.get("LOG_DIR") or os.getcwd()
    log_dir = os.path.normpath(os.path.join(workspace, "..", "..", "log"))
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError:
        # 目录无法创建时仅保留 stdout，不阻断业务
        logger.addHandler(logging.NullHandler())
        return

    log_file = os.path.join(log_dir, "email_parse.log")
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.info("日志初始化完成, workspace=%s, log_dir=%s", workspace, log_dir)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _log(msg: str):
    """内部日志 — 同时写入文件和 stdout（stdout 无前缀，宿主仅 debug 记录）。"""
    print(msg, flush=True)
    logger.info(msg)


def _extract_email_indicators(email_list: list[dict]) -> list[dict]:
    """从邮件列表中提取 IOC 指标（去重）。"""
    seen = set()
    indicators = []

    def _add(ioc_type: str, value: str):
        if not value or not value.strip():
            return
        value = value.strip()
        key = (ioc_type, value.lower())
        if key in seen:
            return
        seen.add(key)
        indicators.append({"type": ioc_type, "value": value})

    for email in email_list:
        if not isinstance(email, dict):
            continue
        _add("email", email.get("senderMailBox", ""))
        for r in (email.get("recipientsMailBox") or []):
            _add("email", r)
        sender_box = email.get("senderMailBox", "")
        if sender_box and "@" in sender_box:
            _add("domain", sender_box.split("@", 1)[1])
        for link in (email.get("containLink") or []):
            _add("url", link)
    return indicators


def _extract_attachment_indicators(attachment_list: list[dict]) -> list[dict]:
    """从附件列表中提取 IOC 指标（去重）。"""
    seen = set()
    indicators = []

    def _add(ioc_type: str, value: str):
        if not value or not value.strip():
            return
        value = value.strip()
        key = (ioc_type, value.lower())
        if key in seen:
            return
        seen.add(key)
        indicators.append({"type": ioc_type, "value": value})

    for att in attachment_list:
        if not isinstance(att, dict):
            continue
        _add("md5", att.get("attachmentMd5", ""))
        _add("file_name", att.get("attachmentName", ""))
    return indicators


def _build_email_evidences(email_list: list[dict]) -> list[dict]:
    """从邮件列表构建结构化证据。"""
    evidences = []
    for email in email_list:
        if not isinstance(email, dict):
            continue
        subject = email.get("subject", "unknown")
        threat = email.get("threatLevel", "未知")
        evidences.append({
            "type": "email_threat_detection",
            "summary": f"邮件 '{subject}' 威胁等级: {threat}",
            "confidence": 0.9 if email.get("threatValue", 0) > 0 else 0.7,
            "attributes": {
                "subject": subject,
                "sender": email.get("senderMailBox", ""),
                "threatLevel": threat,
                "threatValue": email.get("threatValue", 0),
            },
        })
    return evidences


def _build_attachment_evidences(attachment_list: list[dict]) -> list[dict]:
    """从附件列表构建结构化证据。"""
    evidences = []
    for att in attachment_list:
        if not isinstance(att, dict):
            continue
        name = att.get("attachmentName", "unknown")
        threat = att.get("threatLevel", "未知")
        evidences.append({
            "type": "attachment_threat_detection",
            "summary": f"附件 '{name}' 威胁等级: {threat}",
            "confidence": 0.9 if att.get("threatValue", 0) > 0 else 0.7,
            "attributes": {
                "fileName": name,
                "md5": att.get("attachmentMd5", ""),
                "fileType": att.get("fileType", ""),
                "threatLevel": threat,
                "threatValue": att.get("threatValue", 0),
            },
        })
    return evidences


def _resolve_file_paths(raw: str) -> list[str]:
    """
    解析 --file-path 参数为本地文件路径列表。

    支持:
      - 单个路径: /path/to/email.eml
      - 逗号分隔: /path/a.eml,/path/b.eml
      - glob 模式: /path/to/*.eml
    """
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    result = []
    for p in parts:
        if "*" in p or "?" in p:
            import glob
            matched = sorted(glob.glob(p))
            result.extend(matched)
        else:
            result.append(p)
    return result


def _base_url() -> str:
    return os.environ.get("EMAIL_PARSE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _json_request(url: str, method: str = "GET", body: Any = None,
                  headers: Optional[dict] = None, timeout: int = REQUEST_TIMEOUT) -> dict:
    """发送 HTTP 请求并解析 JSON 响应。"""
    logger.debug("HTTP %s %s body=%s", method, url,
                 json.dumps(body, ensure_ascii=False) if body else "(none)")
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    req.add_header("Auth-Key", AUTH_KEY)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            logger.info("HTTP %s %s -> %s, body=%s", method, url, resp.getcode(), resp_body[:2000])
            if resp_body.strip():
                return json.loads(resp_body)
            return {"code": resp.getcode(), "msg": "empty response"}
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        logger.warning("HTTP %s %s -> HTTPError %s, error=%s", method, url, e.code, error_body[:500])
        return {"code": e.code, "msg": f"HTTP {e.code}", "error": error_body}
    except Exception as e:
        logger.warning("HTTP %s %s -> Exception: %s", method, url, e)
        return {"code": -1, "msg": str(e)}


def _multipart_upload(url: str, fields: dict, files: list[tuple[str, str, bytes]],
                      timeout: int = 60) -> dict:
    """
    发送 multipart/form-data 请求。

    Args:
        url: 目标 URL
        fields: 普通表单字段 {name: value}
        files: 文件列表 [(field_name, filename, file_bytes)]
        timeout: 超时秒数

    Returns:
        解析后的 JSON 响应
    """
    boundary = uuid.uuid4().hex
    content_type = f"multipart/form-data; boundary={boundary}"

    body_parts = []

    # 普通字段
    for name, value in fields.items():
        if value is None:
            continue
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )

    # 文件字段
    for field_name, filename, file_bytes in files:
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        )
        body_parts.append(file_bytes)
        body_parts.append(b"\r\n")

    body_parts.append(f"--{boundary}--\r\n")

    # 拼接为 bytes
    body = b""
    for part in body_parts:
        if isinstance(part, str):
            body += part.encode("utf-8")
        else:
            body += part

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", content_type)
    req.add_header("Accept", "application/json")
    req.add_header("Auth-Key", AUTH_KEY)

    logger.debug("MULTIPART POST %s fields=%s file_count=%d", url, list(fields.keys()), len(files))
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            resp_body = resp.read().decode("utf-8", errors="replace")
            logger.info("MULTIPART POST %s -> %s, body=%s", url, resp.getcode(), resp_body[:2000])
            if resp_body.strip():
                return json.loads(resp_body)
            return {"code": resp.getcode(), "msg": "empty response"}
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        logger.warning("MULTIPART POST %s -> HTTPError %s, error=%s", url, e.code, error_body[:500])
        return {"code": e.code, "msg": f"HTTP {e.code}", "error": error_body}
    except Exception as e:
        logger.warning("MULTIPART POST %s -> Exception: %s", url, e)
        return {"code": -1, "msg": str(e)}


def _is_success(resp: dict) -> bool:
    """判断接口响应是否成功（code=000000 或 code=200 或 code=0）。"""
    code = resp.get("code")
    return code in (200, 0, "200", "0", "000000")


def _fail(msg: str, **extra):
    """输出 errorData: 前缀的错误 JSON 并退出。"""
    result = {"success": False, "error": msg}
    result.update(extra)
    logger.error("FAIL: %s | %s", msg, json.dumps(extra, ensure_ascii=False, default=str))
    print(f"{ERROR_DATA_PREFIX}{json.dumps(result, ensure_ascii=False)}", flush=True)
    sys.exit(1)


def _output(data: dict):
    """输出 processData: 前缀的成功 JSON。"""
    data["success"] = True
    logger.info("OUTPUT: %s", json.dumps(data, ensure_ascii=False, default=str))
    print(f"{PROCESS_DATA_PREFIX}{json.dumps(data, ensure_ascii=False)}", flush=True)


def _to_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _to_optional_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in ("true", "1", "yes", "on"):
        return True
    if text in ("false", "0", "no", "off"):
        return False
    return None


def _non_empty_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _state_dir() -> str:
    candidate = os.environ.get("SANDBOX_SKILL_STATE_DIR") or os.environ.get("LOG_DIR") or os.getcwd()
    path = os.path.normpath(candidate)
    os.makedirs(path, exist_ok=True)
    return path


def _task_state_file() -> str:
    return os.path.join(_state_dir(), "email_parse_task_state.json")


def _load_task_state() -> dict:
    path = _task_state_file()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("读取 task state 失败: %s", e)
        return {}


def _save_task_state(data: dict):
    path = _task_state_file()
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data if isinstance(data, dict) else {}, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def _remember_task_id(run_id: str, task_id: str):
    run_key = _non_empty_text(run_id)
    task_key = _non_empty_text(task_id)
    if not run_key or not task_key:
        return
    state = _load_task_state()
    state[run_key] = task_key
    _save_task_state(state)


def _resolve_task_id_arg(args) -> str:
    for name in ("task_id", "external_job_id", "callback_external_job_id"):
        value = _non_empty_text(getattr(args, name, None))
        if value:
            return value
    run_id = _non_empty_text(getattr(args, "run_id", None)) or _get_run_id()
    remembered = _non_empty_text(_load_task_state().get(run_id))
    if remembered:
        return remembered
    return run_id


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
            continue
        return value
    return None


def _dict_value(mapping: Any, *keys: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    for key in keys:
        value = mapping.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _extract_task_info(detail_resp: dict) -> dict:
    if not isinstance(detail_resp, dict) or not _is_success(detail_resp):
        return {}
    data = detail_resp.get("data", {})
    if isinstance(data, dict):
        records = data.get("records", data.get("list", []))
        if isinstance(records, list) and records and isinstance(records[0], dict):
            return records[0]
        if any(key in data for key in ("status", "taskId", "id", "taskName", "emailCount")):
            return data
        return {}
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return {}


def _extract_data_map(resp: dict) -> dict:
    if not isinstance(resp, dict) or not _is_success(resp):
        return {}
    data = resp.get("data", {})
    return data if isinstance(data, dict) else {}


def _decode_escaped_whitespace(text: str) -> str:
    """将字面的 \\r\\n / \\n / \\r / \\t 还原为真实换行/制表符。

    上游接口偶尔会把换行符以字面反斜杠形式返回（例如 "# 标题\\n## 概述"），
    前端按纯文本渲染时会直接显示 "\\n"，因此在返回给异步任务摘要前统一规范化。
    """
    if not text:
        return text
    return (text
            .replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t"))


def _render_report_body(report_data: Any) -> str:
    if report_data is None:
        return ""
    if isinstance(report_data, str):
        return _decode_escaped_whitespace(report_data.strip())
    if isinstance(report_data, dict):
        for key in ("reportData", "report_data", "reportMarkdown", "report_markdown", "reportContent", "report", "content", "markdown", "text"):
            rendered = _render_report_body(report_data.get(key))
            if rendered:
                return rendered
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    if isinstance(report_data, list):
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    return str(report_data).strip()


def _classify_async_status(external_status: str,
                           progress_data: dict,
                           task_info: dict,
                           forced_terminal: Optional[bool] = None,
                           forced_success: Optional[bool] = None) -> tuple[str, bool, bool, Optional[int], Optional[int], Optional[int]]:
    total_count = _first_non_empty(_to_int(task_info.get("allEmailCount")), _to_int(task_info.get("emailCount")))
    done_count = _to_int(task_info.get("parseSuccessCount"))
    failed_count = _to_int(task_info.get("failEmailCount"))
    normalized = _non_empty_text(external_status).lower()
    progress_complete = _to_optional_bool(progress_data.get("isComplete"))
    progress_text = _non_empty_text(progress_data.get("progress"))
    terminal = False
    success = False
    status = "RUNNING"
    if any(token in normalized for token in TASK_TERMINAL_FAILURE_TOKENS):
        terminal = True
        success = False
        status = "FAILED"
    elif progress_complete is True or progress_text in ("100", "100.0", "100.00") or any(token in normalized for token in TASK_TERMINAL_SUCCESS_TOKENS):
        terminal = True
        success = True
        status = "SUCCEEDED"
    if forced_terminal is not None:
        terminal = forced_terminal
    if forced_success is not None:
        success = forced_success
    if terminal:
        status = "SUCCEEDED" if success else "FAILED"
    return status, terminal, success, total_count, done_count, failed_count


def _build_async_message(external_status: str,
                         terminal: bool,
                         success: bool,
                         total_count: Optional[int],
                         done_count: Optional[int],
                         failed_count: Optional[int]) -> str:
    if terminal:
        if success:
            if total_count is not None:
                return f"邮件检测任务已完成：成功 {done_count or 0}/{total_count}，失败 {failed_count or 0}。"
            return "邮件检测任务已完成。"
        return "邮件检测任务失败。"
    if total_count is not None:
        return f"邮件检测任务处理中，当前状态: {external_status or 'RUNNING'}，已完成 {done_count or 0}/{total_count}，失败 {failed_count or 0}。"
    return f"邮件检测任务处理中，当前状态: {external_status or 'RUNNING'}。"


def _build_async_job_payload(task_id: str,
                             forced_terminal: Optional[bool] = None,
                             forced_success: Optional[bool] = None,
                             forced_external_status: Optional[str] = None) -> dict:
    progress_resp = api_get_progress(task_id)
    status_resp = api_check_status(task_id)
    detail_resp = api_task_page_list(task_id)
    progress_data = _extract_data_map(progress_resp)
    status_data = _extract_data_map(status_resp)
    task_info = _extract_task_info(detail_resp)
    external_status = _non_empty_text(
        _first_non_empty(
            forced_external_status,
            _dict_value(status_data, "status", "taskStatus", "state"),
            _dict_value(task_info, "status", "taskStatus", "state"),
        )
    ) or "RUNNING"
    status, terminal, success, total_count, done_count, failed_count = _classify_async_status(
        external_status,
        progress_data,
        task_info,
        forced_terminal=forced_terminal,
        forced_success=forced_success,
    )
    return {
        "externalJobId": task_id,
        "taskId": task_id,
        "status": status,
        "externalStatus": external_status,
        "terminal": terminal,
        "success": success,
        "progressTotal": total_count,
        "progressDone": done_count,
        "progressFailed": failed_count,
        "message": _build_async_message(external_status, terminal, success, total_count, done_count, failed_count),
    }


def _build_custom_task_config(
        analyse_content: bool = True,
        analyse_attachment: bool = True,
        enable_ocr: bool = False,
        fishing: bool = True,
        sensitive: bool = True,
        sandbox_enable: bool = False,
        sandbox_detect_type: str = "STATIC",
        ai_content_detection: bool = False,
        virtual: bool = False,
        lang_content: bool = False,
        lang_attachment: bool = False,
        translate_content: bool = False,
        translate_attachment: bool = False,
) -> dict:
    """
    根据用户选择的检测功能组装 customTaskConfig。

    对应 task-config.md 中的 TaskConfig 结构，优先级高于系统默认 taskConfig。
    """
    return {
        "analysis": {
            "content": analyse_content,
            "attachmentContent": analyse_attachment,
            "enableOcr": enable_ocr,
        },
        "ruleDetection": {
            "fishing": fishing,
            "sensitive": sensitive,
            "sandbox": {
                "enable": sandbox_enable,
                "detectType": sandbox_detect_type,
            },
            "aiContentDetection": ai_content_detection,
            "virtual": virtual,
        },
        "languageDetection": {
            "content": lang_content,
            "attachmentContent": lang_attachment,
        },
        "preTranslation": {
            "content": translate_content,
            "attachmentContent": translate_attachment,
        },
    }


def api_create_task(task_name: str, detection_mode: int = 5,
                    file_paths: Optional[list[str]] = None,
                    custom_task_config: Optional[dict] = None,
                    run_id: Optional[str] = None) -> dict:
    """
    创建检测任务（POST /taskManagement/api/addAgent）。

    通过 multipart/form-data 上传本地邮件文件（对应接口 files 字段 List<MultipartFile>）。
    file_paths 为本地文件路径列表，每个文件作为 multipart 的一个 file part。
    custom_task_config 为可选的自定义任务配置，对应 TaskManagementDto.customTaskConfig。
    run_id 为 smclaw 运行 ID，作为任务 id 传入接口。
    """
    base = _base_url()
    url = f"{base}/taskManagement/api/addAgent"

    if not file_paths:
        return {"code": -1, "msg": "未提供邮件文件路径"}

    # 校验所有文件存在
    for fp in file_paths:
        if not os.path.isfile(fp):
            return {"code": -1, "msg": f"文件不存在: {fp}"}

    fields = {
        "taskName": task_name,
        "uploadType": "1",
        "detectionMode": str(detection_mode),
    }
    if run_id:
        fields["id"] = run_id
    if custom_task_config:
        fields["customTaskConfig"] = json.dumps(custom_task_config, ensure_ascii=False)

    # 读取所有文件，构建 files 列表（field name 均为 "files"，对应 List<MultipartFile>）
    files = []
    for fp in file_paths:
        filename = os.path.basename(fp)
        with open(fp, "rb") as f:
            file_bytes = f.read()
        files.append(("files", filename, file_bytes))

    return _multipart_upload(url, fields, files, timeout=120)


def api_get_progress(task_id: str) -> dict:
    """获取任务进度（GET /taskManagement/api/progress）。"""
    base = _base_url()
    url = f"{base}/taskManagement/api/progress?taskId={urllib.parse.quote(task_id)}"
    return _json_request(url)


def api_check_status(task_id: str) -> dict:
    """检查任务状态（GET /taskManagement/checkStatus/{id}）。"""
    base = _base_url()
    url = f"{base}/taskManagement/checkStatus/{urllib.parse.quote(task_id)}"
    return _json_request(url)


def api_get_report(task_id: str, report_name: str = "邮件威胁综合分析报告") -> dict:
    """获取任务报告数据（POST /api/email/open/app/report）。

    report_name 取值:
        邮件内容解读报告
        邮件安全分析报告
        邮件敏感检测报告
        邮件威胁综合分析报告（默认）
    """
    base = _base_url()
    url = f"{base}/api/email/open/app/report"
    body = {
        "taskId": task_id,
        "reportName": report_name,
    }
    return _json_request(url, method="POST", body=body, timeout=180)


def api_save_knowledge(task_id: str) -> dict:
    """保存知识库（GET /taskManagement/api/kv）。"""
    base = _base_url()
    url = f"{base}/taskManagement/api/kv?taskId={urllib.parse.quote(task_id)}"
    return _json_request(url)


def api_list_emails(task_id: str, current: int = 1, count: int = 20,
                    app_type: str = "synthesisEmail") -> dict:
    """APP邮件列表（POST /api/email/open/app/list）。

    app_type 取值:
        sensitiveEmail  — 敏感邮件
        safeEmail       — 安全邮件
        synthesisEmail  — 综合（默认）
        transactionEmail — 翻译邮件
        summaryEmail    — 总结邮件
    """
    base = _base_url()
    url = f"{base}/api/email/open/app/list"
    body = {
        "taskId": task_id,
        "current": current,
        "count": count,
        "appType": app_type,
    }
    return _json_request(url, method="POST", body=body)



def api_list_attachments(task_id: str, current: int = 1, count: int = 20) -> dict:
    """附件列表查询（POST /api/email/open/attachment/pageList）。"""
    base = _base_url()
    url = f"{base}/api/email/open/attachment/pageList"
    body = {
        "taskId": task_id,
        "current": current,
        "count": count,
    }
    return _json_request(url, method="POST", body=body)


def api_task_page_list(task_id: str) -> dict:
    """任务分页列表 — 查询单个任务详情（POST /taskManagement/pageList）。"""
    base = _base_url()
    url = f"{base}/taskManagement/pageList"
    body = {
        "taskId": task_id,
        "current": 1,
        "count": 1,
    }
    return _json_request(url, method="POST", body=body)


def api_operator_task(task_id: str, status: str) -> dict:
    """任务操作-启动/暂停/停止（GET /taskManagement/operator/{status}/{id}）。"""
    base = _base_url()
    url = f"{base}/taskManagement/operator/{urllib.parse.quote(status)}/{urllib.parse.quote(task_id)}"
    return _json_request(url)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _parse_bool(value: str) -> bool:
    """将字符串参数解析为布尔值。"""
    return value.lower() in ("true", "1", "yes", "on")


def _normalize_detection_mode(raw: Any) -> str:
    """将 detection_mode 规范化为 0-5；未传时默认使用自定义(5)。"""
    text = _non_empty_text(raw)
    if not text:
        return DETECTION_MODE_DEFAULT
    if text in DETECTION_MODES:
        return text
    alias = DETECTION_MODE_ALIASES.get(text.lower())
    if alias is not None:
        logger.info("detection_mode 别名映射: '%s' → '%s'", text, alias)
        return alias
    logger.warning("无法识别 detection_mode='%s'，使用默认值 '%s'", text, DETECTION_MODE_DEFAULT)
    return DETECTION_MODE_DEFAULT


def _normalize_report_name(raw: str) -> str:
    """将 LLM 可能传入的英文/缩写 report_name 规范化为中文全称。"""
    raw = raw.strip()
    if raw in REPORT_NAMES:
        return raw
    alias = REPORT_NAME_ALIASES.get(raw.lower())
    if alias is not None:
        logger.info("report_name 别名映射: '%s' → '%s'", raw, alias)
        return alias
    for name in REPORT_NAMES:
        if raw in name or name in raw:
            logger.info("report_name 模糊匹配: '%s' → '%s'", raw, name)
            return name
    logger.warning("无法识别 report_name='%s'，使用默认值 '%s'", raw, REPORT_NAME_DEFAULT)
    return REPORT_NAME_DEFAULT


def cmd_query_email_job(args):
    """供 packaged async handler 轮询任务状态。"""
    task_id = _resolve_task_id_arg(args)
    if not task_id:
        _fail("缺少必填参数: external_job_id")
    _output({
        "action": "query_email_job",
        **_build_async_job_payload(task_id),
    })


def cmd_callback_email_job(args):
    """供 packaged async handler 处理回调。"""
    task_id = _resolve_task_id_arg(args)
    if not task_id:
        _fail("缺少必填参数: callback_external_job_id")
    _output({
        "action": "callback_email_job",
        "callbackReceived": True,
        **_build_async_job_payload(
            task_id,
            forced_terminal=_to_optional_bool(getattr(args, "callback_terminal", None)),
            forced_success=_to_optional_bool(getattr(args, "callback_success", None)),
            forced_external_status=_non_empty_text(getattr(args, "callback_external_status", None)) or None,
        ),
    })


# ---------------------------------------------------------------------------
# Action: get_task_report
# ---------------------------------------------------------------------------

def cmd_get_task_report(args):
    """获取任务报告数据。"""
    task_id = _resolve_task_id_arg(args)
    if not task_id:
        _fail("缺少必填参数: task_id")

    report_name = _normalize_report_name(args.report_name)

    output_action = _non_empty_text(getattr(args, "output_action", None)) or "get_task_report"

    # 获取报告
    report_resp = api_get_report(task_id, report_name=report_name)
    if not _is_success(report_resp):
        _fail(f"获取报告失败: {report_resp.get('msg', 'unknown error')}", response=report_resp)

    detail_resp = api_task_page_list(task_id)
    task_info = _extract_task_info(detail_resp)

    report_email_count = task_info.get("emailCount", 0)
    report_parse_success = task_info.get("parseSuccessCount", 0)
    report_fail_count = task_info.get("failEmailCount", 0)

    report_data = report_resp.get("data", {})
    if not isinstance(report_data, dict):
        report_data = {}
    report_emails = report_data.get("emails", report_data.get("list", []))
    if not isinstance(report_emails, list):
        report_emails = []
    report_attachments = report_data.get("attachments", [])
    if not isinstance(report_attachments, list):
        report_attachments = []

    report_indicators = _extract_email_indicators(report_emails) + _extract_attachment_indicators(report_attachments)

    _output({
        "action": output_action,
        "externalJobId": task_id,
        "taskId": task_id,
        "taskInfo": {
            "taskName": task_info.get("taskName", ""),
            "emailCount": report_email_count,
            "parseSuccessCount": report_parse_success,
            "allEmailCount": task_info.get("allEmailCount", 0),
            "failEmailCount": report_fail_count,
            "status": task_info.get("status", ""),
            "detectionMode": task_info.get("detectionMode", ""),
        },
        "reportName": report_name,
        "summary": {
            "summaryText": _render_report_body(report_data),
            "taskId": task_id,
            "reportName": report_name,
            "inputTotal": report_email_count,
            "successCount": report_parse_success,
            "failedCount": report_fail_count,
        },
        "reportData": report_data,
        "evidences": [{
            "type": "task_report",
            "summary": f"{report_name}: {report_parse_success}/{report_email_count} 封邮件解析成功",
            "confidence": 0.8,
            "attributes": {
                "taskId": task_id,
                "emailCount": report_email_count,
                "parseSuccessCount": report_parse_success,
            },
        }],
        "indicators": report_indicators,
    })


# Action: list_emails
# ---------------------------------------------------------------------------

def cmd_list_emails(args):
    """查询邮件检测结果列表。"""
    task_id = _resolve_task_id_arg(args)
    if not task_id:
        _fail("缺少必填参数: task_id")

    current = int(args.current)
    count = int(args.count)
    app_type = args.app_type

    resp = api_list_emails(task_id, current, count, app_type=app_type)
    if not _is_success(resp):
        _fail(f"查询邮件列表失败: {resp.get('msg', 'unknown error')}", response=resp)

    data = resp.get("data", {})
    email_list = []
    if isinstance(data, dict):
        email_list = data.get("list", data.get("records", []))
    elif isinstance(data, list):
        email_list = data

    # 提取关键字段
    summary_list = []
    for email in email_list:
        if not isinstance(email, dict):
            continue
        summary_list.append({
            "id": email.get("id", ""),
            "subject": email.get("subject", ""),
            "sender": email.get("sender", ""),
            "senderMailBox": email.get("senderMailBox", ""),
            "recipients": email.get("recipients", []),
            "recipientsMailBox": email.get("recipientsMailBox", []),
            "threatLevel": email.get("threatLevel", ""),
            "threatValue": email.get("threatValue", 0),
            "language": email.get("language", ""),
            "sendDate": email.get("sendDate", ""),
            "attachmentCount": email.get("attachmentCount", 0),
            "attachmentName": email.get("attachmentName", []),
            "ruleNameArr": email.get("ruleNameArr", []),
            "aiSummary": email.get("aiSummary", ""),
            "tags": email.get("tags", []),
            "containLink": email.get("containLink", []),
            "emailDirection": email.get("emailDirection", ""),
        })

    _output({
        "action": "list_emails",
        "taskId": task_id,
        "current": current,
        "count": count,
        "total": len(summary_list),
        "emails": summary_list,
        "evidences": _build_email_evidences(summary_list),
        "indicators": _extract_email_indicators(summary_list),
    })


# ---------------------------------------------------------------------------
# Action: list_attachments
# ---------------------------------------------------------------------------

def cmd_list_attachments(args):
    """查询附件列表。"""
    task_id = _resolve_task_id_arg(args)
    if not task_id:
        _fail("缺少必填参数: task_id")

    current = int(args.current)
    count = int(args.count)

    resp = api_list_attachments(task_id, current, count)
    if not _is_success(resp):
        _fail(f"查询附件列表失败: {resp.get('msg', 'unknown error')}", response=resp)

    data = resp.get("data", {})
    attachment_list = []
    if isinstance(data, dict):
        attachment_list = data.get("list", data.get("records", []))
    elif isinstance(data, list):
        attachment_list = data

    summary_list = []
    for att in attachment_list:
        if not isinstance(att, dict):
            continue
        summary_list.append({
            "attachmentName": att.get("attachmentName", ""),
            "attachmentMd5": att.get("attachmentMd5", ""),
            "attachmentSize": att.get("attachmentSize", 0),
            "fileType": att.get("fileType", ""),
            "threatLevel": att.get("threatLevel", ""),
            "threatValue": att.get("threatValue", 0),
            "isEncrypt": att.get("isEncrypt", 0),
            "checkout": att.get("checkout", []),
            "detectTime": att.get("detectTime", 0),
        })

    _output({
        "action": "list_attachments",
        "taskId": task_id,
        "current": current,
        "count": count,
        "total": len(summary_list),
        "attachments": summary_list,
        "evidences": _build_attachment_evidences(summary_list),
        "indicators": _extract_attachment_indicators(summary_list),
    })


# ---------------------------------------------------------------------------
# Action: upload_email
# ---------------------------------------------------------------------------

def cmd_upload_email(args):
    """上传邮件并创建检测任务，返回 taskId。"""
    task_name = args.task_name or f"email_task_{int(time.time())}"
    detection_mode = _normalize_detection_mode(args.detection_mode)
    file_paths = _resolve_file_paths(args.file_path)

    if not file_paths:
        _fail("需要通过 --file-path 提供至少一个本地邮件文件路径")

    custom_task_config = _build_custom_task_config(
        analyse_content=_parse_bool(args.analyse_content),
        analyse_attachment=_parse_bool(args.analyse_attachment),
        enable_ocr=_parse_bool(args.enable_ocr),
        fishing=_parse_bool(args.fishing),
        sensitive=_parse_bool(args.sensitive),
        sandbox_enable=_parse_bool(args.sandbox_enable),
        sandbox_detect_type=args.sandbox_detect_type,
        ai_content_detection=_parse_bool(args.ai_content_detection),
        virtual=_parse_bool(args.virtual),
        lang_content=_parse_bool(args.lang_content),
        lang_attachment=_parse_bool(args.lang_attachment),
        translate_content=_parse_bool(args.translate_content),
        translate_attachment=_parse_bool(args.translate_attachment),
    )

    run_id = _get_run_id()
    _log(f"正在创建检测任务: {task_name}, 文件数: {len(file_paths)}, runId={run_id}")
    logger.info("customTaskConfig=%s", json.dumps(custom_task_config, ensure_ascii=False))
    create_resp = api_create_task(
        task_name=task_name,
        detection_mode=detection_mode,
        file_paths=file_paths,
        custom_task_config=custom_task_config,
        run_id=run_id,
    )

    # 任务ID已存在时视为成功（幂等）
    if create_resp.get("code") == "000001":
        _log(f"任务已存在（幂等），复用 taskId={run_id}")
        task_id = run_id
    elif not _is_success(create_resp):
        _fail(f"创建任务失败: {create_resp.get('msg', 'unknown error')}", response=create_resp)
    else:
        task_id = None
        data = create_resp.get("data")
        if isinstance(data, dict):
            task_id = data.get("id") or data.get("taskId")
        elif isinstance(data, str) and data:
            task_id = data
        if not task_id:
            task_id = run_id
            _log(f"响应未返回 taskId，使用 runId={run_id}")

    _remember_task_id(run_id, task_id)
    _log(f"任务创建成功, taskId={task_id}")
    _output({
        "action": "upload_email",
        "accepted": True,
        "externalJobId": task_id,
        "externalStatus": "SUBMITTED",
        "taskId": task_id,
        "taskName": task_name,
        "detectionMode": detection_mode,
        "message": f"邮件上传成功，任务已创建: taskId={task_id}",
    })


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="邮件上传与解析脚本")
    subparsers = parser.add_subparsers(dest="action", help="操作类型")

    def _add_task_config_args(p):
        """为子命令注册 customTaskConfig 相关的 CLI 参数。"""
        g = p.add_argument_group("customTaskConfig", "自定义检测功能配置")
        g.add_argument("--analyse-content", default="true", help="解析邮件正文 (true/false)")
        g.add_argument("--analyse-attachment", default="true", help="解析附件内容 (true/false)")
        g.add_argument("--enable-ocr", default="false", help="开启 OCR 识别 (true/false)")
        g.add_argument("--fishing", default="true", help="钓鱼邮件检测 (true/false)")
        g.add_argument("--sensitive", default="true", help="敏感词检测 (true/false)")
        g.add_argument("--sandbox-enable", default="false", help="沙箱检测 (true/false)")
        g.add_argument("--sandbox-detect-type", default="STATIC", help="沙箱检测类型: STATIC/DYNAMIC")
        g.add_argument("--ai-content-detection", default="false", help="AI 内容分析 (true/false)")
        g.add_argument("--virtual", default="false", help="虚拟机检测附件 (true/false)")
        g.add_argument("--lang-content", default="false", help="正文语种检测 (true/false)")
        g.add_argument("--lang-attachment", default="false", help="附件语种检测 (true/false)")
        g.add_argument("--translate-content", default="false", help="正文预翻译 (true/false)")
        g.add_argument("--translate-attachment", default="false", help="附件预翻译 (true/false)")

    # get_task_report
    p_report = subparsers.add_parser("get_task_report", help="获取任务报告数据")
    p_report.add_argument("--task-id", help="任务ID")
    p_report.add_argument("--external-job-id", help="异步任务 externalJobId")
    p_report.add_argument("--report-name", default="邮件威胁综合分析报告",
                          help="报告名称: 邮件内容解读报告/邮件安全分析报告/邮件敏感检测报告/邮件威胁综合分析报告")
    p_report.set_defaults(func=cmd_get_task_report)

    # fetch_email_report (async fetch)
    p_fetch = subparsers.add_parser("fetch_email_report", help="异步协议 fetch: 获取检测报告")
    p_fetch.add_argument("--external-job-id", help="异步任务 externalJobId")
    p_fetch.add_argument("--report-name", default="邮件威胁综合分析报告",
                         help="报告名称: 邮件内容解读报告/邮件安全分析报告/邮件敏感检测报告/邮件威胁综合分析报告")
    p_fetch.set_defaults(output_action="fetch_email_report")
    p_fetch.set_defaults(func=cmd_get_task_report)

    # list_emails
    p_emails = subparsers.add_parser("list_emails", help="查询邮件检测结果列表")
    p_emails.add_argument("--task-id", help="任务ID")
    p_emails.add_argument("--external-job-id", help="异步任务 externalJobId")
    p_emails.add_argument("--current", default="1", help="页码")
    p_emails.add_argument("--count", default="20", help="每页条数")
    p_emails.add_argument("--app-type", default="synthesisEmail",
                          help="邮件类型: sensitiveEmail/safeEmail/synthesisEmail/transactionEmail/summaryEmail")
    p_emails.set_defaults(func=cmd_list_emails)

    # list_attachments
    p_att = subparsers.add_parser("list_attachments", help="查询附件列表")
    p_att.add_argument("--task-id", help="任务ID")
    p_att.add_argument("--external-job-id", help="异步任务 externalJobId")
    p_att.add_argument("--current", default="1", help="页码")
    p_att.add_argument("--count", default="20", help="每页条数")
    p_att.set_defaults(func=cmd_list_attachments)

    # query_email_job (async query)
    p_query = subparsers.add_parser("query_email_job", help="异步协议 query: 查询任务状态")
    p_query.add_argument("--external-job-id", help="异步任务 externalJobId")
    p_query.set_defaults(func=cmd_query_email_job)

    # callback_email_job (async callback)
    p_callback = subparsers.add_parser("callback_email_job", help="异步协议 callback: 处理任务回调")
    p_callback.add_argument("--callback-external-job-id", help="回调 externalJobId")
    p_callback.add_argument("--callback-external-status", default="", help="回调状态")
    p_callback.add_argument("--callback-terminal", default="", help="回调是否终态")
    p_callback.add_argument("--callback-success", default="", help="回调是否成功")
    p_callback.set_defaults(func=cmd_callback_email_job)

    # upload_email (async submit)
    p_ue = subparsers.add_parser("upload_email", help="异步协议 submit: 上传邮件并创建检测任务")
    p_ue.add_argument("--task-name", default="", help="任务名称")
    p_ue.add_argument("--detection-mode", default="5", help="检测模式 (0-5)，默认自定义")
    p_ue.add_argument("--file-path", default="", help="本地邮件文件路径，多个用逗号分隔，支持 glob")
    _add_task_config_args(p_ue)
    p_ue.set_defaults(func=cmd_upload_email)

    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(1)

    _setup_file_logging()
    logger.info("action=%s, args=%s", args.action, vars(args))

    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception:
        import traceback
        tb = traceback.format_exc()
        logger.error("未捕获异常:\n%s", tb)
        print(tb, file=sys.stderr, flush=True)
        _fail(f"脚本异常终止: {tb.splitlines()[-1]}", traceback=tb)


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb, file=sys.stderr, flush=True)
        err = {"success": False, "error": f"启动异常: {tb.splitlines()[-1]}", "traceback": tb}
        print(f"errorData:{json.dumps(err, ensure_ascii=False)}", flush=True)
        sys.exit(1)
