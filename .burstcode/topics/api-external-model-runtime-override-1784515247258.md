---
date: 2026-07-20T02:40:47.258Z
topic: API external model runtime override
files: gateway/platforms/api_server.py, gateway/run.py, tests/gateway/test_api_server.py, tests/gateway/test_auth_fallback.py
---

## Problem
OpenAI-compatible API callers could explicitly request a model, and AIAgent received that model string, but runtime provider/api_mode resolution still used config.yaml model.default, causing internal routing to behave as if the configured model were active.

## Key Files
- gateway/platforms/api_server.py
- gateway/run.py
- tests/gateway/test_api_server.py
- tests/gateway/test_auth_fallback.py

## Findings
APIServerAdapter._resolve_request_model() already extracts non-alias request models and _create_agent() already passes the string to AIAgent. The mismatch was earlier runtime resolution: _resolve_runtime_agent_kwargs() called resolve_runtime_provider() without target_model, so provider-specific api_mode logic consulted persisted model.default.

## Solution
Created branch fix/external-model-override; added target_model to gateway.run._resolve_runtime_agent_kwargs(), forwarded it into resolve_runtime_provider(), and passed API request requested_model from APIServerAdapter._create_agent(). Added regression assertions in gateway API and auth fallback tests.

## Reusable Learnings
An explicit model must drive both AIAgent.model and resolve_runtime_provider(target_model=...), otherwise model identity and transport/api_mode can diverge.
