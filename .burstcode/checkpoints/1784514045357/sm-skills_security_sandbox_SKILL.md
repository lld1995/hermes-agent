---
name: sandbox-file-analyze
description: 上传文件到数默沙箱，获取静态+动态威胁分析报告（malscore、yara、病毒库、行为/网络日志等）
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [sandbox, malware-analysis, static-analysis, dynamic-analysis, file-detection, 沙箱, 威胁分析, 恶意样本, yara, ioc, 数默科技, shumo]
prerequisites:
  commands: [python3]
  python: [requests]
required_environment_variables:
  - name: SANDBOX_URL
    prompt: "数默沙箱 Base URL (例: https://192.168.190.195:6868)"
    help: "沙箱 appliance 的 HTTPS 根地址，含端口"
  - name: SANDBOX_TOKEN
    prompt: "沙箱在线任务组 token"
    help: "沙箱 UI：任务管理 → 新建在线任务 → 复制 token"
---

# Sandbox File Analyze

Thin wrapper around the 数默科技 沙箱 "三方样本在线提交" (online submission)
WebAPI. Uploads a sample, waits for the sandbox to run its static + dynamic
engines, then fetches the brief + full analysis report.

Only the online-submission endpoints are implemented — those use a single
pre-configured **任务组 token** and do not require the RSA login / `Auth-Token`
flow that the full WebAPI surface needs.

## When to use

The user hands you a file (an executable, document, script, PDF, archive,
email attachment, etc.) — or a path to one — and wants to know whether it
is malicious, what it does, or both.

Trigger phrasings include:

- "帮我分析一下这个文件 / 这个样本"
- "跑一下沙箱 / 静态分析 / 动态分析"
- "这个 exe / doc / pdf 是恶意的吗"
- "上传到沙箱看看威胁值 / malscore / yara 命中"
- "帮我提取 IOC / C2 / 行为 / 网络行为"
- "analyze this sample", "sandbox scan", "detonate this file"
- Any follow-up on an alert / IR where the next step is detonation.

**When *not* to use:**

- The user only has a hash (md5) and already has a report — use a simple
  IOC-lookup skill instead.
- The input is not a file (URL, IP, domain → use threat-intel skills).
- The sandbox endpoint is unreachable from the current host (check first
  with `curl -k` if unsure).

## Configuration

The client reads two env vars, or accepts them as CLI flags:

| Variable | Description | Example |
|----------|-------------|---------|
| `SANDBOX_URL` | Base URL of the sandbox | `https://192.168.190.195:6868` |
| `SANDBOX_TOKEN` | Online-task **任务组 token** configured in the sandbox UI | `2703d67…` |

TLS verification is off by default (self-signed certs on internal
deployments are assumed); pass `--verify` when talking to a properly-signed
endpoint.

Resolution order for the client:

1. `--url` / `--token` CLI flags.
2. `SANDBOX_URL` / `SANDBOX_TOKEN` env vars.

If neither is set, the client aborts with a clear error.

## Asset layout

```
sandbox/
├── SKILL.md                         # this file
├── assets/
│   └── sandbox_client.py            # self-contained client (requests only)
├── references/
│   └── sandbox_webapi.docx          # vendor spec, not executed
└── README.md
```

`<skill_dir>` is the directory returned by `skill_view` under `skill_dir`.
Resolve the absolute path to `assets/sandbox_client.py` once and reuse it
(`CLIENT` below).

## Commands

