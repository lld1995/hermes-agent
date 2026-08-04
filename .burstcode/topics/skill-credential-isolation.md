# How do the divergent credential loading strategies across stocks_client.py, nutrition_search.py, canvas_api.py, and telephony.py interact with Hermes' global .env parser and credential pool?

_Topic id: `skill-credential-isolation` — generated at 2026-05-16T06:34:55.108Z_

> Each skill implements its own env var reading (some fallback to demo keys, others require strict config). This fragmentation risks bypassing global credential suppression, redaction, or dynamic reloading mechanisms.

## Summary

No investigation topic was provided in the user message. The message contains only a comprehensive project brief documenting 1017 source files across 20 top-level areas of the hermes-agent workspace (acp_adapter, agent, cron, environments, gateway, hermes_cli, optional-skills, packaging, plugins, providers, scripts, skills, sm-skills, tests, tools, tui_gateway, ui-tui, web, website, plus root-level Python files). No specific question, directive, code area, or investigation topic was included for me to analyze.

## Findings

Workspace: hermes-agent - a large Python project implementing an AI agent system with CLI, gateway, MCP/ACP adapters, RL environments, plugin system, and TUI. Key root files: batch_runner.py (parallel batch processing), cli.py (CLI entry), run_agent.py (agent orchestrator), hermes_*.py (infrastructure modules), model_tools.py (tool orchestration), toolsets.py (tool grouping). Without an investigation topic, no targeted analysis can be performed.
