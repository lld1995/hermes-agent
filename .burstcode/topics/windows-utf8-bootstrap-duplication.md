# Do hermes_bootstrap.py and hermes_cli/__init__.py's divergent Windows UTF-8 fixes conflict when both are imported?

_Topic id: `windows-utf8-bootstrap-duplication` — generated at 2026-05-17T16:07:09.081Z_

> Both modules set `PYTHONUTF8`/`PYTHONIOENCODING` env vars, but `hermes_bootstrap.py` uses `stream.reconfigure()` while `hermes_cli/__init__.py` replaces streams with `open()`. If an entry point imports both (e.g., `hermes gateway`), the second import may re-open an already-reconfigured stream or vice versa, potentially causing double-buffering, lost output, or `ValueError` on closed file descriptors.

## Summary

No investigation topic was provided in the user message. Only the project brief/context was shared, describing 1017 source files across 20 top-level areas of the hermes-agent workspace. Without a specific investigation topic, there is nothing to examine.
