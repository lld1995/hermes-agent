# Sandbox File Analyze Skill (Hermes)

Minimal wrapper around the 数默科技 沙箱 "三方样本在线提交" WebAPI. Lets
Hermes upload a file, wait for static + dynamic analysis to finish, and
fetch the resulting report.

## Layout

```
sandbox/
├── SKILL.md                         # Hermes skill entrypoint
├── assets/
│   └── sandbox_client.py            # Stand-alone Python CLI + library
├── references/
│   └── sandbox_webapi.docx          # Vendor API spec (reference only)
└── README.md
```

## Prerequisites

- Python 3.9+ with `requests` on `PATH` (the skill declares
  `prerequisites.python: [requests]`).
- Network access to the sandbox appliance (HTTPS on the configured port,
  e.g. `https://192.168.190.195:6868`).
- An online-task **任务组 token** pre-provisioned in the sandbox UI
  (菜单：任务管理 → 新建在线任务 → 复制 token).

## Configuration

Set the two env vars once per shell / session:

```bash
export SANDBOX_URL='https://192.168.190.195:6868'
export SANDBOX_TOKEN='2703d6738dcacabefaa57895afc1d928db88'
```

Or pass them as `--url` / `--token` to the client each time.

## Install

Copy into the Hermes skills dir, or point Hermes at this folder via
`~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /data/code/lld/hermes-agent/sm-skills
```

Verify the skill is visible:

```bash
hermes skills                        # interactive enable/disable UI
```

Inside a Hermes session you can also check:

```
/skills                              # search + manage skills
skills_list                          # lists registered skills
skill_view sandbox-file-analyze      # loads full instructions
```

## Trigger

Describe the task in natural language, e.g.:

> 帮我分析一下 `/tmp/malware.exe`，看看静态和动态威胁，出个报告。

The agent loads `SKILL.md`, runs
`python3 assets/sandbox_client.py analyze ...`, polls until the sandbox
finishes, and summarises the report.

## Standalone use

The client also runs outside Hermes as a plain CLI:

```bash
python3 assets/sandbox_client.py analyze /path/to/sample.exe -o report.json
python3 assets/sandbox_client.py check-md5 <md5> --file-name foo.exe --file-size 12345
python3 assets/sandbox_client.py report <taskId> --part signatures
```

See `python3 assets/sandbox_client.py --help` for the full surface.

## What is *not* implemented

Only the four "三方样本在线提交" endpoints
(`checkSampleMD5`, `pushSample`, `waitSampleReport`,
`sandbox/report/{taskId}/{part}`). The rest of the WebAPI (task-group
management, yara rule CRUD, audit logs, attachment download, VM
management, etc.) is documented in `references/sandbox_webapi.docx` but
requires the RSA-login / `Auth-Token` flow which is out of scope for the
"upload a file → get a report" use case.
