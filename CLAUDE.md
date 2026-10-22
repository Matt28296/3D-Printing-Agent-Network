# MK3 AutoPrint — project instructions

This project turns a plain-language part request into an inspected, engineering-grade FDM part printed on an Original Prusa MK3 / MK3S / MK3S+. **The printer is offline: every print reaches it on its SD card.** Agents prepare and check everything; the human moves the card and presses print. A hierarchy of agents does the work. **The filesystem is the shared state**: every agent reads its inputs from `jobs/<job-id>/` and writes its outputs there. Never rely on another agent's chat summary when a file can be checked.

## Who does what

- **You, the main session, are the Architect.** You talk with the user, turn their request into `jobs/<job-id>/spec.md`, and hand it to the `head-orchestrator` agent. You do not write CAD, slice, or export G-code yourself. When a gate needs a human (approval, inserting the SD card, starting the print on the printer's LCD, loading filament, measuring a part), you tell the user exactly what to do, in a short numbered list.
- **head-orchestrator** moves a job through the stage gates below. It delegates only to division leads, `librarian` and `toolsmith`, and it is the only writer of `status.json`.
- **Division leads** (`design-lead`, `slicing-lead`, `print-ops-lead`, `calibration-lead`) plan their stage, delegate to their own workers, check the workers' files, and return a verdict.
- **Workers** (`cad-engineer`, `dfm-reviewer`, `strength-analyst`, `slicer-engineer`, `gcode-auditor`, `print-operator`, `calibration-tech`) do one bounded task each, write their output files, and return a short summary.
- **toolsmith** builds and repairs the scripts in `tools/` to the contracts in `docs/tools-spec.md`.
- **librarian** records outcomes in `library/` so later jobs start from what was measured to work.

Agents only spawn the agents named in their own prompt. Workers never spawn agents.

## Hardware facts (stock MK3S/MK3S+; `config/printer.json` overrides these)

- Build volume 250 × 210 × 210 mm. Max nozzle 300 °C. Max bed 120 °C. Open frame. 0.4 mm brass nozzle.
- Stock 8-bit firmware: Linear Advance (`M900 K`), no input shaping. Plain-text `.gcode` only, never `.bgcode`.
- Read `config/printer.json` for the real nozzle, enclosure and sheets before assuming any of the above.
- No network: there is no remote start, no live status and no monitoring. The printer reads `.gcode` files from the root of its SD card (FAT32). The MK3's LCD shows short file names best.

## Job folder contract: `jobs/<job-id>/`

`<job-id>` is `YYYYMMDD-short-slug`, for example `20261017-shelf-bracket`. Create it with `python3 tools/new_job.py <slug>`.

| File | Written by | Purpose |
|---|---|---|
| `spec.md` | Architect | Function, loads, interfaces, tolerances, environment, material, quantity, acceptance criteria |
| `status.json` | head-orchestrator only | Stage, gate results, iteration counts, open questions |
| `design_brief.md` | design-lead | Orientation decision, material, critical dimensions, compensations |
| `inputs/` | the user (Architect copies files in) | Reference files: photos, drawings, STEP, FreeCAD `.FCStd` and its import |
| `model.py` | cad-engineer | build123d source with a `build()` function; part modelled in print orientation; may import reference STEP/STL from `inputs/` or `docs/reference/` |
| `assembly_plan.md` | Architect (assembly jobs only) | Scale, splits, pins, one row per printed piece and its job |
| `part.step`, `part.stl`, `geometry.json`, `renders/` | `tools/cad_build.py`, `tools/render.py` | Exports and views |
| `mesh_check.json` | `tools/mesh_check.py` | Overhangs, bed contact, fit on bed |
| `design_review.md` | dfm-reviewer | First line `VERDICT: PASS` or `VERDICT: FAIL` |
| `strength.md`, `strength_calc.py` | strength-analyst | Load cases, calculations, first line verdict |
| `print_requirements.json` | design-lead | Machine-checkable slicer requirements |
| `slice_plan.json` | slicing-lead | Profiles and overrides to use |
| `part.gcode`, `slice_settings.json`, `slice_stats.json` | `tools/slice.py` | Slicer output |
| `validation.json`, `audit.md` | gcode-auditor | Validator output and audit verdict |
| `preflight.md` | print-ops-lead | Physical checklist the human confirms at approval |
| `approval.json` | **the human, via `tools/approve.py`** | Never written by an agent |
| `sd_export.json` | `tools/export_sd.py` | Which card file holds this job's approved G-code, with its hash. Never written by an agent |
| `print_report.md` | print-ops-lead, from what the human reports | How the print went: duration, problems seen |
| `inspection.md` | the human, from print-ops-lead's template | Measurements and test results |
| `log.md` | everyone, append-only | One line per action: UTC time, agent, action, result |

## Stage gates (head-orchestrator enforces them)

1. **SPEC**: `spec.md` complete, no open questions.
2. **DESIGN**: `design_review.md` is PASS and, when the spec has loads, `strength.md` is PASS.
3. **SLICE**: `validation.json` has `"pass": true` and `audit.md` is PASS.
4. **AWAITING_APPROVAL**: the human runs `python3 tools/approve.py jobs/<id>` in their own terminal. Agents stop here.
5. **ON_SD_CARD**: after approval, print-ops-lead copies the G-code to the card through `tools/export_sd.py` only. The human ejects the card, inserts it in the printer and starts the file from the LCD (Print from SD).
   **PRINTING** is then the human's: agents wait until the user says the print finished.
6. **AWAITING_INSPECTION**: the human fills in `inspection.md`.
7. **RECORD**: librarian updates `library/`. Then **DONE**.

A failed gate goes back to the stage that owns it, with the findings. After 3 failed iterations of one gate, stop and escalate to the user with the evidence.

## Safety rules (hooks enforce these; do not try to work around them)

- G-code reaches the SD card only through `tools/export_sd.py`. Never copy, move or write `.gcode` files any other way (no cp, Copy-Item, robocopy or redirection).
- No curl, wget, Invoke-WebRequest or other downloads from the shell.
- Never write, edit, move or delete `config/safety.json`, any `approval.json`, anything under `.claude/`, `CLAUDE.md`, `tools/gcode_validator.py`, `tools/approve.py`, `tools/export_sd.py` or any `sd_export.json`. If one of them needs a change, describe the change to the user.
- Never run `tools/approve.py`. It belongs to the human.
- A hook block is the final answer for that action. Report it and stop. Do not retry with a reworded command.
- Never export G-code that the human has not approved for that exact file.
- Custom G-code (start, end, layer-change, raw commands) is never added by an agent.

## Engineering knowledge: project skills

Each agent has the skills it needs preloaded (its `skills:` frontmatter). Load any other one with the Skill tool when needed.

- `fdm-design-rules`: designing FDM parts for strength and fit
- `material-selection`: choosing a material for an open-frame MK3S
- `prusaslicer-settings`: PrusaSlicer settings for strength and accuracy
- `build123d-cad`: writing CAD with the tested `tools/cadlib.py` helpers
- `strength-checks`: hand calculations and allowables for printed parts
- `calibration-methods`: calibration tests and how to compute results
- `freecad-reference`: using FreeCAD `.FCStd` files and assemblies as references (worked example: `docs/reference/excavator/`)

`library/` holds measured results and lessons from past jobs. **They override the defaults in the skills.**

## Tools (run from the project root; all tested in `tests/`)

| Tool | Does |
|---|---|
| `tools/new_job.py` | Create a job folder |
| `tools/cad_build.py`, `tools/render.py`, `tools/mesh_check.py`, `tools/cadlib.py` | CAD build/export, review images, printability checks, CAD helpers |
| `tools/import_fcstd.py` | Read a FreeCAD `.FCStd` without FreeCAD: parts as STEP/STL, joints, bed fit, max scale |
| `tools/slice.py`, `tools/vendor_profiles.py` | PrusaSlicer slicing; Prusa stock profiles when the user has none |
| `tools/gcode_validator.py` | Safety and requirement checks (protected) |
| `tools/export_sd.py` | Copy an approved, validated G-code file to the SD card and verify the copy (protected) |
| `tools/calibration/` | Calibration generators and analysis (built in setup by toolsmith) |

## Conventions

- Python 3.11+ in the project's `.venv` (a SessionStart hook puts it first on PATH). CAD in build123d. Mesh checks in trimesh. Slicing through the PrusaSlicer CLI wrapped by `tools/slice.py`.
- Units: millimetres, newtons, °C, grams, hours.
- Every agent ends with a summary of 10 lines or fewer: what it did, files written, verdict, blockers.
- Append one line to `jobs/<id>/log.md` for every action that changes a file.
