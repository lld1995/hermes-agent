# How does image_routing.py's mode decision logic interact with image_gen_registry.py's active provider resolution when auxiliary vision overrides are configured?

_Topic id: `image-routing-registry-resolution` — generated at 2026-05-17T03:23:51.150Z_

> The routing module decides between native and text modes based on model capabilities and config, while the registry resolves the active provider. Misalignment could cause the router to select a mode unsupported by the resolved provider or bypass explicit auxiliary vision settings.

## Summary

The investigation topic asks how image_routing.py's mode decision logic interacts with image_gen_registry.py's active provider resolution when auxiliary vision overrides are configured. After thorough examination, these two modules serve entirely different purposes and have no interaction:

1. **agent/image_routing.py** decides how user-attached images are presented to the main model: either as native multimodal content parts ("native" mode) or as text descriptions from an auxiliary vision model ("text" mode). In auto mode, it checks `auxiliary.vision.provider` (and related keys) via `_explicit_aux_vision_override()` to determine if the user wants the text pipeline. The auxiliary vision client is resolved by `agent.auxiliary_client.resolve_vision_provider_client()`, NOT by image_gen_registry.

2. **agent/image_gen_registry.py** manages image GENERATION providers (FAL, OpenAI, xAI) for creating new images via the `image_generate` tool. It reads `image_gen.provider` from config.yaml — a completely different config key.

The auxiliary vision pipeline (used when image_routing selects "text" mode) and the image generation pipeline (managed by image_gen_registry) are independent subsystems with separate config keys (`auxiliary.vision.*` vs `image_gen.*`), separate registries, and separate resolution paths. No misalignment is possible because they never interact.

## Findings

Two independent subsystems:

- **Image Input Routing** (`agent/image_routing.py`): Per-turn decision between native multimodal attachment and text-based vision analysis. Config key: `agent.image_input_mode`. Auxiliary vision override detected via `auxiliary.vision.provider`/`model`/`base_url`. The actual auxiliary vision client is resolved by `agent.auxiliary_client.resolve_vision_provider_client()`.

- **Image Generation Registry** (`agent/image_gen_registry.py`): Provider registry for image creation tools (FAL, OpenAI gpt-image-2, xAI grok-imagine). Config key: `image_gen.provider`. Active provider resolved via explicit config → single-provider shortcut → FAL legacy preference.

These subsystems operate on different config paths, different registries, and different code paths. The routing module never consults the image generation registry, and the registry never influences image input mode decisions.

## Files examined

- `agent/image_routing.py`
- `agent/image_gen_registry.py`
- `tests/agent/test_image_routing.py`
- `tests/agent/test_image_gen_registry.py`
