# Preflight: Robot arm base

Job: 20261025-arm-base · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **107 g** on the spool (97.6 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Upside down: top plate on the bed. All wall openings have 45° roofs pointing at the desk side (up in print). Top plate in-plane loads run along the layers.
- [ ] **SD card file:** `1025_arm_base.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_base.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **8.1 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> With the base screwed to a board (desk screws fitted), the base servo, horn, turntable and ring assembled and the servo unpowered, press 50 N (≈5 kg on a bathroom or luggage scale) straight down on the turntable rim, 1 min at each of 4 positions 90° apart. Pass: no cracking or whitening at the 4 servo pilots and bosses, the 3 ring pilots or the top plate around the ring; after unloading, the rim returns to within 0.3 mm of its height. Also plug and unplug the USB cable 5 times with the cradle fitted: no cracks at the cradle bosses.
