---
name: email_parse_plugin
version: v1
description: 分析 .eml 或含邮件的 .zip 文件：必选此 skill 完成邮件威胁检测、钓鱼/敏感研判、附件扫描与综合分析报告。
---

# Email Parse Plugin

## Purpose

该技能用于处理邮件样本上传、异步检测和结果读取任务，当前能力收敛为：

- 上传本地 `.eml` 或 `.zip` 邮件样本并创建检测任务
- 轮询异步任务状态并在恢复后获取指定报告
- 查询邮件列表与附件列表，支持对检测结果继续追问
- 基于脚本标准输出 `processData:<json>` / `errorData:<json>` 返回结构化结果

这是一个以 `SKILL.md` 为主入口、以 `scripts/email_parse.py` 为执行实现的技能。主用户链路应优先走异步任务协议；只有在恢复后获取报告或用户明确要求查看明细时，才继续调用查询类动作。

## Instructions

- 主链路必须使用 `async_job.prepare` → `async_job.submit` → `run.suspend` → `async_job.finalize`，不要跳过挂起/恢复边界直接在同一轮里轮询报告。
- `async_job.prepare` 的 `handlerKey` 必须为 `packaged_skill`。
- `async_job.prepare.handlerConfig.skillName` 必须固定为 `Email Parse Plugin`。
- `handlerConfig.submitAction` / `queryAction` / `fetchAction` / `callbackAction` 必须分别使用 `upload_email` / `query_email_job` / `fetch_email_report` / `callback_email_job`。
- 输入文件必须是本地可访问的 `.eml` 或 `.zip` 路径；如果当前上下文已经有可直接使用的本地路径，优先复用，只有在确实缺少独立本地路径时才使用 `minio_download`。
- `upload_email` 默认使用 `detection_mode=5`（自定义）；主链路通常不需要手工传 `detection_mode`。
- `report_name` 必须使用中文全称；默认值为 `邮件威胁综合分析报告`。
- `get_task_report`、`list_emails`、`list_attachments` 仅在用户明确追问报告明细、邮件列表或附件列表时按需调用。
- `fetch_email_report`、`query_email_job`、`callback_email_job` 主要供异步任务处理链路使用，不是普通用户首选的直接动作。
- 成功输出统一从 stdout 的 `processData:<json>` 读取；失败输出统一从 stdout 的 `errorData:<json>` 读取。

## Action Index

- `upload_email`: 上传邮件样本并创建检测任务
- `get_task_report`: 根据任务 ID 获取指定报告
- `fetch_email_report`: 异步恢复链路获取报告
- `query_email_job`: 查询异步任务状态
- `callback_email_job`: 处理异步回调载荷
- `list_emails`: 查询任务下的邮件列表
- `list_attachments`: 查询任务下的附件列表

## Action Usage

统一脚本入口：`python scripts/email_parse.py <action> [arguments]`

| Action | Command | 说明 |
| --- | --- | --- |
| `upload_email` | `python scripts/email_parse.py upload_email --file-path <file_path> [--task-name <task_name>]` | 上传本地邮件样本并创建检测任务 |
| `get_task_report` | `python scripts/email_parse.py get_task_report --task-id <task_id> --report-name <report_name>` | 获取指定类型的报告 |
| `fetch_email_report` | `python scripts/email_parse.py fetch_email_report --external-job-id <external_job_id> --report-name <report_name>` | 异步恢复链路获取报告 |
| `query_email_job` | `python scripts/email_parse.py query_email_job --external-job-id <external_job_id>` | 查询异步任务状态 |
| `callback_email_job` | `python scripts/email_parse.py callback_email_job --callback-external-job-id <callback_external_job_id> --callback-external-status <callback_external_status> --callback-terminal <callback_terminal> --callback-success <callback_success>` | 处理回调状态 |
| `list_emails` | `python scripts/email_parse.py list_emails --task-id <task_id> --current <current> --count <count> --app-type <app_type>` | 查询邮件检测结果列表 |
| `list_attachments` | `python scripts/email_parse.py list_attachments --task-id <task_id> --current <current> --count <count>` | 查询附件列表 |

参数约束：

- `--file-path`：一个本地 `.eml` 或 `.zip` 文件路径
- `--task-id`：检测任务 ID，通常来自 `upload_email` 返回的 `taskId` / `externalJobId`
- `--external-job-id`：异步任务外部 ID，当前实现与任务 ID 对齐
- `--report-name`：中文全称，推荐默认 `邮件威胁综合分析报告`
- `--current` / `--count`：分页参数
- `--app-type`：邮件列表筛选类型，默认 `synthesisEmail`

输入文件约定：

- 当前主业务输入为单个本地 `.eml` 或 `.zip` 文件
- 如果原始文件位于对象存储且当前上下文没有可直接复用的本地路径，需要先下载到本地再传入 `--file-path`
- `task_name` 可缺省，脚本会自动生成
- 布尔开关如 `fishing`、`sensitive`、`analyse_content`、`analyse_attachment` 默认已经在脚本和分析配置中给出安全默认值

运行约定：

- 脚本统一输出 `processData:<json>` 或 `errorData:<json>`
- `EMAIL_PARSE_BASE_URL` 用于注入邮件检测系统地址（skill 内置默认值 `https://192.168.180.129:8323`，环境变量可覆盖）
- `fetch_email_report` 复用 `get_task_report` 的报告获取逻辑，但输出动作名不同
- `query_email_job` / `callback_email_job` 主要服务于异步任务协议

## Output Contract

成功时调用方应直接读取 `processData:<json>` 中的 JSON 负载。常见字段包括：

- `success`：固定为 `true`
- `action`：本次执行的动作名
- `summary`：结果摘要
- `taskId`：邮件检测任务 ID
- `externalJobId`：异步任务外部 ID
- `externalStatus`：异步状态，例如 `SUBMITTED`、运行中或终态
- `reportName`：当前返回的报告名称
- `status`：任务状态或报告状态

异步主链路中，`upload_email` 常见返回字段包括：

- `accepted`
- `taskId`
- `externalJobId`
- `externalStatus`
- `summary`

报告查询类动作通常返回：

- `taskId`
- `reportName`
- `summary`
- 报告主体数据或平台返回的结构化结果

列表查询类动作通常返回：

- `current`
- `count`
- `total`
- `records` 或同等含义的数据列表字段

失败时调用方应读取 `errorData:<json>`，常见字段包括：

- `success`
- `error`
- 与失败上下文相关的辅助字段，例如 `filePath`、`taskId`、`reportName`、`response`、`exception`

## Examples

主用户链路应优先使用异步任务协议，而不是在同一轮里手工轮询。底层脚本调用示例如下：

```bash
python scripts/email_parse.py upload_email --file-path D:\data\sample.eml --task-name case-001
```

```bash
python scripts/email_parse.py get_task_report --task-id <task_id> --report-name "邮件威胁综合分析报告"
```

```bash
python scripts/email_parse.py list_attachments --task-id <task_id> --current 1 --count 20
```

如果用户只是要求“分析这个 `.eml`/`.zip` 文件”，优先触发异步检测主链路；只有在用户继续追问报告内容、邮件列表或附件列表时，再调用对应查询动作。

## Load More

- `scripts/email_parse.py`: 邮件上传、异步任务状态查询、报告获取、邮件/附件列表查询的唯一执行脚本
- `api-doc.md`: 邮件威胁检测系统接口说明
- `task-config.md`: 任务配置字段与默认值说明
