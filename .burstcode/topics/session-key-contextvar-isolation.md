# How does gateway/run.py's session key contextvar binding interact with tools/approval.py's routing logic under concurrent gateway workers?

_Topic id: `session-key-contextvar-isolation` — generated at 2026-05-17T08:27:21.572Z_

> The test file uses AST to verify `gateway/run.py` wraps agent runs with `set_current_session_key`/`reset_current_session_key`. Ensuring these contextvars correctly isolate approval state across concurrent async tasks prevents cross-session approval leakage or stale state.

## Summary

No investigation topic was provided in the user message. Only the project brief describing 1017 source files across 20 top-level areas was included, with no specific question, bug, or area to investigate.
