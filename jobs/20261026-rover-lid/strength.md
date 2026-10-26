VERDICT: FAIL

# Strength check: 20261026-rover-lid (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-lid/strength_calc.py`

**Result: FAIL.** 1 of 17 verdict rows is below its required SF.

**The failing row (L1).** A 20 N hand press on the rail at the middle of the ESP32 window gives the rail top SF **2.49** against 3.
- **What changed.** This is a correction to the round 1–2 model, not a round-3 regression. Those rounds treated the strip beside the window as a cantilever from the side wall (SF 3.75).
- **Why that model fails.** Between the four corner screws the lid only rests on the wall tops, so nothing can clamp the strip there. A press at the window edge has to travel along the rail, as an edge beam, to the window ends, with plate twist carrying the rest to the wall.
- **How it's modelled.** As a classical plate strip: Kirchhoff plate, Lévy/Fourier solution, with the rail as an edge beam. The model ignores any help from the deck beyond the window ends. With those ends taken as rigid supports the SF would be 3.54. The real ends aren't rigid: the deck beyond them spans 71.5 mm between the side walls, and at the front end the cable slots cut it. So the true value lies between the two, and the verdict uses the lower one.

**The fix.** `RAIL_W` 2.5 → **4.5 mm** gives SF 3.29 (3.17 even under a point load), and it also lifts the rail root (L6) from 3.27 to 10.6. The cost is about 1 g. 4.0 mm is the minimum (SF 3.11).

**Everything else passes**, including the new round-3 features:
- toggle hole (9.06, cyclic);
- tie bar (5.49);
- cable-slot edge (3.77);
- deck strip between the window's far end and the cable slots (3.39);
- insert screws (100 or more).

**Drop rows:** they hold their SF up to an 81.8 cm drop.

## Round-2 findings: what round 3 did

| Round 2 | Round 3 | Result |
|---|---|---|
| NEEDS_TEST; rail root lowest at SF 3.27 | Geometry unchanged at the rail | L6 3.27 ✓, but L1 (re-modelled) governs. See above. |
| Proof tests needed beyond spec §8's 1 × service | Spec §8 tests 1–5 (deck press 4 kg, sideways 2 kg, USB × 10, toggle × 20, refit × 5) | Match, once the rails are widened (below) |
| Screws on the chassis columns | M3 × 8 into heat-set inserts at (−13, ±32.5) and (102, ±32.5) | L9/L10 106 / 102 ✓. Insert retention is chassis E1/E2 (SF 141 / 259). |
| Window corners sharp (DFM round 2, R2) | Still sharp | L1c: Kt 2.5 with the rail fully fixed at the window ends, SF 4.02 ✓ |
| ESP32 stands proud of the rails (upside-down landing) | Not changed | Advisory only. Not a 5 cm design case. |

## Load cases

These come from the shared rover block (the chassis report has the full table) plus spec §4.

| Load | Value | Note | Duration |
|---|---|---|---|
| Hand press beside the window | **20 N on the rail at mid-window** | The worst position "beside the window": the rail is the window edge and the highest feature there. Fingertip taken as 5 mm along the rail (a real fingertip at 20 N spreads over about 10 mm); a point load is advisory. | short-term |
| Hand press at the breadboard centre | 20 N | One-way, b_eff = span/2 (rounds 1–2) | short-term |
| Hand press at a cable-slot edge | 20 N, 5 mm fingertip | Added for the round-3 slots | short-term |
| Press on the seated ESP32 | 20 N at mid-span: 10 N on each end ledge, spread over the board width | Ledge bearing (L4); the far ledge also loads the deck between the window and the cable slots (L4b, new in round 3) | short-term |
| USB plug | 10 N along X | | short-term |
| Sideways jumper pull | 10 N | | short-term |
| Jumpers pushed on from below | 20 N on the tie slots | | short-term |
| Wire bundle pull on the tie bar | 10 N | | short-term |
| Toggle flick | 5 N at the lever tip, 13 mm up: 65 N·mm | | cyclic |
| Lifted by the lid | 2 × W on 4 screws: 3.2 N each | Mass 649 g | short-term |
| 5 cm drop | 20 g on the deck and its electronics (71 g) | | short-term |

## Assumptions

**Support.** The lid rests on the 4.5 mm wall tops and is screwed down only at the 4 corner columns. Where the deck meets a wall it is simply supported, not clamped. Spans are taken to the wall centre lines (71.5), which is conservative, as in rounds 1–2.

