---
name: async-threat-intel-batch
description: 查/分析IP/域名是否可疑/恶意：威胁情报、归属、信誉、APT、C2、Tor、IOC富化
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [threat-intel, ioc, security, async, enrichment, csv, log-analysis, 安全日志, 威胁情报, 日志分析, ip-reputation, domain-reputation, c2-detection, apt]
prerequisites:
  commands: [java]
---

# Async Threat Intel Batch

Enrich a list of IOCs (IPs / domains, one per line) by driving the bundled
`threat-intel-plugin.jar` through its four-action async lifecycle. The JAR
talks to an external threat-intel backend; this skill is just the
orchestration contract.

## When to use

This skill's job is simple: **the user hands you one or more IP addresses
or domains — in any form — and wants to know something about them.**
Load it whenever the task plausibly reduces to that, regardless of file
format, framing, or wording.

Trigger scenarios (non-exhaustive):

- **Any file that might contain IPs / domains.** `.txt` / `.csv` / `.json`
  IOC lists, security logs (`.log`, syslog, firewall / IDS / EDR / WAF /
  proxy / DNS / webserver / audit / VPN), SIEM exports, alert JSON,
  PCAP-derived lists, spreadsheets with IP columns, mail-header dumps,
  `netstat` output, etc.
- **IPs / domains pasted directly in the prompt** — no file needed.
  Persist them to a temp file and run the skill.
- **Questions about specific indicators**, phrased any way: "这些 IP 是谁",
  "这个域名靠谱吗", "这里有没有恶意的", "帮我查一下",
  "看看这些地址", "is this IP malicious", "reputation of foo.com",
  "who owns this IP", "is this a Tor exit", "C2 识别", "APT 归因",
  "威胁情报", "IOC 研判/富化", "enrichment", "attribution".
- **Follow-up work on an alert, incident, or log sample** where the
  natural next step is checking the IPs / domains against TI.

**When *not* to use:**

- The user wants a one-off lookup for a single IP/domain and is happy
  with a direct web search — this skill is tuned for batch jobs.
- The file contains no network indicators at all (e.g. pure source code,
  binary dumps without strings, a CSV of user names).
- The user already has enrichment data and is just asking about
  formatting / statistics on it.

## Preparing the input

The JAR only accepts a plain text file with **one IP or domain per line**.
Normalise whatever the user gave you into that shape first:

1. **Already a clean IOC list?** Use it as-is.
2. **A log, alert, or any other text file?** Extract IPs + domains with
   `grep -oE`, dedupe, write to a temp file, then submit:
   ```bash
   { grep -oE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$SRC";
     grep -oE '\b([a-zA-Z0-9][a-zA-Z0-9-]*\.)+[a-zA-Z]{2,}\b' "$SRC"; } \
     | sort -u > /tmp/ioc.txt
   ```
   Drop obvious false positives (bare filenames like `payload.bin`,
   version strings like `1.2.3`, etc.) before submission.
3. **IPs / domains pasted in the prompt?** Write them to a temp file
   first, one per line.
4. **Binary or non-text input** (pcap, zip, xlsx)? Either decline or
   extract text first with the appropriate tool, then re-enter step 2.

Report to the user what you extracted before submitting — counts and
samples — so they can correct course if the extraction is wrong.

## Inputs

- `input_file` — absolute path to a `.txt` file with one IOC per line.
  Generate it yourself from whatever the user gave you, per the rules
  above.
- `output_dir` — where to drop the final artifact. Default: the same
  directory as `input_file`, or a fresh temp dir if the user is on a
  sandboxed backend.

## Commands

The JAR lives at `assets/threat-intel-plugin.jar` inside this skill. Resolve
its absolute path once and reuse it (`JAR` below). All commands are run via
the `run_command` tool.

```bash
JAR="<skill_dir>/assets/threat-intel-plugin.jar"

# 1. Submit — returns an external_job_id on stdout
java -jar "$JAR" submit_batch <input_file>

# 2. Query — returns status: PENDING | RUNNING | SUCCESS | FAILED | CANCELLED
java -jar "$JAR" query_batch <external_job_id>

# 3. Fetch — downloads the artifact into <output_dir>
java -jar "$JAR" fetch_result <external_job_id> <output_dir>

# 4. Cancel — only if the user explicitly asks to abort
java -jar "$JAR" cancel_batch <external_job_id>
```

`<skill_dir>` is the directory reported by `skill_view` under `skill_dir`.

## Procedure

1. **Validate input.** Read the first few lines of `input_file`; confirm it
   is plain text with one IP or domain per line. Abort with a clear error
   if the file is binary, empty, or looks malformed.
2. **Submit.** Run `submit_batch`; capture the `external_job_id` from
   stdout. Report the job id to the user.
3. **Poll.** Call `query_batch` every 15 seconds. Cap polling at 30 minutes
   by default; if exceeded, surface the current status and ask the user
   whether to keep waiting or cancel. Do **not** busy-loop without sleeping.
4. **Fetch.** On `SUCCESS`, run `fetch_result` into `output_dir` and list
   the produced files to the user with their absolute paths.
5. **Summarise.** After fetch, briefly describe what's in the artifact
   (row count, columns, notable hits if easily extractable). Never invent
   enrichment results — only summarise what the file actually contains.
6. **Handle failure.** On `FAILED` or non-zero exit codes, show the stderr
   from the JAR verbatim and stop. Do not retry automatically unless the
   user asks.

## Notes

- The backend is async by design. Tell the user up-front that the job may
  take several minutes before you begin polling.
- If the caller wants to cancel mid-run, use `cancel_batch <id>` and then
  report the terminal status from one final `query_batch`.
- The skill deliberately does **not** upload artifacts to object storage
  or emit chat events — those were concerns of the original platform. In
  Hermes, the artifact ends up on local disk and the agent cites the path.

## Legacy workflow definition

The original bundle was authored against a different platform's workflow
engine. That YAML is preserved at `references/workflow.yaml` for reference
only — it is not executed by Hermes.