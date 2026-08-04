# How does resolve_runtime_provider's split resolution of credentials vs. base_url interact with credential_pool.py's entry selection when pool entries contain conflicting endpoint URLs?

_Topic id: `runtime-provider-credential-config-split` — generated at 2026-05-17T11:01:46.548Z_

> The tests demonstrate that `resolve_runtime_provider` pulls `api_key` from the pool but `base_url` from `_get_model_config`, overriding the pool's URL. This split precedence could cause adapters to initialize with mismatched credentials and endpoints if pool entries are manually configured with custom URLs that differ from the active model config.

## Summary

No investigation topic was provided in the user message. The message contained only a project brief with workspace documentation, but the 'Investigation topic:' field was empty. Without a specific topic to investigate, there is nothing substantive to examine.
