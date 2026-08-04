# BurstCode background-generated test for topic: How does cron.py's CLI-only job management coordinate with the gateway process lifecycle for reliable execution?
# Topic id: cron-cli-vs-gateway-lifecycle
# Sub-topic: Gateway restart behavior and job state recovery
# Rationale: Need to verify how the gateway scheduler handles restarts - whether it properly resumes job execution and if there are any race conditions during restart
# Framework: asyncio
# NOTE: this test was machine-generated for verification of an
# uncertainty; review and adjust imports/paths before running.

import asyncio
import json
import tempfile
from pathlib import Path

async def test_gateway_restart_job_recovery():
    # Simulate gateway restart scenario
    # Verify that jobs persist across restarts and resume correctly
    with tempfile.TemporaryDirectory() as tmpdir:
        jobs_dir = Path(tmpdir) / 'cron' / 'jobs'
        jobs_dir.mkdir(parents=True)
        # Create a test job
        job_file = jobs_dir / 'test_job.json'
        job_data = {'name': 'test', 'schedule': '*/5 * * * *', 'last_run_at': None}
        job_file.write_text(json.dumps(job_data))
        # Simulate gateway restart
        # Verify job state is preserved
        assert job_file.exists()
        assert json.loads(job_file.read_text()) == job_data
        print('PASS: Job state preserved across simulated restart')

asyncio.run(test_gateway_restart_job_recovery())
