# How do Slack's API-driven thread context fetching and Signal's envelope quote parsing normalize into `MessageEvent.reply_to_*` fields, and does the agent loop handle partial context consistently?

_Topic id: `platform-reply-context-normalization` — generated at 2026-05-17T22:22:29.997Z_

> Both adapters extract reply context but use fundamentally different mechanisms (Slack calls `conversations.replies` with self-bot filtering, Signal parses inline `quote` objects). The gateway must unify these into a single contract for the agent loop to avoid context duplication or missing pointers.

## Summary

No investigation topic was provided in the user message. The message contains only a comprehensive project brief documenting 1017 source files across 20 top-level areas of the hermes-agent workspace, but lacks a specific investigation directive. Without a topic to investigate, no code examination was performed beyond reading the README for general context.

## Findings

The hermes-agent workspace is a self-improving AI agent platform by Nous Research (v0.13.0). It supports multiple LLM providers, messaging platforms (Telegram, Discord, Slack, WhatsApp, Signal), and features a closed learning loop with skill creation, memory management, and scheduled automations. The codebase is organized into 20 top-level areas including acp_adapter, agent, cron, environments, gateway, hermes_cli, plugins, tools, and more.

## Files examined

- `README.md`
