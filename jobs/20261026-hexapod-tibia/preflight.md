# Preflight: Tibia (×6: 3 per plate × 2 plates)

Job: 20261026-hexapod-tibia · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer, for every plate.

- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **23 g** on the spool for one plate (20.7 g + 10 %), or about **46 g** for both.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even glue-stick layer as a release layer. PETG bonds hard to bare smooth PEI (DFM round 4). Let the bed cool before you take the tibias off, and rinse any glue off the bed face with water: it is the back face that runs 3.1 mm from the femur.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** three tibias side by side, flat, with the horn pocket against the bed.
- [ ] **SD card file:** `1026_hexapod_tibia.gcode` (written by `tools/export_sd.py` after you approve). The same file prints both plates.
- [ ] **On the printer:** Print from SD → `1026_hexapod_tibia.gcode`. Watch the whole first layer (about 6 min).
- [ ] **Time:** about **1.9 h** per plate (3.9 h for both). Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Between plates:** take the tibias off a cool sheet, clean it, re-apply glue, and go through this list again.

**After printing:** strength is NEEDS_TEST: run the proof test in spec §8 and record it in inspection.md.
