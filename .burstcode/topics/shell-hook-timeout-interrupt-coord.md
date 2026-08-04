# How does shell_hooks.py's subprocess timeout enforcement interact with the agent loop's interrupt signaling and run_agent.py's cancellation logic?

_Topic id: `shell-hook-timeout-interrupt-coord` — generated at 2026-05-16T17:01:20.222Z_

> Hung shell hooks could block the main event loop or bypass agent cancellation. Understanding how timeout exceptions propagate to `run_agent.py`'s interrupt checks and `GatewayRunner`'s drain lifecycle is critical for responsive shutdowns.

## Summary

The user message contains only a project brief describing the workspace structure of hermes-agent (version 0.13.0 by Nous Research). No specific investigation topic, question, or area of concern was provided to explore. The brief documents 1017 source files across 20 top-level areas including the agent core, gateway, CLI, tools, plugins, skills, and more, but without a concrete investigation directive there is nothing substantive to examine.

## Findings

The hermes-agent workspace is a self-improving AI agent framework by Nous Research. It supports multiple LLM providers, messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal, etc.), scheduled automations via cron, subagent delegation, and runs on various backends (local, Docker, SSH, Modal, Vercel Sandbox). The codebase is organized into major areas: agent/ (core LLM interaction), gateway/ (messaging platform adapters), hermes_cli/ (CLI commands), tools/ (agent tool implementations), plugins/ (extensibility), skills/ (agent capabilities), and tests/ (comprehensive test suite). Python >=3.11 required, MIT licensed.

## Files examined

- `pyproject.toml`
- `README.md`
