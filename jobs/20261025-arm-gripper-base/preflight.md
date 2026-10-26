# Preflight: Gripper base with fixed jaw

Job: 20261025-arm-gripper-base · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **23 g** on the spool (20.9 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Flat, horn pocket on the bed (SG90 pocket bridges 7.9 mm); fixed jaw block grows up from the plate. Jaw-block bending puts its root across layers.
- [ ] **SD card file:** `1025_arm_gripper_base.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_gripper_base.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **1.9 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> Squeeze 16 N between the jaws at their root end (x 55–60) and 5 N at the tips, 1 min each; then, with the wrist horn clamped in a vice, push 7.5 N sideways at the fixed-jaw tip for 1 min each way. Pass: no cracks at the jaw root, the pocket or the SG90 pilots, no lift off the horn, no permanent set.
