# How does the per-guild voice join lock in `test_discord_race_polish.py` interact with Opus codec initialization and `VoiceReceiver` lifecycle in `test_discord_opus.py`?

_Topic id: `discord-voice-concurrency-and-opus` — generated at 2026-05-15T16:28:58.471Z_

> Concurrent voice joins must serialize to avoid duplicate connections, but Opus loading and receiver startup involve blocking or platform-specific ctypes calls. Misalignment could cause race conditions during codec initialization or receiver attachment.

## Summary

No investigation topic was provided in the user message. The message contains only a project brief describing the workspace structure with 1017 documented source files across 20 top-level areas, but the 'Investigation topic:' field is empty. Without a specific topic to investigate, there is nothing to examine.

## Findings

The workspace is a large Python project called hermes-agent, containing an AI agent framework with CLI, gateway, tools, plugins, and various integrations. Key areas include: acp_adapter (ACP protocol), agent (core agent logic, LSP, transports), cron (scheduled jobs), environments (RL training), gateway (messaging platforms), hermes_cli (CLI commands), plugins (memory, web search, video/image gen), tools (terminal, browser, file operations), and tests (comprehensive test suite).
