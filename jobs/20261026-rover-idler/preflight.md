# Preflight: Idler (×2: 2 per plate × 1 plate)

Job: 20261026-rover-idler · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 2 idlers (spec §7 quantity 2).
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **12 g** on the spool (10.5 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the idlers off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** two toothed discs side by side, outer face down, each with its Ø3.5 bore open in the middle. It takes about 3 min.
- [ ] **SD card file:** `1026_rover_idler.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_rover_idler.gcode`. Watch the whole first layer, especially the tooth tips.
- [ ] **Time:** about **1.2 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:** strength is NEEDS_TEST. Spec §8:
- the idler must spin freely on its bolt with under 0.5 mm of axial play;
- run proof test 1 (the rearward pull) after the chassis's idler-clamp plates are fitted;
- record the results in inspection.md.
