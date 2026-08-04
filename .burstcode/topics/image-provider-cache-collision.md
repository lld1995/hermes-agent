# How do openai, openai-codex, and xai image providers coordinate cache prefixing and aspect ratio normalization to prevent file collisions?

_Topic id: `image-provider-cache-collision` — generated at 2026-05-17T18:00:51.963Z_

> All three plugins save generated images to `$HERMES_HOME/cache/images/` using `save_b64_image` with provider-specific prefixes. Divergent prefix naming conventions or aspect ratio handling could cause overwrites, inconsistent retrieval, or cache bloat across providers.

## Summary

No investigation topic was provided. The user message contains only a project brief labeled as context, documenting 1017 source files across 20 top-level areas of the Hermes Agent project. Without a specific investigation topic, there is nothing to analyze.

## Findings

The Hermes Agent project is a self-improving AI agent by Nous Research. It features a terminal UI, multi-platform messaging gateway (Telegram, Discord, Slack, WhatsApp, Signal, etc.), closed learning loop with memory and skills, cron scheduling, subagent delegation, and support for multiple LLM providers. The codebase includes Python modules for agent orchestration, gateway platforms, CLI tools, plugins, skills, and tests.

## Files examined

- `README.md`
