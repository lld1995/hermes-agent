# How do cron's process-global TERMINAL_CWD mutations and sequential workdir serialization coordinate with agent_loop's task_id-scoped sessions and thread-pool dispatch?

_Topic id: `terminal-cwd-isolation-vs-task-id` — generated at 2026-05-19T00:34:23.167Z_

> cron/scheduler.py mutates os.environ['TERMINAL_CWD'] globally and forces sequential execution for workdir jobs to prevent cross-contamination. environments/agent_loop.py relies on task_id for terminal routing and runs tools concurrently in a thread pool. Both paths share tools.terminal_tool, so mismatched isolation strategies could leak working directories or sandbox state across concurrent RL rollouts and cron ticks.

## Summary

No investigation topic was provided. The user message contains only a project brief describing the workspace structure (1017 files across 20 areas) but no specific question, bug, feature, or code area to investigate.
