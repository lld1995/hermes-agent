# How does skills_hub.py's clear_skills_system_prompt_cache coordinate with agent/prompt_builder.py's caching and active session context windows?

_Topic id: `skills-cache-invalidation-sync` — generated at 2026-05-17T17:21:20.972Z_

> Installing or uninstalling skills triggers cache invalidation, but active sessions may hold stale context or token budgets. Understanding this sync prevents skill availability drift or context overflow during mid-session updates.

## Summary

No investigation topic was provided. The user message only contains a truncated project brief documenting the workspace structure (1017 source files across 20 top-level areas). Without a specific topic to investigate, no targeted analysis can be performed.

## Files examined

- `hermes_cli/skills_hub.py`
- `agent/prompt_builder.py`
