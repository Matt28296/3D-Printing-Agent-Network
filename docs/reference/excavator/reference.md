# Reference: AssemblyExample.FCStd

13 parts, 16 joints, 2066.3 cm³ of material (≈ 2623 g if printed solid in PETG; infill makes it less).
Grounded part: BasePin.
Too big for the MK3 bed at full size: Boom, Stick. Largest uniform scale at which every part fits: 61% (check pins and walls stay printable at that scale).

## Parts

| Part | Size as designed (mm) | Volume cm³ | Fits MK3 bed? | Best flat orientation (mm) | Round features Ø (mm) |
|---|---|---|---|---|---|
| BasePin | 20 × 20 × 100 | 31.4 | yes | 100 × 20 × 20 | 20 |
| Base | 88 × 119.5 × 106 | 241.3 | yes | 106 × 119.5 × 88 | 14, 20, 24, 31.2, 31.4, 50 |
| Boom | 60 × 364 × 319 | 1204.6 | **NO** | longest side 364 mm > 240 mm usable: split into at least 2 pieces joined mechanically (bolts, dowels or a lap joint), or scale the assembly | 14, 29, 70.8 |
| Stick | 30 × 388.4 × 109.8 | 333.9 | **NO** | longest side 388 mm > 240 mm usable: split into at least 2 pieces joined mechanically (bolts, dowels or a lap joint), or scale the assembly | 8, 14, 24, 26, 26.6 |
| Bucket | 103 × 107.7 × 124 | 58.3 | yes | 107.7 × 124 × 103 | 3, 8, 15, 20, 23 |
| BucketLink2 | 48 × 78 × 37.6 | 17.1 | yes | 48 × 78 × 37.6 | 8.2, 84, 116 |
| BucketLink1 | 30 × 31.4 × 61.5 | 12.3 | yes | 61.5 × 31.4 × 30 | 8, 16 |
| BoomCylinderOuter | 30 × 143 × 143 | 48.2 | yes | 143 × 143 × 30 | 12, 14, 20, 30 |
| BoomCylinderInner | 15 × 140.2 × 140.2 | 23.0 | yes | 140.2 × 140.2 × 15 | 12, 14, 24 |
| StickCylinderInner | 15 × 146.3 × 133.8 | 23.0 | yes | 133.8 × 146.3 × 15 | 12, 14, 24 |
| StickCylinderOuter | 30 × 148.8 × 136.9 | 48.2 | yes | 136.9 × 148.8 × 30 | 12, 14, 20, 30 |
| BucketCylinderInner | 15 × 182.7 × 39.9 | 9.0 | yes | 39.9 × 182.7 × 15 | 7, 10, 18 |
| BucketCylinderOuter | 15 × 179.4 × 45.6 | 16.0 | yes | 179.4 × 45.6 × 15 | 7, 8, 12, 20 |

## Joints (the interfaces a printed version must keep)

| Joint | Type | Part A (Ø mm) | Part B (Ø mm) | Note |
|---|---|---|---|---|
| Revolute | Revolute | BasePin (20.0) | Base (20.0) | both sides reference Ø20: modelled line-to-line (zero clearance). A printed pin/bore pair needs the measured sliding-fit clearance (≈0.3–0.4 mm on diameter by default) |
| Revolute001 | Revolute | Boom (29.0) | Base (14.0) | referenced circles differ (Ø29 vs Ø14); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Revolute002 | Revolute | BoomCylinderOuter (14.0) | Base (14.0) | both sides reference Ø14: modelled line-to-line (zero clearance). A printed pin/bore pair needs the measured sliding-fit clearance (≈0.3–0.4 mm on diameter by default) |
| Slider | Slider | BoomCylinderInner (12.0) | BoomCylinderOuter (20.0) | referenced circles differ (Ø12 vs Ø20); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Cylindrical | Cylindrical | BoomCylinderInner (14.0) | Boom (14.0) | both sides reference Ø14: modelled line-to-line (zero clearance). A printed pin/bore pair needs the measured sliding-fit clearance (≈0.3–0.4 mm on diameter by default) |
| Revolute003 | Revolute | StickCylinderOuter (20.0) | Boom (14.0) | referenced circles differ (Ø20 vs Ø14); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Slider001 | Slider | StickCylinderInner (12.0) | StickCylinderOuter (20.0) | referenced circles differ (Ø12 vs Ø20); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Revolute004 | Revolute | Stick (14.0) | Boom (14.0) | both sides reference Ø14: modelled line-to-line (zero clearance). A printed pin/bore pair needs the measured sliding-fit clearance (≈0.3–0.4 mm on diameter by default) |
| Cylindrical001 | Cylindrical | Stick (14.0) | StickCylinderInner (–) |  |
| Revolute005 | Revolute | BucketCylinderOuter (–) | Stick (8.0) |  |
| Slider002 | Slider | BucketCylinderInner (7.0) | BucketCylinderOuter (12.0) | referenced circles differ (Ø7 vs Ø12); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Revolute006 | Revolute | BucketLink2 (8.0) | Stick (–) |  |
| Revolute007 | Revolute | Bucket (8.0) | Stick (24.0) | referenced circles differ (Ø8 vs Ø24); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Revolute008 | Revolute | BucketLink1 (–) | Bucket (8.0) |  |
| Cylindrical002 | Cylindrical | BucketLink1 (8.0) | BucketLink2 (8.2) | referenced circles differ (Ø8 vs Ø8.2); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |
| Cylindrical003 | Cylindrical | BucketCylinderInner (18.0) | BucketLink2 (8.2) | referenced circles differ (Ø18 vs Ø8.2); one is probably a boss outline that only defines the axis. Measure the actual pin and bore in parts/ before setting clearances |

Diameters are the circular edge or face each joint references in FreeCAD. They define the joint axis and are usually, but not always, the pin or bore itself. A dash means a non-circular element.
