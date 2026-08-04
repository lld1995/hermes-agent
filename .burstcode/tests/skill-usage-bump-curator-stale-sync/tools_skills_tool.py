# BurstCode background-generated test for topic: How does skills_tool.py's bump_view/bump_use telemetry coordinate with the curator's stale/archive transition logic to prevent active skills from being pruned?
# Topic id: skill-usage-bump-curator-stale-sync
# Sub-topic: Whether bump_view + bump_use double-counting on skill_view is intentional or a subtle over-counting
# Rationale: Every successful skill_view calls both bump_view() and bump_use(), incrementing both view_count and use_count. The comment at skills_tool.py:1550-1552 justifies this as intentional ('counts as use, not just a browse/view'). However, if a skill is viewed many times but never actually invoked in a task, use_count will be high. The curator's latest_activity_at uses the max of all timestamps, so this doesn't affect stale/archive timing — but it could mislead human readers of the usage report.
# Framework: hermes-agent
# NOTE: this test was machine-generated for verification of an
# uncertainty; review and adjust imports/paths before running.

import json, os, tempfile
from pathlib import Path
from unittest.mock import patch

def test_skill_view_bumps_both_view_and_use():
    """Verify that a single skill_view call increments both view_count and use_count."""
    with tempfile.TemporaryDirectory() as tmp:
        hermes_home = Path(tmp) / ".hermes"
        skills_dir = hermes_home / "skills"
        skills_dir.mkdir(parents=True)
        # Create a minimal skill
        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: test-skill\ndescription: test\n---\n# Test")
        os.environ["HERMES_HOME"] = str(hermes_home)
        from tools.skill_usage import load_usage
        from tools.skills_tool import skill_view
        result = skill_view("test-skill")
        data = load_usage()
        rec = data.get("test-skill", {})
        assert rec.get("view_count") == 1, f"Expected view_count=1, got {rec.get('view_count')}"
        assert rec.get("use_count") == 1, f"Expected use_count=1, got {rec.get('use_count')}"
        del os.environ["HERMES_HOME"]
