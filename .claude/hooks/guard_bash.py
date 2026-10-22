#!/usr/bin/env python3
"""PreToolUse hook for Bash and PowerShell (Windows). PROTECTED FILE.

Blocks (exit 2, reason on stderr, which Claude sees):
  1. Writing, moving or deleting protected files from the shell.
  2. Running tools/approve.py (human-only).
  3. Network and download tools (curl, wget, Invoke-WebRequest, ...).
  4. Copying G-code anywhere by hand: it reaches the SD card only through
     tools/export_sd.py, and only if the G-code passes the validator and,
     when config/safety.json requires it, has a fresh human approval bound
     to the file's SHA-256.

This is a guardrail against mistakes, not a sandbox against a determined
adversary. Hooks also fire inside subagents.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import shlex
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()

PROTECTED_MARKERS = [
    "config/safety.json",
    "approval.json",
    ".claude/",
    ".claude\\",
    "CLAUDE.md",
    "tools/gcode_validator.py",
    "tools/approve.py",
    "tools/export_sd.py",
    "sd_export.json",
]
READ_ONLY = {"cat", "less", "more", "head", "tail", "grep", "rg", "ls", "wc", "sha256sum",
             "shasum", "diff", "file", "stat", "jq", "md5sum", "realpath", "readlink",
             # PowerShell read-only cmdlets and aliases
             "get-content", "gc", "type", "get-filehash", "select-string", "sls", "get-childitem",
             "dir", "gci", "get-item", "test-path", "resolve-path"}
PS_NETWORK = {"invoke-webrequest", "iwr", "invoke-restmethod", "irm", "start-bitstransfer", "bitsadmin",
              "certutil", "new-object", "net.webclient", "system.net.webclient", "curl.exe", "wget.exe"}
GIT_READ_ONLY = {"diff", "log", "show", "status", "blame"}
WRAPPERS = {"sudo", "nohup", "time", "nice", "env", "command", "exec", "&", "start-process", "cmd", "/c"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n|(?<![>&])&(?!>)")
REDIRECT_TARGET = re.compile(r">{1,2}\s*[\"']?([^\s\"';|&]+)")


def block(msg: str) -> None:
    print(f"BLOCKED by project safety hook: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def tokens_of(segment: str) -> list[str]:
    seg = segment.replace("\\", "/")  # Windows paths survive POSIX splitting
    try:
        toks = shlex.split(seg, posix=True)
    except ValueError:
        toks = seg.split()
    # drop leading VAR=value assignments and wrapper commands like sudo/timeout
    out = list(toks)
    while out:
        t = out[0]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            out.pop(0)
        elif os.path.basename(t).lower() in WRAPPERS:
            out.pop(0)
        elif os.path.basename(t) == "timeout":
            out.pop(0)
            if out and re.match(r"^\d", out[0]):
                out.pop(0)
        else:
            break
    return out


def program(toks: list[str]) -> str:
    if not toks:
        return ""
    name = toks[0].replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def is_python(prog: str) -> bool:
    return prog in {"py"} or prog.startswith("python")


def script_index(toks: list[str], script_name: str) -> int | None:
    """Index of the script token when the segment is `<python> [flags] tools/<script>`."""
    if not toks or not is_python(program(toks)):
        return None
    for i, t in enumerate(toks[1:], start=1):
        if t.startswith("-"):
            continue
        return i if t.replace("\\", "/").endswith(script_name) else None
    return None


def mentions_protected(text: str) -> str | None:
    norm = text.replace("\\", "/")
    for marker in PROTECTED_MARKERS:
        if marker.replace("\\", "/") in norm:
            return marker
    return None


def check_protected(segment: str, toks: list[str]) -> None:
    for target in REDIRECT_TARGET.findall(segment):
        hit = mentions_protected(target)
        if hit:
            block(f"redirecting output into protected path '{target}'. Protected files are changed by the user only.")

    if "approve.py" in segment.replace("\\", "/") and program(toks) not in READ_ONLY:
        block("tools/approve.py is for the human only, in their own terminal. "
              "Tell the user to run: python3 tools/approve.py jobs/<id>")

    hit = mentions_protected(segment)
    if not hit:
        return
    prog = program(toks)
    if prog in READ_ONLY:
        return
    if prog == "git" and len(toks) > 1 and toks[1] in GIT_READ_ONLY:
        return
    for runnable in ("tools/gcode_validator.py", "tools/export_sd.py"):
        idx = script_index(toks, runnable)
        if idx is not None and not mentions_protected(" ".join(toks[idx + 1:])):
            return  # running these is fine; pointing their output at a protected path is not
    block(f"command touches protected path '{hit}'. Only the user may change protected files; "
          "describe the change you need instead.")


def check_network(segment: str, toks: list[str], safety: dict) -> None:
    prog = program(toks)
    blocked_tools = set(safety.get("network_tools_blocked", ["curl", "wget", "nc", "ncat", "netcat", "telnet", "socat"]))
    low = segment.lower()
    if any(re.search(r"(^|[^a-z0-9_.-])" + re.escape(t) + r"($|[^a-z0-9_-])", low) for t in PS_NETWORK):
        block("web downloads from the shell (Invoke-WebRequest, Invoke-RestMethod, BITS, certutil, WebClient) "
              "are not allowed in this project. Ask the user to download the file.")
    if prog in blocked_tools:
        block(f"'{prog}' is not allowed in this project. Use the WebFetch tool to read web pages, "
              "and ask the user to download files.")


def load_validator():
    path = PROJECT / "tools" / "gcode_validator.py"
    spec = importlib.util.spec_from_file_location("gcode_validator", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


COPY_PROGS = {"cp", "mv", "rsync", "scp", "dd", "install", "tee", "copy-item", "cpi", "copy", "move-item", "mi",
              "move", "robocopy", "xcopy", "set-content", "out-file", "new-item"}


def check_sd_export(command: str, segments: list[str], toks_list: list[list[str]], safety: dict) -> None:
    """G-code reaches the SD card only through tools/export_sd.py, and only when approved."""
    for i, seg in enumerate(segments):
        toks = toks_list[i]
        prog = program(toks)
        low = seg.lower()
        if any(t.lower().endswith((".gcode", ".bgcode")) for t in REDIRECT_TARGET.findall(seg)):
            block("G-code is never written by shell redirection. Use tools/slice.py, and tools/export_sd.py for the SD card.")
        if ".gcode" in low and prog in COPY_PROGS:
            block("G-code is copied to the SD card only by tools/export_sd.py, which checks the approval. "
                  "Use: python3 tools/export_sd.py jobs/<id> --drive <card>")
        if "export_sd.py" not in seg.replace("\\", "/"):
            continue
        if prog in READ_ONLY or (prog == "git" and len(toks) > 1 and toks[1] in GIT_READ_ONLY):
            continue
        idx = script_index(toks, "tools/export_sd.py")
        if idx is None:
            if re.search(r"--drive", seg):
                block("run tools/export_sd.py directly as `python3 tools/export_sd.py ...`, "
                      "not through another shell, wrapper or script.")
            continue  # e.g. running its tests
        args = toks[idx + 1:]
        if "--list" in args or "--dry-run" in args or "-h" in args or "--help" in args:
            continue
        if len(segments) > 1 or "$(" in command or "`" in command:
            block("an SD export must be a single command on its own, with nothing chained.")
        files = [a for a in args if not a.startswith("-")]
        drive_idx = args.index("--drive") if "--drive" in args else -1
        if drive_idx >= 0 and drive_idx + 1 < len(args) and args[drive_idx + 1] in files:
            files.remove(args[drive_idx + 1])
        if not files:
            block("no job folder given to export.")
        job = (PROJECT / files[0]).resolve() if not os.path.isabs(files[0]) else Path(files[0]).resolve()
        if (PROJECT / "jobs").resolve() not in job.parents:
            block("only job folders inside jobs/ can be exported.")
        gcode = job / "part.gcode"
        if not gcode.exists():
            block(f"no part.gcode in {files[0]}")

        gv = load_validator()
        req_path = job / "print_requirements.json"
        requirements = load_json(req_path) if req_path.exists() else None
        result = gv.validate(gcode, gv.load_safety(PROJECT / "config" / "safety.json"), requirements)
        if not result["pass"]:
            block("G-code failed validation: " + "; ".join(result["errors"][:5]))
        if not safety.get("require_human_approval", True):
            return
        approval = load_json(job / "approval.json")
        if not approval:
            block(f"no human approval for this job. The user must run, in their own terminal: "
                  f"python3 tools/approve.py jobs/{job.name}")
        if approval.get("sha256") != result["sha256"]:
            block("the approval does not match this exact G-code (the file changed after approval). "
                  f"The user must re-run: python3 tools/approve.py jobs/{job.name}")
        if approval.get("job_id") != job.name:
            block("approval belongs to a different job.")
        try:
            approved_at = dt.datetime.fromisoformat(approval["approved_at"])
        except (KeyError, ValueError):
            block("approval has no valid timestamp.")
        max_age = float(safety.get("approval_max_age_hours", 24))
        age_h = (dt.datetime.now(dt.timezone.utc) - approved_at).total_seconds() / 3600
        if age_h > max_age or age_h < -0.1:
            block(f"approval is {age_h:.1f} h old (limit {max_age:g} h). The user must re-approve.")


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    if event.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)
    command = (event.get("tool_input") or {}).get("command") or ""
    try:
        safety = load_json(PROJECT / "config" / "safety.json")
        segments = [s.strip() for s in SEGMENT_SPLIT.split(command) if s.strip()]
        toks_list = [tokens_of(s) for s in segments]
        for seg, toks in zip(segments, toks_list):
            check_protected(seg, toks)
            check_network(seg, toks, safety)
        check_sd_export(command, segments, toks_list, safety)
    except SystemExit:
        raise
    except Exception as exc:  # fail closed only where it matters
        if "export_sd" in command or "approve" in command or ".gcode" in command:
            block(f"safety hook error ({exc}); refusing G-code action.")
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
