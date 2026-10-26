# Preflight: Road wheel (×4: 2 per plate × 2 plates)

Job: 20261026-rover-wheel · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer, for every plate.

- [ ] **Plates:** **2 plates** of 2 wheels = the 4 in spec §7. Both plates print the same file. Four on one plate would take longer than the 3 h limit.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **28 g** on the spool for one plate (25.5 g + 10 %), or about **56 g** for both.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the wheels off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** two Ø32 flange faces side by side, each with its bore open in the middle. It takes about 4 min.
- [ ] **SD card file:** `1026_rover_wheel.gcode` (written by `tools/export_sd.py` after you approve). The same file prints both plates.
- [ ] **On the printer:** Print from SD → `1026_rover_wheel.gcode`. Watch the whole first layer.
- [ ] **Time:** about **2.3 h** per plate (4.6 h for both). Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Between plates:** take the wheels off a cool sheet, clean it, re-apply glue, and go through this list again.

**After printing:**
- **Seam line.** Each wheel has one straight seam line down the rim and flanges, and one in the bore, on the side that faced the back of the printer. Feel along both and scrape off any bump: the rim rolls on the links and the bore runs on the bolt.
- **Strength is NEEDS_TEST.** The proof is the chassis tests (spec §8: 5 kg on the rim, then the 5 cm drop). Record them in inspection.md.
