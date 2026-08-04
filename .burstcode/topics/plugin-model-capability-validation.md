# How does plugin_llm.py's model override resolution validate against models_dev.py's capability metadata before routing?

_Topic id: `plugin-model-capability-validation` — generated at 2026-05-15T08:02:09.485Z_

> Plugins can override the active model via trust gates, but there is no visible check ensuring the overridden model actually supports the requested features (vision, tools, structured output). This could lead to silent failures or degraded plugin behavior if a plugin requests a model lacking the necessary capabilities.

## Summary

No investigation topic was provided. The user message contains only a project brief documenting the workspace structure (1017 source files across 20 top-level areas) but does not specify a concrete investigation topic to explore. Without a specific topic (e.g., 'audit the credential pool for race conditions' or 'review the LSP integration for memory leaks'), there is nothing to investigate.

## Findings

The workspace is a large Python project called Hermes Agent with extensive documentation. It includes CLI tools, gateway platform adapters, agent orchestration, plugin systems, RL environments, and a TUI frontend. Key areas include: agent/ (LLM adapters, context management, memory providers), gateway/ (messaging platform integrations), tools/ (terminal, browser, file operations), plugins/ (memory, image/video generation, web search), hermes_cli/ (CLI commands), and tests/ (comprehensive test suite).
