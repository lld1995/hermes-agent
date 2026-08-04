# How do `_active_run_agents`, `_active_run_tasks`, and `_run_streams` coordinate to prevent race conditions during concurrent stop and approval requests?

_Topic id: `run-lifecycle-concurrency-and-cleanup` — generated at 2026-05-17T04:32:54.275Z_

> The runs tests verify that stopping a run cleans up internal dictionaries and handles interrupt exceptions gracefully. Investigating the synchronization primitives protecting these shared state dicts will reveal potential race conditions under high concurrency or rapid stop/approval toggling.

## Summary

No investigation topic was provided in the user message. The message only contains the project brief context describing the workspace structure and file documentation, but lacks a specific investigation topic to research.

## Findings

The workspace appears to be a Python-based project (possibly related to Hermes agent/CLI tooling) with 1017 documented source files across 20 top-level areas. Key components include: CLI tools (hermes_cli/), gateway/platform adapters (gateway/), agent components (agent/), tools (tools/), plugins (plugins/), skills (skills/), and various UI components (ui-tui/, web/). The project uses pytest for testing and appears to be a complex multi-platform messaging/agent system.
