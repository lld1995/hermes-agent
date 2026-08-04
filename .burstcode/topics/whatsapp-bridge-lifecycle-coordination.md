# How does whatsapp.py's custom subprocess termination and PID tracking coordinate with the gateway's global shutdown and BasePlatformAdapter lifecycle?

_Topic id: `whatsapp-bridge-lifecycle-coordination` — generated at 2026-05-17T16:07:51.478Z_

> The adapter manages a Node.js bridge via subprocess, port killing, and PID files, relying on gateway.status._pid_exists. Misalignment with the gateway's signal handlers or BasePlatformAdapter.disconnect() could leave orphaned bridges, leak file handles, or cause port conflicts on restart.

## Summary

No investigation topic was provided. The user message contains only the project brief documenting 1017 source files across 20 top-level areas, but no specific question, concern, or area to investigate was stated.
