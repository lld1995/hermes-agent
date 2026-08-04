# How do surrogate sanitization in run_agent.py and think-tag stripping in cli.py coordinate across the content pipeline to prevent double-processing or missed sanitization?

_Topic id: `surrogate-sanitization-stream-think-tag-pipeline` — generated at 2026-05-16T10:23:25.451Z_

> test_surrogate_sanitization.py tests sanitization at the API message level (run_agent.py), while test_stream_delta_think_tag.py tests reasoning tag handling at the streaming display level (cli.py). Both operate on assistant content but at different stages. If surrogates appear inside reasoning blocks, the order of sanitization vs tag stripping matters for correctness and security.

## Summary

No investigation topic was provided in the user message. The message only contains the project brief (workspace documentation) without any specific area to investigate. Setting skip=true as there is no topic to address.
