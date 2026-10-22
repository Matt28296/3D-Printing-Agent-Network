#!/usr/bin/env python3
"""Read a FreeCAD .FCStd file without FreeCAD: parts, placements, joints, fit checks.

    python3 tools/import_fcstd.py <file.FCStd> --out jobs/<id>/inputs/<name>

An .FCStd is a zip holding Document.xml plus one BREP file per shape. This
tool reads those directly with the OpenCascade kernel that build123d uses,
so FreeCAD does not need to be installed.

Writes to --out:
  reference.json             every part and joint (machine-readable)
  reference.md               the same, for people and agents
  parts/<Label>.step/.stl    each part in its own coordinates (as designed)
  assembled/<Label>.step     each part where the assembly places it
  assembly.png               overview render of the assembled parts

For each part it reports size, volume, an estimated print mass, the round
features (pin and hole diameters), and whether it fits the MK3 bed in any of
its 6 axis-aligned orientations. For each joint (FreeCAD 1.x Assembly) it
reports the joint type, the two parts, and the diameters of the referenced
circular edges/faces: the pin–hole pair a printed version must keep with
the right clearance.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BED = (250.0, 210.0, 210.0)
MARGIN = 5.0
DENSITY_PETG = 1.27  # g/cm³, for the mass estimate
JOINT_TYPES = {0: "Fixed", 1: "Revolute", 2: "Cylindrical", 3: "Slider", 4: "Ball",
               5: "Distance", 6: "Parallel", 7: "Perpendicular", 8: "Angle", 9: "RackPinion",
               10: "Screw", 11: "Gears", 12: "Belt"}


# --------------------------------------------------------------------------- XML
def _props(obj_el) -> dict:
    out = {}
    props = obj_el.find("Properties")
    if props is None:
        return out
    for p in props.findall("Property"):
        kids = list(p)
        if kids:
            out[p.get("name")] = kids[0]
    return out


def _placement(el) -> tuple[tuple[float, float, float], tuple[float, float, float, float]] | None:
    if el is None or el.tag != "PropertyPlacement":
        return None
    pos = tuple(float(el.get(k, 0)) for k in ("Px", "Py", "Pz"))
    q = tuple(float(el.get(k, 0)) for k in ("Q0", "Q1", "Q2", "Q3"))  # x, y, z, w
    if not any(q):
        q = (0.0, 0.0, 0.0, 1.0)
    return pos, q


def parse_document(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    types = {o.get("name"): o.get("type") for o in root.find("Objects").findall("Object")}
    objs = {}
    for od in root.find("ObjectData").findall("Object"):
        name = od.get("name")
        pr = _props(od)
        rec = {"name": name, "type": types.get(name, "")}
        if "Label" in pr:
            rec["label"] = pr["Label"].get("value")
        if "Visibility" in pr:
            rec["visible"] = pr["Visibility"].get("value") == "true"
        if "Shape" in pr and pr["Shape"].get("file"):
            rec["shape_file"] = pr["Shape"].get("file")
        if "Placement" in pr:
            rec["placement"] = _placement(pr["Placement"])
        if "LinkedObject" in pr:
            rec["linked"] = pr["LinkedObject"].get("name")
        if "Group" in pr and pr["Group"].tag == "LinkList":
            rec["group"] = [l.get("value") for l in pr["Group"].findall("Link")]
        if "JointType" in pr:
            rec["joint_type"] = int(pr["JointType"].get("value"))
            for r in ("Reference1", "Reference2"):
                if r in pr:
                    rec[r] = [s.get("value") for s in pr[r].findall("Sub")]
            for k in ("Activated",):
                if k in pr:
                    rec[k.lower()] = pr[k].get("value") == "true"
        if "ObjectToGround" in pr:
            rec["grounds"] = pr["ObjectToGround"].get("value")
        objs[name] = rec
    return objs


# --------------------------------------------------------------------------- geometry
def _load_shape(data: bytes, filename: str):
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    shape = TopoDS_Shape()
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / Path(filename).name
        p.write_bytes(data)
        if filename.lower().endswith(".bin"):
            from OCP.BinTools import BinTools
            BinTools.Read_s(shape, str(p))
        else:
            BRepTools.Read_s(shape, str(p), BRep_Builder())
    return shape


def _indexed(shape, kind: str) -> list:
    """FreeCAD's EdgeN / FaceN numbering = TopExp::MapShapes order (1-based)."""
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp
    try:
        from OCP.TopTools import TopTools_IndexedMapOfShape as IndexedMap
    except ImportError:  # OCP >= 7.8 moved the template instances
        from OCP.OCP.collections import IndexedMap_TopoDS_Shape_TopTools_ShapeMapHasher as IndexedMap

    m = IndexedMap()
    TopExp.MapShapes_s(shape, TopAbs_EDGE if kind == "Edge" else TopAbs_FACE, m)
    return [m.FindKey(i) for i in range(1, m.Extent() + 1)]


