# How do audio_bridge's platform-specific module lifecycle (pactl/BlackHole) and process_manager's subprocess signal handling coordinate to guarantee audio device cleanup when meetings end or crash?

_Topic id: `meet-audio-lifecycle-cleanup` — generated at 2026-05-15T19:25:37.323Z_

> Audio modules loaded during setup must be unloaded on teardown. If process_manager crashes or is killed abruptly, orphaned pactl modules or BlackHole bindings could leak system resources or block future meetings.

## Summary

No investigation topic was provided. The message contains only a project brief describing the workspace structure (1017 source files across 20 top-level areas including batch_runner, hermes modules, acp_adapter, agent, cron, environments, gateway, hermes_cli, optional-skills, packaging, and plugins). Without a specific investigation question, there is nothing to examine.
