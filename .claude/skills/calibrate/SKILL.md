---
name: calibrate
description: Plan or continue a calibration campaign (temperature, flow, Linear Advance, dimensions and fits) for one material on the MK3.
argument-hint: <material> [brand] [next|plan]
disable-model-invocation: true
---

You are the Architect. The user wants to calibrate: $ARGUMENTS

1. Read `config/printer.json`. Confirm the material is on hand and that a filament profile for it exists in `profiles/filament/`. If not, tell the user exactly what to export from PrusaSlicer, and stop.
2. Look for `library/campaigns/<material>-<brand>.md`.
   - **No campaign yet**: send the `head-orchestrator` agent `Calibration: plan a campaign for <material> <brand>, then generate the first test.`
   - **Campaign exists**: send it `Calibration: generate the next test in library/campaigns/<file>.`
3. Pass on the result: which test is next, what it measures, and the approval command for its G-code.
