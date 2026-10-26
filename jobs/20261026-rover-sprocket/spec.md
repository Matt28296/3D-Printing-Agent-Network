# Part spec: Drive sprocket (×2)

Job: 20261026-rover-sprocket · Written by: Architect · Date: 2026-10-26 (round 3) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
10-tooth sprocket disc (pitch radius 16.18, 45° tooth-root chamfers), bolted with 4 × M3 to a Pololu #1996 aluminium hub. The hub clamps the N20's D-shaft with its own M3 set screw on the flat, so the torque path is metal from the shaft to the sprocket. The N20 (rolled 45°) sits in a nacelle that reaches into the track's wrap, so the hub is already at the disc and no printed tube or bore is needed: the shaft overhang from the gearbox face to the track plane is 11 mm (chassis round 4: 2 mm skin).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions:
  - Ø35.8 × 7 mm disc.
  - Its inner face seats on the hub's outer face at world |y| 51.5 (the hub spans 46.5–51.5, on an M3 thrust washer at 46.0–46.5 against the chassis skin).
  - 4 radial slots 3.6 wide (CAD) at 45° + k·90°, open from r 5.5 to 6.85: they take the hub's M3 holes on any circle in that range. The Pololu drawing prints an unlabelled 6.35 [0.25 in], read as the hole-circle radius; it is unconfirmed.
  - Ø3.6 CAD centre hole: the shaft end (world |y| 54 for a 10 mm shaft; at least 53.6) runs free in it, at least 2.1 mm deep.
- Fasteners used (per sprocket): 4 × M3 × 12 socket or button head screws, each under an M3 washer (ISO 7089) on the outer face, threaded 4.5 mm into the hub. The hub's own M3 set screw (in the hub's pack) goes on the shaft's D-flat with a drop of medium threadlocker. 1 × M3 washer (ISO 7089, 0.5 mm) on the shaft as the thrust washer.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch |
| Disc thickness | 7.0 (±3.5 about the track plane) | ±0.1 | sits in the 8 mm link notch |
| Hub slots | 3.4 wide printed (3.6 CAD), r 5.5–6.85 | +0.15/−0 | M3 clearance on any likely hole circle |
| Centre hole | Ø3.4 printed (Ø3.6 CAD) | +0.15/−0 | shaft end runs free |
| Tooth tip radius | 17.9 | ±0.15 | stays inside the link (outer face 18.4) |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, POLOLU_HUB_1996). The motor is an N20 (GA12) 6 V, 100 rpm (≈150:1), low- or medium-power winding (stall ≤ 0.7 A at 6 V), 9 mm gearbox, 3 mm D-shaft 10 mm long from the gearbox face (at least 9.6 mm). A 9 mm shaft is too short: its end reaches only 1.5 mm into the centre hole (strength round 4, H5). Measure your N20 (gearbox section 12 × 10, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat) and the hub's hole circle before printing, and give Claude any difference over 0.3 mm. Track pins: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred.

## 4. Loads
Design loads, as re-derived by strength round 2 (see the strength.md files):
- **Rover mass:** 649 g.
- **Motor stall:** 160 N·mm design value (182 N·mm at 100 % PWM on a fresh pack). That is 9.9 N of pull at the pitch radius.
- **Track:** tight run 14.9 N at stall, pretension 5 N per run.
- **Sprocket radial:** 19.9 N stall / 13.2 N cyclic / 10 N sustained.
- **Drop:** 5 cm onto a hard floor gives 15.9 N per axle flat and 31.8 N per axle on a corner (short-term).

**Tooth case corrected (strength round 2):** the engaged teeth together carry the tight-run tension minus the slack-run tension, 9.9 N, so the design case is 9.9 N on one tooth at the pitch radius. Round 2's 14.9 N on one tooth tip can't occur. A link riding up over a tooth on a slack track (9.9 N at the tip) is prevented by the idler's jack-screw stop.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Motor stall torque | 160 N·mm (182 fresh pack) | hub screws in shear (4 × M3 on r 6.35: 7.2 N each), bolt bearing in the disc | short-term | seconds |
| Tooth load | 9.9 at the pitch radius on one tooth | tooth-root bending (in-plane) | short-term | seconds |
| Radial load | 19.9 stall / 10 sustained; 31.8 at a 5 cm corner | disc → hub → N20 shaft, 11 mm from the gearbox face | as stated | hours / seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 2
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] The disc seats flat on the hub with all 4 screws through the slots; it runs true (no visible wobble)
- [ ] The hub's set screw bites the shaft flat; the hub turns 0.5 mm clear of the skin
- [ ] With the hub on its thrust washer against the skin, the shaft end stands at least 2.1 mm proud of the hub's outer face (calipers' depth rod), so it reaches at least 2.1 mm into the disc's centre hole (strength round 4, H5)
- [ ] **Proof tests** (strength round 3; measure each motor's stall torque first, **with the hub on and before the sprocket disc is fitted**, so a motor stronger than the specified N20 never drives the printed teeth; see the chassis spec §8):
  1. **Torque.** Hold the track still and stall the motor at **100 % PWM on a freshly charged pack for 1 s, 5 times** (about 182 N·mm, 1.14 × the design value and the most the specified N20 gives). Pass: no slip of the hub on the shaft or of the disc on the hub (pen marks); no cracked or sheared tooth; the sprocket still runs true.
  2. **Tooth.** Mount the sprocket on its hub on a spare N20, or on a 3 mm D shaft in a vice. Hang **2 kg (19.6 N, 2 × the 9.9 N stall pull)** for 1 min from one link seated on one horizontal tooth. Pass: no crack at the tooth root, no permanent set.

## 9. Notes and open questions
- The hub's hole circle is not stated in Pololu's text; the slots cover r 5.5–6.85. If your hub's holes fall outside that, tell Claude the measured circle.
- Shared frames and clearances: see the assembly plan and `assembly_check.json`.
