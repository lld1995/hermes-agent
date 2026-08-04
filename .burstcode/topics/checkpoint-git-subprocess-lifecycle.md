# How does checkpoint_manager.py's synchronous git subprocess execution coordinate with the agent loop's interrupt/shutdown lifecycle to prevent orphaned git processes or corrupted indexes during rapid tool calls?

_Topic id: `checkpoint-git-subprocess-lifecycle` — generated at 2026-05-16T16:11:13.614Z_

> The checkpoint manager runs blocking git commands (add, commit-tree, gc) before file-mutating tools. If the agent is interrupted or the gateway shuts down mid-snapshot, orphaned git processes or half-written indexes could corrupt the shared store or block subsequent operations.

## Summary

No investigation topic was provided. The user message contains only a project brief (truncated workspace overview describing 1017 source files across 20 top-level areas) with no specific question or focus area to investigate. The .burstcode/topics/ directory contains 40 pending topic files, but none was designated as the current investigation target.

## Findings

The workspace is the hermes-agent project — an AI agent runner with tool calling, multi-provider LLM support, messaging gateway integrations, and a plugin ecosystem. Key areas include: run_agent.py (main agent orchestrator, 16K lines), tools/ (tool implementations including checkpoint_manager.py), agent/ (modular agent internals), gateway/ (messaging platform adapters), hermes_cli/ (CLI infrastructure), and environments/ (RL training environments). The .burstcode/ directory tracks 40 pending investigation topics and maintains per-file documentation under docs/.

## Files examined

- `.burstcode/README.md`
- `.burstcode/activity.log`
- `.burstcode/project-brief.md`
- `.burstcode/state.json`
- `.burstcode/topics/`
- `tools/checkpoint_manager.py`
- `run_agent.py`
