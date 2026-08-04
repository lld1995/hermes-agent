# How do mcp_config.py's save_env_value calls and memory_setup.py's direct _write_env_vars logic interact with the global .env parser?

_Topic id: `env-write-strategies` — generated at 2026-05-16T23:46:47.382Z_

> Both modules write secrets to `~/.hermes/.env` but use different mechanisms: `mcp_config.py` delegates to `hermes_cli.config.save_env_value`, while `memory_setup.py` implements a custom line-based updater. Divergent parsing/writing strategies risk duplicate keys, formatting conflicts, or stale entries if both wizards run sequentially.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting the workspace structure across 1017 source files in 20 top-level areas, with no specific question, bug report, feature area, or investigation directive.

## Findings

The workspace is a large Python project (hermes-agent) with CLI, gateway, agent, tools, plugins, and UI components. Without a stated investigation topic, there is nothing to examine.
