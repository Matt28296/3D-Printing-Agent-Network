# Tool contracts (for the toolsmith)

Each tool is a Python 3.11+ script in `tools/`, run as `python3 tools/<name>.py ...` from the project root.

**Rules for every tool:**
- Exit code 0 on success, non-zero on failure. On failure, print a one-paragraph human-readable reason to stderr.
- Write machine-readable results as JSON files in the job folder.
- Never print secrets.
- Has tests in `tests/` (pytest). Tests must not need an SD card or PrusaSlicer unless they are marked `@pytest.mark.integration`.

**Already provided and protected. Do not modify; report bugs to the user:**
- `tools/gcode_validator.py`
- `tools/approve.py`
- `tools/export_sd.py` (item 6)
- `.claude/hooks/*`
- `config/safety.json`

**Already provided and tested, not protected.** Fix bugs if you find them, and keep their tests passing:

| Item | File | Tested how |
|---|---|---|
| 1 | `tools/new_job.py` | unit tests |
| 2 | `tools/cad_build.py` | plus `tools/cadlib.py` (CAD helpers); against build123d 0.13 |
| 3 | `tools/render.py` | headless z-buffer renderer |
| 4 | `tools/mesh_check.py` | unit tests |
| 5 | `tools/slice.py` | against PrusaSlicer 2.7.2 real output, which also passes `gcode_validator.py` |
| — | `tools/vendor_profiles.py` | flat Prusa stock profiles from PrusaSlicer's vendor bundle |
| — | `tools/import_fcstd.py` | FreeCAD `.FCStd` reader (parts, joints, bed fit, max scale); tested on `docs/reference/excavator/` |

**On the user's machine, re-run the full suite.** `slice.py` was tested on PrusaSlicer 2.7.2, so confirm the integration test passes on the user's PrusaSlicer (2.9.x expected). If a CLI flag or output format differs, fix `slice.py` and tell the user.

**Build items 8 and 9.** Each is done when its tests pass. Item specs 1–6 below are the contracts for the provided tools.

---

## 1. `tools/new_job.py <slug>`

- Creates `jobs/<YYYYMMDD>-<slug>/` and refuses if it exists.
- Creates these files:
  - `spec.md`, copied from `docs/templates/spec.md`
  - `log.md`, with one header line
  - `renders/`, empty
  - `status.json`, in this form:
    ```json
    {"job_id": "...", "stage": "SPEC", "iterations": {"DESIGN": 0, "SLICE": 0},
     "gates": {"SPEC": null, "DESIGN": null, "SLICE": null, "APPROVAL": null, "PRINT": null, "INSPECT": null, "RECORD": null},
     "open_questions": [], "kind": "part", "updated": "<UTC ISO>"}
    ```
- `--kind calibration` sets `"kind": "calibration"`.
- Prints the job path.

## 2. `tools/cad_build.py jobs/<id> [--timeout 300]`

