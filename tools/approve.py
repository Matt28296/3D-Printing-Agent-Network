#!/usr/bin/env python3
"""Human approval for one MK3 print. PROTECTED FILE.

Run this yourself, in your own terminal, never through Claude:

    python3 tools/approve.py jobs/<job-id>            # approve jobs/<id>/part.gcode
    python3 tools/approve.py jobs/<job-id> --gcode other.gcode
    python3 tools/approve.py jobs/<job-id> --revoke

It re-validates the G-code, shows what will be printed and the preflight
checklist, and asks you to type the job id. The approval is bound to the
file's SHA-256, so any later change to the G-code voids it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gcode_validator as gv  # noqa: E402


def fmt_hours(seconds):
    if not seconds:
        return "unknown"
    h, rem = divmod(int(seconds), 3600)
    return f"{h}h {rem // 60:02d}m"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Approve one MK3 print (human only).")
    ap.add_argument("job_dir")
    ap.add_argument("--gcode", default="part.gcode")
    ap.add_argument("--revoke", action="store_true")
    args = ap.parse_args(argv)

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("approve.py must be run by a person in an interactive terminal.", file=sys.stderr)
        return 3

    job_dir = Path(args.job_dir).resolve()
    approval_path = job_dir / "approval.json"
    if args.revoke:
        if approval_path.exists():
            approval_path.unlink()
            print(f"Approval revoked for {job_dir.name}.")
        else:
            print("No approval to revoke.")
        return 0

    gcode = job_dir / args.gcode
    if not gcode.exists():
        print(f"G-code not found: {gcode}", file=sys.stderr)
        return 2

    safety = gv.load_safety()
    req_path = job_dir / "print_requirements.json"
    requirements = gv.load_json(req_path) if req_path.exists() else None
    result = gv.validate(gcode, safety, requirements)
    st = result["stats"]

    print("=" * 64)
    print(f" Job:        {job_dir.name}")
    print(f" File:       {gcode.relative_to(ROOT) if gcode.is_relative_to(ROOT) else gcode}")
    print(f" SHA-256:    {result['sha256'][:16]}…")
    print(f" Sliced by:  {st.get('generator') or 'unknown'}")
    print(f" Material:   {st.get('filament_type')}   nozzle max {st.get('max_nozzle_c')} °C   bed max {st.get('max_bed_c')} °C")
    print(f" Settings:   layer {st.get('layer_height')} mm, {st.get('perimeters')} perimeters, infill {st.get('fill_density')}% {st.get('fill_pattern') or ''}")
    print(f" Estimate:   {fmt_hours(st.get('print_time_s'))}, {st.get('filament_g')} g filament")
    ext = st.get("extents_mm", {})
    print(f" Extents:    X {ext.get('X')}  Y {ext.get('Y')}  Z {ext.get('Z')}")
    print(f" Requirements file: {'yes' if requirements else 'NONE'}")
    print("=" * 64)
    for w in result["warnings"]:
        print(f" warning: {w}")
    if not result["pass"]:
        print("\nValidation FAILED. This file cannot be approved:")
        for e in result["errors"]:
            print(f"  - {e}")
        return 1

    preflight = job_dir / "preflight.md"
    if preflight.exists():
        print("\nPreflight checklist (confirm each one at the printer):\n")
        print(preflight.read_text(encoding="utf-8"))
    else:
        print("\n(no preflight.md for this job; check material, sheet and bed yourself)")

    typed = input(f"\nType the job id ({job_dir.name}) to approve this exact file, anything else cancels: ").strip()
    if typed != job_dir.name:
        print("Not approved.")
        return 1
    note = input("Optional note (Enter to skip): ").strip()

    approval = {
        "job_id": job_dir.name,
        "gcode": args.gcode,
        "sha256": result["sha256"],
        "approved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "approver": getpass.getuser(),
        "host": socket.gethostname(),
        "validator_version": gv.VERSION,
        "note": note,
    }
    approval_path.write_text(json.dumps(approval, indent=2) + "\n", encoding="utf-8")
    hours = safety.get("approval_max_age_hours", 24)
    print(f"\nApproved. Valid for {hours} h and only for this exact file.")
    print(f"Now insert the SD card in this computer and tell Claude: /resume-job {job_dir.name} approved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
