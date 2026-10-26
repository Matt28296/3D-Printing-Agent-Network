# Preflight: Forearm (elbow → wrist, round 6)

Job: 20261025-arm-forearm · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 forearm (spec §7 quantity 1).
- [ ] **Before printing, measure your MG90S** (spec §3 and §8): body 22.8 × 12.2 nominal, and its tab-hole spacing. The round-6 pilots are at x 70.6 and 99.7. Give Claude any difference.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **32 g** on the spool (28.6 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the forearm off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the flat FRONT face, 129 × 26 mm, with the MG90S window and pilots open. The horn pocket, ribs and cross-rib build up from the top. It takes about 7 min.
- [ ] **SD card file:** `1025_arm_forearm.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_forearm.gcode`. Watch the whole first layer.
- [ ] **Time:** about **2.6 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- **Screw-strip check first** (spec §8, your decision of 26 Oct). Drive the M2 × 12 (lead end, through the filed slit) and the M2 × 16 (far end) snug, then look at both strips beside the window.
  - If either whitens or cracks, stop and tell Claude: the pilots move and the forearm is reprinted.
- **Then the spec §8 proof test**, and record it in inspection.md:
  - (1) 1 kg at the wrist axis;
  - (2) 17 N square to the plate at 83 mm on a bar set at 60°.
