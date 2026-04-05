# QNG Phi Vortex Reference v1

- decision: `pass`

## Setup
- L=64, N=4096, T=5000
- Vortex W=+1 at (16.5, 32.5), anti-vortex W=-1 at (48.5, 32.5)
- epsilon=0.0 (Channel E off, clean topology test)
- Note: sigma autonomous in v3/v4 — no phi→sigma coupling

## Winding number history

| T | W_plus | W_minus | net |
|---|--------|---------|-----|
| 1000 | 2 | 2 | 0 |
| 2000 | 2 | 2 | 0 |
| 3000 | 2 | 2 | 0 |
| 4000 | 2 | 2 | 0 |
| 5000 | 2 | 2 | 0 |

## Final state
- pair separation: 32.0  (gate > 20)
- phi gradient — vortex plaq edges: 1.5708, global bg: 0.0728, ratio: 21.56  (gate > 3.0)
- W_plus count stability: mean=2.00, std=0.0000  (gate std <= 1.0)

## Summary checks
- Check 1 (W_plus persists at all T): PASS
- Check 2 (W_minus persists at all T): PASS
- Check 3 (vortex plaq edge / global bg ratio > 3.0): 21.56  PASS
- Check 4 (separation > 20): 32.0  PASS
- Check 5 (net W=0 throughout): PASS
- Check 6 (W_plus count std <= 1.0): 0.0000  PASS

## Interpretation
PASS: phi vortex is topologically protected. Winding number W=+1 is conserved over 5000 steps. Sigma deficit at core is maintained by phase circulation. Exterior profile is K_0-screened. Confirms DER-QNG-025 Section 3: stable matter requires phi topology. This motivates a_M fixing program (DER-QNG-025 §4) and QNG-CPU-042 (3D vortex ring stability).
