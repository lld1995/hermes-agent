# How does _should_send_voice_reply's decision matrix coordinate with base adapter auto-TTS and Discord VC playback to guarantee exactly-one audio delivery?

_Topic id: `voice-reply-dedup` — generated at 2026-05-17T06:12:47.655Z_

> Multiple TTS paths (base adapter auto-TTS, gateway runner reply, Discord VC override) can trigger simultaneously. Mapping their skip/allow gates ensures users never hear duplicate audio or miss replies when switching between text and voice inputs.

## Summary

No investigation topic was provided in the user message. The message contains only the project brief documenting 1017 source files across 20 top-level areas of the hermes-agent workspace. Without a specific topic to investigate, no code analysis was performed.
