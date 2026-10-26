# Preflight: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **28 g** on the spool (25.1 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Flat, FRONT face on the bed (horn pocket opens upward, no bridge). Bending along the layers.
- [ ] **SD card file:** `1025_arm_forearm.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_forearm.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **2.2 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> (1) Clamp at the elbow horn, 1 kg at the wrist axis for 1 min: no cracks, no set. (2) Same clamping, 15 N sideways (out of plane) at the wrist axis for 1 min each way, then 7.5 N sideways at the end of a 95 mm lever on the wrist tab holes. Pass: no cracks at the pocket or the SG90 pilots, the SG90 tabs don't lift, no lift off the horn, no permanent set. Run (2) with the M2×12 tab screws fitted.
