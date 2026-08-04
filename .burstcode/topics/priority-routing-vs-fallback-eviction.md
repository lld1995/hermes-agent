# How do priority processing overrides and failed-run eviction guards interact during provider fallbacks?

_Topic id: `priority-routing-vs-fallback-eviction` — generated at 2026-05-16T11:23:37.446Z_

> `test_fast_command.py` injects `service_tier: "priority"` into agent runs, while `test_fallback_eviction.py` guards against cache eviction on failures. If priority routing triggers a fallback or error, the eviction logic must correctly preserve the agent cache to avoid MCP reinitialization loops while respecting tier-specific routing states.

## Summary

The investigation topic was not provided in the user message. The message contained only the project brief/context documentation describing 1017 source files across 20 top-level areas of the hermes-agent workspace, but no specific investigation topic or question was stated. Without a concrete investigation topic, there is nothing targeted to examine.

## Findings

No investigation topic was specified in the user message. The message consisted entirely of a project brief documenting the hermes-agent codebase structure, including modules like acp_adapter, agent, cron, environments, gateway, hermes_cli, plugins, tools, and more. No bugs, uncertainties, or code issues could be identified without a specific area of focus.

## Files examined

- `utils.py`
- `hermes_constants.py`