**Window edge (L1).** The plate strip runs from the window edge to the wall centre line, b = 20.9.
- **Edge beam.** The rail (2.5 × 4.1 on the deck, measured on the solid) acts compositely with a deck flange of rail + 2t.
  - Composite I 125.6 mm⁴, rail top 4.58 above the neutral axis.
  - The beam stiffness entered is the part the plate doesn't already carry.
- **Window ends ignored.** This is the verdict basis: an infinitely long strip, the lower bound.
- **Rigid-end bound.** Simply supported across the window ends; advisory only, an upper bound.
- **Model checks in the script.** A very stiff edge beam reproduces the rigid-rotation beam model (ratio 1.000). With no plate, rigid ends give the beam's P·a/4 (248.0 = 248.0).
- **Stress direction.** The rail top carries x-direction stress along the layers, so it is in-plane. It is in compression.

**Cable slot (L2).** The slot edge is a free edge without a beam. The slot ends (10.2 apart) are simply supported. The slot is short next to the surrounding deck, so its ends move with the deck. The fingertip contact is 5 mm; 2 mm (a fingernail or a tool edge) is advisory.

**Far end of the window (L4b).**
- **Section.** At |y| 9–12.1, beside the tongue and through the slots, the deck between the far ledge and the cable slots is the only material from x 66.0 to 70.9 (measured on the solid), plus the deck in front of the slots out to x 85.4.
- **Model.** One-way slab across the side walls, with b_eff = span/2 centred on the far ledge, net of the window and the slots.
- **Strip-alone bound (advisory, 2.77).** The strip carrying it alone, with no help from the deck in front of the slots. The deck in front is joined to the strip by the tie bar and the solid deck at |y| > 12.1, so it does share the load.

**Other features.**
- **Rail root (L6):** across layers, Kt 2.5 at the sharp root.
- **Toggle hole:** treated as a rigid nut boss in a plate, Kt 2.
- **Tie bar:** measured on the solid, 2.80 × 3.0.
- **Inserts:** checked in the chassis.

## Allowables and sources

**No measured data.** The skill's placeholders apply:
- PETG 25 MPa in-plane and 12.5 MPa across layers;
- E 1800 MPa, ν 0.35;
- shear allowable 0.5 × normal.

NEEDS_TEST is the best verdict possible.

**Compression.** The placeholder allowable doesn't separate tension from compression. The L1 rail top is in compression; the tension side (deck bottom under the rail, L1b) is at SF 4.54.

**Required SF:**

| Load type | Required SF |
|---|---|
| Short-term | 3 |
| Cyclic | 4 |
| Proof | 1.0 |

