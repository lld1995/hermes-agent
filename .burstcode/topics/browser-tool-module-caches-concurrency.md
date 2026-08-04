# How do `browser_tool`'s module-level caches (`_active_sessions`, `_cached_cloud_provider`) interact under concurrent task execution to prevent state leakage or race conditions?

_Topic id: `browser-tool-module-caches-concurrency` — generated at 2026-05-16T15:12:43.778Z_

> Multiple tests monkeypatch these caches to ensure isolation. In production, concurrent agent loops sharing the same module state need thread-safe or task-scoped access to prevent cross-contamination of session info or provider instances.

## Summary

No specific investigation topic was provided in the user message. The project brief was truncated and only described the workspace structure (1017 source files, 20 top-level areas) without specifying what aspect of the codebase to investigate. The .burstcode/topics/ directory contains 40+ pre-defined investigation topics, but none was selected or referenced.

## Findings

The workspace is the Hermes Agent project by Nous Research — a self-improving AI agent with multi-platform messaging gateway, browser automation tools, RL training environments, and a plugin ecosystem. Without a concrete investigation topic, no targeted code review can be performed.

## Files examined

- `.burstcode/project-brief.md`
- `.burstcode/state.json`
- `.burstcode/topics/`
- `README.md`
- `tools/browser_tool.py`
- `tests/tools/test_browser_cloud_fallback.py`
- `tests/tools/test_browser_cloud_provider_cache.py`
- `tests/tools/test_browser_console.py`
