import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

import export_sd
import gcode_validator as gv

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def job(make_gcode):
    j = ROOT / "jobs" / "20261017-test-bracket"
    shutil.rmtree(j, ignore_errors=True)
    make_gcode(directory=j)
    yield j
    shutil.rmtree(j, ignore_errors=True)


@pytest.fixture
def card(tmp_path):
    c = tmp_path / "SDCARD"
    c.mkdir()
    return c


def approve(job, sha=None, hours_ago=0.0):
    when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours_ago)
    (job / "approval.json").write_text(json.dumps({
        "job_id": job.name, "gcode": "part.gcode", "sha256": sha or gv.sha256_file(job / "part.gcode"),
        "approved_at": when.isoformat(timespec="seconds")}))


def test_sd_name():
    assert export_sd.sd_name("20261017-shelf-bracket") == "1017_shelf_bracket.gcode"
    assert len(export_sd.sd_name("20261017-" + "x" * 80)) <= export_sd.MAX_NAME + 6


def test_refuses_without_approval(job, card, capsys):
    assert export_sd.main([str(job), "--drive", str(card)]) == 1
    assert "approve.py" in capsys.readouterr().err
    assert not list(card.iterdir())


def test_exports_and_verifies_with_approval(job, card):
    approve(job)
    assert export_sd.main([str(job), "--drive", str(card)]) == 0
    out = card / "1017_test_bracket.gcode"
    assert out.read_bytes() == (job / "part.gcode").read_bytes()
    rec = json.loads((job / "sd_export.json").read_text())
    assert rec["sd_file"] == out.name and rec["sha256"] == gv.sha256_file(out)


def test_refuses_changed_gcode(job, card):
    approve(job)
    g = job / "part.gcode"
    g.write_text(g.read_text() + "\n; edited after approval\n")
    assert export_sd.main([str(job), "--drive", str(card)]) == 1


def test_refuses_stale_approval(job, card):
    approve(job, hours_ago=30)
    assert export_sd.main([str(job), "--drive", str(card)]) == 1


def test_refuses_invalid_gcode_even_if_approved(job, card, make_gcode):
    make_gcode(directory=job, temp=320)
    approve(job)
    assert export_sd.main([str(job), "--drive", str(card)]) == 1


def test_refuses_target_inside_project(job):
    approve(job)
    assert export_sd.main([str(job), "--drive", str(ROOT / "jobs")]) == 1


def test_refuses_missing_card(job, tmp_path):
    approve(job)
    assert export_sd.main([str(job), "--drive", str(tmp_path / "nope")]) == 1


def test_no_silent_overwrite(job, card):
    approve(job)
    (card / "1017_test_bracket.gcode").write_text("something else")
    assert export_sd.main([str(job), "--drive", str(card)]) == 1
    assert export_sd.main([str(job), "--drive", str(card), "--overwrite"]) == 0


def test_dry_run_copies_nothing(job, card):
    approve(job)
    assert export_sd.main([str(job), "--drive", str(card), "--dry-run"]) == 0
    assert not list(card.iterdir())


def test_only_jobs_folders(card, make_gcode, tmp_path):
    other = tmp_path / "elsewhere"
    make_gcode(directory=other)
    assert export_sd.main([str(other), "--drive", str(card)]) == 2
