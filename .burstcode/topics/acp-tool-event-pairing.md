# How do acp_adapter.events' callback factories and acp_adapter.server's tool result handling pair ToolCallStart and ToolCallUpdate events across concurrent executions?

_Topic id: `acp-tool-event-pairing` — generated at 2026-05-17T19:19:58.863Z_

> test_events.py tests the callback factories that track tool call IDs and metadata, while test_mcp_e2e.py validates the full flow where these callbacks emit paired ACP events. Ensuring FIFO ID tracking and metadata capture aligns with step callback completion is vital for accurate client-side tool state.

## Summary

No investigation topic was provided. The message contains only the project brief context describing 1017 source files across 20 top-level areas, but lacks a specific question, directive, or area to investigate. Without a concrete topic, no targeted file examination or bug analysis can be performed.

## Findings

The workspace is the hermes-agent project — a multi-platform AI agent system with CLI, gateway, MCP/ACP adapters, RL environments, plugin ecosystem, and TUI/web interfaces. Key areas include: acp_adapter (ACP protocol bridge), agent (core LLM orchestration), cron (scheduled jobs), environments (RL training), gateway (messaging platform adapters), hermes_cli (CLI commands), plugins (extensibility), tools (agent capabilities), and tui_gateway/web (UI layers). The project has extensive test coverage under tests/.
