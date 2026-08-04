# How does image_routing.py's MIME sniffing and native content part building integrate with provider adapters' multimodal format translation, and what happens when sniffing disagrees with file extensions?

_Topic id: `image-routing-mime-sniffing-and-provider-adapter-integration` — generated at 2026-05-16T21:17:34.262Z_

> agent/image_routing.py sniffs MIME from magic bytes and builds OpenAI-style content parts, but provider adapters (Anthropic, Gemini, Bedrock, Codex, OpenAI) must translate these into vendor-specific formats. The reactive shrinking path references run_agent._try_shrink_image_parts_in_messages. Understanding this integration seam is critical for multimodal reliability across providers.

## Summary

No specific investigation topic was provided in the user's message. Only a truncated project brief was given, mentioning 1017 source files across 20 top-level areas. Without a concrete topic (e.g., a module to audit, a bug to trace, or an architectural concern to explore), a meaningful investigation cannot proceed.

## Findings

The workspace is a large Python project (hermes-agent) with 1017 documented source files. Key areas include agent adapters (Anthropic, Gemini, Codex/Responses), image routing and vision handling, CLI/TUI gateways, MCP integration, and various tools. Per-file documentation lives under docs/. The project brief was truncated and did not contain an investigation directive.

## Files examined

- `agent/image_routing.py`
- `run_agent.py`
- `agent/anthropic_adapter.py`
- `agent/codex_responses_adapter.py`
- `tests/agent/test_image_routing.py`
- `tests/run_agent/test_image_shrink_recovery.py`
