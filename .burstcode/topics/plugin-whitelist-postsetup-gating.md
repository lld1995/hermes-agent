# How does the plugin system's thread-local tool whitelist interact with tools_config.py's post-setup binary gating during background review forks?

_Topic id: `plugin-whitelist-postsetup-gating` — generated at 2026-05-19T08:47:09.182Z_

> Background forks restrict tools via whitelists, while tools_config gates toolsets based on external binary availability. Conflicts could cause silent failures or bypass security gates when whitelisted tools require uninstalled dependencies.

## Summary

No investigation topic was provided. The project brief was truncated and contained no specific question, module, or area to investigate. The brief cuts off at 'providers/__init__.py — Lazy provider profile registry that discov...' without completing the description or stating what to investigate.

## Findings

The workspace is a large Python project (hermes-agent) with 1017+ source files across 20 top-level areas. Key areas examined include: hermes_cli/plugins.py (plugin system with discovery, lifecycle hooks, thread-local tool whitelisting for background review), hermes_cli/tools_config.py (provider-aware tool configuration with post-setup hooks), and their corresponding test files. The codebase includes features like background review forks, plugin-based tool registration, multi-platform gateway support, and various AI agent capabilities.

## Files examined

- `hermes_cli/plugins.py`
- `hermes_cli/tools_config.py`
- `tests/hermes_cli/test_plugins.py`
- `tests/hermes_cli/test_post_setup_gating.py`