def _element_diameter(shape, element: str) -> float | None:
    """Diameter of a circular edge or cylindrical face named like 'Edge12' / 'Face3'."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Circle, GeomAbs_Cylinder
    from OCP.TopoDS import TopoDS
    to_edge = getattr(TopoDS, "Edge_s", None) or TopoDS.Edge  # name differs across OCP versions
    to_face = getattr(TopoDS, "Face_s", None) or TopoDS.Face

    m = re.fullmatch(r"(Edge|Face)(\d+)", element)
    if not m:
        return None
    kind, idx = m.group(1), int(m.group(2))
    items = _indexed(shape, kind)
    if not 1 <= idx <= len(items):
        return None
    if kind == "Edge":
        c = BRepAdaptor_Curve(to_edge(items[idx - 1]))
        return round(2 * c.Circle().Radius(), 3) if c.GetType() == GeomAbs_Circle else None
    s = BRepAdaptor_Surface(to_face(items[idx - 1]))
    return round(2 * s.Cylinder().Radius(), 3) if s.GetType() == GeomAbs_Cylinder else None


def _round_features(part) -> list[float]:
    from build123d import GeomType
    out = set()
    for f in part.faces().filter_by(GeomType.CYLINDER):
        try:
            if f.radius:
                out.add(round(2 * f.radius, 2))
        except Exception:
            pass
    return sorted(out)


def _best_orientation(size: tuple[float, float, float]) -> dict:
    lim = (BED[0] - 2 * MARGIN, BED[1] - 2 * MARGIN, BED[2])
    perms = set(itertools.permutations(size))
    max_scale = math.floor(max(min(l / max(v, 1e-9) for l, v in zip(lim, p)) for p in perms) * 1000) / 1000
    fits = [p for p in perms if p[0] <= lim[0] and p[1] <= lim[1] and p[2] <= lim[2]]
    if fits:
        best = min(fits, key=lambda p: p[2])  # lowest = fastest, most stable
        return {"fits_bed": True, "flat_on_bed_mm": [round(v, 1) for v in best], "max_scale_to_fit": round(max_scale, 3)}
    longest = max(size)
    pieces = math.ceil(longest / (lim[0] - 5))
    return {"fits_bed": False, "flat_on_bed_mm": None, "max_scale_to_fit": round(max_scale, 3),
            "split_hint": f"longest side {longest:.0f} mm > {lim[0]:.0f} mm usable: split into at least {pieces} pieces "
                          f"joined mechanically (bolts, dowels or a lap joint), or scale the assembly"}


def _apply(part, placement):
    from build123d import Location, Pos, Rotation
    from OCP.gp import gp_Quaternion, gp_Trsf, gp_Vec
    from OCP.TopLoc import TopLoc_Location
    if not placement:
        return part
    (px, py, pz), (qx, qy, qz, qw) = placement
    t = gp_Trsf()
    t.SetRotation(gp_Quaternion(qx, qy, qz, qw))
    t.SetTranslationPart(gp_Vec(px, py, pz))
    return part.moved(Location(TopLoc_Location(t)))


# --------------------------------------------------------------------------- main work
def analyse(fcstd: Path, out: Path | None = None, render: bool = True) -> dict:
    from build123d import Part, Shape, export_step, export_stl

    with zipfile.ZipFile(fcstd) as z:
        objs = parse_document(z.read("Document.xml"))
        blobs = {n: z.read(n) for n in z.namelist()}

    # parts: the shapes that links point at (assembly) or, without an assembly, visible solid features
    links = [o for o in objs.values() if o.get("type") == "App::Link" and o.get("linked") in objs]
    if links:
        instances = [(l["name"], l.get("label", l["name"]), objs[l["linked"]], l.get("placement")) for l in links]
    else:
        instances = [(o["name"], o.get("label", o["name"]), o, o.get("placement")) for o in objs.values()
                     if o.get("shape_file") and o.get("visible", True)]

    shapes, parts = {}, []
    for inst_name, label, src, placement in instances:
        sf = src.get("shape_file")
        if not sf or sf not in blobs:
            continue
        if sf not in shapes:
            shapes[sf] = _load_shape(blobs[sf], sf)
        raw = Part(Shape.cast(shapes[sf]).solids())
        if not raw.solids():
            continue
        bb = raw.bounding_box()
        size = (bb.size.X, bb.size.Y, bb.size.Z)
        vol = raw.volume / 1000.0
        rec = {
            "instance": inst_name, "label": src.get("label", label), "source_object": src["name"],
            "solids": len(raw.solids()), "bbox_mm": [round(v, 1) for v in size],
            "volume_cm3": round(vol, 1), "est_mass_petg_solid_g": round(vol * DENSITY_PETG, 0),
            "round_feature_diameters_mm": _round_features(raw),
        }
        rec.update(_best_orientation(size))
        parts.append(rec)
        if out:
            safe = re.sub(r"[^A-Za-z0-9_-]+", "_", rec["label"])
            (out / "parts").mkdir(parents=True, exist_ok=True)
            (out / "assembled").mkdir(parents=True, exist_ok=True)
            export_step(raw, str(out / "parts" / f"{safe}.step"))
            export_stl(raw, str(out / "parts" / f"{safe}.stl"), tolerance=0.02, angular_tolerance=0.15)
            export_step(_apply(raw, placement), str(out / "assembled" / f"{safe}.step"))
            rec["files"] = {"part_step": f"parts/{safe}.step", "part_stl": f"parts/{safe}.stl",
                            "assembled_step": f"assembled/{safe}.step"}

    inst_to_shape = {name: shapes.get(src.get("shape_file")) for name, _, src, _ in instances}
    inst_to_label = {p["instance"]: p["label"] for p in parts}
    joints = []
    for o in objs.values():
        if "joint_type" not in o:
            continue
        sides = []
        for r in ("Reference1", "Reference2"):
            subs = o.get(r) or []
            inst = subs[0].split(".", 1)[0] if subs else None
            elems = sorted({s.split(".", 1)[1] for s in subs if "." in s})
            diam = None
            shp = inst_to_shape.get(inst)
            if shp is not None:
                for e in elems:
                    try:
                        diam = _element_diameter(shp, e)
                    except Exception:
                        diam = None
                    if diam:
                        break
            sides.append({"part": inst_to_label.get(inst, inst), "elements": elems, "diameter_mm": diam})
        jt = JOINT_TYPES.get(o["joint_type"], f"type{o['joint_type']}")
        j = {"name": o.get("label", o["name"]), "type": jt, "active": o.get("activated", True), "between": sides}
        d1, d2 = sides[0]["diameter_mm"], sides[1]["diameter_mm"] if len(sides) > 1 else None
        moving = jt in ("Revolute", "Cylindrical", "Slider")
        if d1 and d2 and moving and abs(d1 - d2) < 0.15:
            j["print_note"] = (f"both sides reference Ø{min(d1, d2):g}: modelled line-to-line (zero clearance). "
                               "A printed pin/bore pair needs the measured sliding-fit clearance "
                               "(≈0.3–0.4 mm on diameter by default)")
        elif d1 and d2 and moving:
            j["print_note"] = (f"referenced circles differ (Ø{d1:g} vs Ø{d2:g}); one is probably a boss outline "
                               "that only defines the axis. Measure the actual pin and bore in parts/ before "
                               "setting clearances")
        joints.append(j)
    grounded = [inst_to_label.get(o.get("grounds"), o.get("grounds")) for o in objs.values() if o.get("grounds")]

    result = {
        "source": fcstd.name,
        "printer_bed_mm": list(BED),
        "parts": parts,
        "joints": joints,
        "grounded": grounded,
        "summary": {
            "parts": len(parts),
            "parts_too_big_for_bed": [p["label"] for p in parts if not p["fits_bed"]],
            "joints": len(joints),
            "total_volume_cm3": round(sum(p["volume_cm3"] for p in parts), 1),
            "total_est_mass_petg_solid_g": round(sum(p["est_mass_petg_solid_g"] for p in parts), 0),
            "max_uniform_scale_all_parts_fit": round(min((p["max_scale_to_fit"] for p in parts), default=1.0), 3),
        },
    }
    if out:
        (out / "reference.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (out / "reference.md").write_text(to_markdown(result), encoding="utf-8")
        if render:
            try:
                render_assembly(out, parts)
            except Exception as exc:  # rendering is a convenience, never a failure
                print(f"(overview render skipped: {exc})", file=sys.stderr)
    return result


def to_markdown(r: dict) -> str:
    s = r["summary"]
    lines = [f"# Reference: {r['source']}", "",
             f"{s['parts']} parts, {s['joints']} joints, {s['total_volume_cm3']} cm³ of material "
             f"(≈ {s['total_est_mass_petg_solid_g']:.0f} g if printed solid in PETG; infill makes it less).",
             f"Grounded part: {', '.join(r['grounded']) or 'none'}.",
             f"Too big for the MK3 bed at full size: {', '.join(s['parts_too_big_for_bed']) or 'none'}. "
             f"Largest uniform scale at which every part fits: {math.floor(s['max_uniform_scale_all_parts_fit'] * 100)}% "
             "(check pins and walls stay printable at that scale).", "",
             "## Parts", "",
             "| Part | Size as designed (mm) | Volume cm³ | Fits MK3 bed? | Best flat orientation (mm) | Round features Ø (mm) |",
             "|---|---|---|---|---|---|"]
    for p in r["parts"]:
        fit = "yes" if p["fits_bed"] else "**NO**"
        orient = " × ".join(f"{v:g}" for v in p["flat_on_bed_mm"]) if p["flat_on_bed_mm"] else p.get("split_hint", "")
        lines.append(f"| {p['label']} | {' × '.join(f'{v:g}' for v in p['bbox_mm'])} | {p['volume_cm3']} | {fit} | "
                     f"{orient} | {', '.join(f'{d:g}' for d in p['round_feature_diameters_mm'][:8])} |")
    lines += ["", "## Joints (the interfaces a printed version must keep)", "",
              "| Joint | Type | Part A (Ø mm) | Part B (Ø mm) | Note |", "|---|---|---|---|---|"]
    for j in r["joints"]:
        a, b = (j["between"] + [{}, {}])[:2]
        fa = f"{a.get('part')} ({a.get('diameter_mm') or '–'})"
        fb = f"{b.get('part')} ({b.get('diameter_mm') or '–'})"
        lines.append(f"| {j['name']} | {j['type']} | {fa} | {fb} | {j.get('print_note', '')} |")
    lines += ["", "Diameters are the circular edge or face each joint references in FreeCAD. They define the joint "
              "axis and are usually, but not always, the pin or bore itself. A dash means a non-circular element.", ""]
    return "\n".join(lines)


def render_assembly(out: Path, parts: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import trimesh
    from build123d import export_stl, import_step

    sys.path.insert(0, str(ROOT / "tools"))
    from render import render_view  # the project's z-buffer renderer

    meshes = []
    with tempfile.TemporaryDirectory() as td:
        for p in parts:
            f = out / p["files"]["assembled_step"]
            stl = Path(td) / (f.stem + ".stl")
            export_stl(import_step(str(f)), str(stl), tolerance=0.1, angular_tolerance=0.3)
            meshes.append(trimesh.load(stl, force="mesh"))
    scene = trimesh.util.concatenate(meshes)
    img, _ = render_view(scene, 25, -60, with_bed=False)
    fig = plt.figure(figsize=(8, 8.4), dpi=100)
    ax = fig.add_axes([0, 0, 1, 0.95])
    ax.imshow(img)
    ax.set_axis_off()
    size = scene.bounds[1] - scene.bounds[0]
    fig.suptitle(f"assembly overview · {len(parts)} parts · {size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f} mm", y=0.985)
    fig.savefig(out / "assembly.png")
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read a FreeCAD .FCStd (parts, joints, MK3 fit) without FreeCAD.")
    ap.add_argument("fcstd")
    ap.add_argument("--out", help="output folder, e.g. jobs/<id>/inputs/<name> (omit to only print the summary)")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args(argv)
    src = Path(args.fcstd)
    if not zipfile.is_zipfile(src):
        print(f"{src} is not a FreeCAD .FCStd file (not a zip archive).", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    r = analyse(src, out, render=not args.no_render)
    s = r["summary"]
    print(f"{s['parts']} parts, {s['joints']} joints, {s['total_volume_cm3']} cm³. "
          f"Too big for the bed: {', '.join(s['parts_too_big_for_bed']) or 'none'}."
          + (f" -> {out}/reference.md" if out else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
