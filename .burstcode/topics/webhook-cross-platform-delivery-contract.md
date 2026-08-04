# How does webhook.py's cross-platform delivery routing coordinate with SMS/Signal adapters' send contracts and metadata handling?

_Topic id: `webhook-cross-platform-delivery-contract` — generated at 2026-05-16T04:38:04.678Z_

> webhook.py routes responses via `gateway_runner.adapters.get(target_platform).send()` and passes `metadata` (e.g., `thread_id`). SMS strips markdown and ignores metadata, while Signal uses metadata for typing/reactions but may drop thread context. Misalignment could cause lost forum routing, formatting degradation, or silent failures when delivering webhook-triggered responses.

## Summary

No specific investigation topic was provided. The user message contains only a truncated project brief describing the workspace structure (1017 source files, 20 top-level areas, docs/ directory) but no concrete question or area to investigate. Without a target topic, I cannot perform a meaningful investigation.

## Files examined

- `gateway/platforms/webhook.py`
- `gateway/platforms/sms.py`
- `gateway/platforms/signal.py`
- `gateway/platforms/base.py`