- Runs `jobs/<id>/model.py` in a **separate Python process** with the job folder as the working directory, and kills it at the timeout.
- `build()` must return a build123d `Part` or `Compound`.
- Exports:
  - `part.step`
  - `part.stl`, with linear tolerance 0.01 mm and angular tolerance 0.1 rad (tolerance arguments of build123d `export_stl`; check the installed version's API)
- Writes `geometry.json`:
  ```json
  {"bbox_mm": [x, y, z], "min_z_mm": 0.0, "volume_mm3": 0, "area_mm2": 0,
   "solids": 1, "watertight": true, "fits_bed": true, "bed_mm": [250, 210, 210], "margin_mm": 5}
  ```
  - `watertight` comes from loading the STL with trimesh.
  - `fits_bed` uses the bed size from `config/printer.json` (default 250 × 210 × 210) minus a 5 mm margin on X and Y.
- Fails if `min_z_mm` is not within 0.01 of 0, if there are no solids, or if the mesh is not watertight.

## 3. `tools/render.py jobs/<id>`

- Writes PNGs from `part.stl` to `renders/`: `iso.png`, `front.png`, `right.png`, `top.png`, `bottom.png`.
- 800 × 800, using trimesh + matplotlib with the Agg backend (headless).
- Draws a grey bed plane at Z = 0 and a 10 mm scale bar in each view.
- Reviewers look at these images, so the part must be clearly lit and readable.

## 4. `tools/mesh_check.py jobs/<id> [--overhang-deg 45]`

Writes `mesh_check.json` with:
- `overhang_area_mm2` and `overhang_pct`: area of downward-facing faces steeper than the threshold, excluding faces within 0.2 mm of Z = 0
- `bed_contact_area_mm2`: faces with normal close to −Z and Z < 0.05
- `bbox_mm`, `fits_bed`
- `bridges`: a list of downward-facing horizontal regions above Z = 0.2 with their max span in mm, measured from the region's oriented bounding box
- `thin_wall_warnings`: optional; via ray casting, report regions thinner than 0.9 mm

## 5. `tools/slice.py jobs/<id> --plan jobs/<id>/slice_plan.json`

`slice_plan.json` takes this form:
```json
{"printer_profile": "profiles/printer/MK3S.ini",
 "print_profile": "profiles/print/0.20mm_QUALITY_MK3S.ini",
 "filament_profile": "profiles/filament/Prusament_PETG.ini",
 "overrides": {"perimeters": 5, "fill_density": "50%", "fill_pattern": "gyroid"},
 "model": "part.stl", "copies": 1, "rationale": "short text"}
```

What the tool does:
- Builds the PrusaSlicer CLI call: `--export-gcode`, a `--load` for each profile, one flag per override, then the model and `--output jobs/<id>/part.gcode`.
  - The executable comes from `config/printer.json` `prusaslicer_path`.
  - Override keys map to CLI flags by replacing `_` with `-`. Verify every flag against `prusa-slicer --help-fff` for the installed version and fail clearly on an unknown key.
  - Always forces plain-text G-code.
  - When `copies` > 1, uses PrusaSlicer's duplicate/arrange options.
- **Refuses** overrides of any key containing `gcode`, plus `post_process`, `printhost_*` and `binary_gcode`.
- Writes `slice_settings.json`: the exact command, SHA-256 of each profile file, the overrides and the PrusaSlicer version.
- Writes `slice_stats.json`, parsed from the G-code comments: `print_time_s`, `filament_g`, `filament_mm`, `layers`, `max_z_mm`, `filament_type`, `nozzle_temp_c`, `bed_temp_c`.

## 6. `tools/export_sd.py` (provided and protected)

The printer is offline. This tool is the only way G-code reaches the SD card:
`python3 tools/export_sd.py --list` · `python3 tools/export_sd.py jobs/<id> --drive <E: or mount path> [--dry-run] [--overwrite]`.
It re-validates, checks the approval (same SHA-256, same job, not expired), refuses system drives and the project folder, copies under a short name (`1017_shelf_bracket.gcode`), verifies the copy by hash and writes `sd_export.json`. Don't modify it; report bugs to the user.

## 7. (removed)

There is no printer client and no monitor: the printer has no network connection.

## 8. Calibration generators in `tools/calibration/`

Each one creates or uses a job folder (`--kind calibration`) and produces a `model.py`, or post-processes G-code produced by `tools/slice.py`. The output must still pass `tools/gcode_validator.py`.

| Script | Produces | Notes |
|---|---|---|
| `temp_tower.py --material X --from 250 --to 230 --step 5` | Temperature tower | Model plus a G-code post-processor that inserts `M104 S<t>` at the Z of each segment, with a marker comment |
| `flow_cube.py` | Single-wall 30 mm cube | User measures wall thickness at 4 points |
| `dims_test.py` | 20 × 20 × 20 mm cube plus a fit gauge | Holes Ø 3/5/8/10 mm nominal and matching pegs |
| `la_pattern.py --k-start 0 --k-end 0.1 --k-step 0.01` | Linear Advance test lines | Uses the start and end G-code from the user's printer profile verbatim; inserts only `M900 K` changes and extrusion moves |
| `analyze.py <job> --test <name>` | Calibration results | Reads the user's measurements from `inspection.md` and computes: flow ratio, xy_comp_mm, hole_comp_mm, xy_shrink_pct, best temperature, best K. Writes `calibration_result.json` |

## 9. `tests/`

- A tiny known-good STL in `tests/fixtures/`.
- An integration test that slices it when PrusaSlicer is installed.
- Tests proving that `slice.py` refuses custom G-code overrides.
