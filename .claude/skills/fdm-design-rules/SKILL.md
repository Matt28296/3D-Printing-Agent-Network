---
name: fdm-design-rules
description: "FDM design rules for engineering parts on the MK3 (0.4 mm nozzle): orientation versus load paths, walls, overhangs, holes and fits, fasteners, strength strategies, dimensional accuracy, and the model.py contract. Use when deciding orientation, designing, modelling or reviewing a part."
---

# FDM design rules for engineering parts (MK3S, 0.4 mm nozzle)

These are starting points. Measured values in `library/` override every number here. When you use a default from this file instead of a measured value, say so in your output.

## 1. Decide orientation before detail

- Model the part **in print orientation**: Z up is the build direction, the first layer sits at Z = 0.
- The bond between layers is the weak direction. Until `library/materials.csv` has a measured value for the material, assume strength across layers (Z) is **half or less** of strength along layers (XY).
- Trace every load path. If a load pulls layers apart (peel or tension across layers) or bends the part so the tension face runs across layers, re-orient the part or redesign it.
  - Hooks, brackets and clips: print on their side so the curve lies in the XY plane.
  - Snap-fit cantilevers: the beam runs along XY, never along Z.
  - Screw bosses taking pull-out load: avoid an insert axis along Z with the load pulling up through the layers, or give the boss a wide flanged base.
- Orientation also decides overhangs, support needs, bed contact and which faces get the best finish. Record the trade-off you made in `design_brief.md`.
- If one orientation can't serve every load, split the part and join the pieces mechanically (bolts, dowels, dovetails).

## 2. Walls, features, overhangs

- Extrusion width is about 0.45 mm. Make walls multiples of it: 0.9, 1.35, 1.8, 2.25 mm and so on.
- Structural walls: at least 4 perimeters, which is 1.8 mm or more. Avoid walls under 0.9 mm.
- Smallest reliable feature: about 0.8 mm. Smallest reliable vertical hole: about Ø 2 mm.
- Overhangs: 45° or less without support. Bridges: 10 mm or less is reliable.
- Horizontal holes: use a teardrop or flat-top profile so they print without support.
- Bottom edges: use a 45° chamfer of 0.3 to 0.5 mm, never a fillet. A fillet on the bed edge is an overhang, and the chamfer also hides elephant's foot.
- Internal corners on load paths: fillet them with r ≥ 1 to 2 mm. Sharp internal corners concentrate stress.
- Avoid abrupt thickness changes. They warp and concentrate stress. Taper or rib instead.

## 3. Holes, fits and tolerances

- Vertical holes print undersized. Default compensation is +0.2 mm on diameter; replace it with the measured `hole_comp_mm` from `library/materials.csv`.
- PrusaSlicer has no hole-only XY compensation, so hole compensation is applied **in CAD** through a named parameter (`HOLE_COMP`) in `model.py`.
- Diametral clearance defaults (replace with values measured on the fit gauge):
  - Press fit: 0.0 to 0.1 mm
  - Snug or locating fit: 0.15 to 0.2 mm
  - Sliding fit: 0.3 to 0.4 mm
  - Free running: 0.5 mm or more
- Every critical dimension in the spec gets a named parameter in `model.py`, and appears in `design_brief.md` with its tolerance.

## 4. Fasteners

- Heat-set inserts: use the insert maker's recommended hole size; a typical brass M3 insert wants a hole of about Ø 4.0 to 4.2 mm. Boss outer diameter at least 2 × the insert diameter.
- Captive hex nuts: pocket across-flats nominal + 0.2 to 0.3 mm. Add a sacrificial bridge layer if the pocket is printed upside down.
- Screws threading directly into plastic: only for parts assembled a few times. Otherwise use inserts or nuts.
- Plastic creeps under clamping load. Use washers or wide heads, and do not count on bolt preload lasting in PLA or PETG.

## 5. Strength strategies

- Perimeters carry most bending and torsion. Adding walls beats adding infill.
- Put material where stress is: ribs, gussets and local thickening. Remove it where stress is low.
- Size for the worst load case, including assembly and handling loads, not only service loads.
- Sustained load plus heat is the usual failure mode: PLA softens around 55 °C, PETG around 70 °C. See the `material-selection` skill.
- For any part whose failure would hurt someone or damage something expensive, require a physical proof test (in `spec.md` acceptance criteria) before relying on it.

## 6. Dimensional accuracy

- Elephant's foot: bottom-edge chamfer plus slicer compensation (`elefant_foot_compensation`).
- ASA, PC and PA shrink more than PLA or PETG. Apply the per-material XY scale from `library/` if one has been measured.
- Never fudge a dimension in CAD by guesswork. Use a named compensation parameter, and record its source.

## 7. `model.py` conventions (contract with `tools/cad_build.py`)

- Defines `build()` that returns a build123d `Part` (or `Compound`), modelled in print orientation, with the lowest point at Z = 0.
- All key dimensions are UPPER_CASE parameters at the top of the file, with units and the spec line they come from in a comment.
- Compensations (`HOLE_COMP`, `XY_SCALE`) are parameters with a comment naming the library row or "default".
- No file I/O except reading reference STEP/STL from `inputs/` or `docs/reference/`. No network access or subprocess calls. `tools/cad_build.py` does the exporting.
