# How do the reconnect watcher's retryable error classifications and `httpx` keepalive limits interact with `GatewayRunner`'s startup sequence to prevent fd exhaustion during mass platform failures?

_Topic id: `platform-lifecycle-and-resource-limits` — generated at 2026-05-17T21:51:42.056Z_

> `test_platform_reconnect.py` and `test_platform_http_client_limits.py` reveal that platform adapters share tight resource constraints (sockets, fds) and rely on coordinated retry/backoff logic. Investigating how `_platform_reconnect_watcher` schedules retries alongside `platform_httpx_limits()` can uncover bottlenecks or leak paths during network partitions or proxy interference.

## Summary

No investigation topic was provided. The message contains only a project brief describing the workspace structure (1017 source files across 20 top-level areas) without specifying what to investigate. Without a concrete topic—such as a specific module, bug pattern, architectural concern, or feature area—there is nothing targeted to examine.
