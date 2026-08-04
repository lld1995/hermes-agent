# How does the hermes-tools MCP server's stateless dispatch via handle_function_call interact with tools that require AIAgent loop context?

_Topic id: `hermes-mcp-tool-dispatch-lifecycle` — generated at 2026-05-19T00:48:26.468Z_

> The MCP server exposes tools like memory, session_search, and kanban_* that are dispatched through `model_tools.handle_function_call()`. The docstring notes that delegate_task, memory, and session_search are `_AGENT_LOOP_TOOLS` requiring running AIAgent context, yet memory and session_search ARE in the EXPOSED_TOOLS tuple. This apparent contradiction needs investigation: do these tools degrade gracefully when called from the MCP subprocess, or do they fail silently? The kanban tools are explicitly noted as stateless (reading env vars and writing to kanban.db), but the memory and session_search tools may have hidden dependencies.

## Summary

The investigation topic provided in the prompt was truncated — the project brief ends mid-word with `- `websi` and the `[summary] truncated` marker indicates the actual topic was cut off. Without a clear investigation topic, I cannot meaningfully proceed. I examined the workspace root structure, AGENTS.md for project context, and the two files referenced in the truncated excerpts (agent/transports/hermes_tools_mcp_server.py and model_tools.py) to understand the codebase, but there is no specific area to investigate.

## Findings

No investigation topic was provided. The prompt contained only a truncated project brief ending with `- `websi` (likely the start of `website`).

## Files examined

- `AGENTS.md`
- `model_tools.py`
- `agent/transports/hermes_tools_mcp_server.py`
