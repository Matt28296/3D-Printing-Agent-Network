# Preflight: Track link (×70: 35 per plate × 2 plates)

Job: 20261026-rover-track-link · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer, for every plate.

- [ ] **Plates:** **2 plates** of 35 links = 70, the 68 + 2 spares in spec §7. Both plates print the same file. This replaces the spec's 34 + 36, because a job holds one G-code file.
- [ ] **Pins on hand** before plate 1 finishes, because the test chain needs them: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred. BUILD_GUIDE §1 lists 68 + 2 spare.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **50 g** on the spool for one plate (44.9 g + 10 %), or about **99 g** for both.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings, and strings in the 0.5 mm knuckle gaps stop the hinges flexing.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer over the whole print area (about 170 × 145 mm) as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the links off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** 35 small links in 8 columns × 5 rows, inner face down, about 12 min. Each link touches the bed with only about 120 mm². Watch that every one sticks. If one lifts or gets dragged, stop the print and restart the plate: a loose link gets pushed into its neighbours and can knock them off too.
- [ ] **SD card file:** `1026_rover_track_link.gcode` (written by `tools/export_sd.py` after you approve). The same file prints both plates.
- [ ] **On the printer:** Print from SD → `1026_rover_track_link.gcode`. Watch the whole first layer.
- [ ] **Time:** about **6.2 h** per plate (12.5 h for both). Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Between plates: test chain first** (spec §8, BUILD_GUIDE "Before you start"). Before printing plate 2:
  1. Take plate 1's links off the cool sheet and pick off any strings in the knuckle gaps.
  2. Pin 5 links into a test chain.
  3. Run proof tests 1–3: pressing, 4.5 kg tension, 5 kg hinge crush.

  If an outer knuckle cracks when you press a pin, stop and tell Claude: the fix (`PIN_GRIP_CLR` +0.05 and CA on the pins) is a design change, so plate 2 needs a new file. If the chain passes, clean the sheet, re-apply glue, and go through this list again for plate 2.

**After printing:** pick strings out of the knuckle gaps before pinning, then check that pinned links flex freely to 40° both ways (spec §8). Record the proof tests in inspection.md.
