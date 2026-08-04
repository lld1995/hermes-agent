# Async Threat Intel Batch Skill (Hermes)

Hermes-compatible skill that batch-enriches IOC text files through the
bundled `threat-intel-plugin.jar`. The agent submits an async job, polls
for completion, fetches the artifact to local disk, and reports the path.

## Layout

```
async-threat-intel-batch-importable/
├── SKILL.md                          # Required — frontmatter + instructions
├── assets/
│   └── threat-intel-plugin.jar       # Executable bundle
├── references/
│   └── workflow.yaml                 # Legacy platform definition (not executed)
└── README.md
```

## Prerequisites

- Java on `PATH` (the skill declares `prerequisites.commands: [java]`).

## Install

Copy the directory into Hermes' skills dir (skills are seeded from
`~/.hermes/skills/`):

```powershell
Copy-Item -Recurse -Force .\ $env:USERPROFILE\.hermes\skills\async-threat-intel-batch
```

Or leave it in place and point Hermes at this folder via
`~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - E:\project\hermes-agent\sm-skills
```

Then confirm the skill is visible:

```powershell
hermes skills              # interactive enable/disable UI
```

Inside a Hermes session you can also check:

```
/skills                    # search + manage skills
skills_list                # tool — lists registered skills
skill_view async-threat-intel-batch   # tool — loads full instructions
```

## Trigger

Just describe the task to the agent in natural language:

> 这是一份 IOC 列表 `C:\tmp\ioc.txt`，帮我跑一次批量威胁情报富化，结果存到 `C:\tmp\out\`。

The agent will load `SKILL.md`, call `java -jar
assets/threat-intel-plugin.jar submit_batch ...`, poll, then fetch the
artifact.

## Notes on the legacy bundle

The original `workflow.yaml` (kept in `references/`) targeted a different
platform's workflow engine with `async_job.prepare` / `async_job.submit` /
`run.suspend` task refs and a `/api/skills/import` BFF endpoint. Hermes
has none of those — it executes the JAR directly via `run_command`. The
YAML is retained only as historical documentation.
