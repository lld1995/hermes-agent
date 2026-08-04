# How does TUI npm install detection coordinate with session resume environment exports to prevent stale dependency states?

_Topic id: `tui-npm-install-vs-resume-env-coord` — generated at 2026-05-16T13:48:49.797Z_

> test_tui_npm_install.py verifies lockfile freshness checks while test_tui_resume_flow.py verifies environment variable exports to the TUI subprocess. If npm install runs mid-session or after resume, the TUI process may have been launched with stale environment or missing dependencies. Understanding whether `_tui_need_npm_install` runs before or after `_launch_tui` env setup matters for correctness.

## Summary

The provided message contains only a project brief documenting the workspace structure (1017 source files across 20 top-level areas). No investigation topic, question, or area of concern was stated. Without a specific topic to investigate, there is nothing substantive to examine.

## Findings

The workspace is the hermes-agent project (v0.13.0), a self-improving AI agent with CLI, gateway, TUI, plugin, and tooling components. The project brief documents all modules, tests, skills, and plugins. No investigation topic was provided in the user message.

## Files examined

- `pyproject.toml`
