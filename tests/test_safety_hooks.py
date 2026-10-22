"""The safety hooks are the last line of defence; test them like it."""
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import gcode_validator as gv

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def project(tmp_path, make_gcode):
    proj = tmp_path / "proj"
    (proj / ".claude").mkdir(parents=True)
    shutil.copytree(ROOT / ".claude" / "hooks", proj / ".claude" / "hooks")
    (proj / "tools").mkdir()
    shutil.copy(ROOT / "tools" / "gcode_validator.py", proj / "tools")
    (proj / "config").mkdir()
    shutil.copy(ROOT / "config" / "safety.json", proj / "config")
    shutil.copy(ROOT / "config" / "printer.json", proj / "config")
    make_gcode(directory=proj / "jobs" / "20261017-bracket")
    return proj


def run_hook(project, hook, tool_name, tool_input):
    event = {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(project),
             "hook_event_name": "PreToolUse"}
    proc = subprocess.run(
        [sys.executable, str(project / ".claude" / "hooks" / hook)],
        input=json.dumps(event), capture_output=True, text=True,
        env={"CLAUDE_PROJECT_DIR": str(project), "PATH": "/usr/bin:/bin"},
    )
    return proc.returncode, proc.stderr


def bash(project, command):
    return run_hook(project, "guard_bash.py", "Bash", {"command": command})


def approve(project, job="20261017-bracket", sha=None, hours_ago=0.0):
    gcode = project / "jobs" / job / "part.gcode"
    when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours_ago)
    (gcode.parent / "approval.json").write_text(json.dumps({
        "job_id": job, "gcode": "part.gcode", "sha256": sha or gv.sha256_file(gcode),
        "approved_at": when.isoformat(timespec="seconds"),
    }))


START = "python3 tools/export_sd.py jobs/20261017-bracket --drive E:"


# ---- guard_bash: protected files and approve.py -------------------------------------
@pytest.mark.parametrize("cmd", [
    "cat config/safety.json",
    "ls .claude/agents",
    "git diff CLAUDE.md",
    "python3 tools/gcode_validator.py jobs/20261017-bracket/part.gcode --out jobs/20261017-bracket/validation.json",
    "python3 -m pytest -q tests/test_export_sd.py",
    "python3 tools/export_sd.py --list",
    "python3 tools/cad_build.py jobs/20261017-bracket 2>&1 | tail -20",
])
def test_allowed_commands(project, cmd):
    assert bash(project, cmd)[0] == 0


@pytest.mark.parametrize("cmd", [
    "sed -i 's/true/false/' config/safety.json",
    "echo '{}' > jobs/20261017-bracket/approval.json",
    "cp /tmp/x jobs/20261017-bracket/approval.json",
    "rm -rf .claude/hooks",
    "python3 -c \"open('config/safety.json','w').write('{}')\"",
    "python3 tools/approve.py jobs/20261017-bracket",
    "echo 20261017-bracket | python3 tools/approve.py jobs/20261017-bracket",
    "python3 tools/gcode_validator.py jobs/x/part.gcode --out jobs/x/approval.json",
    "cat x > CLAUDE.md",
])
def test_protected_commands_blocked(project, cmd):
    code, err = bash(project, cmd)
    assert code == 2, cmd
    assert "BLOCKED" in err


# ---- guard_bash: network --------------------------------------------------------------
@pytest.mark.parametrize("cmd", [
    "curl https://example.com",
    "sudo wget http://x",
])
def test_network_blocked(project, cmd):
    assert bash(project, cmd)[0] == 2


# ---- guard_bash: SD export ------------------------------------------------------
def test_start_without_approval_blocked(project):
    code, err = bash(project, START)
    assert code == 2 and "approve.py" in err


def test_start_with_valid_approval_allowed(project):
    approve(project)
    assert bash(project, START)[0] == 0


def test_start_after_gcode_changed_blocked(project):
    approve(project)
    g = project / "jobs" / "20261017-bracket" / "part.gcode"
    g.write_text(g.read_text() + "\n; edited\n")
    code, err = bash(project, START)
    assert code == 2 and "does not match" in err


def test_start_with_stale_approval_blocked(project):
    approve(project, hours_ago=30)
    code, err = bash(project, START)
    assert code == 2 and "old" in err


def test_start_chained_blocked(project):
    approve(project)
    assert bash(project, "python3 tools/export_sd.py --list && " + START)[0] == 2


def test_start_via_wrapper_shell_blocked(project):
    approve(project)
    assert bash(project, f'bash -c "{START}"')[0] == 2


@pytest.mark.parametrize("cmd", [
    "cp jobs/20261017-bracket/part.gcode /e/",
    "cp jobs/20261017-bracket/part.gcode E:/x.gcode",
    "Copy-Item jobs\\20261017-bracket\\part.gcode E:\\x.gcode",
    "robocopy jobs E:\\ part.gcode",
    "cat jobs/20261017-bracket/part.gcode > /media/sd/x.gcode",
])
def test_manual_gcode_copy_blocked(project, cmd):
    approve(project)
    assert bash(project, cmd)[0] == 2, cmd


