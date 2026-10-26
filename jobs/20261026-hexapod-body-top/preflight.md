# Preflight: Hexapod top plate / electronics deck (×1)

Job: 20261026-hexapod-body-top · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Switch:** the deck's Ø12 hole fits a 12 mm-bushing toggle rated 10 A DC or more. If your switch is a different size, don't print yet; tell Claude (spec §9).
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **40 g** on the spool (36.2 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even glue-stick layer over the deck's 130 × 104 mm area as a release layer. PETG bonds hard to bare smooth PEI (DFM round 4). Let the bed cool before you take the deck off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the deck flat and centred, with its windows, slots and lead notches in the outline.
- [ ] **SD card file:** `1026_hexapod_body_top.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_hexapod_body_top.gcode`. The first layer takes about 25 min: watch at least its outline and the first few minutes of fill.
- [ ] **Time:** about **2.7 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:** strength is NEEDS_TEST: run the proof test in spec §8 (with the bottom plate's columns fitted) and record it in inspection.md.
