VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-lid (round 4)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-lid/strength_calc.py` (about 40 s)

**Result: NEEDS_TEST.** All 26 verdict rows meet their required SF. The allowables are placeholders, so PASS is not possible.

- **Round 3's failing row now passes.** The rail press at mid-window (L1) is at **SF 3.20** (round 3: 2.49 on the 2.5 mm rails).
  - That figure includes the moved tie slots: cutting their zones out of the plate strip raises the rail stress by 2.9 %.
  - Without the slots it would be 3.29, round 3's prediction for the 4.5 mm rail.
- **Lowest SF: 3.15, at L7d.** The ESP32 zip tie bears on the inner wall of its slot.
  - The spec's 20 N push from below puts **44 N** into the nearly flat strap.
  - L7d reaches SF 3 at 46.5 N, so pull the ties snug by hand (see Notes).
  - A strap proof test is proposed below.
- **The moved slots and their ligaments pass:**
  - press on the rail beside a slot (L1e): 7.28;
  - slot-to-wall ligament, press at the slot's outer edge (L2b): 5.25;
  - window-edge-to-slot ligament, strap shear-out (L7a): 5.08;
  - far-end bridge, the rail on its 6 mm strip between the slot and the window: in-plane bending (L7b) 7.09, twist (L7c) 22 or more;
  - window corners on the slot-reduced section (L1c): 3.77;
  - deck band through the far slots under the ESP32 press (L4c): 5.97.
- **The wider rails help elsewhere:** the rail root (L6) is at 10.6 (it was 3.27), and a press on the deck outboard of the rail (L1d, new) is at 5.56.
- **Drop rows:** they hold their SF up to a **40.5 cm** drop (round 3: 81.8 cm). The limit is now the deck band at the tie slots (L12b).

## Round 3's required change: what round 4 did

| Round 3 | Round 4 | Result |
|---|---|---|
| FAIL: L1 rail top at mid-window, SF 2.49 (rail as the edge beam of a plate strip) | `RAIL_W` 2.5 → 4.5, widened outward to \|y\| 14.85–19.35. The window, pocket and ledges are unchanged. | L1 is 3.29 on round 3's model and 3.20 with the moved tie slots cut out of the strip ✓ |
| The tie slots move out with the rails | \|y\| 20.85–22.65, 1.5 outside the rail. The 30- and 38-pin boards' far-end slots overlap into one 6.1 mm slot (x 62.7–68.8). | New rows L1c (slot-reduced section), L1e, L2b, L4c, L7a–L7d and L12b all pass ✓ |
| Proof test 1a on the rail top | Spec §8 test 1a reworded | Matches: SF 1.60 at 40 N on the placeholder ✓ |

## Load cases

These come from the shared rover block (the chassis report has the full table) and spec §4.

| Load | Value | Note | Duration |
|---|---|---|---|
| Hand press beside the window | **20 N on the rail**, 5 mm fingertip | At mid-window, the spec's position (L1). Also beside the tie slots (L1e) and on the deck outboard of the rail (L1d). | short-term |
| Hand press at a slot edge | 20 N, 5 mm fingertip | Cable slot (L2); a tie slot's outer edge, the slot-to-wall ligament (L2b) | short-term |
| Hand press at the breadboard centre | 20 N | One-way, b_eff = span/2 (L3) | short-term |
| Press on the seated ESP32 | 20 N at mid-span: 10 N on each end ledge, spread over the board width | Ledge bearing (L4); far-end deck (L4b) and its band through the tie slots (L4c) | short-term |
| USB plug | 10 N along X | | short-term |
| Sideways jumper pull | 10 N | | short-term |
| Jumpers pushed on from below | **20 N under one tie → 44 N in the strap** | Round 3 applied the 20 N to the ligament directly; see the strap assumptions | short-term |
| Wire bundle pull on the tie bar | 10 N | | short-term |
| Toggle flick | 5 N at the lever tip, 13 mm up: 65 N·mm | | cyclic |
| Lifted by the lid | 2 × W on 4 screws: 3.2 N each | Mass 649 g | short-term |
| 5 cm drop | 20 g on the deck and its electronics (73 g) | | short-term |

## Assumptions

**Support (unchanged).** The lid rests on the 4.5 mm wall tops and is screwed down only at the 4 corner columns. Where the deck meets a wall it is simply supported, at the wall centre lines (span 71.5).

**Rail press at mid-window (L1): round 3's verdict basis, plus the tie slots.**
- **Basis.** The plate strip runs from the window edge to the wall centre line (b = 20.9).
  - The rail is its edge beam: composite I 196.1 mm⁴, rail top 4.29 above the neutral axis.
  - The window ends are ignored (an infinitely long strip).
  - Round 3's model checks still hold: 1.000, and 248.0 = 248.0.
- **The tie slots.** They cut the strip at |y| 20.85–22.65 over x 13.6–16.8 and 62.7–68.8, 21.5 mm or more from mid-window.
  - The strip's response reaches far: its decay length is 34.5 mm, and at the far slot the rail curvature is still about half its peak. So distance alone doesn't rule the slots out.
  - The Lévy solution can't take a hole. The factor therefore comes from the 1-D rigid-rotation model of the same strip (round 3's model check: the edge beam plus D·b/3 in bending, plate twist 2D(1−ν)/b), solved by finite differences.
  - In a slot zone, only the rail on its 6.0 mm deck strip carries bending (I 154.2), and nothing outboard of the slot helps: no twist.
  - **Result:** with the zones cut over their full length, the rail stress at mid-window rises by **2.9 %**. Cut only where the slots lie beside the open window, it rises by 1.1 %.
  - The 1-D model reproduces the analytic infinite-beam value (1.0000) and sits 1.1 % below the Lévy result, so every 1-D result is scaled up by 1.0113.
- **The basis is very conservative.** It gives the window ends no stiffness at all.
  - Credit only the ledge strip at each window end: a 3.0 × 2 mm ledge on the deck, spanning the walls, which is 12.4 N/mm at the rail line. All the closed deck beyond is still ignored.
  - That alone nearly halves the mid-window rail moment (178 against 333 N·mm), giving SF 6.17 (advisory).
  - The verdict keeps round 3's basis.

**Window corners (L1c).** Both corners now have a tie slot beside them, so the rail acts only with its 6.0 mm deck strip (I 154.2, neutral axis 3.30).
- **Moment.** Taken as the rail fixed at both window ends: PL/8 = 124 N·mm (hogging), with Kt 2.5.
- **Check of that bound.** In the end-supported model above, the corner moments are +31 and +32 N·mm, well inside it.
- The infinite strip has no corners, so it can't be used at them.

**Press on the deck outboard of the rail (L1d, new).** This is the same plate strip with the load on an interior line and the edge beam unloaded.
- **Conditions at the load line:** W, W' and W'' continuous, and a jump in shear equal to the load.
- **Model check:** a load 0.05 mm inside the edge reproduces the edge-load result (0.9966).
- **Load shape:** the fingertip is given no width across y, which is conservative for M_y.
- **Result:** worst at |y| 25.9, with 4.49 MPa in the deck; the rail top sees only 3.19 MPa.

**Press beside the tie slots (L1e, new).**
- **Range.** Presses from 8 mm before each slot zone to its end.
- **Model.** The 1-D strip with the slot zones cut and the end ledges as lower-bound springs.
- **Result.** The stress falls toward the slots: the worst point is at the end of the scan nearest mid-window, 3.43 MPa.
- **Bounds without the ledges** (the infinite strip, as in L1):
  - a press at x 62.4, beside the far slot, is at SF 3.01 (advisory);
  - at the USB end the same model gives 2.98 for a press at x 16.9. There the fingertip is partly over the USB-end ledge that the model ignores, so that number isn't a credible bound.

**Zip-tie strap (L7, new).**
- **Path.** Each tie runs over the board's end, over both rails, down through a tie slot 1.5 mm outside the rail, and under the deck to the other slot.
- **Tension.**
  - The highest part of the board under the far tie is the ESP32 module's 0.8 mm antenna PCB. It stands only about 0.3 mm above the rail tops, so the strap is nearly flat.
  - A nearly flat strap holds a push P from below with T = P/(2 sin φ). The board lifts until the tie's stretch raises φ.
  - For a 2.5 × 1.0 mm PA66 strap (E 2500 MPa, 95 mm loop, 66 N/mm) pulled snug by hand (25 N), it settles at φ 13° and **T = 44.3 N**, 2.2 × the push.
  - At the USB end, where the strap runs over the micro-USB connector: 42.6 N.
- **Forces on one side.**
  - The two strands pull the slot's side inward with up to 2T.
  - The slot's inner wall takes 1.34 T, at its top and bottom edges.
  - Wrapping over the rail and under the deck twists the bridge by only 16 N·mm.
- **Sections.**
  - **L7a:** the ligament from the window edge to the slot is 6.0 mm; shear-out uses the deck only.
  - **The bridge:** at the far end the slot zone runs 3.3 mm alongside the open window. There the rail and its 6.0 mm strip form a bridge (x 62.7–66.0) between the plate and the far ledge.
  - **L7b:** the 30-pin board's tie at x 64.3 bends the bridge in-plane. Fixed ends, with Kt 2.5 at its sharp corners.
  - **L7c:** the bridge's twist. The short faces shear along the layers, so that row uses the across-layer allowable.
  - **L7d:** strap bearing on the slot's inner wall, over the strap width × the deck (2.5 × 3), as a bolt-bearing analogue.
- **Where only L7d applies:** at the USB end and under the 38-pin board's far tie, the slot's inner side is the solid ledge region.
- **The tie breaks first.** A 2.5 mm tie breaks at about 80 N (18 lb). At that tension every strap row is still above SF 1 (lowest 1.74).
- **The slot-to-wall ligament takes no strap load:** the strap bears only on the slot's inner side.

**Slot-to-wall ligament and slot bands.**
- **L2b:** a press at a tie slot's outer edge, in the L2 model: free edge, slot ends simply supported. It uses the merged 6.1 mm slot and the 13.1 mm strip to the wall centre line.
- **L4c:** the L4b slab at the band through the far tie slots (deck x 49.6–62.7 and 68.8–85.4 on the solid). Kt 2.5 at the square slot ends, the chassis strap-slot convention.
- **L12b:** the drop load at the tie slots' inner edge, net of the slot in a span/2 band, with Kt 2.5.

**Other features (round 3, unchanged).**
- **Rail root (L6):** across layers, Kt 2.5 at the sharp root.
- **Toggle hole:** treated as a rigid nut boss in a plate, Kt 2.
- **Tie bar:** measured on the solid, 2.80 × 3.0.
- **Inserts:** checked in the chassis report.

## Allowables and sources

**No measured data.** `library/materials.csv` has only its header row, so the skill's placeholders apply:
- PETG 25 MPa in-plane and 12.5 MPa across layers;
- E 1800 MPa, ν 0.35;
- shear allowable 0.5 × normal.

NEEDS_TEST is the best verdict possible.

**Compression.** The placeholder allowable doesn't separate tension from compression. The L1 rail top is in compression; the tension side under it (L1b) is at SF 4.88.

**Required SF:**

| Load type | Required SF |
|---|---|
| Short-term | 3 |
| Cyclic | 4 |
| Proof, and the strap at the tie's rated strength | 1.0 |

**Temperature:** service is 40 °C against a softening point of about 70 °C.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | L1 rail at mid-window, hand 20 N (5 mm fingertip): rail top, plate strip with the window ends ignored (round 3 basis), tie-slot zones cut (x 1.029) | XY | 7.81 | 25.0 | 3.20 | 3.0 | OK |
| 2 | L1b deck bottom under the rail, same case (tension) | XY | 5.12 | 25.0 | 4.88 | 3.0 | OK |
| 3 | L1c window corners (sharp, Kt 2.5): rail fixed at the window ends, P L/8 = 124 N*mm, on the rail with its 6.0 mm deck strip (the tie slots run past both corners) | XY | 6.63 | 25.0 | 3.77 | 3.0 | OK |
| 4 | L1d deck outboard of the rail at mid-window, hand 20 N (5 mm fingertip), worst position \|y\| 25.9: plate moment under the load (rail top 3.19 MPa) | XY | 4.49 | 25.0 | 5.56 | 3.0 | OK |
| 5 | L1e rail beside the tie slots, hand 20 N anywhere from 8 mm before a slot zone to its end (worst: press at x 54.7): slot zones cut, end ledges as lower-bound springs | XY | 3.43 | 25.0 | 7.28 | 3.0 | OK |
| 6 | L2 deck at a cable-slot edge, hand 20 N (5 mm fingertip): free edge, slot ends (10.2 apart) simply supported | XY | 6.63 | 25.0 | 3.77 | 3.0 | OK |
| 7 | L2b slot-to-wall ligament (10.85 mm to the wall face): hand 20 N at a tie slot's outer edge, free edge, slot ends (6.1 apart) simply supported | XY | 4.76 | 25.0 | 5.25 | 3.0 | OK |
| 8 | L3 deck at the breadboard centre, hand 20 N (one-way, b_eff span/2) | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 9 | L4 end-ledge bearing, 20 N on the ESP32 | XY | 0.14 | 25.0 | 178.20 | 3.0 | OK |
| 10 | L4b deck between the far ledge and the cable slots, ESP32 press (10 N on the far ledge): one-way slab, b_eff span/2 net of the window and slots | XY | 7.38 | 25.0 | 3.39 | 3.0 | OK |
| 11 | L4c same press, deck band through the far tie slots (Kt 2.5 at the square slot ends) | XY | 4.19 | 25.0 | 5.97 | 3.0 | OK |
| 12 | L5 window end face bearing, USB 10 N (2 header strips 2.5 x 2.5) | XY | 0.80 | 25.0 | 31.25 | 3.0 | OK |
| 13 | L6 side rail root, sideways jumper pull 10 N over 26 mm (Z, Kt 2.5 sharp root) | Z | 1.18 | 12.5 | 10.60 | 3.0 | OK |
| 14 | L7a tie-slot ligament (6.0 mm, window edge to slot, deck only) shear-out, strap pull 2 x 44 N | XY shear | 2.46 | 12.5 | 5.08 | 3.0 | OK |
| 15 | L7b far-end bridge (x 62.7-66.0: rail on the 6.0 mm strip) bent in-plane by the 30-pin tie's 2 x 44 N, fixed ends, Kt 2.5 at the sharp corners | XY | 3.52 | 25.0 | 7.09 | 3.0 | OK |
| 16 | L7c bridge twisted by the strap's wrap (16.3 N*mm, 8.4 at one end): long faces | XY shear | 0.29 | 12.5 | 42.88 | 3.0 | OK |
| 17 | L7c' same, short faces (shear along the layers) | Z shear | 0.28 | 6.2 | 22.04 | 3.0 | OK |
| 18 | L7d strap bearing on a tie slot's inner wall (1.34 x 44 N on 2.5 x 3) | XY | 7.94 | 25.0 | 3.15 | 3.0 | OK |
| 19 | L8 tie bar, wire bundle pulled 10 N at mid-span (fixed ends, Kt 1.5 r2.0 corners) | XY | 4.55 | 25.0 | 5.49 | 3.0 | OK |
| 20 | L9 screw-head bearing, rover lifted by the lid (3.2 N per M3 x 8) | XY | 0.23 | 25.0 | 106.65 | 3.0 | OK |
| 21 | L10 screw-hole push-through (plug shear, Z), lifted by the lid | Z shear | 0.06 | 6.2 | 101.77 | 3.0 | OK |
| 22 | L11 deck round the toggle bushing, flick 65 N*mm (nut Ø10 boss in a plate, Kt 2 at the hole), cyclic | XY | 2.76 | 25.0 | 9.06 | 4.0 | OK |
| 23 | L12 deck under its own and the electronics' inertia, 5 cm (73 g x 20 g) | XY | 0.52 | 25.0 | 48.28 | 3.0 | OK |
| 24 | L12b same, at the tie slots' inner edge (\|y\| 20.85), net of the 6.1 mm slot in a span/2 band, Kt 2.5 | XY | 1.03 | 25.0 | 24.27 | 3.0 | OK |
| 25 | L13 end ledge to deck, ESP32 inertia 2.0 N, 5 cm (Z shear) | Z shear | 0.01 | 6.2 | 454.13 | 3.0 | OK |
| 26 | L14 screw-head bearing, deck inertia 5 cm (3.6 N per screw) | XY | 0.26 | 25.0 | 95.46 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, proof loads, the tie's own strength, assembly):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| L1 round 3's basis on the round-4 rails, no tie slots (for comparison) | XY | 7.59 | 25.0 | 3.29 | 3.0 | OK |
| L1 with the tie-slot zones cut only beside the open window (x 1.011) | XY | 7.68 | 25.0 | 3.26 | 3.0 | OK |
| L1 with rigid window ends (strip simply supported across x 16.4 and 66.0): upper bound of the end help | XY | 4.60 | 25.0 | 5.43 | 3.0 | OK |
| L1 with the end ledges as lower-bound springs (12.4 N/mm) and the slot zones cut, mid-window | XY | 4.05 | 25.0 | 6.17 | 3.0 | OK |
| L1e with no credit for the far ledge (infinite strip, slot zones cut): press at x 62.4 | XY | 8.30 | 25.0 | 3.01 | 3.0 | OK |
| L1 with a point load on the rail (no fingertip spread), tie-slot zones cut | XY | 8.12 | 25.0 | 3.08 | 3.0 | OK |
| L4b with the strip behind the slots alone (no help from the deck in front of the slots) | XY | 9.03 | 25.0 | 2.77 | 3.0 | no |
| L2 with 2 mm contact (a fingernail or a tool edge, not a hand press) | XY | 9.81 | 25.0 | 2.55 | 3.0 | no |
| proof (§8 test 1a) 40 N on the rail at mid-window (5 mm contact): rail top | XY | 15.63 | 25.0 | 1.60 | 1.0 | OK |
| proof (§8 test 1b) 40 N at the breadboard centre | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |
| proof (§8 test 2) 20 N sideways on the seated ESP32: rail root | Z | 2.36 | 12.5 | 5.30 | 1.0 | OK |
| L7a at the tie's rated strength (it must break first) tie-slot ligament (6.0 mm, window edge to slot, deck only) shear-out, strap pull 2 x 80 N | XY shear | 4.44 | 12.5 | 2.81 | 1.0 | OK |
| L7b at the tie's rated strength (it must break first) far-end bridge (x 62.7-66.0: rail on the 6.0 mm strip) bent in-plane by the 30-pin tie's 2 x 80 N, fixed ends, Kt 2.5 at the sharp corners | XY | 6.36 | 25.0 | 3.93 | 1.0 | OK |
| L7d at the tie's rated strength (it must break first) strap bearing on a tie slot's inner wall (1.34 x 80 N on 2.5 x 3) | XY | 14.33 | 25.0 | 1.74 | 1.0 | OK |
| proof (§8 test 6, proposed) 30 N push from below beside one tie: strap 56 N, slot inner wall bearing | XY | 10.02 | 25.0 | 2.50 | 1.0 | OK |
| assembly: M3 x 8 lid screw, no washer at 0.15 N*m (P 250 N), bearing on the deck | XY | 18.41 | 25.0 | 1.36 | 3.0 | no |
| assembly: M3 x 8 lid screw, no washer at 0.5 N*m (P 833 N), bearing on the deck | XY | 61.37 | 25.0 | 0.41 | 3.0 | no |
| assembly: M3 x 8 with an ISO 7089 washer at 0.5 N*m (P 833 N), bearing on the deck | XY | 29.44 | 25.0 | 0.85 | 3.0 | no |
| assembly: toggle M6 nut at 0.6 N*m (P 500 N) on the deck (54 mm²) | XY | 9.19 | 25.0 | 2.72 | 3.0 | no |

- **Lowest SF:** 3.15 (required 3.0), at L7d: the strap bearing on a tie slot's inner wall. Next is L1, the rail at mid-window, at 3.20.
- **Drop rows:** they hold their SF up to a 40.5 cm drop, limited by L12b (the deck at the tie slots' inner edge).
- **Verdict rows:** 0 of 26 are below their required SF.

## Proof tests

**Spec §8 tests 1–5 still match** the NEEDS_TEST verdict. Placeholder SFs at the test loads:
- **test 1a**, 4 kg on the rail top at mid-window: 1.60, with the tie-slot factor included;
- **test 1b**, 4 kg at the breadboard centre: 1.88;
- **test 2**, the sideways push: 5.30.

**Two changes to make in spec §8.** None of tests 1–5 loads the round-4 tie slots, and the strap is now the lowest row.

1. **Add test 6 after test 5:**
   > 6. **Strap.** Before fitting the jumpers, tie the bare ESP32 into its seat. Holding the lid, push the board up out of its seat from below, through the window between the pin rows, next to one tie, with **3 kg (≈ 30 N, 1.5 × service)** for 10 s. Repeat next to the other tie.

   That puts about 56 N into the strap. The slot wall is then at SF 2.50 on the placeholder, and the tie stays below its 80 N rating.
2. **Change the first pass bullet to:**
   > no crack or whitening at the window corners, rails, ledges, tie slots, screw holes, toggle hole or tie bar;

**Optional, spec §4.** In the "Jumpers pushed on from below" row, the force could read "20 (about 44 N in the tie: the strap is nearly flat)". The tests don't depend on it.

## Notes

- **ESP32 ties.** Pull them snug by hand. Don't use pliers or a tie gun.
  - **Why:** the slot's inner wall (L7d) reaches SF 3 at 46.5 N of strap tension, and a snug hand pull plus the 20 N push already gives 44 N.
  - **The tie fails first:** even at its own 80 N rating, everything round the slot stays above SF 1 (lowest 1.74).
- **Lid screws (round 3 advice, unchanged).** Tighten until the head just seats (about 0.1 N·m). At 0.5 N·m the head crushes the deck, even with a washer (SF 0.41 without one, 0.85 with).
- **Toggle nuts (unchanged).** Run them up finger-tight plus about a quarter turn (≤ 0.3 N·m). At 0.6 N·m the M6 nut is at SF 2.72 on the deck.
- **Advisory rows below 3, unchanged from round 3:**
  - a firm fingernail or tool at a cable-slot edge (2.55);
  - the strip behind the cable slots if the deck in front of them didn't help (2.77).
- **ESP32 above the rails.** The ESP32 module and its USB still stand 3.5 mm proud of the rails. An upside-down landing would hit the board first. That is not a design case at 5 cm the right way up.
- **Margin hidden in L1.** The verdict basis gives the window ends no stiffness. Crediting only the end ledges, at a lower bound, nearly halves the mid-window rail moment (SF 6.17). The true L1 margin is therefore much larger than 3.20, and test 1a will show it.
