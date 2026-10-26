# Preflight: Turntable with shoulder upright (×1: 1 copy × 1 plate)

Job: 20261025-arm-turntable · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 turntable on it.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **116 g** on the spool (105.3 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI, and the disk's bottom 6 mm prints solid. Let the sheet cool fully before you take the turntable off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the Ø96 disk, flat on the bed, with the Ø3.4 clamp hole in its centre.
- [ ] **SD card file:** `1025_arm_turntable.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_turntable.gcode`. Watch the whole first layer (about 16 min).
- [ ] **Time:** about **6.9 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- Check the disk's underside is flat: it seats on the Ø25 disc horn and runs 0.4 mm over the ring.
- Strength is NEEDS_TEST: run spec §8's proof tests (arm-up sideways push, disc-horn slip check) and record them in inspection.md.
