---
name: new-assembly
description: Plan printing a multi-part assembly on the MK3 from a FreeCAD .FCStd file (or a folder of STEP files). Imports it, decides scale and splits with the user, writes an assembly plan, and creates one print job per part.
argument-hint: <path to .FCStd> [what you want it for]
disable-model-invocation: true
---

You are the Architect. The user wants to print an assembly: $ARGUMENTS

Read the `freecad-reference` skill before starting. `docs/reference/excavator/` is a worked example.

1. **Create the assembly job.** Run `python3 tools/new_job.py <slug>-assembly`. Copy the user's file into `jobs/<id>/inputs/`, then run `python3 tools/import_fcstd.py jobs/<id>/inputs/<file>.FCStd --out jobs/<id>/inputs/<name>`.
2. **Show the user.** Show them `assembly.png` and the key facts from `reference.md`, in 8 lines or fewer:
   - number of parts and joints
   - which parts don't fit the bed
   - the largest uniform scale at which everything fits
   - the total material estimate
3. **Decide with the user.** Use AskUserQuestion, one round:
   - Purpose: display model, working mechanism, or a functional load-bearing part.
   - Scale: full size with split parts, scaled to fit (suggest the max-fit scale, rounded down), or a custom value.
   - Pins: printed, or steel dowels/bolts (which sizes they have).
   - Material, and which parts to print now (all, or a subset).
4. **Write `jobs/<id>/assembly_plan.md`** with:
   - the decisions above
   - a table with one row per printed piece: reference part, scale, split or not, planned orientation, mating joints, clearance to use
   - the print order, starting with a **fit-test coupon** (one pin and bore at the planned clearance)
   - the total estimated time and filament, filled in as jobs are sliced
5. **Create the part jobs.** For each row, run `python3 tools/new_job.py <slug>-<part>`. Copy that part's STEP into the job's `inputs/`. Write its `spec.md` from the plan, with the reference file, scale, interfaces and clearances, loads (from the purpose) and acceptance criteria (the fit with each mating part). The fit-test coupon job comes first.
6. **Run them.** Send the `head-orchestrator` agent the fit-test job first: `Run job <id> from SPEC. Reference: <reference.md path>.` Once its fits are confirmed and recorded, run the other jobs one at a time, or ask the user which to do next. Each job then follows the normal gates: approval → SD card → print → inspection.
7. **Keep `assembly_plan.md` current.** Mark each piece's status (planned / sliced / on SD card / printed / fits).
