# How do relaunch inherited flag extraction and active_profile file management coordinate when --profile overrides conflict with persisted state?

_Topic id: `relaunch-flag-inheritance-vs-active-profile` — generated at 2026-05-15T19:08:20.153Z_

> test_relaunch.py extracts --profile/-p flags for relaunch argv construction, while test_profiles.py manages the active_profile file and HERMES_HOME resolution. When a user relaunches with --profile work but the active_profile file points to coder, the system must deterministically resolve which profile's config, sessions, and credentials are active. Misalignment could cause credential leakage or session corruption across relaunch boundaries.

## Summary

No investigation topic was provided. The user message contains only a project brief describing the workspace structure (1017 source files, 20 top-level areas) but no specific directive about what to investigate. Without a concrete topic (e.g., security audit, race condition hunt, specific module review), there is nothing to investigate.

## Findings

The workspace is the hermes-agent project — a CLI-based AI agent platform with profile management, gateway services, LSP integration, plugin system, and various subcommands. Key modules examined during workspace exploration include hermes_cli/relaunch.py (process self-relaunch), hermes_cli/profiles.py (multi-profile isolation), and their corresponding test suites. No investigation topic was specified.

## Files examined

- `hermes_cli/relaunch.py`
- `hermes_cli/profiles.py`
- `tests/hermes_cli/test_relaunch.py`
- `tests/hermes_cli/test_profiles.py`
