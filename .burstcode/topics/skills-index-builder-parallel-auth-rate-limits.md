# How does build_skills_index.py's parallel source crawling and batch path resolution handle GitHub API rate limits and auth failures across concurrent ThreadPoolExecutor workers?

_Topic id: `skills-index-builder-parallel-auth-rate-limits` — generated at 2026-05-16T08:00:01.165Z_

> The script uses ThreadPoolExecutor with max_workers=4 for source crawling and max_workers=6 for repo tree resolution. Each worker makes independent httpx calls to GitHub API. If rate limits are hit mid-execution, some futures may fail silently (caught in except blocks). The `batch_resolve_paths()` function groups by repo but doesn't implement retry or backoff. Understanding how partial failures affect the final index completeness is important for CI reliability.

## Summary

No specific investigation topic was provided. The user message only contained a truncated project brief about the hermes-agent workspace (1017 source files across 20 top-level areas). I examined the workspace root, README.md, pyproject.toml, cli.py, run_agent.py, utils.py, scripts/build_skills_index.py, and tools/skills_hub.py to understand the project structure. Hermes Agent is a self-improving AI agent by Nous Research with features including skills system, messaging gateway, cron scheduling, and support for multiple LLM providers. Without a concrete investigation topic, there is nothing specific to investigate.

## Findings

Hermes Agent is an AI agent framework (v0.13.0) built by Nous Research. Key files examined:

- **cli.py** (13,737 lines): Interactive terminal CLI with prompt_toolkit, slash commands, toolset selection
- **run_agent.py** (16,060 lines): Core agent runner with tool calling, conversation loop, multi-provider support
- **utils.py** (362 lines): Shared utilities including atomic file writes, env var helpers
- **scripts/build_skills_index.py** (326 lines): Builds centralized JSON catalog of all skills from multiple sources
- **tools/skills_hub.py** (3,262 lines): Skills Hub source adapters, hub state management, GitHub auth
- **pyproject.toml** (265 lines): Package config with exact-pinned dependencies, many optional extras
- **README.md**: Project overview, install instructions, feature table

The workspace has 20+ top-level directories including agent/, tools/, hermes_cli/, gateway/, skills/, plugins/, providers/, tests/, website/, etc.

## Files examined

- `README.md`
- `pyproject.toml`
- `cli.py`
- `run_agent.py`
- `utils.py`
- `scripts/build_skills_index.py`
- `tools/skills_hub.py`
