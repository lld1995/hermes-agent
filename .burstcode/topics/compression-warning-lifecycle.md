# How does the two-phase compression warning system handle race conditions or missing callbacks when the agent is instantiated outside the standard gateway lifecycle?

_Topic id: `compression-warning-lifecycle` — generated at 2026-05-19T09:20:15.210Z_

> The test verifies that warnings are stored in `_compression_warning` and replayed via `status_callback`. If the callback isn't wired or the agent runs headless, ensuring warnings aren't lost or duplicated requires checking the lifecycle hooks in `run_agent.py` and `gateway/run.py`.

## Summary

No investigation topic was provided. The user message contains only the project brief documentation (catalog of 1017 source files across 20 top-level areas) but no specific question, bug report, feature inquiry, or investigation directive. Without a concrete topic, there is nothing to investigate.
