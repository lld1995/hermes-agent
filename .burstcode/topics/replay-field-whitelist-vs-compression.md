# How does `_build_replay_entry`'s reasoning field whitelist coordinate with context compression and provider adapters to prevent thinking-block truncation or API contract violations?

_Topic id: `replay-field-whitelist-vs-compression` — generated at 2026-05-19T07:33:05.735Z_

> The test pins a strict whitelist of reasoning fields for transcript replay, but context compression and provider-specific adapters may strip, transform, or re-serialize these fields. Misalignment could break prefix-cache hits, cause 400 errors on thinking-mode echoes, or leak internal markers into compressed summaries.

## Summary

No specific investigation topic was provided. The message contains only a project brief/documentation of the workspace structure (hermes-agent by Nous Research), but no concrete question, bug report, feature inquiry, or investigation directive. Without a topic to investigate, there is nothing actionable to research.

## Findings

The workspace is hermes-agent v0.13.0, a self-improving AI agent by Nous Research. It supports multiple LLM providers (OpenRouter, Anthropic, OpenAI, etc.), messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal, etc.), and features a closed learning loop with skill creation, memory management, and cron scheduling. The codebase is Python-based with a Node.js TUI component.

## Files examined

- `pyproject.toml`
- `README.md`
- `docs/`
