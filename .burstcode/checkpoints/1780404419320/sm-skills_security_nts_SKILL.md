---
name: nts-pcap-fetch
description: 根据告警四元组+时间从智隼 NTS 下载 pcap：列链路 / 批量取包 / payload / IOC 查询
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [nts, 智隼, 威胁分析, pcap, 数据包, 四元组, 告警, 数默科技, shumo, threat-analysis, packet-capture, forensics, log-analysis]
prerequisites:
  commands: [python3]
  python: [requests]
---

# NTS PCAP Fetch

Thin client for the 智隼网络高级威胁分析系统 (WebAPI v7.3.0).

Drives the `/open-api/v1/*` endpoints that v7.3.0 actually exposes:
list netlinks → download pcap by **四元组+时间** → payload / IOC queries.

## When to use

Load this skill when the user wants to pull packet evidence out of an NTS
appliance. Typical asks:

- "拉一下 NTS 最近 10 分钟的告警包"
- "根据这条告警的四元组+时间在智隼里下 pcap"
- "从智隼下线一段时间段的流量"
- "查 NTS 里这个 ip/域名/hash/url 有没有出现过"
- "用智隼的 payload 接口看前 N 个包负载"

**When *not* to use:**

- The user hasn't got an NTS appliance; this skill only talks to v7.3.0
  boxes from 成都数默科技 (智隼).
- The user wants the **full WebAPI surface** (task management, upgrade
  packages, country/protocol/app enums). Extend `assets/nts_client.py`
  rather than starting from scratch.
- The user wants to *upload* a pcap back into NTS to rerun analysis.
  **v7.3.0 does not expose that path** — see "Scope & limits" below.

## Scope & limits

The v7.3.0 docx (`references/智隼网络高级威胁分析系统_webapi接口说明_V7.3.0.docx`)
does **not** document:

- An **alert pull** API. NTS pushes alerts out over syslog/kafka/flume
  (see `/open-api/v1/status/push`). The canonical workflow is therefore:
  the user brings an alert log file (or a list of four-tuples) from
  their SIEM → this skill turns it into pcap files on disk.
- An **upload-pcap / create-offline-link / rerun-model** API. Offline
  link creation and re-analysis are UI-only in v7.3.0. Once the pcap is
  on disk, hand the path to a separate analysis skill (for example
  `sm-skills/security/sandbox`) or to the user to upload manually.
- A unified **analysis-result** API beyond the 2.2.x IOC queries. Use
  `query-ioc` after the fact if the caller wants to see what NTS already
  knows about an IP / domain / hash / URL / email / cert / ja3.

If a later docx version adds these, extend `nts_client.py` with
`create_offline_link()` / `upload_pcap()` / `get_analysis()` and update
`workflow` to chain them.

## Configuration

Two env vars or CLI flags:

| Variable | Description | Example |
|----------|-------------|---------|
| `NTS_URL` | Base URL of the NTS appliance | `https://192.168.180.212:2443` |
| `NTS_TOKEN` | `Auth-Key` token configured under 安全运营 → 数据对接配置 → API接口 | *(60-char opaque ASCII; never transcribe)* |

TLS verification is off by default (self-signed certs on appliance
deployments). Pass `--verify` if the operator installed a proper CA.

Resolution order: `--url` / `--token` > env vars. If neither is set, the
client aborts with a clear error.

**Token handling rule — non-negotiable.** Never hardcode or re-type
`NTS_TOKEN` / `NTS_URL` values in generated shell commands. Reference
them as `$NTS_TOKEN` / `$NTS_URL` or pass `--token "$NTS_TOKEN"` /
`--url "$NTS_URL"`. Writing a literal-looking token is almost always a
hallucination and will silently shadow the correct value from the
parent environment. If the env var seems unset, run
`echo "NTS_TOKEN=${NTS_TOKEN:+set}${NTS_TOKEN:-unset}"` to check; ask
the user, do **not** invent one.

## Asset layout

```
nts/
├── SKILL.md                                        # this file
├── README.md
├── assets/
│   └── nts_client.py                               # self-contained client (requests only)
└── references/
    └── 智隼网络高级威胁分析系统_webapi接口说明_V7.3.0.docx  # vendor spec, not executed
```

`<skill_dir>` is the directory reported by `skill_view` under `skill_dir`.
Resolve the absolute path to `assets/nts_client.py` once and reuse it
(`CLIENT` below).

## Commands

