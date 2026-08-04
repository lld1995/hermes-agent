# How does Bedrock's region-aware live model discovery interact with the provider overlay registration and runtime routing to ensure consistent model IDs across the picker, credential validation, and actual API calls?

_Topic id: `bedrock-region-model-id-consistency` — generated at 2026-05-19T08:22:41.353Z_

> test_bedrock_model_picker.py validates picker-side behavior, but the same region resolution must propagate through `agent/bedrock_adapter.py`'s Converse kwargs builder and `hermes_cli/providers.py` overlay config. Drift between picker display and runtime routing would cause silent model resolution failures.

## Summary

The investigation topic was truncated in the system prompt. Only a project brief was provided (describing 1017 source files across 20 top-level areas), but the actual investigation topic was cut off mid-sentence. Without a concrete topic, no meaningful investigation could be performed.

## Findings

The workspace is a large Python project (Hermes Agent) with 1017 documented source files. Key areas examined during initial exploration include: agent/bedrock_adapter.py (AWS Bedrock Converse API adapter, 1277 lines), hermes_cli/model_switch.py (shared model-switching logic, 1778 lines), hermes_cli/providers.py (provider identity and overlays, 711 lines), and hermes_cli/models.py (model catalogs, 3770 lines). The project supports multiple AI providers (OpenAI, Anthropic, Bedrock, etc.) with a plugin-like architecture.

## Files examined

- `agent/bedrock_adapter.py`
- `hermes_cli/model_switch.py`
- `hermes_cli/providers.py`
- `hermes_cli/models.py`
