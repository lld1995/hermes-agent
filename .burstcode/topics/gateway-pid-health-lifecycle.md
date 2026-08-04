# How do gateway PID detection strategies (/proc scanning vs ps fallback) coordinate with runtime health reporting and linger state to provide accurate process lifecycle visibility?

_Topic id: `gateway-pid-health-lifecycle` — generated at 2026-05-17T06:48:02.248Z_

> test_gateway_proc_fallback.py shows PID detection diverges between Docker (/proc) and host (ps), while test_gateway_linger.py shows linger affects service persistence, and test_gateway_runtime_health.py shows health lines report startup failures. If PID detection fails in Docker, health reporting may show stale or missing process state, and linger enablement may be skipped incorrectly.

## Summary

No specific investigation topic was provided in the user message. The project brief was truncated and contained only a high-level overview of the workspace (1017 source files across 20 top-level areas). Without a concrete investigation topic (e.g., 'investigate gateway restart logic', 'audit PID file handling', 'review Docker /proc fallback'), no focused investigation could be performed. I examined the gateway-related files that were referenced in the truncated brief excerpts to understand the workspace structure.

## Findings

The workspace is a Python-based project called 'hermes-agent' with a CLI gateway system. Key areas include:

- `hermes_cli/gateway.py` (5400 lines) — Main gateway subcommand handler with process management, PID scanning, service installation (systemd/launchd), and graceful restart via SIGUSR1.
- `gateway/status.py` (972 lines) — Runtime status helpers including PID-file detection, cross-platform PID existence checks, file locking, and scoped identity locks.
- Test files cover /proc-based PID detection fallback, systemd linger auto-enable, and runtime health status reporting.

The gateway system supports multiple platforms (Linux/systemd, macOS/launchd, Windows), handles process lifecycle management, and uses both PID files and file locks for coordination.

## Files examined

- `hermes_cli/gateway.py`
- `gateway/status.py`
- `tests/hermes_cli/test_gateway_proc_fallback.py`
- `tests/hermes_cli/test_gateway_linger.py`
- `tests/hermes_cli/test_gateway_runtime_health.py`
