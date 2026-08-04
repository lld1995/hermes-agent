# How does fallback_cmd.py's config.yaml mutation trigger env cache invalidation and credential pool reloading to ensure new fallback providers are immediately usable?

_Topic id: `fallback-config-cache-sync` — generated at 2026-05-17T06:30:25.290Z_

> test_fallback_cmd.py shows fallback add/remove/clear mutate config.yaml, but test_env_load_cache.py shows .env caching is keyed on mtime/size. If fallback changes require new credentials in .env, the cache and credential pool must be invalidated. Without coordination, agents may continue using stale primary providers even after fallback chain changes.

## Summary

No investigation topic was provided. The message contained only the project brief with documentation for 1017 source files across 20 top-level areas, but no specific investigation directive (e.g., 'investigate credential pool race conditions' or 'review LSP integration for bugs').

## Files examined

- `hermes_constants.py`