**Temperature:** service is 40 °C against a softening point of about 70 °C.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | L1 rail at mid-window, hand 20 N (5 mm fingertip): rail top, edge beam of a plate strip, window ends ignored | XY | 10.03 | 25.0 | 2.49 | 3.0 | **FAIL** |
| 2 | L1b deck bottom under the rail, same case (tension) | XY | 5.51 | 25.0 | 4.54 | 3.0 | OK |
| 3 | L1c window corner (sharp, Kt 2.5): rail edge beam fixed at the window ends, PL/8 = 124 N*mm | XY | 6.21 | 25.0 | 4.02 | 3.0 | OK |
| 4 | L2 deck at a cable-slot edge, hand 20 N (5 mm fingertip): free edge, slot ends (10.2 apart) simply supported | XY | 6.63 | 25.0 | 3.77 | 3.0 | OK |
| 5 | L3 deck at the breadboard centre, hand 20 N (one-way, b_eff span/2) | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 6 | L4 end-ledge bearing, 20 N on the ESP32 | XY | 0.14 | 25.0 | 178.20 | 3.0 | OK |
| 7 | L4b deck between the far ledge and the cable slots, ESP32 press (10 N on the far ledge): one-way slab, b_eff span/2 net of the window and slots | XY | 7.38 | 25.0 | 3.39 | 3.0 | OK |
| 8 | L5 window end face bearing, USB 10 N (2 header strips 2.5 x 2.5) | XY | 0.80 | 25.0 | 31.25 | 3.0 | OK |
| 9 | L6 side rail root, sideways jumper pull 10 N over 26 mm (Z, Kt 2.5 sharp root) | Z | 3.82 | 12.5 | 3.27 | 3.0 | OK |
| 10 | L7 zip-tie slot ligament (4.0 mm) shear, 20 N tie load | XY shear | 0.83 | 12.5 | 15.00 | 3.0 | OK |
| 11 | L8 tie bar, wire bundle pulled 10 N at mid-span (fixed ends, Kt 1.5 r2.0 corners) | XY | 4.55 | 25.0 | 5.49 | 3.0 | OK |
| 12 | L9 screw-head bearing, rover lifted by the lid (3.2 N per M3 x 8) | XY | 0.23 | 25.0 | 106.65 | 3.0 | OK |
| 13 | L10 screw-hole push-through (plug shear, Z), lifted by the lid | Z shear | 0.06 | 6.2 | 101.77 | 3.0 | OK |
| 14 | L11 deck round the toggle bushing, flick 65 N*mm (nut Ø10 boss in a plate, Kt 2 at the hole), cyclic | XY | 2.76 | 25.0 | 9.06 | 4.0 | OK |
| 15 | L12 deck under its own and the electronics' inertia, 5 cm (71 g x 20 g) | XY | 0.51 | 25.0 | 49.06 | 3.0 | OK |
| 16 | L13 end ledge to deck, ESP32 inertia 2.0 N, 5 cm (Z shear) | Z shear | 0.01 | 6.2 | 454.13 | 3.0 | OK |
| 17 | L14 screw-head bearing, deck inertia 5 cm (3.5 N per screw) | XY | 0.26 | 25.0 | 97.01 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| L1 with rigid window ends (strip simply supported across x 16.4 and 66.0): upper bound of the end help | XY | 7.07 | 25.0 | 3.54 | 3.0 | OK |
| L1 with a point load on the rail (no fingertip spread) | XY | 10.53 | 25.0 | 2.37 | 3.0 | no |
| L4b with the strip behind the slots alone (no help from the deck in front of the slots) | XY | 9.03 | 25.0 | 2.77 | 3.0 | no |
| L2 with 2 mm contact (a fingernail or a tool edge, not a hand press) | XY | 9.81 | 25.0 | 2.55 | 3.0 | no |
| proof (§8 test 1a) 40 N on the rail at mid-window (5 mm contact): rail top | XY | 20.06 | 25.0 | 1.25 | 1.0 | OK |
| proof (§8 test 1b) 40 N at the breadboard centre | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |
| proof (§8 test 2) 20 N sideways on the seated ESP32: rail root | Z | 7.64 | 12.5 | 1.64 | 1.0 | OK |
| FIX RAIL_W 3.5 (rails widen outward, tie slots move with them): L1 rail top | XY | 8.56 | 25.0 | 2.92 | 3.0 | no |
| FIX RAIL_W 4.0 (rails widen outward, tie slots move with them): L1 rail top | XY | 8.03 | 25.0 | 3.11 | 3.0 | OK |
| FIX RAIL_W 4.5 (rails widen outward, tie slots move with them): L1 rail top | XY | 7.59 | 25.0 | 3.29 | 3.0 | OK |
| FIX RAIL_W 4.5: L1 with a point load | XY | 7.89 | 25.0 | 3.17 | 3.0 | OK |
| FIX RAIL_W 4.5: L1b deck bottom under the rail | XY | 4.98 | 25.0 | 5.02 | 3.0 | OK |
| FIX RAIL_W 4.5: L1c window corner (Kt 2.5) | XY | 4.44 | 25.0 | 5.63 | 3.0 | OK |
| FIX RAIL_W 4.5: L6 rail root, sideways pull 10 N | Z | 1.18 | 12.5 | 10.60 | 3.0 | OK |
| FIX RAIL_W 4.5: L7 tie-slot ligament | XY shear | 0.56 | 12.5 | 22.50 | 3.0 | OK |
| FIX RAIL_W 4.5: proof 40 N on the rail at mid-window | XY | 15.19 | 25.0 | 1.65 | 1.0 | OK |
| assembly: M3 x 8 lid screw, no washer at 0.15 N*m (P 250 N), bearing on the deck | XY | 18.41 | 25.0 | 1.36 | 3.0 | no |
| assembly: M3 x 8 lid screw, no washer at 0.5 N*m (P 833 N), bearing on the deck | XY | 61.37 | 25.0 | 0.41 | 3.0 | no |
| assembly: M3 x 8 with an ISO 7089 washer at 0.5 N*m (P 833 N), bearing on the deck | XY | 29.44 | 25.0 | 0.85 | 3.0 | no |
| assembly: toggle M6 nut at 0.6 N*m (P 500 N) on the deck (54 mm²) | XY | 9.19 | 25.0 | 2.72 | 3.0 | no |

