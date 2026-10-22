#!/usr/bin/env python3
"""Create a job folder: python3 tools/new_job.py <slug> [--kind part|calibration]"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Create jobs/<YYYYMMDD>-<slug>/ with templates.")
    ap.add_argument("slug")
    ap.add_argument("--kind", choices=["part", "calibration"], default="part")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    root = Path(args.root)
    slug = re.sub(r"[^a-z0-9]+", "-", args.slug.lower()).strip("-")
    if not slug:
        print("Slug must contain letters or digits.", file=sys.stderr)
        return 2
    now = dt.datetime.now(dt.timezone.utc)
    job_id = f"{now:%Y%m%d}-{slug}"
    job = root / "jobs" / job_id
    if job.exists():
        print(f"{job} already exists; pick another slug.", file=sys.stderr)
        return 1

    (job / "renders").mkdir(parents=True)
    (job / "inputs").mkdir()
    template = root / "docs" / "templates" / "spec.md"
    if template.exists():
        shutil.copy(template, job / "spec.md")
    status = {
        "job_id": job_id,
        "stage": "SPEC",
        "kind": args.kind,
        "iterations": {"DESIGN": 0, "SLICE": 0},
        "gates": {k: None for k in ("SPEC", "DESIGN", "SLICE", "APPROVAL", "PRINT", "INSPECT", "RECORD")},
        "open_questions": [],
        "updated": now.isoformat(timespec="seconds"),
    }
    (job / "status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (job / "log.md").write_text(
        f"# Log for {job_id}\n\n- {now.isoformat(timespec='seconds')} · new_job.py · created ({args.kind})\n",
        encoding="utf-8")
    print(f"jobs/{job_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
