# How does `tui_gateway.server`'s `slash.exec` rejection of skill/pending-input commands coordinate with `command.dispatch` to ensure correct TUI fallback without blocking the RPC loop?

_Topic id: `tui-gateway-slash-dispatch-routing` — generated at 2026-05-16T15:51:24.356Z_

> Protocol tests verify 4018 errors force TUI clients to `command.dispatch`, but plugin discovery failures, async handler routing, and pool offloading must not strand the worker pool or leak session state.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting 1017 source files across 20 top-level areas, but lacks a concrete investigation directive. Without a specific topic (e.g., 'review the credential pool for race conditions' or 'examine the LSP integration for bugs'), there is nothing to investigate.

## Findings

The workspace is the hermes-agent project by NousResearch. It contains a large Python codebase with CLI, gateway, agent, tools, plugins, TUI, and web components. The project brief documents all major modules and their responsibilities. No investigation topic was specified in the user message.

## Files examined

- `hermes_constants.py`
