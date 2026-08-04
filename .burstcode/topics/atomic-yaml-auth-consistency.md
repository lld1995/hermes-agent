# How does _reset_config_provider's atomic_yaml_write coordinate with auth.json credential clearing to ensure crash-consistent logout state?

_Topic id: `atomic-yaml-auth-consistency` — generated at 2026-05-15T23:13:07.552Z_

> Logout modifies both config.yaml (provider/base_url reset) and auth.json (credential removal). If a crash occurs between the two writes, the user ends up with a mismatched state where config points to a provider whose credentials have been deleted (or vice versa). The atomic write utility prevents partial config.yaml corruption, but the cross-file ordering with auth.json mutations is not explicitly tested.

## Summary

The host message provides a comprehensive project brief for the hermes-agent workspace (1017 files, 20 top-level areas) but does not specify any investigation topic. The workspace is a large Python-based AI agent platform with plugin architecture, multi-platform messaging gateway, RL training environments, TUI/web dashboards, and extensive test coverage. Without a specific topic, question, or bug to investigate, no further file examination is warranted.

## Findings

The hermes-agent workspace is a mature, large-scale Python project implementing an AI agent platform. Key components include: (1) Core agent loop in run_agent.py with tool orchestration via model_tools.py, (2) Plugin system for memory providers, web search, image/video generation, and platform adapters, (3) Messaging gateway supporting 15+ platforms (Telegram, Discord, Slack, Matrix, Signal, WhatsApp, etc.), (4) RL training environments for benchmark evaluation, (5) React/Ink TUI and web dashboard, (6) Extensive test suite mirroring the package structure. The project uses async-first patterns, SQLite for persistence, and a provider abstraction layer for LLM backends.
