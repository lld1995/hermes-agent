#!/usr/bin/env python3
"""Minimal client for the 数默科技 沙箱 online-submission WebAPI.

Covers only the "三方样本在线提交" path (simple token auth — no RSA login).
Implements the four endpoints that together let you upload a file, wait for
its static + dynamic analysis to finish, and fetch the report:

    POST /api/fileDetect/v1/sandbox/checkSampleMD5     # dedupe by md5
    POST /api/fileDetect/v1/sandbox/pushSample         # multipart upload
    POST /api/fileDetect/v1/sandbox/waitSampleReport   # poll brief (blocks ~5s)
    GET  /api/fileDetect/v1/sandbox/report/{taskId}/{part}?token=...

Env vars (used as defaults):
    SANDBOX_URL     base URL, e.g. https://192.168.190.195:6868
    SANDBOX_TOKEN   online-task group token

Usage:
    python sandbox_client.py analyze /path/to/sample.exe
    python sandbox_client.py analyze sample.exe --detect-type STATIC -o out.json
    python sandbox_client.py check-md5 <md5> --file-name foo.exe --file-size 1234
    python sandbox_client.py submit sample.exe
    python sandbox_client.py poll
    python sandbox_client.py report <taskId> --part report -o report.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REPORT_PARTS = (
    "report", "target", "signatures", "behavior",
    "network", "dropped", "procdump",
)
DETECT_TYPES = ("DYNAMIC", "STATIC")


class SandboxError(RuntimeError):
    pass


class SandboxClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        verify: bool = False,
        timeout: int = 120,
    ) -> None:
        if not base_url:
            raise SandboxError("base_url is required (e.g. SANDBOX_URL env var)")
        if not token:
            raise SandboxError("token is required (e.g. SANDBOX_TOKEN env var)")
        self.base = base_url.rstrip("/")
        self.token = token
        self.verify = verify
        self.timeout = timeout

    # --- low-level endpoints ------------------------------------------------

    def check_md5(
        self,
        md5: str,
        file_name: str,
        file_size: int,
        detect_type: str = "DYNAMIC",
        file_type: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "token": self.token,
            "md5": md5,
            "file_name": file_name,
            "file_size": file_size,
            "detect_type": detect_type,
        }
        if file_type:
            body["file_type"] = file_type
        r = requests.post(
            f"{self.base}/api/fileDetect/v1/sandbox/checkSampleMD5",
            json=body, verify=self.verify, timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def push_sample(
        self,
        file_path: str | os.PathLike[str],
        *,
        detect_type: str = "DYNAMIC",
        dict_pw: str | None = None,
        environment: str | None = None,
        detect_sys: str | None = None,
    ) -> dict[str, Any]:
        p = Path(file_path)
        if not p.is_file():
            raise SandboxError(f"file not found: {p}")
        params: dict[str, Any] = {
            "token": self.token,
            "detectType": detect_type,
            "fileName": p.name,
            "fileSize": p.stat().st_size,
        }
        if dict_pw:
            params["dict"] = dict_pw
        if environment:
            params["environment"] = environment
        if detect_sys:
            params["detectSys"] = detect_sys
        with open(p, "rb") as f:
            files = {"file": (p.name, f, "application/octet-stream")}
            data = {"params": json.dumps(params, ensure_ascii=False)}
            r = requests.post(
                f"{self.base}/api/fileDetect/v1/sandbox/pushSample",
                files=files, data=data,
                verify=self.verify, timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()

    def wait_sample_report(self) -> dict[str, Any]:
        r = requests.post(
            f"{self.base}/api/fileDetect/v1/sandbox/waitSampleReport",
            data={"token": self.token},
            verify=self.verify, timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_report(self, task_id: str, part: str = "report") -> dict[str, Any]:
        if part not in REPORT_PARTS:
            raise SandboxError(f"invalid part {part!r}; choose from {REPORT_PARTS}")
        r = requests.get(
            f"{self.base}/api/fileDetect/v1/sandbox/report/{task_id}/{part}",
            params={"token": self.token},
            verify=self.verify, timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    # --- high-level orchestration ------------------------------------------

    def analyze(
        self,
        file_path: str | os.PathLike[str],
        *,
        detect_type: str = "DYNAMIC",
        dict_pw: str | None = None,
        force: bool = False,
        part: str = "report",
        poll_interval: float = 5.0,
        poll_timeout: float = 1800.0,
        on_event: callable | None = None,
    ) -> dict[str, Any]:
        """Upload → wait → fetch. Returns {task_id, brief, full, cached}."""
        p = Path(file_path)
        if not p.is_file():
            raise SandboxError(f"file not found: {p}")

        def emit(stage: str, **kw: Any) -> None:
            if on_event:
                on_event(stage, **kw)

        md5 = _md5_file(p)
        size = p.stat().st_size
        emit("md5", md5=md5, size=size)

        # 1. dedupe check
        if not force:
            chk = self.check_md5(md5, p.name, size, detect_type=detect_type)
            emit("check_md5", response=chk)
            if chk.get("code") == "000000" and chk.get("data"):
                # Sample already analyzed; brief is returned directly.
                # checkSampleMD5 does not include a taskId so we cannot fetch
                # the full report for a cached hit without re-submission.
                return {
                    "task_id": None,
                    "brief": chk["data"],
                    "full": None,
                    "cached": True,
                }

        # 2. submit
        sub = self.push_sample(p, detect_type=detect_type, dict_pw=dict_pw)
        emit("submit", response=sub)
        if sub.get("code") != "000000":
            raise SandboxError(f"pushSample failed: {sub}")
        data = sub.get("data") or {}
        # spec says `taskId` (singular); real server returns `taskIds` (array).
        task_id = data.get("taskId")
        if not task_id:
            task_ids = data.get("taskIds") or []
            if task_ids:
                task_id = task_ids[0]
        if not task_id:
            raise SandboxError(f"pushSample returned no taskId: {sub}")
        emit("submitted", task_id=task_id)

        # 3. poll the report endpoint directly by taskId. We use `target`
        # (base-info block) since it is small and is the first thing the
        # sandbox populates when a task completes.
        target = self._poll_target(
            task_id=task_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            on_event=emit,
        )
        brief = (target.get("data") or {}).get("baseInfo") or target.get("data")

        # 4. fetch requested full block
        if part == "target":
            full = target
        else:
            full = self.get_report(task_id, part=part)
        emit("report", task_id=task_id, part=part)
        return {
            "task_id": task_id,
            "brief": brief,
            "full": full,
            "cached": False,
        }

    def _poll_target(
        self,
        *,
        task_id: str,
        poll_interval: float,
        poll_timeout: float,
        on_event: callable,
    ) -> dict[str, Any]:
        """Poll GET report/{taskId}/target until success code appears.

        We do not rely on waitSampleReport because the appliance's
        implementation of that endpoint is inconsistent with the spec
        (method-not-supported / token-not-recognised on common variants).
        The `target` block is the smallest and returns as soon as the
        task has a persisted report record.
        """
        start = time.time()
        attempts = 0
        last = {}
        while time.time() - start < poll_timeout:
            attempts += 1
            try:
                resp = self.get_report(task_id, part="target")
                last = resp
            except requests.RequestException as e:
                last = {"error": str(e)}
                resp = last
            code = str(resp.get("code")) if isinstance(resp, dict) else ""
            on_event(
                "poll", attempt=attempts,
                elapsed=time.time() - start,
                code=code, msg=(resp.get("msg") if isinstance(resp, dict) else None),
            )
            if code == "000000" and (resp.get("data") or {}):
                return resp
            time.sleep(poll_interval)
        raise TimeoutError(
            f"report for taskId={task_id} not ready after {poll_timeout}s "
            f"({attempts} poll attempts); last response: {last}"
        )


def _md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- CLI ------------------------------------------------------------------

def _client_from_args(args: argparse.Namespace) -> SandboxClient:
    url = args.url or os.environ.get("SANDBOX_URL")
    token = args.token or os.environ.get("SANDBOX_TOKEN")
    return SandboxClient(url, token, verify=args.verify, timeout=args.timeout)


def _dump(obj: Any, out_path: str | None) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    if out_path and out_path != "-":
        Path(out_path).write_text(text, encoding="utf-8")
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        print(text)


def _cmd_check_md5(args: argparse.Namespace) -> int:
    client = _client_from_args(args)
    resp = client.check_md5(
        md5=args.md5, file_name=args.file_name, file_size=args.file_size,
        detect_type=args.detect_type, file_type=args.file_type,
    )
    _dump(resp, args.output)
    return 0


def _cmd_submit(args: argparse.Namespace) -> int:
    client = _client_from_args(args)
    resp = client.push_sample(
        args.file, detect_type=args.detect_type, dict_pw=args.dict,
        environment=args.environment, detect_sys=args.detect_sys,
    )
    _dump(resp, args.output)
    return 0 if resp.get("code") == "000000" else 2


def _cmd_poll(args: argparse.Namespace) -> int:
    client = _client_from_args(args)
    resp = client.wait_sample_report()
    _dump(resp, args.output)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    client = _client_from_args(args)
    resp = client.get_report(args.task_id, part=args.part)
    _dump(resp, args.output)
    return 0 if resp.get("code") == "000000" else 2


def _cmd_analyze(args: argparse.Namespace) -> int:
    client = _client_from_args(args)

    def on_event(stage: str, **kw: Any) -> None:
        if args.quiet:
            return
        if stage == "md5":
            print(f"[md5] {kw['md5']}  ({kw['size']} bytes)", file=sys.stderr)
        elif stage == "check_md5":
            resp = kw["response"]
            has = bool(resp.get("data"))
            print(f"[check] existing report: {has}", file=sys.stderr)
        elif stage == "submitted":
            print(f"[submit] taskId={kw['task_id']}", file=sys.stderr)
        elif stage == "poll":
            extra = f" code={kw.get('code')}" if kw.get("code") else ""
            print(f"[poll] attempt={kw['attempt']} elapsed={kw['elapsed']:.1f}s{extra}",
                  file=sys.stderr)
        elif stage == "report":
            print(f"[report] fetched part={kw['part']}", file=sys.stderr)

    result = client.analyze(
        args.file,
        detect_type=args.detect_type,
        dict_pw=args.dict,
        force=args.force,
        part=args.part,
        poll_interval=args.poll_interval,
        poll_timeout=args.poll_timeout,
        on_event=on_event,
    )
    _dump(result, args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sandbox_client",
        description="Minimal client for the 数默科技 sandbox online-submission API.",
    )
    p.add_argument("--url", help="Base URL; defaults to $SANDBOX_URL")
    p.add_argument("--token", help="Online task group token; defaults to $SANDBOX_TOKEN")
    p.add_argument("--verify", action="store_true",
                   help="Verify TLS certs (default: off; self-signed assumed)")
    p.add_argument("--timeout", type=int, default=120, help="HTTP timeout seconds")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="One-shot: dedupe → submit → poll → report")
    a.add_argument("file")
    a.add_argument("--detect-type", choices=DETECT_TYPES, default="DYNAMIC",
                   help="DYNAMIC runs dynamic+static engines; STATIC skips dynamic")
    a.add_argument("--part", choices=REPORT_PARTS, default="report")
    a.add_argument("--dict", help="Archive passwords (comma-separated)")
    a.add_argument("--force", action="store_true",
                   help="Skip checkSampleMD5 and always re-submit")
    a.add_argument("--poll-interval", type=float, default=5.0)
    a.add_argument("--poll-timeout", type=float, default=1800.0)
    a.add_argument("-o", "--output", help="Write JSON to file (- for stdout)")
    a.add_argument("-q", "--quiet", action="store_true")
    a.set_defaults(func=_cmd_analyze)

    c = sub.add_parser("check-md5", help="Lookup existing report by MD5")
    c.add_argument("md5")
    c.add_argument("--file-name", required=True)
    c.add_argument("--file-size", type=int, required=True)
    c.add_argument("--file-type")
    c.add_argument("--detect-type", choices=DETECT_TYPES, default="DYNAMIC")
    c.add_argument("-o", "--output")
    c.set_defaults(func=_cmd_check_md5)

    s = sub.add_parser("submit", help="Upload a sample (raw pushSample call)")
    s.add_argument("file")
    s.add_argument("--detect-type", choices=DETECT_TYPES, default="DYNAMIC")
    s.add_argument("--dict")
    s.add_argument("--environment")
    s.add_argument("--detect-sys")
    s.add_argument("-o", "--output")
    s.set_defaults(func=_cmd_submit)

    pl = sub.add_parser("poll", help="One waitSampleReport call (blocks ~5s)")
    pl.add_argument("-o", "--output")
    pl.set_defaults(func=_cmd_poll)

    r = sub.add_parser("report", help="Fetch a report block by taskId")
    r.add_argument("task_id")
    r.add_argument("--part", choices=REPORT_PARTS, default="report")
    r.add_argument("-o", "--output")
    r.set_defaults(func=_cmd_report)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except SandboxError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except requests.RequestException as e:
        print(f"http error: {e}", file=sys.stderr)
        return 3
    except TimeoutError as e:
        print(f"timeout: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())
