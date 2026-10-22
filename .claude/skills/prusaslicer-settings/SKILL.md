---
name: prusaslicer-settings
description: "PrusaSlicer settings for strong, accurate MK3 parts: baseline values for load-bearing parts, temperature and cooling for layer strength, accuracy settings, and keys agents must never override. Use when planning a slice, writing print requirements, or auditing settings."
---

# PrusaSlicer settings for strength and accuracy (MK3S, 0.4 mm nozzle)

Start from the user's exported Prusa profiles in `profiles/` (printer, print and filament `.ini` files). Express every change as an override in `slice_plan.json` so it can be reviewed and reproduced. Key names below are PrusaSlicer config keys; `tools/slice.py` maps them to CLI flags.

## Baseline for load-bearing parts

| Key | Value | Why |
|---|---|---|
| `layer_height` | 0.15–0.20 | Thinner layers don't reliably add strength; temperature and cooling matter more |
| `perimeters` | 4–6 | Walls carry bending and torsion |
| `top_solid_layers` / `bottom_solid_layers` | 6–7 / 5–6 | Solid skins for stiffness |
| `fill_density` | 40–60% general; 100% for small, highly loaded parts | |
| `fill_pattern` | `gyroid` or `cubic` | Even strength in all directions |
| `extrusion_width`, `external_perimeter_extrusion_width` | 0.45 | Matches wall rules in the `fdm-design-rules` skill |
| `seam_position` | `rear` or `aligned` | Keep seams off mating and load surfaces; say where in the plan |
| `elefant_foot_compensation` | 0.2 | Paired with bottom chamfers |
| `brim_width` | 5–8 for ASA, PC, PA | Warping |
| `support_material` | only if the design truly needs it; prefer organic (`support_material_style = organic`) | |

## Temperature and cooling for layer strength

- Print in the **upper half** of the TDS nozzle range for structural parts.
- Part-cooling fan: PETG 30–50% max; ASA, PC and PA 0–15%. Keep `slowdown_below_layer_time` so small layers still cool enough.
- These belong in the filament profile. If you override them, explain why in the plan.

## Accuracy

- `xy_size_compensation`: use the calibrated value from `library/materials.csv`; default 0.
- Hole compensation is done in CAD, not in the slicer (PrusaSlicer has no hole-only compensation).
- Linear Advance K is set by `M900` in the filament profile's start G-code. Agents never edit custom G-code; a new K value comes from calibration and is applied by the user in their profile, or by the toolsmith if the user explicitly asks.

## Hard rules

- Never override `start_gcode`, `end_gcode`, `before_layer_gcode`, `layer_gcode`, `toolchange_gcode`, `between_objects_gcode`, `color_change_gcode`, `pause_print_gcode`, `template_custom_gcode` or `post_process`. `tools/slice.py` refuses these.
- Output plain-text G-code only (`binary_gcode = 0`).
- Every value in `print_requirements.json` must be met; the validator checks it.
- Strength tricks such as staggered or "brick" layers are experimental: only with a test coupon and the user's agreement.
