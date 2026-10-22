---
name: material-selection
description: "Choosing a filament for an open-frame Prusa MK3S/MK3S+: selection questions, temperature ranges, softening points, enclosure and nozzle needs, drying. Use when choosing or checking a material, or writing a preflight checklist."
---

# Material selection for an open-frame MK3S/MK3S+

Temperatures below are typical ranges. **The datasheet (TDS) of the actual spool wins**, and measured values in `library/materials.csv` win over both.

## Selection questions, in order

1. **Service temperature.** Keep the hottest the part will see at least 20 °C below the material's softening point. A dashboard, a car interior or a spot near a motor rules out PLA, and often PETG.
2. **Sustained load.** Loads held for days or more cause creep. Avoid PLA. Prefer PC, PA or ASA, or derate heavily.
3. **Outdoor / UV exposure.** Use ASA.
4. **Impact and toughness.** PETG, PC and PA are tough. PLA is brittle.
5. **Stiffness.** PLA and fibre-filled grades are stiffest. PETG and PA flex more.
6. **Chemicals, oils, fuel.** PA and PETG resist many oils. Check the TDS.
7. **Printability on this printer.** An open frame means large ASA, PC or PA parts warp and delaminate. If `config/printer.json` says no enclosure, limit those to small parts or warn the user.

## Materials

| Material | Nozzle °C | Bed °C | Softens around | Enclosure | Nozzle | Use it for | Watch out for |
|---|---|---|---|---|---|---|---|
| PLA | 205–220 | 55–60 | ~55 °C | No | Brass OK | Jigs, fixtures, fit checks, stiff parts at room temperature | Creep, heat, brittle failure |
| PETG | 230–250 | 80–90 | ~70 °C | No | Brass OK | **Default engineering material on an open MK3** | Bonds hard to smooth PEI (use glue as a release layer); strings; keep fan low for layer strength |
| ASA | 250–265 | 100–110 | ~95 °C | Recommended; required for large parts | Brass OK | Outdoor, UV, warm environments | Warping, fumes (ventilate), cracking between layers in drafts |
| PC / PC blend | 260–290 | 110–120 | ~110 °C+ | Strongly recommended | Brass OK | High strength and heat | Warping, needs drying, near the 300 °C limit |
| PA (nylon) | 250–290 | 90–110 | varies by grade | Recommended | Brass OK (unfilled) | Tough, wear-resistant, fatigue-resistant parts | Very hygroscopic: dry before and during printing; poor bed adhesion without glue or garolite |
| CF/GF-filled grades | per base polymer | per base polymer | higher than base | per base polymer | **Hardened nozzle required** | Stiffness, dimensional stability | Abrasive: destroys brass nozzles; hardened steel needs about +5 to 10 °C and lower max flow |
| TPU | 220–240 | 50–60 | n/a | No | Brass OK | Gaskets, bumpers, flexible parts | Print slowly; no retraction tuning shortcuts |

## Rules for agents

- Only choose a filled (CF/GF) material if `config/printer.json` lists a hardened nozzle.
- Only choose a material the user has on hand (`config/printer.json` `materials_on_hand`) unless the spec says buying is fine.
- If the spec's service temperature is within 20 °C of the material's softening point, the design fails the material check.
- Drying: PA, PC and PETG that has sat in open air should be dried before engineering prints. Put the drying step in `preflight.md`.