- **Lowest SF:** 2.49 (required 3.0), at L1: the rail top at mid-window.
- **Drop rows:** they hold their SF up to an 81.8 cm drop.
- **Verdict rows:** 1 of 17 is below its required SF.
- **Round-2 cantilever model of L1, for comparison:** 6.67 MPa (SF 3.75). It isn't used, because it needs a clamped root at the wall.

## Required change

**Widen the window rails outward: `RAIL_W` 2.5 → 4.5 mm.**
- The window and pocket stay as they are.
- The tie slots move out with the rails: their position already includes `RAIL_W`.
- The rail spans x 13.4–69.0 and widens to |y| 14.85–19.35. That is clear of the toggle (x ±3.2), the cable slots (x ≥ 70.9) and the screws.

**What it gives:**
- L1: SF 3.29 (3.17 under a point load);
- deck bottom: 5.02;
- window corner: 5.63;
- rail root (L6): 10.6;
- tie-slot ligament: 22.5.

**Minimum width:** 4.0 mm (SF 3.11, but 2.99 under a point load). 3.5 mm is not enough (2.92).

**Optional extras.** Rounding the window corners to r 2 mm (DFM round 2, R2) and making the rails taller would add margin. Neither is needed for the verdict.

With the change made, the verdict becomes **NEEDS_TEST**: the placeholder allowables rule out a PASS.

## Proof tests

Spec §8's five tests then match the NEEDS_TEST verdict, with one clarification to test 1a: **press on the rail top**, which is where the stress is.

**Test 1a. Rail press.**
- Lid screwed on, ESP32 removed.
- Press **4 kg (≈ 40 N, 2 × service)** for **1 min** through a 10 mm rubber pad on one rail top at mid-window (x ≈ 41). Repeat on the other rail.
- Placeholder SF at this load: 1.65 after the fix (1.25 on the current rails).

**Test 1b. Breadboard press.** 4 kg at the breadboard centre for 1 min (SF 1.88).

**Test 2. Sideways push.** Push the seated ESP32 sideways with 2 kg (≈ 20 N) for 10 s each way (rail root SF 1.64 on the current rails, 5.3 after the fix).

**Tests 3–5. Use cycles.** USB × 10, toggle × 20, lid refit × 5.

**Pass, all tests:**
- no crack or whitening at the rails, the window corners, the ledges, the screw holes, the toggle hole, the tie bar or the strip between the window and the cable slots;
- permanent set 0.2 mm or less (straight-edge along each rail and across the deck);
- the board stays on both ledges;
- no insert turns or pulls up.

## Notes

- **Lid screws.** The lid needs no clamp force: it rests on the walls, and the screws only hold it down against handling loads of 3.2 N each.
  - **Advice:** tighten until the head just seats (about 0.1 N·m).
  - **Why:** at 0.5 N·m the head crushes the deck, even with an ISO 7089 washer (SF 0.41 without, 0.85 with).
  - **Thread engagement:** M3 × 8 through the 3 mm deck leaves 5 mm in the 5.7 mm insert (4.5 mm with a washer). That is enough.
  - **Insert hole:** the Ø4.0 insert holes print about Ø3.8. The chassis report covers this: retention isn't reduced.
- **Toggle nuts.** Run them up finger-tight plus about a quarter turn (≤ 0.3 N·m). At 0.6 N·m the M6 nut presses the deck at SF 2.72. Round 3 already lets the inner nut come off if the bushing is short (spec §3).
- **Cable slots.**
  - **Slot edge.** A firm fingernail or tool press at a slot edge (2 mm contact) is at SF 2.55. The slots are full of wires in use, so this isn't a design case.
  - **Far end of the window.** The strip between the window's far end and the slots is the deck's other weak spot: 3.39 with the deck in front of the slots helping, 2.77 if it didn't.
- **ESP32 above the rails.** The ESP32 module and its USB stand 3.5 mm proud of the rails. An upside-down landing would hit the board first. That is not a design case at 5 cm the right way up; taller rails would protect it.
