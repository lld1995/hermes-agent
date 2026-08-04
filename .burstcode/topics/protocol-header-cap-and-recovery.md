# How does `agent.lsp.protocol`'s 8 KiB header cap and truncated body handling interact with `agent.lsp.eventlog` and `agent.lsp.manager`'s recovery logic?

_Topic id: `protocol-header-cap-and-recovery` — generated at 2026-05-17T02:52:19.717Z_

> The protocol tests enforce an 8 KiB header limit and raise `LSPProtocolError` on truncation, but it's unclear how these errors propagate to the eventlog's `log_server_error` and whether the manager retries or marks the client broken.

## Summary

No investigation topic was provided. The user message contains only a truncated project brief describing the workspace structure (1017 source files, 20 top-level areas) but no specific question, bug report, feature area, or code region to investigate. I explored the LSP subsystem (agent/lsp/) as it was the most prominent code area visible, reading protocol.py, client.py, manager.py, eventlog.py, servers.py, workspace.py, and the module's __init__.py, along with the test suite. The LSP layer is a well-documented, well-tested async JSON-RPC client for language servers with proper error handling, broken-set tracking, delta diagnostics, and structured logging. Without a specific investigation topic, there is nothing actionable to report.

## Files examined

- `agent/lsp/__init__.py`
- `agent/lsp/protocol.py`
- `agent/lsp/client.py`
- `agent/lsp/manager.py`
- `agent/lsp/eventlog.py`
- `agent/lsp/servers.py`
- `agent/lsp/workspace.py`
- `tests/agent/lsp/test_protocol.py`
