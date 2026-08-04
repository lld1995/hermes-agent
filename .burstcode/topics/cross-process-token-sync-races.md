# How do credential_pool.py's _sync_*_entry_from_* methods and _auth_store_lock coordinate with external CLI refreshes to prevent stale token usage or exhaustion state corruption?

_Topic id: `cross-process-token-sync-races` — generated at 2026-05-16T20:51:40.009Z_

> Single-use refresh tokens and concurrent Hermes instances can cause race conditions where one process marks a credential exhausted while another successfully refreshes it; verifying lock granularity and sync timing prevents unnecessary cooldowns.

## Summary

No investigation topic was provided. The message contains only a project brief/workspace documentation overview of the Hermes Agent codebase (1017 files across 20 areas) but no specific question, bug, feature, or code area to investigate.
