# Part spec: Rover lid / electronics deck

Job: 20261026-rover-lid · Written by: Architect · Date: 2026-10-26 (round 3; round 4 by design-lead: strength round 3's rail change) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
A 3 mm deck screwed to the chassis's four insert columns. It carries:
- **ESP32 DevKit:** pins down through a window, PCB on end ledges, held by zip ties over its pin-free ends.
- **Breadboard:** a 170-point mini breadboard with the TB6612FNG driver.
- **Power switch:** the MTS-102 toggle, lever up.
- **Cable slots:** two slots either side of a zip-tie bar.

The MP1584 buck hangs under the deck, stuck on with foam tape. Changed in round 3 (deep review 04: S-06, S-09, S-10, S-13):
- the screws go into heat-set inserts;
- the toggle moved here from the rear wall;
- the Ø10 cable hole became two slots with a tie bar between them;
- the buck's place is fixed under the deck.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions:
  - **Overall:** 154 × 76 × 7.1 mm. The deck underside sits on the chassis wall tops (world Z 48.68).
  - **Screw holes:** 4 × Ø3.4 printed (Ø3.6 CAD) at (−13, ±32.5) and (102, ±32.5), over the chassis's Ø10 columns. Each column carries an M3 heat-set insert.
  - **ESP32 seat:** 55.6 × 29.7, with ledges 2 mm above the deck. The USB end is at x 14 (rear). Side rails 4.5 wide (|y| 14.85–19.35, round 4) and 4.1 tall on the deck, x 13.4–69.0.
  - **Tie slots:** 6 × 3.2 × 1.8 at the board ends, 1.5 outside the rails (|y| 20.85–22.65).
  - **Breadboard area:** 47 × 35 from x 84.
  - **Cable slots:** two 10 × 10.5 slots at x 71–81, |y| 1.5–12, either side of a 3 mm tie bar.
  - **Toggle hole:** Ø6.2 printed (Ø6.4 CAD) at (0, −23).
  - **Buck:** under the deck at x 85–107, centred on y 0. It is 12 mm above the battery holder.
- Fasteners used:
  - 4 × M3 × 8 socket or pan head screws into the chassis inserts (M3 × 5.7 heat-set inserts, Ø4.0 holes 6.5 deep).
  - 2 small zip ties for the ESP32, ≤ 2.5 mm wide, across its USB end and its far end.
  - 1 zip tie ≤ 3.6 mm wide round the tie bar, for the wire bundle.
  - The MTS-102's own two M6 nuts, one each side of the deck.
  - Double-sided foam tape for the buck.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance |
| Side rails | 4.5 wide (`RAIL_W`) | ±0.2 | edge beams beside the window (strength round 3: 4.0 minimum) |
| Screw holes | Ø3.4 printed | +0.2/−0 | M3 clearance, on the insert columns |
| Toggle hole | Ø6.2 printed | +0.2/−0 | M6 × 0.75 bushing |
| Cable slots | 10 × 10.5 each | ±0.3 | 15–17 Dupont housings in two groups, each housing needs a 3.6 mm diagonal |

**Toggle bushing.** It must stand at least 6 mm above the switch body: 3 mm deck + a 2 mm nut + 1 mm. If yours is shorter, leave the inner nut off and run the body up against the deck underside; the outer nut then clamps the deck. The MTS-102's bushing length could not be confirmed from a datasheet.

Bought-part sizes are nominal (tools/hobby_parts.py: ESP32_DEVKIT_38/30, MINI_BREADBOARD, TB6612_CARRIER, MP1584_BUCK). Measure your boards before printing, and give Claude any difference over 0.3 mm.

## 4. Loads
Design loads, as re-derived by strength round 2 (see strength.md):
- **Rover mass:** 649 g. Lifting it by the lid puts 3.2 N on each screw head.
- **Drop:** 5 cm onto a hard floor. The deck and its electronics (64 g) see a 20 g peak, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Hand pressure on the deck | 20 at mid-span (beside the window; breadboard centre) | plate bending | short-term | seconds |
| USB plug / jumper pull | 10 along X at the ESP32 seat | window end face, ledges | short-term | seconds |
| Sideways jumper pull | 10 on the PCB edge | side-rail root (across layers) | short-term | seconds |
| Jumpers pushed on from below | 20 | zip-tie slot ligament | short-term | seconds |
| Lifted by the lid | 3.2 per screw | screw-head bearing, hole push-through | short-term | seconds |
| Toggle flick | about 5 at the lever tip | bushing nut on the deck | cyclic | life |
| Drop (5 cm) | 64 g × 20 g | deck, end ledges, screws | short-term | seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 5

## 8. Acceptance criteria (measurable)
- [ ] ESP32 (38- or 30-pin) seats on both ledges with jumpers on every pin
- [ ] The four M3 × 8 screws line up with the inserts and pull the lid down flat on the wall tops
- [ ] The toggle's outer nut is fully on its thread, and the lever clears the ESP32's USB plug
- [ ] **Proof tests** (strength rounds 2 and 3), with the lid screwed on:
  1. **Deck press.** Press **4 kg (≈ 40 N, 2 × service)** for 1 min at (a) **the rail top beside the ESP32 window, at mid-window (x ≈ 41)**, with the ESP32 removed, through a 10 mm rubber pad, then on the other rail, and (b) the centre of the breadboard area.
  2. **Sideways push.** Push the seated ESP32 sideways with **2 kg (≈ 20 N)** at mid-length, for 10 s each way.
  3. **USB.** Plug and unplug the USB cable 10 times.
  4. **Toggle.** Flick the toggle 20 times.
  5. **Lid refit.** Take the lid off and refit it 5 times: the 4 screws into the inserts.
  6. **Strap** (strength round 4). Before fitting the jumpers, tie the bare ESP32 into its seat, the ties pulled snug by hand only. Holding the lid, push the board up out of its seat from below, through the window between the pin rows, next to one tie, with **3 kg (≈ 30 N, 1.5 × service)** for 10 s. Repeat next to the other tie.
  - Pass:
    - no crack or whitening at the window corners, rails, ledges, tie slots, screw holes, toggle hole or tie bar;
    - no permanent set over 0.2 mm (straight-edge along each rail and across the deck);
    - the board stays on both ledges;
    - no insert turns or pulls up.

## 9. Notes and open questions
None open. Shared frames and clearances: see the assembly plan and `assembly_check.json`.