def test_start_invalid_gcode_blocked_even_if_approved(project, make_gcode):
    make_gcode(directory=project / "jobs" / "20261017-bracket", temp=320)
    approve(project)
    code, err = bash(project, START)
    assert code == 2 and "failed validation" in err


def test_start_outside_jobs_blocked(project, make_gcode):
    make_gcode(directory=project / "elsewhere")
    assert bash(project, "python3 tools/export_sd.py elsewhere --drive E:")[0] == 2


def test_dry_run_allowed_without_approval(project):
    assert bash(project, START + " --dry-run")[0] == 0


def test_auto_approve_mode_still_validates(project, make_gcode):
    safety = json.loads((project / "config" / "safety.json").read_text())
    safety["require_human_approval"] = False
    (project / "config" / "safety.json").write_text(json.dumps(safety))
    assert bash(project, START)[0] == 0
    make_gcode(directory=project / "jobs" / "20261017-bracket", bed=130)
    assert bash(project, START)[0] == 2


# ---- protect_paths ------------------------------------------------------------------------
def write(project, path, content="x", tool="Write"):
    key = "content" if tool == "Write" else "new_string"
    return run_hook(project, "protect_paths.py", tool, {"file_path": str(project / path), key: content})


@pytest.mark.parametrize("path", [
    "config/safety.json", "CLAUDE.md", ".claude/agents/cad-engineer.md", ".claude/settings.json",
    "jobs/20261017-bracket/approval.json", "tools/gcode_validator.py", "tools/approve.py",
])
def test_protected_paths_blocked(project, path):
    assert write(project, path)[0] == 2
    assert write(project, path, tool="Edit")[0] == 2


def test_handwritten_gcode_blocked(project):
    assert write(project, "jobs/20261017-bracket/part.gcode", "G1 X0")[0] == 2


def test_normal_job_file_allowed(project):
    assert write(project, "jobs/20261017-bracket/model.py", "from build123d import *")[0] == 0



def test_gcode_on_sd_card_blocked(project, tmp_path):
    event_input = {"file_path": str(tmp_path / "SDCARD" / "x.gcode"), "content": "G1 X0"}
    assert run_hook(project, "protect_paths.py", "Write", event_input)[0] == 2


def test_sd_export_record_protected(project):
    assert write(project, "jobs/20261017-bracket/sd_export.json")[0] == 2
    assert write(project, "tools/export_sd.py")[0] == 2

# ---- Windows / PowerShell ---------------------------------------------------------------
def ps(project, command):
    return run_hook(project, "guard_bash.py", "PowerShell", {"command": command})


@pytest.mark.parametrize("cmd", [
    "Invoke-WebRequest https://example.com/x.exe -OutFile x.exe",
    "iwr https://example.com -o x",
    "(New-Object Net.WebClient).DownloadFile('http://x','y')",
    "Set-Content config/safety.json '{}'",
    "Remove-Item .claude\\hooks\\guard_bash.py",
    "Copy-Item x.json jobs\\20261017-bracket\\approval.json",
    "python tools\\approve.py jobs\\20261017-bracket",
    "& .venv\\Scripts\\python.exe tools\\export_sd.py jobs\\20261017-bracket --drive E:",
])
def test_powershell_blocked(project, cmd):
    assert ps(project, cmd)[0] == 2, cmd


@pytest.mark.parametrize("cmd", [
    "Get-Content config\\safety.json",
    "Get-FileHash .claude\\hooks\\guard_bash.py",
    "python tools\\export_sd.py --list",
    ".venv\\Scripts\\python.exe -m pytest -q",
])
def test_powershell_allowed(project, cmd):
    assert ps(project, cmd)[0] == 0, cmd


def test_windows_path_start_with_approval_allowed(project):
    approve(project)
    assert ps(project, "& .venv\\Scripts\\python.exe tools\\export_sd.py jobs\\20261017-bracket --drive E:")[0] == 0


def run_launcher(project, hook, event, path_env):
    return subprocess.run(["bash", str(project / ".claude" / "hooks" / "run_py.sh"), hook],
                          input=json.dumps(event), capture_output=True, text=True,
                          env={"CLAUDE_PROJECT_DIR": str(project), "PATH": path_env})


def test_launcher_runs_hook(project):
    ev = {"tool_name": "Bash", "tool_input": {"command": "curl x"}}
    r = run_launcher(project, "guard_bash.py", ev, str(Path(sys.executable).parent) + ":/usr/bin:/bin")
    assert r.returncode == 2 and "BLOCKED" in r.stderr
    ev = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
    assert run_launcher(project, "guard_bash.py", ev, str(Path(sys.executable).parent) + ":/usr/bin:/bin").returncode == 0


def test_launcher_fails_closed_without_python(project, tmp_path):
    empty = tmp_path / "emptybin"
    empty.mkdir()
    for tool in ("dirname", "cat"):  # only bash builtins + nothing named python
        pass
    bash = shutil.which("bash")
    r = subprocess.run([bash, str(project / ".claude" / "hooks" / "run_py.sh"), "guard_bash.py"],
                       input="{}", capture_output=True, text=True,
                       env={"CLAUDE_PROJECT_DIR": str(project), "PATH": str(empty)})
    assert r.returncode == 2 and "no working Python" in r.stderr
