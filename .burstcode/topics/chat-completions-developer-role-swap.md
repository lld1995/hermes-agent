# How does chat_completions.py's developer role swap for GPT-5 models interact with system prompt injection and context compression?

_Topic id: `chat-completions-developer-role-swap` — generated at 2026-05-16T17:40:37.181Z_

> Swapping system to developer roles changes how providers parse instructions. It must align with prompt_builder.py's block assembly and context_engine.py's summarization to avoid losing system directives during compression or retry.

## Summary

The investigation topic was truncated in the user's message. The project brief ends mid-word at `- websi` (likely `website`), and no specific investigation topic was provided. Without a clear topic to investigate, I cannot proceed with a targeted code review.

## Findings

The workspace is the `hermes-agent` project — an AI agent framework with 1017+ source files across 20+ top-level areas. Key components include: `agent/` (core agent logic, transports, prompt builder, context engine), `providers/` (provider profiles for OpenAI-compatible APIs), `tests/` (test suite), `gateway/`, `plugins/`, `skills/`, and `website/`. The project brief was truncated before the actual investigation topic could be specified.

## Files examined

- `agent/transports/chat_completions.py`
- `agent/prompt_builder.py`
- `agent/context_engine.py`
- `tests/agent/transports/test_chat_completions.py`
