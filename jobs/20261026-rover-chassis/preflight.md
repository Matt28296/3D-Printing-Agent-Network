# Preflight: Chassis (×1: 1 per plate × 1 plate)

Job: 20261026-rover-chassis · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Plates:** 1 plate, 1 chassis (spec §7 quantity 1).
- [ ] **Before printing, measure** your N20 motors (gearbox 12 × 10, can Ø12 with 10 mm flats, shaft 10 mm from the gearbox face, at least 9.6 mm) and your 2 × 18650 holder (up to 80 × 41 × 21). Give Claude any difference over 0.3 mm (spec §3).
- [ ] **Filament:** PETG, loaded (`config/printer.json` lists no materials on hand yet, so confirm you have it). The G-code uses the Prusament PETG profile: 240 °C on the first layer, then 250 °C; bed 85 °C, then 90 °C. Have at least **157 g** on the spool (142.5 g + 10 %). A spool that runs out 11 h in ruins the print.
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it first (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI, cleaned with isopropyl alcohol, then a thin, even **glue-stick** layer over the whole 154 × 92 mm footprint as a release layer. PETG bonds hard to bare smooth PEI. Let the bed cool fully before you take the tub off.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **First layer:** the whole tub floor, 154 × 92 mm, about 26 min. Watch it all the way round, especially the four corners.
- [ ] **SD card file:** `1026_rover_chassis.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1026_rover_chassis.gcode`. Watch the first layer.
- [ ] **Time:** about **11.5 h** (11.7 h in stealth mode), close to the 12 h limit. Start it when someone can check it after the first layer and again later: the printer is offline, so nothing reports a failure. Check for corner lift during the first hour.
- [ ] **Steel idler plates (make them while it prints, BUILD_GUIDE §1 "Making the idler plates"):**
  - four identical plates, 20.6 × 10 × **2 mm** steel, each with a 3.4 × 12 mm slot from 6 to 18 mm along;
  - cut from 14-gauge (1.9 mm) or metric 2 mm flat bar. Not 1/8 in (3.2 mm): a head plate that thick stands 1.2 mm proud of its 2 mm recess;
  - deburr every edge and **break each corner slightly**. The slicer puts seam bumps in the corners of the head-plate recesses;
  - mark the 6 mm end of each plate; it goes to the rear.
- [ ] **Tools for the idler snug (BUILD_GUIDE step 3):** a **2.5 mm ball-end hex key** (L-key, 18 mm short arm). A plain long arm doesn't fit between the idler blocks (about 50 mm apart). Also: light machine oil for the plates' faces (required), a kitchen scale to feel the 230 g snug at the short arm's tip, and a soldering iron for the 4 heat-set inserts.

**After printing:**
- **Plate fit** (spec §8):
  - a head plate drops flush into the recess in each idler block's face;
  - a nut plate stands on each outer lip, between the end stops;
  - an M3 bolt slides the full slot.

  If a head plate won't sit flush, scrape the small bump in the recess's back corners, or file the plate's ends (BUILD_GUIDE §1 step 5).
- **Strength is NEEDS_TEST** (lowest SF 3.01). Run the spec §8 proof tests only with both idler plates fitted, after measuring each motor's stall torque with the hub on and the disc off. Record them in inspection.md.
