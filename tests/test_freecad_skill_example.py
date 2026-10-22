"""The model.py example in the freecad-reference skill must build and fit the bed."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("build123d")
ROOT = Path(__file__).resolve().parent.parent


def test_skill_example_builds():
    text = (ROOT / ".claude" / "skills" / "freecad-reference" / "SKILL.md").read_text()
    code = re.search(r"```python\n(.*?)```", text, re.S).group(1)
    job = ROOT / "jobs" / "_pytest_skill_example"
    shutil.rmtree(job, ignore_errors=True)
    (job / "inputs").mkdir(parents=True)
    try:
        shutil.copytree(ROOT / "docs" / "reference" / "excavator", job / "inputs" / "excavator")
        (job / "model.py").write_text(code)
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "cad_build.py"), str(job)],
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr
        geo = json.loads((job / "geometry.json").read_text())
        assert geo["fits_bed"] and geo["bbox_mm"][2] < 20
    finally:
        shutil.rmtree(job, ignore_errors=True)
