# Preflight: Claw frame (round 7)

Job: 20261026-arm-claw-frame · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 claw frame (spec §7 quantity 1).
- [ ] **Before printing, measure your MG90S** (spec §3): body 22.8 × 12.2 nominal, and its tab-hole spacing. Give Claude any difference.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **46 g** on the spool (41.3 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the frame off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the flat back face with the wrist-horn pocket open. It takes about 6 min.
- [ ] **SD card file:** `1026_arm_claw_frame.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_arm_claw_frame.gcode`. Watch the whole first layer.
- [ ] **Time:** about **3.9 h** (4.0 h in stealth mode), close to the 4 h limit. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- **Groove check.** The V-groove in the rail block's top should be open along its length (about 1.5 mm wide at the top). The cover's ridge seats in it.
- **Screw-strip check** (spec §8, your decision of 26 Oct): drive the MG90S tab screws snug and look at the strips beside the holes. If either whitens or cracks, stop and tell Claude.
- **At assembly (BUILD_GUIDE step 9), the seat check, with the cover pressed straight down over the inner post (third hole):**
  1. Before any screw goes in, a **0.03 mm** feeler (blade at least 10 mm wide) **must** go in between the cover's top wall and this bulkhead, at the end where the lower slot is open.
  2. Drive the screws: the M3 × 45 anchor and washer snug first, then the M2.5 and M3 screws.
  3. After the screws, a **0.3 mm** feeler (the same wide blade) **must not** go in.

  If either check fails, stop and tell Claude.
- **Strength is NEEDS_TEST.** Run the spec §8 proof tests and record them in inspection.md.