```bash
CLIENT="<skill_dir>/assets/nts_client.py"
# assume NTS_URL / NTS_TOKEN are already exported in the parent shell;
# never inline the token literal — see "Token handling rule" above.

# system info
python3 "$CLIENT" version
python3 "$CLIENT" health
python3 "$CLIENT" netlinks                 # find the linkId you care about

# canonical user flow — one alert file → many pcaps on disk
python3 "$CLIENT" workflow \
  --alerts-file /path/to/alerts.jsonl \
  --link-id 2 \
  --out-dir /tmp/nts-pcaps \
  --window-seconds 60

# parse alerts without hitting NTS (debugging / dry run)
python3 "$CLIENT" parse-alerts --input /path/to/alerts.jsonl

# single-shot pcap download by explicit four-tuple + alert time
python3 "$CLIENT" download-pcap \
  --link-id 2 \
  --src-ip 192.168.9.82 --src-port 54321 \
  --dst-ip 8.8.8.8      --dst-port 53 \
  --time "2026-04-21 15:30:00" --window-seconds 60 \
  -o /tmp/alert.pcap

# single-shot with a pre-built filter (any of the docx's filter_ IDs)
python3 "$CLIENT" download-pcap \
  --link-id 2 --begin-time "now-10m" --end-time now \
  --filter 'filter_port=443 && filter_ip_addr=8.8.8.8' \
  -o /tmp/tls-to-google.pcap

# first-N-packet payload peek
python3 "$CLIENT" payload \
  --link-id 2 --start-time "now-5m" --end-time now \
  --filter "filter_port=56706;80" --limit 10

# IOC queries (kind ∈ dns | ip | hash | url | email | cert | ja3)
python3 "$CLIENT" query-ioc dns --link-id 2 \
  --start-time "now-1d" --end-time now \
  --values www.baidu.com example.com
python3 "$CLIENT" query-ioc ip --link-id 2 \
  --start-time "now-1d" --end-time now \
  --values 192.168.9.58 192.168.9.208
```

All commands read `NTS_URL` / `NTS_TOKEN` from the environment. Use
`-o <file>` to dump JSON to disk (defaults to stdout).

### Time inputs

Accepted everywhere `--time` / `--start-time` / `--end-time` /
`--begin-time` are used:

- epoch seconds or milliseconds (auto-detected by magnitude)
- `YYYY-MM-DD HH:MM:SS` (local time)
- ISO 8601, e.g. `2026-04-21T15:30:00Z` or `...+08:00`
- `YYYY-MM-DD`
- `now`, `now-10m`, `now-1h`, `now-2d`, `now+5s`

### Filter grammar (docx §3.1)

| ID | Meaning | Example |
|---|---|---|
| `filter_ip_se` | IP 会话 | `filter_ip_se=192.168.5.1<->192.168.5.2` |
| `filter_ip_port_se` | TCP/UDP 四元组会话 | `filter_ip_port_se=[192.168.0.5]:28084<->[192.168.0.6]:80` |
| `filter_ip_addr` | IP（可用 `;` 多选） | `filter_ip_addr=1.1.1.1;2.2.2.2` |
| `filter_ip_range` | IP 段 | `filter_ip_range=192.168.9.0-192.168.9.255` |
| `filter_port` | 端口 | `filter_port=80;443` |
| `filter_port_range` | 端口段 | `filter_port_range=80-90` |
| `filter_app` | 应用 ID | `filter_app=1;335` |
| `filter_protocol` | 协议 ID | `filter_protocol=655;445` |
| `filter_country` | 国家 ID | `filter_country=34` |

Connectors: `;` (or within a filter), `&&` (and), `||` (or), `=` / `!=`.
`download-pcap` auto-builds `filter_ip_port_se=[sip]:sport<->[dip]:dport`
when you pass the four-tuple flags; use `--filter` for anything else.

### Alert record schema (auto-extracted)

`parse-alerts` / `batch-download` / `workflow` accept:

1. **JSON / JSONL** with one object per alert. Any of these keys work
   for src/dst:
   - `src_ip` / `srcIp` / `source_ip` / `sourceIp` / `sip`
   - `dst_ip` / `dstIp` / `dest_ip` / `destIp` / `dip`
   - ports: `src_port` / `srcPort` / `sport`, `dst_port` / `dstPort` /
     `dport` (optional — omitted → falls back to `filter_ip_se`)
   - timestamp (one of):
     `timestamp` / `ts` / `time` / `event_time` / `@timestamp` /
     `alarm_time` / `detect_time` / `createTime` / `firstSeenTime`
2. **Syslog-ish line**: regex picks the **first two** `IP[:port]` pairs
   as src/dst and the first ISO / `YYYY-MM-DD HH:MM:SS` timestamp.
3. **Plain dict with raw IPs** also works — it falls back to pulling the
   first two IPs out of the stringified record.

Lines that do not yield a timestamp + src/dst IP are silently skipped.

## Procedure

0. **Pin today's date.** If the user uses relative time words like
   "昨晚 / 昨天 / 上午 / yesterday / last night / last hour", run
   `date +'%F %T %z'` **once** before building any time spec — models
   sometimes miscompute dates by a day or two and you will silently
   download an empty pcap from the future. Prefer `now-<N>{s,m,h,d}`
   over hand-computed absolute timestamps when the user was relative.
