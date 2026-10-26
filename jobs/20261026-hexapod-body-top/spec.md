# Part spec: Hexapod top plate / electronics deck

Job: 20261026-hexapod-body-top · Written by: Architect · Date: 2026-10-26 (round 3: §1–4 and §8 updated by design-lead after strength round 1 and the deep review) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
3 mm deck (130 × 104 mm) on the four columns. It carries the ESP32 seat (pins down through a window), two PCA9685 servo drivers on M2.5 posts, the MP1584 buck and the main switch. The UBEC is not on the deck: it stands on its side on the bottom plate, beside the LiPo. Each leg's leads come over the deck edge through that leg's lead notch, and two cable slots per side take leads that come up inside the body.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 130 × 104 × 8 mm.
  - Columns: 4 × Ø3.6 CAD holes at **(±36, ±25)** (`hex_frame.COLUMNS`).
  - ESP32 seat: 55.6 × 29.7 CAD, ledges 2 above the deck.
  - PCA9685: 8 posts Ø5.5 × 5 with Ø2.4 CAD pilots on a 56 × 19 pattern at y ±34.5.
  - Cable slots 8 × 16 at (±50, ±22).
  - **6 lead notches** 10 × 5 (r1.5 inner corners) at x −40, 0, 40 in both long edges, each with a 3.2 × 1.8 tie slot beside it (deep review SYS-4).
  - **Ø12.2 CAD switch hole** at (−50, 0), for a 12 mm-bushing toggle rated ≥ 10 A DC (deep review SYS-10, 02-H4).
- Fasteners used: 4 × M3 × 8 self-tapping into the columns; 8 × M2.5 × 6 self-tapping for the PCA9685 boards; 1 zip tie for the ESP32; small zip ties at the lead notches

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Column screw holes | Ø3.4 printed at (±36, ±25) | ±0.2 | M3 clearance, on the bottom plate's columns |
| PCA9685 post pattern | 56 × 19 | ±0.2 | board holes |
| ESP32 pocket width | 29.5 printed (29.7 CAD) | +0.3/−0 | 0.6 clearance on a 28.3 board |
| Switch hole | Ø12.0 printed | +0.3/−0 | 12 mm bushing |

## 4. Loads
Load cases as strength round 1 re-derived them (`strength.md`); the earlier 0.6 kg was low (deep review SYS-2).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Handling: robot lifted by the top plate (× 2) | the robot below the deck (579 g at 683 g; ≈ 760 g at round 3's 877 g) × 2, through 4 screws; lifted by both long edges or by one end | deck at the column line and through the cable slots, screw pull-out | short-term (SF 3) | seconds |
| USB plug | 10 along x | header strips on the window end | short-term (SF 3) | seconds |
| Jumper pulled sideways | 10 | ESP32 seat side rail | short-term (SF 3) | seconds |
| Jumpers pushed on from below | 20 | zip-tie slot ligament | short-term (SF 3) | seconds |
| Servo lead pulled sideways / board unplugged | 10 / 15 | PCA9685 post roots / M2.5 pull-out | short-term (SF 3) | seconds |
| 20 cm drop | deck group at 17.2 g (6 feet) | deck between the columns, screw heads | short-term (SF 3) | impact |

Round-3 mass raises the handling case by up to 31 % (lowest strength SF 5.01 → ≈ 3.8; the deck is unchanged elsewhere). The new notches at x ±40 sit beside the cable slots (x 46–54), not in their section.

## 5. Environment
- Max temperature (°C): 40 (indoor floor; MG90S cases warm under load)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under constant servo-holding load); TPU only as optional foot socks

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 5

## 8. Acceptance criteria (measurable)
- [ ] Both PCA9685 boards sit on their posts; the deck comes off with them fitted (screw heads ≥ 1.75 mm from the boards)
- [ ] ESP32 seats with jumpers on every pin
- [ ] Each leg's three leads lie in that leg's notch and tie there
- [ ] **Proof test (strength round 3):**
  1. **Lift by both long edges:** lift the assembled robot by the top plate 5 times, holding both long edges.
  2. **Lift by one end:** lift it by the **rear (switch) end** of the deck only, so the robot hangs from that edge, and hold **1 min** with **0.8 kg** added to the bottom plate (for example a bag hung from the strap slots): 2 × the static load below the deck. Do this with the final body-bottom columns fitted.
  3. **USB:** plug and unplug USB 5 times.
  4. **Side push on the ESP32:** push the seated ESP32 sideways with **2 kg (≈ 20 N, 2 × the jumper-pull case)** at mid-length, for 10 s each way.

  Pass:
  - no cracks or whitening at the screw holes, the cable-slot corners, the lead notches, the PCA9685 post roots, or the seat rails and ledges;
  - the board stays on both ledges.

## 9. Notes and open questions
The switch hole fits a 12 mm-bushing toggle. If the electrical BOM names another switch, change `SWITCH_D` before printing. Shared frames: see the assembly plan.
