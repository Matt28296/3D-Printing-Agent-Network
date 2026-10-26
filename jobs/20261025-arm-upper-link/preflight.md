# Preflight: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · print-ops-lead · 2026-10-26 · confirm each item at approval and again at the printer.

- [ ] **Filament:** Prusament PETG (or another PETG; the G-code uses the Prusament PETG profile: 240 °C first layer, then 250 °C; bed 85 then 90 °C). At least **37 g** on the spool (33.9 g + 10 %).
- [ ] **Drying:** if the spool has been out of its bag for more than a few days, dry it (65 °C, 4 h). Wet PETG strings and prints weak.
- [ ] **Sheet:** smooth PEI cleaned with isopropyl alcohol, then a thin glue-stick layer as a release agent (PETG can tear chunks out of bare smooth PEI). A textured sheet needs no glue.
- [ ] **Bed clear** of objects and old prints; nozzle clean.
- [ ] **Orientation check on the LCD preview / first layer:** Flat, FRONT face on the bed (the horn pocket opens upward, so no bridge). In-plane and out-of-plane bending run along the layers; horn-joint pull-out shears the layers, which the centre-screw clamp now carries.
- [ ] **SD card file:** `1025_arm_upper_link.gcode` (written by `tools/export_sd.py` after you approve).
- [ ] **On the printer:** Print from SD → `1025_arm_upper_link.gcode`. Watch the whole first layer (about 5 min).
- [ ] **Time:** about **3.0 h**. Decide whether someone will be nearby; the printer is offline, so nothing reports a failure.

After printing and assembly, the strength verdict is NEEDS_TEST: do this proof test and record it in inspection.md:

> (1) Shoulder horn in a vice (horn clamped in its slot), 1 kg at the elbow axis for 1 min: deflection at the elbow < 2 mm, no permanent set. (2) Same clamping, 21 N (≈2.1 kg) sideways (out of the link plane) at the elbow axis for 1 min each way, then 7.5 N sideways at the end of a 185 mm lever bolted to the elbow tab holes. Pass: no cracks at the pocket, no lift of the link off the horn, no permanent set.
