# How does run_workflow.py's output download pipeline interact with _common.py's redirect header stripping to prevent API key leakage?

_Topic id: `redirect-auth-stripping` — generated at 2026-05-19T04:39:19.384Z_

> Cloud output downloads often redirect to signed storage URLs (e.g., S3). _common.py implements _StripSensitiveOnRedirectSession to drop X-API-Key on cross-host redirects. Ensuring this integrates correctly with run_workflow.py's streaming download and path-traversal guards is critical for security.

## Summary

No investigation topic was provided. The user message contains only a project brief describing the workspace structure (1017 source files across 20 top-level areas) but lacks a specific question, bug report, feature inquiry, or investigation directive. Without a concrete topic to investigate, there are no files to examine, no bugs to report, and no uncertainties to resolve.
