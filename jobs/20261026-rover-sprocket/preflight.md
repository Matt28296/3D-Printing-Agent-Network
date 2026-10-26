# Preflight: Drive sprocket (×2: 2 per plate × 1 plate)

Job: 20261026-rover-sprocket · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 2 sprockets (spec §7 quantity 2).
- [ ] **Before printing, measure** (spec §3 and §9):
  - your N20 motors: gearbox 12 × 10, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat;
  - the shaft length from the flat gearbox face: 10 mm, at least 9.6 mm. A 9 mm shaft is too short;
  - the Pololu hub's hole circle. The slots cover r 5.5–6.85.

  Give Claude any difference over 0.3 mm.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **10 g** on the spool (8.4 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the sprockets off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** two toothed discs side by side, outer face down. It takes about 3 min.
- [ ] **SD card file:** `1026_rover_sprocket.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_rover_sprocket.gcode`. Watch the whole first layer, especially the tooth tips.
- [ ] **Time:** about **1.0 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.
- [ ] **Before you fit the discs (spec §8, chassis spec §8 test 2, BUILD_GUIDE step 6):** measure each motor's stall torque **with the hub on and before the sprocket disc is fitted**, so a motor stronger than the specified N20 never drives the printed teeth.
  1. Screw a 50 mm arm to the hub.
  2. Connect the motor straight to the freshly charged pack for 1 s (100 % PWM), with the arm pressing on a kitchen scale.
  3. The scale must read **≤ 371 g** (182 N·mm). If it reads more, the motor isn't the specified type: don't fit a sprocket disc to it.

**After printing:** strength is NEEDS_TEST. Spec §8:
- check the shaft end stands at least 2.1 mm proud of the hub's outer face;
- then run the torque and tooth proof tests;
- record the results in inspection.md.
