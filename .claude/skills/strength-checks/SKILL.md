---
name: strength-checks
description: "Hand-calculation method for 3D-printed FDM parts: load cases, stress formulas (bending, tension, bearing, net section, tear-out, buckling, deflection), direction-dependent allowables, safety factors, proof tests, and a strength_calc.py template. Use when checking whether a printed part survives its loads."
---

# Strength checks for printed parts

Printed parts are weaker across layers than along them, they creep under sustained load, and they soften with heat. Be conservative, and write down every assumption.

## Allowables, in priority order

1. A measured row in `library/materials.csv` for this material and spool (cite it). `z_strength_ratio` gives the across-layer strength as a fraction of in-plane.
2. A printed-specimen datasheet the user supplied: in-plane = 0.6 × TDS tensile; across layers = 0.3 × TDS tensile.
3. No data: use the placeholders below and state that they are placeholders. The best verdict you can give is then **NEEDS_TEST**.

**Placeholder values** (rough, conservative, room temperature, 0.4 mm nozzle). In-plane values are already knocked down; for across-layer stress use half the in-plane value.

| Material | In-plane allowable (MPa) | E (GPa) |
|---|---|---|
| PLA | 30 | 2.5 |
| PETG | 25 | 1.8 |
| ASA | 25 | 1.8 |
| PC | 35 | 2.0 |
| PA (dry) | 30 | 1.5 |

## Required safety factors (SF = allowable / stress)

- Short-term static load: **SF ≥ 3**
- Sustained load (creep) or cyclic load: **SF ≥ 4**
- Service temperature within 20 °C of the softening point: **FAIL**, whatever the SF.
- Failure would injure someone, or damage something expensive: also require a proof test.

## Formulas (SI-consistent: N, mm, MPa)

| Case | Formula |
|---|---|
| Rectangular section b × h, bending | I = b·h³/12, σ = M·(h/2)/I = 6M/(b·h²) |
| Round section d | I = π·d⁴/64, σ = 32M/(π·d³) |
| Cantilever, tip load F at length L | M_root = F·L, tip deflection δ = F·L³/(3·E·I) (E in MPa) |
| Direct tension or compression | σ = F/A |
| Shear (rectangle) | τ_max = 1.5·V/A |
| Bolt bearing in a plate of thickness t | σ_b = F/(d·t) |
| Net section across a hole (width w) | σ = F/((w − d)·t) |
| Shear tear-out, edge distance e (hole centre to edge) | τ = F/(2·(e − d/2)·t) |
| Slender column (Euler) | P_cr = π²·E·I/(K·L)², K = 1 pinned–pinned, 2 cantilever |

**Stress concentration factors, applied to σ:**
- sharp internal corner: Kt = 2.5
- fillet with r ≥ 0.25·h: Kt = 1.5
- hole in a plate: Kt = 3 on the net-section stress for brittle materials (PLA); use 2 for tough ones (PETG, PA, PC)

## Method

1. Build the load-case table: force, point of application, direction, duration (static / cyclic / sustained), temperature. Add a handling or assembly case.
2. Find the critical sections and the stress type at each one.
3. Map each stress to the build direction. Use the across-layer allowable wherever the stress pulls layers apart.
4. Compute in `jobs/<id>/strength_calc.py` (template below) and run it.
5. Write the verdict and, if needed, geometry changes that would pass, or a proof test.

## Proof test (when the verdict is NEEDS_TEST, or the stakes are high)

Specify the load (1.5 to 2 × service load), how to apply it (hanging weight, luggage scale), the hold time (≥ 1 min static), and the pass criterion: no cracking, no layer separation, deflection under X mm, no permanent set. The test goes into the spec's acceptance criteria.

## `strength_calc.py` template

```python
"""Strength check for jobs/<id>. Run: python3 jobs/<id>/strength_calc.py"""
ALLOW_INPLANE_MPA = 25.0   # source: placeholder PETG (no library data) -> verdict at best NEEDS_TEST
Z_RATIO = 0.5              # across-layer / in-plane; placeholder
SF_REQUIRED = 3.0          # short-term static

cases = []

def bending_rect(name, F_N, L_mm, b_mm, h_mm, across_layers, Kt=1.0):
    M = F_N * L_mm
    sigma = Kt * 6 * M / (b_mm * h_mm ** 2)
    allow = ALLOW_INPLANE_MPA * (Z_RATIO if across_layers else 1.0)
    cases.append((name, sigma, allow, allow / sigma))

# --- cases ---------------------------------------------------------------------
bending_rect("leg root, 50 N tip load", F_N=50, L_mm=36, b_mm=20, h_mm=4, across_layers=False, Kt=1.5)
# --------------------------------------------------------------------------------

worst = min(sf for *_, sf in cases)
for name, s, a, sf in cases:
    print(f"{name:40s} σ={s:7.2f} MPa  allow={a:6.2f} MPa  SF={sf:5.2f} {'OK' if sf >= SF_REQUIRED else 'FAIL'}")
print(f"lowest SF {worst:.2f} (required {SF_REQUIRED})")
```
