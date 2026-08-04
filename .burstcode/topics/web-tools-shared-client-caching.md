# How do Exa, Firecrawl, and Parallel plugins coordinate module-level client caching on `tools.web_tools` to support legacy test mocking without causing cross-plugin state pollution?

_Topic id: `web-tools-shared-client-caching` — generated at 2026-05-19T04:14:53.918Z_

> All three providers explicitly cache their SDK clients on `tools.web_tools` attributes (`_exa_client`, `_firecrawl_client`, etc.) rather than locally. This shared caching strategy must be verified to prevent race conditions, stale references, or test interference when multiple plugins are active or when state is reset between test cases.

## Summary

No investigation topic was provided. The user message contains only a project brief describing the workspace structure (1017 source files across 20 top-level areas), but no specific question, bug report, code review request, or investigation directive. The brief is also truncated at the end, suggesting an incomplete message delivery.
