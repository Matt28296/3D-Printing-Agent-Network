#!/usr/bin/env python3
"""PreToolUse hook for Write / Edit / MultiEdit / NotebookEdit. PROTECTED FILE.

Blocks (exit 2):
  - edits to protected files (safety config, approvals, .claude/, CLAUDE.md,
    the validator and the approval tool)
  - hand-written G-code anywhere (.gcode / .bgcode files come from the tools,
    and reach the SD card only through tools/export_sd.py)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()

PROTECTED_EXACT = {"config/safety.json", "CLAUDE.md", "tools/gcode_validator.py", "tools/approve.py",
                   "tools/export_sd.py"}
PROTECTED_PREFIX = (".claude/",)


def block(msg: str) -> None:
    print(f"BLOCKED by project safety hook: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    tool = event.get("tool_name", "")
    ti = event.get("tool_input") or {}
    raw_path = ti.get("file_path") or ti.get("notebook_path") or ""
    if not raw_path:
        sys.exit(0)

    path = Path(raw_path)
    if not path.is_absolute():
        path = Path(event.get("cwd") or PROJECT) / path
    path = path.resolve()

    if path.suffix.lower() in (".gcode", ".bgcode"):  # anywhere, including the SD card
        block("G-code is never written by hand. Produce it with tools/slice.py or a tools/calibration/ script, "
              "and copy it to the SD card with tools/export_sd.py.")

    try:
        rel = path.relative_to(PROJECT).as_posix()
    except ValueError:
        sys.exit(0)  # outside the project: not this hook's concern

    if rel in PROTECTED_EXACT or rel.startswith(PROTECTED_PREFIX) or path.name in ("approval.json", "sd_export.json"):
        block(f"'{rel}' is protected. Only the user changes it; describe the change you need instead.")
    sys.exit(0)


if __name__ == "__main__":
    main()
