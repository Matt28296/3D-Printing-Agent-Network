import json
import shutil
import subprocess
import sys
from pathlib import Path

import new_job

ROOT = Path(__file__).resolve().parent.parent


def test_new_job_creates_folder(tmp_path, capsys):
    (tmp_path / "docs" / "templates").mkdir(parents=True)
    shutil.copy(ROOT / "docs" / "templates" / "spec.md", tmp_path / "docs" / "templates")
    assert new_job.main(["Shelf Bracket!", "--root", str(tmp_path)]) == 0
    job_rel = capsys.readouterr().out.strip()
    job = tmp_path / job_rel
    assert job.name.endswith("-shelf-bracket")
    status = json.loads((job / "status.json").read_text())
    assert status["stage"] == "SPEC" and status["kind"] == "part"
    assert (job / "spec.md").exists() and (job / "renders").is_dir() and (job / "inputs").is_dir()
    assert new_job.main(["Shelf Bracket", "--root", str(tmp_path)]) == 1  # no overwrite


def test_approve_refuses_without_terminal(make_gcode, tmp_path):
    job = tmp_path / "jobs" / "20261017-x"
    make_gcode(directory=job)
    proc = subprocess.run([sys.executable, str(ROOT / "tools" / "approve.py"), str(job)],
                          input="20261017-x\n", capture_output=True, text=True)
    assert proc.returncode == 3
    assert not (job / "approval.json").exists()
