#!/usr/bin/env python3
"""Minimal client for 智隼网络高级威胁分析系统 (NTS) WebAPI v7.3.0.

Covers the subset the v7.3.0 docx actually exposes:

    POST /open-api/v1/system/serviceinfo      # version
    POST /open-api/v1/system/healthy          # system health
    POST /open-api/v1/system/netlinks         # list netlinks (linkId)
    POST /open-api/v1/pcap/packets            # download packets (binary stream)
    POST /open-api/v1/pcap/payload            # first N payloads (hex string)
    POST /open-api/v1/query/{dns,ipAddr,hash,url,email,cert,ja3}  # IOC queries

Plus local helpers:
    parse-alerts     -- extract (src, sport, dst, dport, ts) records from a
                        local alert file (json / jsonl / syslog-ish).
    batch-download   -- for each alert record, download the matching pcap
                        window into an output directory.

NTS does *not* expose "alert pull", "upload pcap", or "re-run model" APIs in
this spec. The skill deliberately stops at the pcap on disk and hands the
file path back to the caller.

Auth:
    header `Auth-Key: <token>`; configured via NTS_URL / NTS_TOKEN env vars
    or --url / --token CLI flags.

pcap download response format (application/octet-stream):
    magic_code (4B, BE, fixed 0x2E415354 = "TSA.")
    handle     (4B, BE)
    more_data  (1B)
    [ head{ media(1B), ts(8B BE, microseconds since epoch),
            pktlen(4B BE), caplen(4B BE) },
      data (caplen bytes) ]*

    When more_data == 1 the client must re-POST with the returned handle and
    same downloadTaskId until more_data == 0. Progress markers carry
    pktlen==caplen==0 and are skipped.

    We translate the stream into a standard libpcap file on disk.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- protocol constants ----------------------------------------------------

MAGIC_CODE = 0x2E415354  # "TSA."
PCAP_MAGIC = 0xA1B2C3D4  # microsecond resolution, big-endian writer
# LINKTYPE: NTS uses 1B `media` in each packet header; on ethernet taps the
# typical value is 1 (LINKTYPE_ETHERNET). We fall back to 1 unconditionally
# and let the user convert later if an exotic media type shows up.
DEFAULT_LINKTYPE = 1  # LINKTYPE_ETHERNET

IOC_ENDPOINTS = {
    "dns":    ("/open-api/v1/query/dns",     "domainInfoList"),
    "ip":     ("/open-api/v1/query/ipAddr",  "ipInfoList"),
    "hash":   ("/open-api/v1/query/hash",    "hashList"),
    "url":    ("/open-api/v1/query/url",     "urlList"),
    "email":  ("/open-api/v1/query/email",   "emailList"),
    "cert":   ("/open-api/v1/query/cert",    "certHashList"),
    "ja3":    ("/open-api/v1/query/ja3",     "ja3List"),
}

ERROR_CODES = {
    "000000": "成功",
    "000001": "系统异常",
    "100001": "系统繁忙",
    "100010": "处理超时",
    "100012": "处理失败",
    "300001": "账号或密码错误",
    "300002": "参数为空",
    "300103": "身份未认证或认证过期",
    "300004": "调用接口失败",
    "300005": "用户已被锁定",
    "300006": "参数错误",
    "300007": "数据包下载超时",
    "300009": "系统未就绪",
    "300010": "传入链路不可用",
}


class NTSError(RuntimeError):
    pass


# --- client ----------------------------------------------------------------


class NTSClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        verify: bool = False,
        timeout: int = 120,
    ) -> None:
        if not base_url:
            raise NTSError("base_url required (NTS_URL env or --url)")
        if not token:
            raise NTSError("token required (NTS_TOKEN env or --token)")
        self.base = base_url.rstrip("/")
        self.token = token
        self.verify = verify
        self.timeout = timeout

    def _headers(self, extra: dict | None = None) -> dict:
        h = {"Auth-Key": self.token}
        if extra:
            h.update(extra)
        return h

    def _post_json(self, path: str, body: dict, *, stream: bool = False) -> requests.Response:
        r = requests.post(
            f"{self.base}{path}",
            json=body,
            headers=self._headers({"Content-Type": "application/json"}),
            verify=self.verify,
            timeout=self.timeout,
            stream=stream,
        )
        r.raise_for_status()
        return r

    def _json_call(self, path: str, body: dict) -> dict[str, Any]:
        r = self._post_json(path, body)
        try:
            return r.json()
        except ValueError:
            raise NTSError(f"non-JSON response from {path}: {r.text[:200]!r}")

    # --- simple endpoints --------------------------------------------------

    def version(self) -> dict:
        return self._json_call("/open-api/v1/system/serviceinfo", {})

    def health(self) -> dict:
        return self._json_call("/open-api/v1/system/healthy", {})

    def netlinks(self) -> dict:
        return self._json_call("/open-api/v1/system/netlinks", {})

    # --- payload query -----------------------------------------------------

    def payload(
        self,
        link_id: str | int,
        start_time_ms: int,
        end_time_ms: int,
        filter_str: str,
        limit_count: int = 10,
    ) -> dict:
        body = {
            "linkId": str(link_id),
            "startTime": int(start_time_ms),
            "endTime": int(end_time_ms),
            "filter": filter_str,
            "limitCount": int(limit_count),
        }
        return self._json_call("/open-api/v1/pcap/payload", body)

    # --- IOC queries -------------------------------------------------------

    def query_ioc(
        self,
        kind: str,
        link_id: str | int,
        start_time_ms: int,
        end_time_ms: int,
        values: list[str],
        *,
        limit: int | None = None,
        request_ip: str | None = None,
    ) -> dict:
        if kind not in IOC_ENDPOINTS:
            raise NTSError(f"unknown ioc kind {kind!r}; choose from {sorted(IOC_ENDPOINTS)}")
        path, key = IOC_ENDPOINTS[kind]
        body: dict[str, Any] = {
            "linkId": str(link_id),
            "startTime": int(start_time_ms),
            "endTime": int(end_time_ms),
            key: list(values),
        }
        if limit is not None:
            body["limit"] = int(limit)
        if request_ip:
            body["requestIp"] = request_ip
        return self._json_call(path, body)

    # --- pcap download -----------------------------------------------------

    def download_pcap(
        self,
        link_id: str | int,
        begin_time_sec: int,
        end_time_sec: int,
        filter_str: str,
        out_path: str | os.PathLike[str],
        *,
        download_task_id: str | None = None,
        progress: bool = False,
        max_chunks: int = 10_000,
        on_event: callable | None = None,
    ) -> dict[str, Any]:
        """Loop /pcap/packets until `more_data == 0`, writing a libpcap file.

        Returns a summary dict: {packets, bytes, chunks, linktype, out_path,
        downloadTaskId}.
        """
        task_id = download_task_id or f"nts-{uuid.uuid4().hex[:16]}"
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        def emit(stage: str, **kw):
            if on_event:
                on_event(stage, **kw)

        total_packets = 0
        total_bytes = 0
        chunks = 0
        handle = 0
        linktype = DEFAULT_LINKTYPE
        # NB: the v7.3.0 docx sample JSON shows `netlinkId`, but the parameter
        # table and the production appliance both require `linkId` (as string).
        # Using `netlinkId` yields HTTP 417 with code 300004.
        body_base = {
            "linkId": str(link_id),
            "beginTime": int(begin_time_sec),
            "endTime": int(end_time_sec),
            "filter": filter_str,
            "process": bool(progress),
            "downloadTaskId": task_id,
        }

        with open(out, "wb") as fp:
            # libpcap global header
            fp.write(struct.pack(
                ">IHHiIII",
                PCAP_MAGIC, 2, 4, 0, 0, 65535, linktype,
            ))

            while True:
                chunks += 1
                if chunks > max_chunks:
                    raise NTSError(
                        f"exceeded max_chunks={max_chunks}; handle={handle}, "
                        f"taskId={task_id}"
                    )
                body = dict(body_base, handle=int(handle))
                emit("request", chunk=chunks, handle=handle)
                r = self._post_json(
                    "/open-api/v1/pcap/packets", body, stream=True,
                )
                # NTS may return JSON on error codes even when the docs say
                # octet-stream; check content-type first.
                ctype = r.headers.get("Content-Type", "")
                if "json" in ctype.lower():
                    try:
                        err = r.json()
                    except ValueError:
                        err = {"raw": r.text[:500]}
                    raise NTSError(f"pcap/packets returned JSON: {err}")

                packets, handle_resp, more_data, pkts, bts = _parse_stream(
                    r.iter_content(chunk_size=1 << 20), fp,
                )
                total_packets += pkts
                total_bytes += bts
                handle = handle_resp
                emit("chunk_done", chunk=chunks, packets=pkts, bytes=bts,
                     more_data=more_data, handle=handle)
                if not more_data:
                    break

        return {
            "downloadTaskId": task_id,
            "out_path": str(out),
            "packets": total_packets,
            "bytes": total_bytes,
            "chunks": chunks,
            "linktype": linktype,
            "filter": filter_str,
            "beginTime": int(begin_time_sec),
            "endTime": int(end_time_sec),
        }


# --- pcap stream parser ----------------------------------------------------


class _StreamReader:
    """Small helper to read exact byte counts from an iter_content generator."""
    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self._buf = bytearray()
        self._eof = False

    def read(self, n: int) -> bytes:
        while len(self._buf) < n and not self._eof:
            try:
                part = next(self._chunks)
            except StopIteration:
                self._eof = True
                break
            if part:
                self._buf.extend(part)
        if len(self._buf) < n:
            raise NTSError(
                f"unexpected end of stream (wanted {n}B, got {len(self._buf)}B)"
            )
        out = bytes(self._buf[:n])
        del self._buf[:n]
        return out

    def eof(self) -> bool:
        return self._eof and not self._buf


def _parse_stream(chunks: Iterable[bytes], fp) -> tuple[None, int, int, int, int]:
    """Parse one pcap/packets response and append to libpcap file `fp`.

    Returns (None, handle, more_data, packets_written, bytes_written).
    """
    r = _StreamReader(chunks)
    header = r.read(4 + 4 + 1)
    magic, handle, more_data = struct.unpack(">IIB", header)
    if magic != MAGIC_CODE:
        raise NTSError(
            f"bad magic: got 0x{magic:08x}, expected 0x{MAGIC_CODE:08x}"
        )

    packets = 0
    bytes_written = 0
    # iterate packets; loop stops when the stream ends
    while True:
        # try to read a head (17B: media(1) + ts(8) + pktlen(4) + caplen(4))
        try:
            head = r.read(1 + 8 + 4 + 4)
        except NTSError:
            # stream ended cleanly at packet boundary
            if r.eof():
                break
            raise

        media, ts_us, pktlen, caplen = struct.unpack(">BqII", head)
        if pktlen == 0 and caplen == 0:
            # progress marker — no payload follows
            continue
        data = r.read(caplen)
        # convert microseconds since epoch to (sec, usec)
        # if ts_us looks like nanoseconds, scale down
        if ts_us > 10_000_000_000_000_000:
            ts_us //= 1000  # nanoseconds -> microseconds
        ts_sec, ts_rem = divmod(int(ts_us), 1_000_000)
        fp.write(struct.pack(">IIII", ts_sec, ts_rem, caplen, pktlen))
        fp.write(data)
        packets += 1
        bytes_written += caplen

    return None, handle, more_data, packets, bytes_written


# --- time parsing helpers --------------------------------------------------


_REL_RE = re.compile(r"^now(?:([+-])(\d+)([smhd]))?$")
_TS_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d",
)


def parse_time_to_epoch(spec: str | int | float, *, unit: str = "s") -> int:
    """Return epoch seconds (or ms if unit='ms') for a variety of inputs.

    Accepted:
      - int / float   treated as epoch seconds (or ms if >= 10^12)
      - 'now' / 'now-10m' / 'now+1h'
      - 'YYYY-MM-DD HH:MM:SS' (local time)
      - ISO 8601 'YYYY-MM-DDTHH:MM:SS[Z|+hh:mm]'
      - plain 'YYYY-MM-DD'
    """
    if isinstance(spec, (int, float)):
        v = int(spec)
        if v >= 10_000_000_000:  # looks like milliseconds
            sec = v // 1000
        else:
            sec = v
    else:
        s = spec.strip()
        if not s:
            raise NTSError("empty time spec")
        if s.isdigit():
            return parse_time_to_epoch(int(s), unit=unit)
        m = _REL_RE.match(s)
        if m:
            now = int(time.time())
            if not m.group(1):
                sec = now
            else:
                mul = {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(3)]
                delta = int(m.group(2)) * mul
                sec = now + delta if m.group(1) == "+" else now - delta
        else:
            dt = None
            for fmt in _TS_FORMATS:
                try:
                    dt = datetime.strptime(s, fmt)
                    break
                except ValueError:
                    continue
            if dt is None:
                raise NTSError(f"unrecognised time spec: {spec!r}")
            if dt.tzinfo is None:
                sec = int(dt.timestamp())
            else:
                sec = int(dt.astimezone(timezone.utc).timestamp())
    if unit == "ms":
        return sec * 1000
    if unit == "s":
        return sec
    raise NTSError(f"unknown unit {unit!r}")


# --- four-tuple filter ------------------------------------------------------


def build_ip_port_session_filter(
    src_ip: str, src_port: int, dst_ip: str, dst_port: int,
) -> str:
    """Return filter_ip_port_se=[sip]:sport<->[dip]:dport (tcp/udp session)."""
    return f"filter_ip_port_se=[{src_ip}]:{src_port}<->[{dst_ip}]:{dst_port}"


def build_ip_session_filter(src_ip: str, dst_ip: str) -> str:
    return f"filter_ip_se={src_ip}<->{dst_ip}"


# --- alert record extraction -----------------------------------------------


@dataclass
class AlertRecord:
    src_ip: str
    src_port: int | None
    dst_ip: str
    dst_port: int | None
    ts_epoch: int           # seconds
    raw: dict | str | None = None


_IP_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
_IP_PORT_RE = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})[:\s](\d{1,5})\b")
_TS_LINE_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
)

_SRC_IP_KEYS = ("src_ip", "srcIp", "source_ip", "sourceIp", "sip", "srcAddr", "src", "attacker_ip")
_DST_IP_KEYS = ("dst_ip", "dstIp", "dest_ip", "destIp", "destination_ip", "dip", "dstAddr", "dst", "victim_ip", "target_ip")
_SRC_PORT_KEYS = ("src_port", "srcPort", "source_port", "sport")
_DST_PORT_KEYS = ("dst_port", "dstPort", "dest_port", "destination_port", "dport")
_TS_KEYS = ("timestamp", "ts", "time", "event_time", "eventTime",
            "@timestamp", "alarm_time", "alarmTime", "detectTime",
            "detect_time", "created", "createTime", "create_time", "first_seen",
            "firstSeen", "firstSeenTime")


def _first_key(d: dict, keys: Iterable[str]) -> Any:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    # also try case-insensitive
    lower = {k.lower(): v for k, v in d.items()}
    for k in keys:
        v = lower.get(k.lower())
        if v not in (None, ""):
            return v
    return None


def _coerce_ts(raw: Any) -> int | None:
    if raw in (None, ""):
        return None
    if isinstance(raw, (int, float)):
        v = int(raw)
        return v // 1000 if v >= 10_000_000_000 else v
    s = str(raw).strip()
    if s.isdigit():
        v = int(s)
        return v // 1000 if v >= 10_000_000_000 else v
    for fmt in _TS_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                return int(dt.timestamp())
            return int(dt.astimezone(timezone.utc).timestamp())
        except ValueError:
            continue
    # generic ISO
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return int(dt.timestamp())
        return int(dt.astimezone(timezone.utc).timestamp())
    except ValueError:
        return None


def extract_from_dict(obj: dict) -> AlertRecord | None:
    src_ip = _first_key(obj, _SRC_IP_KEYS)
    dst_ip = _first_key(obj, _DST_IP_KEYS)
    if not src_ip or not dst_ip:
        # last-resort: scan any IPs in string representation
        ips = _IP_RE.findall(json.dumps(obj, default=str))
        if len(ips) < 2:
            return None
        src_ip, dst_ip = ips[0], ips[1]
    sport = _first_key(obj, _SRC_PORT_KEYS)
    dport = _first_key(obj, _DST_PORT_KEYS)
    ts = _coerce_ts(_first_key(obj, _TS_KEYS))
    if ts is None:
        # fall back to regex on stringified blob
        for m in _TS_LINE_RE.finditer(json.dumps(obj, default=str)):
            ts = _coerce_ts(m.group(1))
            if ts:
                break
    if ts is None:
        return None
    return AlertRecord(
        src_ip=str(src_ip).strip(),
        src_port=int(sport) if sport not in (None, "") else None,
        dst_ip=str(dst_ip).strip(),
        dst_port=int(dport) if dport not in (None, "") else None,
        ts_epoch=ts,
        raw=obj,
    )


def extract_from_line(line: str) -> AlertRecord | None:
    line = line.strip()
    if not line:
        return None
    # try JSON first
    if line.startswith("{"):
        try:
            return extract_from_dict(json.loads(line))
        except json.JSONDecodeError:
            pass
    # regex fallback (syslog-ish)
    pairs = _IP_PORT_RE.findall(line)
    if len(pairs) >= 2:
        src_ip, sport = pairs[0]
        dst_ip, dport = pairs[1]
        sp, dp = int(sport), int(dport)
    else:
        ips = _IP_RE.findall(line)
        if len(ips) < 2:
            return None
        src_ip, dst_ip = ips[0], ips[1]
        sp = dp = None
    ts = None
    tsm = _TS_LINE_RE.search(line)
    if tsm:
        ts = _coerce_ts(tsm.group(1))
    if ts is None:
        return None
    return AlertRecord(src_ip, sp, dst_ip, dp, ts, raw=line)


def parse_alerts_file(path: str | os.PathLike[str], *, fmt: str = "auto") -> list[AlertRecord]:
    p = Path(path)
    if not p.is_file():
        raise NTSError(f"alerts file not found: {p}")
    text = p.read_text(encoding="utf-8", errors="replace")
    records: list[AlertRecord] = []
    stripped = text.lstrip()
    if fmt in ("auto", "json") and stripped.startswith(("[", "{")):
        try:
            obj = json.loads(text)
            items = obj if isinstance(obj, list) else obj.get("data", [obj])
            if isinstance(items, dict):
                items = [items]
            for item in items:
                if isinstance(item, dict):
                    rec = extract_from_dict(item)
                    if rec:
                        records.append(rec)
            if records or fmt == "json":
                return records
        except json.JSONDecodeError:
            if fmt == "json":
                raise NTSError(f"invalid JSON in {p}")
    # jsonl / syslog / plain
    for line in text.splitlines():
        rec = extract_from_line(line)
        if rec:
            records.append(rec)
    return records


# --- CLI -------------------------------------------------------------------


def _client_from_args(args: argparse.Namespace) -> NTSClient:
    url = args.url or os.environ.get("NTS_URL")
    token = args.token or os.environ.get("NTS_TOKEN")
    return NTSClient(url, token, verify=args.verify, timeout=args.timeout)


def _dump(obj: Any, out_path: str | None) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    if out_path and out_path != "-":
        Path(out_path).write_text(text, encoding="utf-8")
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        print(text)


def _check_code(resp: dict, endpoint: str) -> None:
    code = resp.get("code")
    if code and code != "000000":
        meaning = ERROR_CODES.get(code, "unknown")
        raise NTSError(f"{endpoint} failed: code={code} ({meaning}) msg={resp.get('msg')!r}")


def _cmd_version(args):
    c = _client_from_args(args)
    r = c.version()
    _dump(r, args.output)
    return 0


def _cmd_health(args):
    c = _client_from_args(args)
    r = c.health()
    _dump(r, args.output)
    return 0


def _cmd_netlinks(args):
    c = _client_from_args(args)
    r = c.netlinks()
    _dump(r, args.output)
    return 0


def _cmd_payload(args):
    c = _client_from_args(args)
    start_ms = parse_time_to_epoch(args.start_time, unit="ms")
    end_ms = parse_time_to_epoch(args.end_time, unit="ms")
    r = c.payload(args.link_id, start_ms, end_ms, args.filter, args.limit)
    _check_code(r, "pcap/payload")
    _dump(r, args.output)
    return 0


def _cmd_query_ioc(args):
    c = _client_from_args(args)
    start_ms = parse_time_to_epoch(args.start_time, unit="ms")
    end_ms = parse_time_to_epoch(args.end_time, unit="ms")
    r = c.query_ioc(
        args.kind, args.link_id, start_ms, end_ms, args.values,
        limit=args.limit, request_ip=args.request_ip,
    )
    _check_code(r, f"query/{args.kind}")
    _dump(r, args.output)
    return 0


def _cmd_download(args):
    c = _client_from_args(args)
    # filter: explicit --filter wins; otherwise build from four-tuple
    if args.filter:
        filt = args.filter
    elif args.src_ip and args.dst_ip:
        if args.src_port is not None and args.dst_port is not None:
            filt = build_ip_port_session_filter(
                args.src_ip, args.src_port, args.dst_ip, args.dst_port,
            )
        else:
            filt = build_ip_session_filter(args.src_ip, args.dst_ip)
    else:
        raise NTSError("need either --filter or --src-ip/--dst-ip")

    if args.time:
        ts = parse_time_to_epoch(args.time, unit="s")
        half = args.window_seconds // 2
        begin_sec = ts - half
        end_sec = ts + (args.window_seconds - half)
    else:
        begin_sec = parse_time_to_epoch(args.begin_time, unit="s")
        end_sec = parse_time_to_epoch(args.end_time, unit="s")
        if end_sec <= begin_sec:
            raise NTSError("end_time must be > begin_time")

    out = args.output or f"/tmp/nts-{uuid.uuid4().hex[:8]}.pcap"

    def on_event(stage, **kw):
        if args.quiet:
            return
        if stage == "request":
            print(f"[pcap] chunk={kw['chunk']} handle={kw['handle']}", file=sys.stderr)
        elif stage == "chunk_done":
            print(
                f"[pcap] chunk={kw['chunk']} packets={kw['packets']} "
                f"bytes={kw['bytes']} more_data={kw['more_data']}",
                file=sys.stderr,
            )

    summary = c.download_pcap(
        args.link_id, begin_sec, end_sec, filt, out,
        progress=args.progress_markers, on_event=on_event,
    )
    _dump(summary, args.summary_output)
    return 0


def _cmd_parse_alerts(args):
    records = parse_alerts_file(args.input, fmt=args.format)
    data = [asdict(r) for r in records]
    _dump({"count": len(data), "records": data}, args.output)
    return 0


def _cmd_batch_download(args):
    c = _client_from_args(args)
    records = parse_alerts_file(args.alerts_file, fmt=args.format)
    if args.limit:
        records = records[: args.limit]
    if not records:
        raise NTSError(f"no alert records parsed from {args.alerts_file}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for i, rec in enumerate(records, start=1):
        if rec.src_port is not None and rec.dst_port is not None:
            filt = build_ip_port_session_filter(
                rec.src_ip, rec.src_port, rec.dst_ip, rec.dst_port,
            )
        else:
            filt = build_ip_session_filter(rec.src_ip, rec.dst_ip)
        half = args.window_seconds // 2
        begin_sec = rec.ts_epoch - half
        end_sec = rec.ts_epoch + (args.window_seconds - half)
        fname = (
            f"{i:04d}_{rec.src_ip.replace(':','-')}_{rec.src_port or 'x'}"
            f"_{rec.dst_ip.replace(':','-')}_{rec.dst_port or 'x'}"
            f"_{rec.ts_epoch}.pcap"
        )
        out_path = out_dir / fname
        if not args.quiet:
            print(f"[{i}/{len(records)}] filter={filt} window=[{begin_sec},{end_sec}] -> {out_path}",
                  file=sys.stderr)
        try:
            summary = c.download_pcap(
                args.link_id, begin_sec, end_sec, filt, out_path,
                on_event=None,
            )
            manifest.append({"ok": True, "alert": asdict(rec), **summary})
        except Exception as e:
            manifest.append({"ok": False, "alert": asdict(rec), "error": str(e)})
            if args.fail_fast:
                break
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    _dump({"out_dir": str(out_dir), "manifest": str(manifest_path),
           "total": len(records), "items": manifest}, args.output)
    return 0


def _cmd_workflow(args):
    """Convenience: parse alerts for a time window → batch-download pcaps.

    Bridges the user's typical ask: "get alerts for the last 10 minutes and
    download their pcaps" — except the alert source must be a local file
    (NTS pushes alerts out via syslog/kafka; there is no pull API).
    """
    # just delegate; time filtering is the caller's job when parsing
    if not args.alerts_file:
        raise NTSError("--alerts-file is required (NTS has no alert pull API)")
    return _cmd_batch_download(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nts_client", description=__doc__.splitlines()[0])
    p.add_argument("--url", help="Base URL; defaults to $NTS_URL")
    p.add_argument("--token", help="Auth-Key token; defaults to $NTS_TOKEN")
    p.add_argument("--verify", action="store_true",
                   help="Verify TLS certs (default off: NTS uses self-signed)")
    p.add_argument("--timeout", type=int, default=600)
    sub = p.add_subparsers(dest="cmd", required=True)

    # version / health / netlinks
    for name, fn, desc in (
        ("version", _cmd_version, "GET platform version"),
        ("health", _cmd_health, "GET system health"),
        ("netlinks", _cmd_netlinks, "List netlinks (linkId, status, category)"),
    ):
        sp = sub.add_parser(name, help=desc)
        sp.add_argument("-o", "--output")
        sp.set_defaults(func=fn)

    # payload
    pl = sub.add_parser("payload", help="Query first N packet payloads (hex string)")
    pl.add_argument("--link-id", required=True)
    pl.add_argument("--start-time", required=True,
                    help="epoch s/ms, 'YYYY-MM-DD HH:MM:SS', or 'now-10m'")
    pl.add_argument("--end-time", required=True)
    pl.add_argument("--filter", required=True,
                    help="e.g. filter_ip_port_se=[1.1.1.1]:80<->[2.2.2.2]:443")
    pl.add_argument("--limit", type=int, default=10)
    pl.add_argument("-o", "--output")
    pl.set_defaults(func=_cmd_payload)

    # download-pcap
    dl = sub.add_parser("download-pcap",
                        help="Download pcap by link+filter+time into a libpcap file")
    dl.add_argument("--link-id", required=True)
    grp = dl.add_mutually_exclusive_group()
    grp.add_argument("--time", help="alert timestamp; window built with --window-seconds")
    grp.add_argument("--begin-time", help="begin of window (implies --end-time)")
    dl.add_argument("--end-time")
    dl.add_argument("--window-seconds", type=int, default=60)
    dl.add_argument("--src-ip")
    dl.add_argument("--src-port", type=int)
    dl.add_argument("--dst-ip")
    dl.add_argument("--dst-port", type=int)
    dl.add_argument("--filter", help="override: raw filter string")
    dl.add_argument("-o", "--output", help="pcap output path")
    dl.add_argument("--summary-output", help="write JSON summary here")
    dl.add_argument("--progress-markers", action="store_true",
                    help="ask server to send pktlen=caplen=0 progress packets")
    dl.add_argument("-q", "--quiet", action="store_true")
    dl.set_defaults(func=_cmd_download)

    # query-ioc
    qi = sub.add_parser("query-ioc",
                        help="IOC query (dns/ip/hash/url/email/cert/ja3)")
    qi.add_argument("kind", choices=sorted(IOC_ENDPOINTS))
    qi.add_argument("--link-id", required=True)
    qi.add_argument("--start-time", required=True)
    qi.add_argument("--end-time", required=True)
    qi.add_argument("--values", nargs="+", required=True,
                    help="one or more IOCs to look up")
    qi.add_argument("--limit", type=int)
    qi.add_argument("--request-ip")
    qi.add_argument("-o", "--output")
    qi.set_defaults(func=_cmd_query_ioc)

    # parse-alerts
    pa = sub.add_parser("parse-alerts",
                        help="Extract (src, sport, dst, dport, ts) records from a local alert file")
    pa.add_argument("--input", required=True)
    pa.add_argument("--format", choices=("auto", "json", "jsonl", "syslog"),
                    default="auto")
    pa.add_argument("-o", "--output")
    pa.set_defaults(func=_cmd_parse_alerts)

    # batch-download
    bd = sub.add_parser("batch-download",
                        help="Parse alerts → for each record, download its pcap window")
    bd.add_argument("--alerts-file", required=True)
    bd.add_argument("--link-id", required=True)
    bd.add_argument("--out-dir", required=True)
    bd.add_argument("--window-seconds", type=int, default=60)
    bd.add_argument("--format", choices=("auto", "json", "jsonl", "syslog"),
                    default="auto")
    bd.add_argument("--limit", type=int,
                    help="cap number of records processed")
    bd.add_argument("--fail-fast", action="store_true")
    bd.add_argument("-q", "--quiet", action="store_true")
    bd.add_argument("-o", "--output")
    bd.set_defaults(func=_cmd_batch_download)

    # workflow alias
    wf = sub.add_parser("workflow",
                        help="Alias of batch-download; the canonical user flow")
    wf.add_argument("--alerts-file", required=True)
    wf.add_argument("--link-id", required=True)
    wf.add_argument("--out-dir", required=True)
    wf.add_argument("--window-seconds", type=int, default=60)
    wf.add_argument("--format", choices=("auto", "json", "jsonl", "syslog"),
                    default="auto")
    wf.add_argument("--limit", type=int)
    wf.add_argument("--fail-fast", action="store_true")
    wf.add_argument("-q", "--quiet", action="store_true")
    wf.add_argument("-o", "--output")
    wf.set_defaults(func=_cmd_workflow)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except NTSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except requests.RequestException as e:
        print(f"http error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
