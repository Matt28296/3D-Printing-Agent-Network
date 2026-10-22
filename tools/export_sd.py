#!/usr/bin/env python3
"""Copy an APPROVED job's G-code to the MK3's SD card. PROTECTED FILE.

    python3 tools/export_sd.py --list                         # show SD card candidates
    python3 tools/export_sd.py jobs/<id> --drive E:           # Windows
    python3 tools/export_sd.py jobs/<id> --drive /Volumes/PRUSA   # macOS / Linux
    python3 tools/export_sd.py jobs/<id> --drive E: --dry-run

Before copying it re-runs the G-code validator and, when config/safety.json
requires it, checks jobs/<id>/approval.json: same SHA-256, same job, not
expired. The copy is verified byte-for-byte, then recorded in sd_export.json.
The user then puts the card in the printer and starts the file from the LCD.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gcode_validator as gv  # noqa: E402

MAX_NAME = 24  # the MK3 LCD shows short names best


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sd_name(job_id: str) -> str:
    """'20261017-shelf-bracket' -> '1017_shelf_bracket.gcode' (ASCII, short)."""
    m = re.match(r"^\d{4}(\d{4})-(.+)$", job_id)
    stem = f"{m.group(1)}_{m.group(2)}" if m else job_id
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_")[:MAX_NAME].rstrip("_")
    return f"{stem}.gcode"


def _windows_removable() -> list[str]:
    import ctypes
    out = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    sysdrive = os.environ.get("SystemDrive", "C:").upper()
    for i in range(26):
        if bitmask & (1 << i):
            letter = f"{chr(65 + i)}:"
            if letter.upper() != sysdrive and ctypes.windll.kernel32.GetDriveTypeW(letter + "\\") == 2:
                out.append(letter)
    return out


def candidates() -> list[str]:
    system = platform.system()
    if system == "Windows":
        return _windows_removable()
    user = os.environ.get("USER", "")
    roots = [Path("/Volumes")] if system == "Darwin" else [Path("/media") / user, Path("/run/media") / user, Path("/media")]
    found = []
    for r in roots:
        if r.is_dir():
            for p in sorted(r.iterdir()):
                if p.is_dir() and p.name not in ("Macintosh HD", "Recovery", user) and os.access(p, os.W_OK):
                    found.append(str(p))
    return found


def drive_root(drive: str) -> Path:
    if re.fullmatch(r"[A-Za-z]:?[\\/]?", drive):
        return Path(drive[0].upper() + ":\\")
    m = re.fullmatch(r"/([A-Za-z])(/.*)?", drive)  # Git Bash style /e or /e/folder
    if m and platform.system() == "Windows":
        return Path(m.group(1).upper() + ":\\" + (m.group(2) or "").lstrip("/"))
    return Path(drive)


def is_safe_target(root: Path) -> tuple[bool, str]:
    if not root.exists() or not root.is_dir():
        return False, f"{root} does not exist; is the SD card inserted?"
    resolved = root.resolve()
    if resolved == Path(resolved.anchor) and platform.system() != "Windows":
        return False, "refusing to write to a filesystem root"
    if ROOT.resolve() == resolved or ROOT.resolve() in resolved.parents:
        return False, "target is inside the project folder, not an SD card"
    home = Path.home().resolve()
    if resolved == home:
        return False, "target is your home folder, not an SD card"
    if platform.system() == "Windows":
        sysdrive = os.environ.get("SystemDrive", "C:").upper()
        if str(resolved).upper().startswith(sysdrive):
            return False, f"{root} is the system drive, not an SD card"
    if not os.access(root, os.W_OK):
        return False, f"{root} is not writable (is the card's lock switch on?)"
    return True, ""


def check_job(job: Path, safety: dict) -> tuple[Path, str, list[str]]:
    gcode = job / "part.gcode"
    problems: list[str] = []
    if not gcode.exists():
        return gcode, "", [f"no part.gcode in {job}"]
    req_path = job / "print_requirements.json"
    req = gv.load_json(req_path) if req_path.exists() else None
    result = gv.validate(gcode, safety, req)
    if not result["pass"]:
        problems.append("G-code failed validation: " + "; ".join(result["errors"][:5]))
    digest = result["sha256"] or sha256(gcode)
    if safety.get("require_human_approval", True):
        ap_path = job / "approval.json"
        if not ap_path.exists():
            problems.append(f"no human approval. The user must run: python3 tools/approve.py jobs/{job.name}")
        else:
            ap = json.loads(ap_path.read_text())
            if ap.get("sha256") != digest:
                problems.append("approval is for a different version of this G-code; the user must re-approve")
            if ap.get("job_id") != job.name:
                problems.append("approval belongs to another job")
            try:
                age_h = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(ap["approved_at"])).total_seconds() / 3600
                if age_h > float(safety.get("approval_max_age_hours", 24)) or age_h < -0.1:
                    problems.append(f"approval is {age_h:.1f} h old; the user must re-approve")
            except (KeyError, ValueError):
                problems.append("approval has no valid timestamp")
    return gcode, digest, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Copy an approved job's G-code to the printer's SD card.")
    ap.add_argument("job", nargs="?")
    ap.add_argument("--drive", help="SD card drive letter (E:) or mount path")
    ap.add_argument("--list", action="store_true", help="list likely SD card drives")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        c = candidates()
        print("\n".join(c) if c else "No removable drives found. Insert the SD card (or pass --drive).")
        return 0
    if not args.job or not args.drive:
        ap.error("give a job folder and --drive (use --list to find the card)")

    job = Path(args.job).resolve()
    if (ROOT / "jobs").resolve() not in job.parents:
        print("Only folders inside jobs/ can be exported.", file=sys.stderr)
        return 2
    safety = gv.load_safety(ROOT / "config" / "safety.json")
    gcode, digest, problems = check_job(job, safety)
    if problems:
        print("NOT EXPORTED:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1

    root = drive_root(args.drive)
    ok, why = is_safe_target(root)
    if not ok:
        print(f"NOT EXPORTED: {why}", file=sys.stderr)
        return 1
    target = root / sd_name(job.name)
    if target.exists() and not args.overwrite and sha256(target) != digest:
        print(f"NOT EXPORTED: {target} already exists with different content (use --overwrite).", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"DRY RUN: would copy {gcode.name} ({digest[:12]}…) to {target}")
        return 0

    tmp = target.with_suffix(".tmp")
    shutil.copyfile(gcode, tmp)
    os.replace(tmp, target)
    try:
        os.sync()
    except AttributeError:
        pass
    if sha256(target) != digest:
        print(f"Copy verification FAILED for {target}; the card may be faulty. Delete the file and retry.", file=sys.stderr)
        return 1
    record = {"job_id": job.name, "sd_file": target.name, "drive": str(root), "sha256": digest,
              "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (job / "sd_export.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"OK: copied and verified {target}. Safely eject the card, insert it in the printer, "
          f"and select '{target.name}' from Print from SD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
