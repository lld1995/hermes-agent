# How do auxiliary URL normalization, beta header stripping, and credential guards coordinate to prevent Anthropic credential leakage to MiniMax endpoints?

_Topic id: `minimax-credential-isolation` — generated at 2026-05-16T09:44:30.487Z_

> The tests cover URL path translation (`/anthropic` -> `/v1`), selective beta header omission, and explicit credential routing in `switch_model()`. Understanding how these safeguards interact across `auxiliary_client.py`, `anthropic_adapter.py`, and `run_agent.py` is critical to ensuring that provider switches don't accidentally route Anthropic keys to third-party endpoints or break tool streaming.

## Summary

No investigation topic was provided. The user message contains only a project brief with workspace documentation (1017 source files across 20 top-level areas) but lacks a specific investigation question or topic to explore.

## Findings

The workspace is Hermes Agent, a self-improving AI agent by Nous Research. It supports multiple LLM providers (OpenRouter, Anthropic, OpenAI, MiniMax, Kimi/Moonshot, etc.), messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal), and features a cron scheduler, skill system, memory providers, and RL training environments. The codebase is primarily Python with some TypeScript/Node.js for the TUI and web dashboard.
