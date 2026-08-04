# How do `_normalize_multimodal_content` and `_normalize_chat_content` coordinate to prevent image data from leaking into logs or being dropped during agent execution?

_Topic id: `multimodal-vs-chat-normalization-drift` — generated at 2026-05-19T06:37:35.467Z_

> The multimodal tests expect images to be preserved for `_run_agent`, while the normalize tests expect images to be silently stripped for chat content. Understanding the routing logic in `api_server.py` is critical to ensure the correct normalizer is applied per endpoint without state corruption or logging pollution.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting the workspace structure (1017 source files across 20 top-level areas) but does not specify any question, bug, feature, or area to investigate.
