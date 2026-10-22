---
name: build123d-cad
description: How to write correct, printable build123d models for MK3 jobs. Covers the model.py contract, the tested cadlib helpers (teardrop holes, hole compensation, nut pockets, bottom chamfers, hole measurement), API patterns that work, common failures, and the build/render/check loop. Use whenever writing, fixing or reviewing CAD code.
---

# build123d CAD for MK3 jobs

Verified against build123d 0.13. Check the installed version with `python3 -c "import build123d; print(build123d.__version__)"`. If a call below fails on a newer version, read its docstring with `python3 -c "import build123d; help(build123d.<Name>)"` before guessing.

## Contract (`tools/cad_build.py` enforces it)

- `jobs/<id>/model.py` defines `build()`. It returns one solid, in **print orientation**, with its lowest point at **Z = 0**, and it fits the bed.
- Parameters are UPPER_CASE at the top of the file. Each has units and a source: a spec line, a library row, or "default".
- No file I/O except reading reference STEP/STL from `inputs/` or `docs/reference/` (`import_step`, `import_stl`). No network access or subprocess calls. Exporting is the tool's job.

## Tested helpers: `from cadlib import *`

`tools/cadlib.py` is covered by `tests/test_cad_tools.py`. Subtract cutters with `part -= cutter`.

| Helper | What it gives you |
|---|---|
| `comp(d, HOLE_COMP)` | Diameter to model so the printed hole measures `d` |
| `teardrop_cutter(d, length, axis="X" or "Y", center=(x, y, z))` | Horizontal hole that prints without support (45° point toward +Z) |
| `vertical_hole_cutter(d, depth, top_center=(x, y, z))` | Hole drilled downward from `top_center` |
| `hex_nut_pocket(af, depth, clearance=0.25, bottom_center=(x, y, z))` | Captive-nut pocket rising from `bottom_center` |
| `chamfer_bottom(part, 0.4)` | 45° chamfer on every bed edge (beats elephant's foot) |
| `to_bed(part)` | Lift the part so min Z = 0 (never rotates) |
| `measure_holes(part)` | Concave holes: diameter, axis, point on axis, arc°. Bosses are excluded |
| `bbox(part)` | `{"min": [...], "size": [...]}` |

## Patterns that work

```python
from build123d import *
from cadlib import *

# Profile + extrude: best for parts printed on their side (load paths in XY)
with BuildPart() as bp:
    with BuildSketch():
        with BuildLine():
            Polyline((0, 0), (40, 0), (40, 4), (4, 4), (4, 40), (0, 40), close=True)
        make_face()
    extrude(amount=20)
    corner = (bp.edges().filter_by(Axis.Z)
              .filter_by_position(Axis.X, 3.99, 4.01).filter_by_position(Axis.Y, 3.99, 4.01))
    fillet(corner, radius=3)
part = bp.part

# Primitives: the default align is CENTRED, which puts half the part below the bed
plate = Box(60, 40, 4, align=(Align.MIN, Align.MIN, Align.MIN))
boss = Pos(8, 8, 0) * Cylinder(4, 12, align=(Align.CENTER, Align.CENTER, Align.MIN))
part = plate + boss                                # union; also `-` (cut) and `&` (intersect)
part = Rot(0, 0, 45) * part                        # rotate about Z
edges = part.edges().group_by(Axis.Z)[-1]          # edges on the top face
part = fillet(edges, radius=1)                     # algebra-mode fillet returns a new part
```

**Order that avoids kernel failures:**
1. Main body.
2. Fillets on the body.
3. Cuts (holes, pockets).
4. `chamfer_bottom` last.

If a fillet or chamfer raises an error, use a smaller radius, or apply it before the cut that crosses its edge.

## Common failures and fixes

| Symptom | Cause | Fix |
|---|---|---|
| cad_build: "lowest point is Z=-…" | Default centred `align` | `align=(…, …, Align.MIN)` or `to_bed(part)` |
| `solids` > 1 | A feature doesn't touch the body | Overlap the features by ≥ 0.01 mm, or check the positions |
| Fillet raises `StdFail_NotDone` | Radius ≥ an adjacent face, or the edge was cut | Smaller radius, or fillet before cutting |
| Hole measured smaller in print | No compensation | `comp(d, HOLE_COMP)` for fit holes. Insert holes use the maker's size |
| Hole needs supports | Horizontal round hole | `teardrop_cutter` |

## The loop (every build)

1. Write or modify `model.py`.
2. `python3 tools/cad_build.py jobs/<id>`. Read the error if it fails.
3. `python3 tools/render.py jobs/<id>`, then **look at** `renders/iso.png`, `front.png` and `top.png`.
4. `python3 tools/mesh_check.py jobs/<id>`
5. Copy `docs/cad-cookbook/cad_checks_template.txt` to `jobs/<id>/cad_checks.py`. Add one `check(...)` per critical dimension from the brief. Run it with `python3 jobs/<id>/cad_checks.py`; it must exit 0.

## Examples

- `docs/cad-cookbook/l_bracket.py`: printed on its side, inner fillet, teardrop mounting holes, bottom chamfer.
- `docs/cad-cookbook/insert_mount.py`: plate with heat-set insert bosses, a stiffening rib, a captive nut and corner fillets.

Both are built by the test suite, so they are known to work.

## Interactive geometry tools: the build123d MCP server

When the `mcp__build123d__*` tools are connected (project `.mcp.json`, build123d-mcp 0.3.90), use them to explore and check *before* committing code to `model.py`:

| Tool | Use it for |
|---|---|
| `workflow_hints` | Call first in a session |
| `execute`, `execute_file` | Run snippets, or your `model.py`, in a persistent session |
| `inspect_part`, `measure`, `find_holes`, `find_bosses` | Check dimensions and features |
| `analyze_printability` | FDM printability analysis (extra evidence for DFM) |
| `validate`, `locate_gate_defects`, `repair_hints`, `last_error` | Fix invalid geometry and kernel errors |
| `render_view` | Quick look at a shape |

`export`, `bank_candidate` and `install_skill` are denied in project settings. Files are exported only by `tools/cad_build.py`, so `model.py` stays the single source of truth. Always finish with the loop above.
