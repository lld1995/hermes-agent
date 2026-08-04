# How does feishu_comment_rules' document-level policy resolution interact with the adapter's group-level admission engine when routing Feishu doc comment webhooks?

_Topic id: `feishu-comment-rule-integration` — generated at 2026-05-15T16:40:47.168Z_

> The comment rule engine uses a 3-tier fallback (exact/wildcard/top) for document access, while the adapter uses group rules and bot policies for chat admission. Understanding how these two rule systems merge or conflict during webhook dispatch is critical for consistent access control across Feishu's unified event stream.

## Summary

No investigation topic was provided. The user message contains only the project brief describing the workspace structure with 1017 documented source files across 20 top-level areas, but no specific question, bug report, feature analysis, or investigation request was included.

## Findings

The workspace is hermes-agent v0.13.0, a self-improving AI agent by Nous Research. It includes a CLI, gateway for messaging platforms, MCP server, RL training environments, plugin system, and various tools. The project uses exact-pinned dependencies for supply chain security. Key areas include: acp_adapter (ACP protocol), agent (LLM orchestration), cron (scheduling), environments (RL training), gateway (messaging platforms), hermes_cli (CLI commands), plugins (extensibility), tools (agent capabilities), and tui_gateway (terminal UI).

## Files examined

- `pyproject.toml`
