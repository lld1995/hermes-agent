# How do detached async delete tasks and thread-safe approval callbacks coordinate with the gateway's event loop lifecycle?

_Topic id: `ephemeral-tasks-vs-approval-callbacks` — generated at 2026-05-15T16:32:59.716Z_

> Both `test_ephemeral_reply.py` and `test_feishu_approval_buttons.py` rely on background async tasks and cross-thread coroutine submissions. Understanding how these interact with adapter shutdown, event loop closure, and task cancellation is critical to preventing unawaited coroutines or orphaned state.

## Summary

No investigation topic was provided. The user message contains only the project brief (workspace documentation) without a specific area to investigate. Cannot proceed without a concrete investigation directive.
