# Preflight: Brio 4K camera mount (×1: 1 copy × 1 plate)

Job: 20261026-arm-camera-mount · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 mount on it.
- [ ] **Before printing (spec §3):** measure the Brio's thread depth and the height of its USB-C port on the back. The lip is 6 mm tall, and the right-angle plug must clear it.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **15 g** on the spool (12.9 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. The 5 mm brim holds this 50 mm tall part: let the sheet cool before you take it off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the mount's side profile, standing on its end (a small 40 × 32 mm outline), with a 5 mm brim all round. The brim must stick everywhere.
- [ ] **SD card file:** `1026_arm_camera_mount.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_arm_camera_mount.gcode`. Watch the whole first layer (about 2 min).
- [ ] **Time:** about **1.4 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- Trim the brim flush with the 0.3 mm bed chamfer.
- Strength is NEEDS_TEST: run spec §8's proof test (sweeps, 15 N cable pulls, 15 N twist pulls, 20 N end push) and record it in inspection.md.
