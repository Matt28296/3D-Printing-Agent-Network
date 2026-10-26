# Preflight: Turntable support ring (×1: 1 copy × 1 plate)

Job: 20261025-arm-turntable-ring · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 ring on it.
- [ ] **Before printing (spec §3):** measure your MG996R with its disc horn pressed home, top plate to horn face. Nominal 16.5 mm. If it differs by more than 0.1 mm, tell Claude first: it sets the ring's height and the running gap.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **19 g** on the spool (16.9 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the sheet cool before you take the ring off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the ring's foot and its 3 tabs, flat on the bed.
- [ ] **SD card file:** `1025_arm_turntable_ring.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_turntable_ring.gcode`. Watch the whole first layer (about 2 min).
- [ ] **Time:** about **1.8 h** (0.15 mm layers, so the top lands on 16.1 mm). Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- Fit with the PTFE tape on and check the 0.3–0.4 mm gap at 8 points (spec §8). It should need no sanding.
- M3 × 6 + Ø7 washers into the base: snug, no harder.
- Strength is NEEDS_TEST: covered by the base's proof test (spec §8); record it in inspection.md.
