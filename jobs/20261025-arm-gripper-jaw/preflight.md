# Preflight: Moving jaw

Job: 20261025-arm-gripper-jaw · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **7 g** on the spool (6.2 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Flat, pocket side on the bed (bridge 7.9 mm). Bending along the layers.
- [ ] **SD card file:** `1025_arm_gripper_jaw.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_gripper_jaw.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **0.6 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> Covered by the gripper-base squeeze test, plus: with the gripper horn held, push 7.5 N sideways at the jaw tip for 1 min each way. Pass: no crack over the pocket, no lift off the horn, no permanent set; the jaw then opens 0–60° without rubbing.
