# nts-pcap-fetch

Minimal client for **智隼网络高级威胁分析系统 (NTS) WebAPI v7.3.0**.

Provides just the endpoints v7.3.0 actually exposes:

- `POST /open-api/v1/system/{serviceinfo,healthy,netlinks}` — basic info
- `POST /open-api/v1/pcap/packets` — download pcap by `linkId` + time
  range + filter (four-tuple session supported)
- `POST /open-api/v1/pcap/payload` — first N packet payloads as hex
- `POST /open-api/v1/query/{dns,ipAddr,hash,url,email,cert,ja3}` — IOC
  lookups by time window

The skill does **not** implement:

- alert pull (NTS pushes alerts out over syslog/kafka/flume; bring your
  own alert file)
- pcap upload / offline-link creation / model rerun (not in v7.3.0)

See [`SKILL.md`](./SKILL.md) for the agent-facing contract and
[`references/智隼网络高级威胁分析系统_webapi接口说明_V7.3.0.docx`](./references/)
for the vendor spec.

## Quick start

```bash
export NTS_URL="https://192.168.180.212:2443"
export NTS_TOKEN="WWUU..."                       # Auth-Key token from the UI

CLIENT=./assets/nts_client.py
python3 "$CLIENT" netlinks                       # find a usable linkId

# single alert — ±30s around the event
python3 "$CLIENT" download-pcap \
  --link-id 2 \
  --src-ip 10.0.0.1 --src-port 54321 \
  --dst-ip 8.8.8.8  --dst-port 53 \
  --time "2026-04-21 15:30:00" --window-seconds 60 \
  -o /tmp/alert.pcap

# many alerts at once
python3 "$CLIENT" workflow \
  --alerts-file /tmp/alerts.jsonl \
  --link-id 2 --out-dir /tmp/nts-pcaps
```

Alert file formats accepted: JSON array, JSONL, and raw syslog lines.
Run `parse-alerts --input <file>` first if you want to inspect what the
extractor pulled before hitting the appliance.

## Smoke tests (offline)

The client's pure-Python pieces can be exercised without the appliance:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, './assets')
import nts_client as m, struct, io, json, pathlib

# time parsing
assert m.parse_time_to_epoch("now-10m") < m.parse_time_to_epoch("now")
assert m.parse_time_to_epoch(1501550400) == 1501550400

# filter builder
assert m.build_ip_port_session_filter("1.1.1.1", 80, "2.2.2.2", 443) == \
       "filter_ip_port_se=[1.1.1.1]:80<->[2.2.2.2]:443"

# alert parsing
tmp = pathlib.Path("/tmp/_alerts.jsonl")
tmp.write_text(json.dumps({"srcIp":"1.1.1.1","srcPort":100,
                           "dstIp":"2.2.2.2","dstPort":200,
                           "ts":1700000000}))
assert len(m.parse_alerts_file(tmp)) == 1

# binary pcap-stream decoder
MAGIC = 0x2E415354
body  = struct.pack(">IIB", MAGIC, 0xdead, 0)
body += struct.pack(">BqII", 1, 1_700_000_000_000_000, 0, 0)        # progress
body += struct.pack(">BqII", 1, 1_700_000_000_000_000, 10, 10) + b"A"*10
buf = io.BytesIO()
buf.write(struct.pack(">IHHiIII", m.PCAP_MAGIC, 2, 4, 0, 0, 65535, 1))
_, handle, more, pkts, nbytes = m._parse_stream(iter([body]), buf)
assert (handle, more, pkts, nbytes) == (0xdead, 0, 1, 10)

print("ok")
PY
```

## Dependencies

- Python 3.9+
- `requests` (the only third-party dep)

## License

MIT. The vendor docx under `references/` is redistributed under the
terms granted by 成都数默科技 for the Hermes skill bundle.
