---
name: freecad-reference
description: How to use FreeCAD .FCStd files (single parts or Assembly-workbench assemblies) as the reference for MK3 print jobs. Covers importing without FreeCAD, reading parts, joints and bed-fit, reusing reference STEP geometry in model.py, joint clearances, splitting parts too big for the bed, scaling, and print orientation for mechanisms. Use whenever a job has a .FCStd input or docs/reference/ is relevant.
---

# FreeCAD files as the reference for printed parts

The user designs, or collects, reference models in FreeCAD. A `.FCStd` file is a zip holding `Document.xml` plus one BREP file per shape. `tools/import_fcstd.py` reads it with the same OpenCascade kernel build123d uses, so **FreeCAD does not need to be installed**.

## 1. Import first, then read the summary

```
python3 tools/import_fcstd.py jobs/<id>/inputs/<file>.FCStd --out jobs/<id>/inputs/<name>
```

It writes:

| File | Contents |
|---|---|
| `reference.md` | Read this first. Parts table, joints table, which parts don't fit the bed, the largest uniform scale at which everything fits |
| `reference.json` | The same, machine-readable |
| `parts/<Label>.step` / `.stl` | Each part in its own design coordinates. Use these for geometry |
| `assembled/<Label>.step` | Each part where the assembly places it. Use these to check interfaces and clearances between parts |
| `assembly.png` | Overview render. Look at it |

**Worked example, always available:** `docs/reference/excavator/`, imported from FreeCAD's excavator-arm Assembly example. It has 13 parts and 16 joints (revolute, slider, cylindrical). The Boom (364 × 319 mm) and Stick (388 mm) don't fit the MK3 bed at full size, and every part fits at 61 % scale. The Stick is a fork at one end: laid flat at 60 % it fits (233 × 66 × 18 mm), but one fork plate then bridges about 35 mm over the gap (`mesh_check` reports it), so a DFM review should push to split it or re-model it.

## 2. What the reference is for

The reference defines **function and interfaces**: pin and bore positions, joint axes, mating faces, overall envelope. It does **not** define how to print. FreeCAD parts are usually modelled for looks or for a different process. The pipeline's rules still apply in full: the `fdm-design-rules` skill, the spec, the DFM review and the strength check.

## 3. Using reference geometry in `model.py`

`model.py` may read STEP or STL **only** from `jobs/<id>/inputs/` or `docs/reference/`, using build123d's importers. It is run with the job folder as the working directory.

```python
from build123d import *
from cadlib import *

REF = "inputs/excavator/parts/Stick.step"   # source: reference.md, part "Stick"
SCALE = 0.60                                # source: spec §2 (user approved); max-fit was 0.617

def build():
    stick = import_step(REF)
    stick = scale(stick, by=SCALE)
    stick = Rot(0, 90, 0) * stick           # lay it flat: thickness (X) becomes Z, profile in XY
    stick = Rot(0, 0, 90) * stick           # long side along X, the bed's longest usable axis (240 mm)
    return to_bed(stick)
```

**Two ways to use it. Say which in `design_brief.md`:**

1. **Reuse.** Import the reference solid, then modify it: re-orient, scale, add clearance, split, add chamfers. This is fastest and keeps the geometry exact. Check every printed feature against the design rules: walls, overhangs, hole compensation.
2. **Re-model.** Write the part in build123d from dimensions you measure on the reference (bores, centre distances, thicknesses), designed for FDM from the start. Prefer this when the reference is thin-walled, has big overhangs, or needs ribs or teardrops added.

**Measure, don't guess.** `measure_holes(import_step(...))` gives the bores. `bbox(...)` gives the envelope. With the build123d MCP server, `import_cad_file` plus `find_holes` / `inspect_part` do the same interactively.

## 4. Joints → printed clearances

The joints table lists, per joint, the two parts and the diameter of the circle each side references.

| Joint type | What it means for printing |
|---|---|
| Revolute (pin turns in a bore) / Cylindrical (turns and slides) | Bore = pin Ø + **sliding-fit clearance**: the measured value in `library/materials.csv`, otherwise 0.3–0.4 mm on diameter. Apply hole compensation on the bore as well |
| Slider (rod in a tube) | Same clearance along the whole length. Print the tube with its axis vertical (Z) so the bore is round |
| Fixed | Press fit (0–0.1 mm), or a glued or bolted joint |

**Line-to-line pairs.** Reference models are often modelled with zero clearance (`print_note: zero clearance`). A printed pair made that way will not move. Always add clearance.

**Steel pins.** If the spec allows metal hardware, replace printed pins under ~Ø5 mm, or any heavily loaded pin, with steel dowels or bolts of the nearest standard size. The bore becomes that size + clearance.

## 5. Parts too big for the bed (250 × 210 × 210, 5 mm margin)

`reference.md` flags them and gives the maximum scale. The options, which are **the user's decision** (put them in the spec):

1. **Scale the whole assembly.** Pick a uniform scale at or below `max_uniform_scale_all_parts_fit` (it's already rounded down). Then re-check the smallest pins, walls and teeth: anything under ~0.8 mm, or pins under Ø3 mm, needs re-modelling.
2. **Split the large parts.** Choose the cut where bending stress is low, away from joints and bores. Join with an overlapping lap plus two or more bolts, or with dowel pins and glue. Each piece is its own build (one job, or one job with both pieces side by side if they fit together). Record the joint design in the brief.
3. **Print another way.** Rotate it to fit diagonally. This only gains about 15 %, and `reference.md` already tries all six axis-aligned orientations.

## 6. Orientation for mechanism parts

- **Links, arms and booms.** Lay them flat so the profile sits in XY. Bending then runs along the layers, and the pivot bores are vertical, which gives round holes.
- **Pins.** Print them lying down (axis along X or Y): standing pins snap at the layer lines. Put a small flat on the bed side, about 0.3 × pin Ø, so the pin doesn't roll and needs no support. Or use steel pins.
- **Hydraulic-cylinder tubes and rods.** Print with the axis vertical for round bores and rods. Add a brim if they are tall and thin.

## 7. Assemblies: one job per printed part

For a multi-part build, the Architect writes `jobs/<assembly-id>/assembly_plan.md` (see the `/new-assembly` command). Each part gets its own job whose `spec.md` names:
- the reference part file (`inputs/<name>/parts/<Label>.step`)
- the scale
- its joints with the mating parts and the clearances to use

Start with a small **fit-test coupon**: one pin and its bore at the chosen clearance. Only then print the big parts.
