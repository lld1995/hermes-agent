# How does SkillsShSource's HTML scraping for metadata and security audits coordinate with GitHubSource's API-driven fetch/inspect, and does it handle rate limits or structural changes gracefully?

_Topic id: `skillssh-html-vs-api-delegation` — generated at 2026-05-18T01:18:07.262Z_

> The tests reveal heavy reliance on HTML parsing for fallback metadata and security status. If skills.sh changes its layout or rate-limits scrapers, the fallback chain could break or return stale data, impacting skill installation reliability.

## Summary

No specific investigation topic was provided. The user message contained only a truncated project brief mentioning tools/skills_hub.py and tests/tools/test_skills_hub.py, but the actual investigation topic was cut off. Without a clear topic to investigate, I am skipping this turn.

## Files examined

- `tools/skills_hub.py`
- `tests/tools/test_skills_hub.py`
