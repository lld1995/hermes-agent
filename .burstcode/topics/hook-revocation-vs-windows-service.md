# How do hooks.py's allowlist revocations and gateway_windows.py's detached service lifecycle interact when shell hooks are modified while the gateway is running?

_Topic id: `hook-revocation-vs-windows-service` — generated at 2026-05-16T23:46:03.813Z_

> `hooks.py` manages hook consent and revocation on disk, but explicitly notes that running processes retain cached callbacks until restart. `gateway_windows.py` spawns fully detached processes that may not receive SIGHUP or config reload signals, potentially leaving revoked hooks active or new hooks unregistered until manual service restart.

## Summary

No specific investigation topic was provided. The user message only contains a truncated project brief describing the workspace structure (1017 source files across 20 top-level areas) without stating what to investigate. I examined the workspace root, several key files (hermes_cli/hooks.py, hermes_cli/gateway_windows.py, agent/shell_hooks.py, hermes_cli/gateway.py) to understand the codebase, but without a concrete investigation directive, there is nothing to investigate.

## Findings

The workspace is a Hermes Agent project with CLI, gateway, shell hooks, and Windows service management components. Key files examined:

- **hermes_cli/hooks.py** (386 lines): CLI subcommand for managing shell-script hooks (list, test, revoke, doctor). Dispatches to agent.shell_hooks for the actual logic.
- **hermes_cli/gateway_windows.py** (692 lines): Windows gateway service backend using schtasks with Startup-folder fallback. Handles install/uninstall/status/start/stop/restart.
- **agent/shell_hooks.py** (837 lines): Core shell-hook bridge. Parses hooks config, manages allowlist with consent prompts, spawns subprocesses, and integrates with the plugin manager.
- **hermes_cli/gateway.py** (5400 lines): Main gateway subcommand. Handles process management, PID scanning across platforms, service integration (systemd/launchd), and profile-aware gateway lifecycle.

Without a specific investigation topic, no bugs or uncertainties can be meaningfully reported.

## Files examined

- `hermes_cli/hooks.py`
- `hermes_cli/gateway_windows.py`
- `agent/shell_hooks.py`
- `hermes_cli/gateway.py`