1. **Resolve config.** Ensure `NTS_URL` and `NTS_TOKEN` are set. Remind
   the user of where the token lives in the UI if they don't have one.
2. **Find the link.** Run `netlinks` and pick the `id` whose
   `netlink_category` matches the environment — `1: 在线`, `2: 离线`,
   `3: OMA`. Online links are the usual "last 10 minutes" case.
3. **Get the alerts on disk.** NTS does not pull alerts. Ask the user
   where their SIEM export lives (`.json` / `.jsonl` / syslog), or let
   them paste four-tuples directly and you write them into a temp JSONL.
   Run `parse-alerts` first and **show the user the extracted records**
   so they can correct course before hitting the appliance.
4. **Batch-download.** Run `workflow` (alias of `batch-download`) with
   a reasonable `--window-seconds` (default 60 — i.e. ±30s around the
   alert time). Output is one pcap per record plus a `manifest.json`.
   For a single ad-hoc request, call `download-pcap` directly with the
   four-tuple flags.
5. **Report back.** List the pcap paths, packet counts, total bytes, and
   any `ok=false` rows in the manifest. Do **not** silently drop
   failures.
6. **Next step.** If the user wants the pcap re-analysed, hand it off to
   `sm-skills/security/sandbox` (the sandbox skill accepts a file path
   and returns a threat report) or tell them to upload it via the NTS
   UI — the v7.3.0 WebAPI does not expose a re-analysis endpoint.

## Streaming pcap details

`/open-api/v1/pcap/packets` returns a custom binary format:

```
magic_code (4B BE, 0x2E415354 "TSA.")
handle     (4B BE)
more_data  (1B)
[ head { media(1B), ts(8B BE, µs since epoch),
         pktlen(4B BE), caplen(4B BE) }, data (caplen bytes) ]*
```

- `more_data == 1` → reissue the POST with the same `downloadTaskId`
  and the returned `handle`; the client does this automatically.
- `pktlen == caplen == 0` packets are progress markers; skipped.
- The client writes a standard libpcap file (LINKTYPE_ETHERNET by
  default). If `media` indicates a different L2 type on your deployment,
  open the pcap and re-tag with `editcap -T <linktype>`.
- Error handling: if the server returns `application/json` instead of
  the binary stream (common when `linkId` is down — error `300010`),
  the client raises with the decoded error body.

## Error codes (docx §3.3)

| code | meaning |
|------|---------|
| 000000 | 成功 |
| 000001 | 系统异常 |
| 100001 | 系统繁忙 |
| 100010 | 处理超时 |
| 100012 | 处理失败 |
| 300001 | 账号或密码错误 |
| 300002 | 参数为空 |
| 300103 | 身份未认证或认证过期 |
| 300004 | 调用接口失败 |
| 300005 | 用户已被锁定 |
| 300006 | 参数错误 |
| 300007 | 数据包下载超时 |
| 300009 | 系统未就绪 |
| 300010 | 传入链路不可用 |

## Quirks observed on real appliances

- **`linkId` vs `netlinkId`**: the v7.3.0 docx sample JSON shows
  `"netlinkId": "1"`, but the parameter table lists `linkId` — and the
  production server requires `linkId` (as a string). Sending
  `netlinkId` gets you `HTTP 417 {"code":"300004","msg":"invalid
  request parameters"}`. The client uses `linkId` everywhere.
- **`/system/serviceinfo` 不一定在默认白名单**。Auth-Key 通常只放行
  了一小批接口；`version` 可能返回
  `{"code":100001,"msg":"UNAUTHORIZED"}` 即使 token 本身有效。用
  `netlinks` 当探活检查。
- **Pcap 流真的会分页**。实测 15 分钟窗口的 `filter_ip_addr=<host>`
  返回了 15 个分片、≈1.5 GB pcap，所以 `--timeout` 给 10 分钟+、
  磁盘留够空间。

## Notes

- TLS: NTS appliances ship self-signed certs; `--verify` is off by
  default. Turn it on only after confirming a trusted chain.
- Time units differ between endpoints: `pcap/packets` takes
  **epoch seconds**, while `pcap/payload` and `query/*` take
  **milliseconds**. The client handles this internally — always pass
  human-friendly times or epoch seconds and let it convert.
- Window policy: default `--window-seconds 60` centres ±30s on the
  alert. Larger windows catch more context at the cost of pcap size.
- The client does not retry automatically on non-000000 codes. If the
  user wants retry-on-timeout, wrap the call externally.
- Full WebAPI surface (hardware status, log-push config, upgrade,
  country/protocol/app enums, etc.) is documented in
  `references/智隼网络高级威胁分析系统_webapi接口说明_V7.3.0.docx`
  but **not** wired up here — extend `nts_client.py` as needed.
