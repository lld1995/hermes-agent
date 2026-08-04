# How do session boundary hooks (on_session_finalize/on_session_reset) coordinate with resume display and session preloading to ensure consistent state across session transitions?

_Topic id: `session-hooks-resume-display-lifecycle` — generated at 2026-05-15T15:39:18.440Z_

> test_session_boundary_hooks.py verifies hooks fire on /new, /reset, and cleanup. test_resume_display.py tests _preload_resumed_session() and _display_resumed_history(). Both interact with session lifecycle — hooks may need to run before or after resume display, and the session DB state must be consistent when hooks access session metadata.

## Summary

No investigation topic was provided. The user message contains only a project brief listing 1017 documented source files across 20 top-level areas, but no specific question, bug report, feature inquiry, or investigation directive to explore.
