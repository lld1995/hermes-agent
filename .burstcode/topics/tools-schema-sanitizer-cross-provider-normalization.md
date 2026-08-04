# How does tools/schema_sanitizer.py's strip_nullable_unions handle Pydantic/MCP edge cases across different providers?

_Topic id: `tools-schema-sanitizer-cross-provider-normalization` — generated at 2026-05-16T20:38:57.443Z_

> The adapter delegates nullable union stripping to a shared sanitizer before sending tool schemas to Anthropic. Investigating how this utility preserves metadata and handles complex discriminated unions ensures tool definitions don't silently break or lose validation constraints.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting 1017 source files across 20 top-level areas of the Hermes Agent workspace, but no specific question, bug, module, security concern, or architectural area to investigate.

## Findings

The workspace is a large Python-based AI agent platform (Hermes Agent) with components including: a CLI (hermes_cli/), gateway for messaging platforms (gateway/), agent orchestration (agent/), tool implementations (tools/), RL training environments (environments/), cron scheduling (cron/), MCP/ACP adapters (acp_adapter/), plugins (plugins/), skills (skills/), and a TUI frontend (ui-tui/). Without a specific investigation topic, no targeted analysis could be performed.
