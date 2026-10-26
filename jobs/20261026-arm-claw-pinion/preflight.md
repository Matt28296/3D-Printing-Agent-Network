# Preflight: Claw pinion (×1: 1 copy × 1 plate)

Job: 20261026-arm-claw-pinion · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 pinion on it.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **5 g** on the spool (4.3 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak, and this small gear prints solid.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer as a release layer. PETG bonds hard to bare smooth PEI. Let the sheet cool before you take the pinion off, and rinse any glue out of the horn pocket with water.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** a 20-tooth gear outline with the horn pocket (hub and two stubs) open in its middle.
- [ ] **SD card file:** `1026_arm_claw_pinion.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_arm_claw_pinion.gcode`. Watch the whole first layer (under 1 min), and stay for the pocket's bridged ceiling at about 2 mm.
- [ ] **Time:** about **0.5 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:**
- Before fitting, measure your MG90S double-arm horn (hub Ø, arm width near the hub) and cut both arms to 5.5 mm from the centre (spec §3, BUILD_GUIDE). The pinion should press on with a light fit.
- Strength is NEEDS_TEST: run spec §8's proof test (32 N pulls, 10.7 N sideways, grip test) and record it in inspection.md.
