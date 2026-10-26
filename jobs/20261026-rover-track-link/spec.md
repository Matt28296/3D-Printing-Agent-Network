# Part spec: Track link (×68, 34 per side, + 2 spares)

Job: 20261026-rover-track-link · Written by: Architect · Date: 2026-10-26 (round 3) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with Ø2 steel pins. The pin runs free in the centre knuckle (Ø2.3 printed, a 0.3 sliding fit) and is gripped by the outer knuckles (Ø2.0 printed), so it can't walk out. The centre notch takes a sprocket tooth; grousers on the outer face.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 16 × 24 × 7.5 mm. Pin holes at x 0 (Ø2.5 CAD, running) and x 10 (Ø2.2 CAD, grip), teardrops pointing at the grouser face.
- Fasteners used: 1 pin per link: a Ø2 × 24 mm steel dowel pin (ISO 8734 / ISO 2338, m6, Ø2.002–2.008), or 2 mm steel rod cut to 23.5 mm and deburred. Pressed into the outer knuckles, flush (a 24 mm pin may stand up to 0.25 mm proud each side, which still clears the wheel flanges).

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket |
| Centre-knuckle hole | Ø2.3 printed (Ø2.5 CAD) | +0.1/−0 | sliding fit on the Ø2 pin (0.3 clearance; fdm-design-rules §3: 0.3–0.4) |
| Outer-knuckle holes | Ø2.0 printed (Ø2.2 CAD) | +0.05/−0.05 | grip fit on the Ø2 pin |
| Knuckle wall round the running hole | 1.75 | min | four 0.45 mm extrusion lines at 0.41 spacing (1.68) |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge |

## 4. Loads
Design loads, as re-derived by strength round 2 (see the strength.md files):
- **Rover mass:** 649 g.
- **Motor stall:** 160 N·mm, 9.9 N of pull.
- **Track:** tight run 14.9 N at stall, 8.2 N everyday; pretension 5 N sustained.
- **Drop:** 5 cm onto a hard floor gives 15.9 N per axle flat and 31.8 N per axle on a corner, with a road wheel landing on a hinge.
- **Pin pressing:** an assembly hoop strain of 1–2.5 % across the layers in the outer knuckles (not in the verdict; covered by proof test 1).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track pull | 14.9 stall, 8.2 everyday, 5 sustained | pin bending/shear, knuckle bearing and tear-out | as stated | hours |
| Drop (5 cm) | 15.9 flat / 31.8 corner per axle, wheel on a hinge | pin bending, knuckle bearing | short-term | seconds |
| Side drag | 3 | knuckle end face | cyclic | hours |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 68 + 2 spares (two plates of 34, plus 2 on either plate)
- Max acceptable print time per batch (h): 7

## 8. Acceptance criteria (measurable)
- [ ] Pinned links flex freely to 40° both ways
- [ ] 34 links close into a loop round sprocket and idler, with the idler in its slot
- [ ] **Proof tests** (strength round 2), on a 5-link test chain from the first plate, before printing the rest:
  1. **Pressing.** Press all 10 pins of the chain. Pass: no crack or white line at any outer knuckle, especially along the layer line through the pin, and each pin flush and firm. If knuckles crack, set `PIN_GRIP_CLR` 0 → +0.05 and retain each pin with a drop of CA at both ends instead.
  2. **Tension.** Hang **4.5 kg (44 N, 3 × the 14.9 N stall tension)** from the chain for 1 min. Pass: no cracked knuckle, the pins haven't moved, the chain flexes freely to 40° both ways.
  3. **Hinge crush.** Lay the chain grousers-down on a hard surface. Press a road wheel on its bolt across a pinned joint with **5 kg (49 N, 1.5 × the 31.8 N corner load per axle)** for 1 min. Pass: no cracking, pin straight, the joint still flexes freely.

## 9. Notes and open questions
None open. Shared frames and clearances: see the assembly plan and `assembly_check.json`.
