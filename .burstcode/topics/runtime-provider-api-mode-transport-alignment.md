# How does runtime_provider.py's api_mode assignment coordinate with transport registry discovery and adapter initialization?

_Topic id: `runtime-provider-api-mode-transport-alignment` — generated at 2026-05-17T07:13:35.455Z_

> The tests verify api_mode mapping per provider (e.g., anthropic_messages, codex_responses), but the actual transport routing and adapter kwargs building happen downstream. Misalignment between resolved api_mode and transport capabilities could cause schema mismatches, dropped reasoning blocks, or incorrect request formatting.

## Summary

No specific investigation topic was provided in the project brief — it was truncated after the introductory context about the workspace containing 1017 source files. Without a concrete investigation target (e.g., a specific module, bug class, or subsystem to audit), there is nothing actionable to investigate. The files examined during initial exploration cover the transport layer (agent/transports/) and runtime provider resolution (hermes_cli/runtime_provider.py), which together form the provider abstraction and credential resolution system for this AI agent framework.

## Findings

The workspace appears to be an AI agent framework (Hermes) that supports multiple LLM providers through a transport abstraction layer. Key components examined:

1. **Transport Layer** (agent/transports/): A plugin-style system with a base ProviderTransport ABC and four concrete transports: Anthropic (anthropic_messages), Codex/Responses API (codex_responses), Chat Completions (chat_completions), and Bedrock Converse (bedrock_converse). Transports auto-register on import via a global registry.

2. **Runtime Provider Resolution** (hermes_cli/runtime_provider.py): A 1403-line module that resolves which provider, API mode, base URL, and credentials to use. It supports credential pools, custom providers, named providers, and environment-based fallbacks. It handles complex provider-specific logic for Azure Foundry, OpenRouter, Anthropic, Copilot, Nous, and others.

3. **Provider-specific transports** delegate to adapter modules (anthropic_adapter.py, codex_responses_adapter.py, bedrock_adapter.py) for the actual format conversion, keeping transports thin wrappers.

## Files examined

- `hermes_cli/runtime_provider.py`
- `agent/transports/__init__.py`
- `agent/transports/base.py`
- `agent/transports/anthropic.py`
- `agent/transports/codex.py`
- `agent/transports/chat_completions.py`
- `agent/transports/bedrock.py`