```bash
CLIENT="<skill_dir>/assets/sandbox_client.py"
export SANDBOX_URL="https://192.168.190.195:6868"
export SANDBOX_TOKEN="..."

# One-shot: md5 dedupe → submit → poll brief → fetch full report
python3 "$CLIENT" analyze /path/to/sample.exe -o /tmp/report.json

# Force a re-submission even if the sandbox already has a cached report
python3 "$CLIENT" analyze sample.exe --force

# Static-only (skip dynamic detonation)
python3 "$CLIENT" analyze sample.exe --detect-type STATIC

# Protected archive
python3 "$CLIENT" analyze malware.zip --dict 'infected,infected123'

# Pick a specific report block:
#   report | target | signatures | behavior | network | dropped | procdump
python3 "$CLIENT" analyze sample.exe --part behavior -o /tmp/behavior.json

# Lower-level commands
python3 "$CLIENT" check-md5 <md5> --file-name foo.exe --file-size 12345
python3 "$CLIENT" submit   sample.exe                    # just pushSample
python3 "$CLIENT" poll                                   # one waitSampleReport
python3 "$CLIENT" report   <taskId> --part signatures
```

The `analyze` subcommand prints progress lines to stderr (`[md5]`,
`[check]`, `[submit] taskId=…`, `[poll]`, `[report]`). Use `-q` to silence.

## Procedure

1. **Validate input.** Confirm `file_path` exists and is a regular file.
   Abort early if the file is empty or a directory.
2. **Resolve config.** Ensure `SANDBOX_URL` and `SANDBOX_TOKEN` are set
   (env vars or explicit flags). If missing, ask the user.
3. **Run `analyze`.** Default `--detect-type DYNAMIC` — this runs both
   static and dynamic engines server-side (the brief's `engine_type`
   comes back as `dynamic_static`). Use `STATIC` only when the user
   explicitly asks to skip detonation.
4. **Redirect the full JSON** to a file via `-o /tmp/<name>.report.json`.
   Reports can be large (dozens of MB for dropped/procdump blocks).
5. **Summarise for the user.** Read `brief.malscore`, `brief.threat_tags`,
   `brief.virus_lib`, `brief.yara_lib`, `brief.engine_type`, `brief.file_type`,
   plus a short digest of the full report's `signatures` / `network` blocks.
   Never invent findings — only summarise what the JSON actually contains.
6. **Handle cached samples.** When the file's MD5 is already known to the
   sandbox, `analyze` returns `cached: true` with the brief from the
   server's cache. The `full` field may be `null` if the server didn't
   requeue a report for us — tell the user it's a cached result and offer
   `--force` to re-detonate.
7. **Handle timeouts.** The default poll budget is 30 minutes. On timeout,
   surface the taskId to the user so they can check the sandbox UI or
   re-run `python3 "$CLIENT" report <taskId>` later.

## Threat-value scale

From the 检测报告列表查询 spec — `malscore` / `threatValue` interpretation:

| Range | Level |
|-------|-------|
| `[0, 2)`  | 正常 / normal |
| `[2, 4)`  | 低危 / low |
| `[4, 6)`  | 中危 / medium |
| `[6, 10]` | 高危 / high |

## Notes

- The endpoint uses HTTPS on a non-standard port (`:6868`) with a
  self-signed cert on appliance deployments — do not turn on `--verify`
  unless the operator has installed a proper CA.
- **Polling strategy.** The client polls `GET report/{taskId}/target`
  (a small JSON block) rather than `waitSampleReport`, because some
  appliance builds return `method not supported` for POST on
  `waitSampleReport` and reject the token when that endpoint is hit
  via GET. Querying the report endpoint directly with the `taskId`
  returned by `pushSample` is the most portable path.
- The `poll` subcommand (raw `waitSampleReport`) is kept for parity with
  the vendor spec but may return a method-not-supported error on those
  appliance builds.
- The full WebAPI surface (task-group management, yara rules, audit logs,
  attachment download, etc.) is documented in
  `references/sandbox_webapi.docx` but is **not** implemented here — it
  needs the RSA-login / `Auth-Token` flow which is out of scope for this
  "upload a file → get a report" skill.
- `report/{taskId}/{part}` returns JSON describing where the pcap /
  procdump / dropped files live on the sandbox; downloading those
  attachments requires the WebAPI `Auth-Token` flow and is not wired in.
