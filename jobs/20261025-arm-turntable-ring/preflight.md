# Preflight: Turntable support ring

Job: 20261025-arm-turntable-ring · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **15 g** on the spool (14.1 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Flat, tabs on the bed. Compression in the wall runs across layers but in pure compression (layer bonding not loaded in tension).
- [ ] **SD card file:** `1025_arm_turntable_ring.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_turntable_ring.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **1.2 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> Covered by the base proof test (50 N on the turntable rim, 1 min at each of 4 positions 90° apart). Pass: no cracks in the tabs or the ring wall, no crushing of the ring top (the 1.5 mm running gap still clears), and the turntable then turns freely through ±90° with no rubbing.
