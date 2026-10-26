# Preflight: Claw cover (round 7)

Job: 20261026-arm-claw-cover · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 claw cover (spec §7 quantity 1).
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **38 g** on the spool (34.3 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer, including under the brim. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the cover off, then peel the brim away.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the cover stands on its end: a small 704 mm² footprint inside a 5 mm brim. It takes about 4 min. The cover grows 64 mm tall, so the brim must be stuck down all round.
- [ ] **SD card file:** `1026_arm_claw_cover.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_arm_claw_cover.gcode`. Watch the whole first layer and brim.
- [ ] **Time:** about **3.6 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure. At about 39 mm height the two side pieces start over their support pillars; a quick look then is worthwhile.

**After printing:**
- **Pillars** (BUILD_GUIDE step 9). Snap off the two support pillars inside the round hole, then trim any nub flush with a knife: the pinion passes 0.45 mm from the hole's edge.
- **Seat check at assembly** (BUILD_GUIDE step 9), with the cover pressed straight down over the inner post (third hole):
  1. Before any screw goes in, a **0.03 mm** feeler (blade at least 10 mm wide) **must** go in between the top wall and the frame's bulkhead, at the end where the lower slot is open.
  2. Drive the screws: the M3 × 45 anchor and washer snug first, then the M2.5 and M3 screws.
  3. After the screws, a **0.3 mm** feeler (the same wide blade) **must not** go in.

  If either check fails, stop and tell Claude.
- **Strength is NEEDS_TEST.** Run the spec §8 proof tests and record them in inspection.md.
