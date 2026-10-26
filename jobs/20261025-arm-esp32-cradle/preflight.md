# Preflight: ESP32 cradle

Job: 20261025-arm-esp32-cradle · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **12 g** on the spool (10.8 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Upright, frame bottom (Z −20) on the bed; all ledges rise from the bed; counterbore ceilings bridge 6.7 mm.
- [ ] **SD card file:** `1025_arm_esp32_cradle.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_esp32_cradle.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **1.0 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> Board seated and the cradle screwed in, pull 15 N (≈1.5 kg on a luggage scale) straight down on the board's USB end for 1 min, then plug and unplug the USB cable 5 times. Pass: no crack at the USB-end ledge, the −Y wall or the screw pads; the board still sits on both ledges.
