# Part spec: Brio 4K camera mount (optional)

Job: 20261026-arm-camera-mount · Written by: Architect · Date: 2026-10-26 (round 3: 2026-10-26, deep reviews 01 S5/S6 and 03 SYS-13, camera-mount DFM and strength round 1) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Holds a Logitech Brio 4K (clip removed) on top of the claw, lens pointing along the fingers and tilted 34° down, so the fingertips sit just above the middle of the picture (v +0.05 of the half-height at the 90° preset, +0.08 at 65°) and the whole grip zone at the tips clears the cover's chamfered front edge by 0.6°. The fingertips are ≈83 mm from the lens; the cover fills the bottom 37–42 % of the frame. The camera's own 1/4"-20 thread takes a knurled thumb screw from under the seat; a 5 mm rear lip with an r 2 root fillet stops it turning. The USB-C port on the camera's back takes a right-angle plug above the lip. Shares the cover's two top screws, so the claw works without it.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 40.3 × 32.4 mm side profile × 50 mm wide (print 40.3 × 32.4 × 50, standing on its −y end; claw frame G: x −26.3…14, y −28…22, z 51.5…83.9). Interfaces: pad x 0–14 on the cover's top wall (z 51.5–55); seat under the camera's bottom face (34°, thread at G (−8.5, 0, 68.4)); lip 6 tall, 5 thick, 0.3 behind the camera's back; 1/4" slot Ø7.05 CAD (6.85 printed), ±4 mm along the camera; 2 × Ø3.6 teardrop holes at (6.75, −23) and (6.75, 14); 0.3 mm chamfer on the −y (bed) end. The seat's front face stays at x ≤ 3.0, behind the M3 button heads (x 3.9–9.6), with room for a 2 mm hex key with the camera off.
- Fasteners used: 2 × M3 × 18 button heads (ISO 7380) through pad + top wall into the bulkhead's 14 mm pilots, 11.5 mm engaged (they replace the cover's 2 × M3 × 10); 1 × 1/4"-20 × 5/16" knurled thumb screw: 7.9 mm under the head, so 3.9 mm into the camera after the 4 mm seat (deep review 01 S6; or a 3/8" screw with a 1.5 mm washer under its head)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Seat angle | 34° nose-down | ±1° | aims the camera |
| 1/4" slot | Ø6.85 printed, ±4 along y | +0.3/−0 | clearance |
| Lip to camera back | 0.3 | ±0.2 | anti-rotation |
| Seat front face | x 3.0 | ±0.3 | clears the M3 button heads by 0.9 |

Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide), USB-C on its back (deep review 01 S5); measure the thread depth and the port's height on the back before printing.

## 4. Loads
The camera package (Brio 63 g, this mount ≈13 g, thumb screw 5 g) hangs ≈80 mm outboard of the claw's back face and moves with the arm (×3 for accelerations). The Brio's USB cable can tug the camera with ≈10 N, now through a right-angle plug on the camera's back.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Camera weight with arm accelerations | 0.67 N × 3 | seat cantilever from the pad, lip | cyclic | hours |
| USB cable tug | 10 N at the camera's back, any direction | thumb screw + lip, seat root, lip root fillet | short-term | seconds |
| Camera package's sideways moment (SYS-04) | ≈0.8 N, ≈30 mm over the cover's top wall | pad, 2 screws | sustained (every pose) | hours |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; MG90S cases warm under sustained grip)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] Camera sits flat on the seat against the lip
- [ ] Thumb screw reachable from below the seat with the mount fitted
- [ ] Both M3 button heads seat flat on the pad, and a 2 mm hex key reaches them with the camera off
- [ ] The right-angle USB-C plug goes into the camera's port above the lip
- [ ] **Proof test (claw strength round 2, 1.5 × the design loads):**
  1. Camera fitted, arm powered: run the arm through its fastest full-range sweep 10 times.
  2. Claw off the arm, wrist horn in a vice. Pull the USB cable at the plug with **15 N** (1.5 kg on a luggage scale, 1.5 × the 10 N tug), 10 s each: both ways along the lens axis, both ways along the camera's length, and both ways across them (up and down).
  3. Loop a cord round the camera 45 mm from its centre (6 mm in from one end). Pull **15 N** along the lens axis, forwards then backwards, 10 s each. Repeat at the other end. This is the twist from a port 45 mm off-centre.
  4. Push the camera's end face along its length with **20 N** (1.5 × the 13 N desk hit), 10 s each way.

  Pass:
  - no crack or whitening at the lip's root fillet, the seat's root or the slot's ends;
  - the camera hasn't turned on the thumb screw (pen line across the camera and the seat);
  - the screws are still tight.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.
