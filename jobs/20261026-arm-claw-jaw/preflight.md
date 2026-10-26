# Preflight: Claw jaw (×2: 2 copies × 1 plate)

Job: 20261026-arm-claw-jaw · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate with both jaws on it (jaw A and jaw B are the same part).
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **44 g** on the spool (39.5 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. There is no brim (it would fill the tooth gaps), so the glue also has to hold two 61 mm-tall parts on 572 mm² each. Let the sheet cool before you take them off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** two rack outlines side by side, each with its row of 18 teeth. If a jaw rocks or lifts, stop and tell Claude: the fix is two sacrificial ears (brief, DFM R1).
- [ ] **SD card file:** `1026_arm_claw_jaw.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_arm_claw_jaw.gcode`. Watch the whole first layer (about 3 min).
- [ ] **Time:** about **4.0 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- Spec §8 fit: both jaws slide in from the open slot ends with no binding; closed, the grip faces meet flat (0.2 mm feeler at most). If they don't, scrape the seam line on the grip face's edge (audit note 2).
- Strength is NEEDS_TEST: run spec §8's proof test (32 N pulls and pushes, 10.7 N sideways, grip and dowel tests) and record it in inspection.md.
