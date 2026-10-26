# Preflight: Lid / electronics deck (×1: 1 per plate × 1 plate)

Job: 20261026-rover-lid · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 lid (spec §7 quantity 1).
- [ ] **Before printing, measure your boards** (spec §3): the ESP32 DevKit, the mini breadboard, the TB6612 carrier and the MP1584 buck. Give Claude any difference over 0.3 mm from the nominal sizes; the ESP32 pocket is 29.7 mm wide.
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **37 g** on the spool (33.5 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer over the whole 154 × 76 mm footprint as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool before you take the lid off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the whole flat underside of the deck, 154 × 76 mm, with the screw, toggle and cable-slot holes open. It takes about 23 min.
- [ ] **SD card file:** `1026_rover_lid.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_rover_lid.gcode`. Watch the first layer all the way round, especially the corners.
- [ ] **Time:** about **2.4 h**. Decide whether someone will be nearby: the printer is offline, so nothing reports a failure.

**After printing:** strength is NEEDS_TEST. Run the spec §8 proof tests and record them in inspection.md: deck press, sideways push, USB, toggle, lid refit and strap. If the toggle bushing catches in its hole, scrape off the small seam bump at the back of the hole.
