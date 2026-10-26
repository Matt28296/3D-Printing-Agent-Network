# Preflight: Hexapod bottom body plate (×1)

Job: 20261026-hexapod-body-bottom · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **104 g** on the spool (94.2 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even glue-stick layer over the whole 166 × 147 mm area as a release layer. This is 19,700 mm² of PETG on the bed, which bonds hard to bare smooth PEI (DFM round 4). Let the sheet cool fully, then flex it to release the plate; never pry it off hot.
- [ ] **Bed clear** of objects and old prints; nozzle clean. The print with its skirt covers X 40–210 and Y 29–181 mm, most of the bed.
- [ ] **First layer:** the whole plate outline with its six coxa windows, centred.
- [ ] **SD card file:** `1026_hexapod_body_bottom.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_hexapod_body_bottom.gcode`. The first layer takes about 45 min: watch the first 10 min, then check the far corners before it finishes.
- [ ] **Time:** about **7.8 h** (7.85 h in silent mode), close to spec §7's 8 h limit. Start it when someone can check on it during the day: the printer is offline, so nothing reports a failure.

**After printing:** strength is NEEDS_TEST: run the proof tests in spec §8 and record them in inspection.md. Those are the standing load, the handling hold, and the drop on spare coxa servos with paint-marked nuts.
