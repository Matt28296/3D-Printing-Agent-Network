# Preflight: Coxa bracket (×6: 2 per plate × 3 plates)

Job: 20261026-hexapod-coxa · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer, for every plate.

- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **65 g** on the spool for one plate (59.1 g + 10 %), or about **195 g** for all three.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak, and these brackets print solid.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even glue-stick layer as a release layer. PETG bonds hard to bare smooth PEI (DFM round 4). Let the bed cool before you take the brackets off, and rinse any glue out of the horn pockets with water.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** two brackets side by side, each flat on its hub plate with the horn pocket against the bed.
- [ ] **SD card file:** `1026_hexapod_coxa.gcode` (written by `tools/export_sd.py` after you approve). The same file prints all three plates.
- [ ] **On the printer:** Print from SD → `1026_hexapod_coxa.gcode`. Watch the whole first layer (about 6 min).
- [ ] **Time:** about **4.4 h** per plate (13.1 h for all three). Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Screw-strip check (spec §8, BUILD_GUIDE §1):** print the first coxa plate and the first femur plate first. Before printing the other two coxa plates, fit a femur servo in one bracket, drive both M2 × 10 snug and look at the strips beside both pilots. If a strip whitens or cracks, stop and tell Claude.
- [ ] **Between plates:** take the brackets off a cool sheet, clean it, re-apply glue, and go through this list again.

**After printing:**
- If the femur servo's case is tight in the window, lightly deburr the window's edges on the gusset face. The seam line runs up those edges (audit note 1).
- Strength is NEEDS_TEST: run the proof test in spec §8 and record it in inspection.md.
