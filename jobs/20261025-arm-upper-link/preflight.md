# Preflight: Upper link (shoulder → elbow, round 6)

Job: 20261025-arm-upper-link · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 upper link (spec §7 quantity 1).
- [ ] **Before printing, measure** your MG996R and its horn (spec §3): body length and width, tab-hole spacing, shaft-to-end distance, lead exit, horn hub Ø, arm length and tip width. Give Claude any difference.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **43 g** on the spool (38.6 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the link off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the flat FRONT face, 146 × 34 mm, with the servo window and holes open. The horn pocket and back-face ribs build up from the top. It takes about 9 min.
- [ ] **SD card file:** `1025_arm_upper_link.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_upper_link.gcode`. Watch the whole first layer.
- [ ] **Time:** about **3.5 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:** strength is NEEDS_TEST. Do the spec §8 proof test with the MG996R fitted on its 4 tab screws, and record it in inspection.md:
- (1) 1 kg at the elbow axis;
- (2) 16 N square to the plate at 175 mm on a bar set at 60°.
