# How does clarify_tool.py's callback interface bridge to clarify_gateway.py's blocking state machine, and how are timeouts or session resets propagated back to the agent loop?

_Topic id: `clarify-tool-gateway-bridge` — generated at 2026-05-16T15:09:39.620Z_

> The tool layer handles schema validation and input sanitization, while the gateway layer manages the actual user interaction state machine and thread blocking. Understanding their handoff ensures that validation errors, timeouts, and session boundary events correctly terminate the agent's wait state without deadlocks or orphaned threads.

## Summary

No investigation topic was provided in the user message. The message contains only the project brief (workspace documentation listing 1017 source files across 20 top-level areas). The .burstcode/topics/ directory has 40 existing topic files, but none were referenced or assigned for this turn. Without a specific investigation topic, there is nothing to examine.

## Findings

The workspace is the hermes-agent project — a large Python-based AI agent framework with CLI, gateway, tools, plugins, and TUI components. The .burstcode/topics/ directory contains 40 pre-existing investigation topics covering areas like argparse fallback handling, atomic YAML writes, credential isolation, cron lifecycle, Discord voice concurrency, and more. No topic was assigned for this investigation cycle.

## Files examined

- `.burstcode/state.json`
- `.burstcode/topics/`
