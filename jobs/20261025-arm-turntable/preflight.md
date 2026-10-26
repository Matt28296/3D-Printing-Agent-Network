# Preflight: Turntable with shoulder upright

Job: 20261025-arm-turntable · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **85 g** on the spool (77.0 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Disk on the bed, upright vertical. All upright bending, in-plane and out of plane, puts stress across the layers (Z); the 7 mm upright, the 3 mm root wedges and the 70 mm gussets size for that with the across-layer allowable. Disk bending runs along the layers.
- [ ] **SD card file:** `1025_arm_turntable.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_turntable.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **6.8 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> (1) Assembled arm, shoulder servo powered and holding with the upper link horizontal: hang 1 kg at the elbow axis for 1 min. (2) Arm pointing straight up, servos unpowered: push 10 N (≈1 kg on a luggage scale) sideways (±Y) at the fingertip, 1 min each way, then repeat with the elbow at 90°. Pass: no cracks or whitening at the upright window corners, the tab pilots, the gusset toes or the upright–disk corner; the base horn doesn't lift off; the fingertip returns to within 1 mm.
