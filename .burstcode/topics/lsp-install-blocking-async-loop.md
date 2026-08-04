# How do synchronous install calls in servers.py interact with manager.py's background asyncio loop and timeout gates?

_Topic id: `lsp-install-blocking-async-loop` — generated at 2026-05-15T08:06:40.351Z_

> Spawn builders in `servers.py` call `install.try_install()` synchronously. If an npm/Go install blocks for minutes, it could starve the background loop or trigger `manager.py`'s outer timeouts, potentially marking healthy servers as broken.

## Summary

The investigation topic provided was truncated — only a project brief header was included with no actual investigation question or focus area. The brief itself was cut off mid-sentence ('batch_runner.py — Paralle...' and '... - websi'). Without a concrete topic to investigate, no meaningful analysis can be performed.

## Findings

The workspace is the Hermes Agent project by Nous Research — a self-improving AI agent with LSP integration, skill creation, scheduled automations, and multi-platform support. The project contains 1017 documented source files across 20 top-level areas. Key areas include: agent/ (core agent logic), agent/lsp/ (LSP client/server management), tools/, skills/, plugins/, providers/, gateway/, and various CLI entry points (cli.py, run_agent.py, batch_runner.py).

## Files examined

- `README.md`
- `batch_runner.py`
- `agent/lsp/servers.py`
- `agent/lsp/install.py`
- `agent/lsp/manager.py`
