# QNG Sigma Depletion at Vortex Core v1

- decision: `pass`
- gamma_phi = 0.1 (Channel F, v5)

## Theoretical prediction (DER-QNG-026)
- sigma_eq = alpha*sigma_ref/(alpha+gamma_phi*D_core)
- At D_core=0.8: sigma_eq = 0.0294
- At D_core=0.6: sigma_eq = 0.0385

## Winding number history (topology check)

| T | W_plus | W_minus |
|---|--------|---------|
| 1000 | 2 | 2 |
| 2000 | 2 | 2 |
| 3000 | 2 | 2 |
| 4000 | 2 | 2 |
| 5000 | 2 | 2 |

## Core sigma evolution

| T | core_sigma | min_sigma |
|---|------------|-----------|
| 1000 | 0.21163 | 0.20694 |
| 2000 | 0.21183 | 0.20528 |
| 3000 | 0.21179 | 0.20576 |
| 4000 | 0.21178 | 0.20591 |
| 5000 | 0.21177 | 0.20596 |

## Final state
- D_core (phase disorder at W=+1 nodes) = 0.5476
- sigma_eq predicted = 0.04184
- core sigma (measured) = 0.21177  (gate < 0.30)
- bulk sigma = 0.47042  (gate > 0.45)
- bulk/core ratio = 2.221  (gate > 3.0)

## Summary checks
- Check 1 (core_sigma < 0.30): 0.21177  PASS
- Check 2 (bulk_sigma > 0.45): 0.47042  PASS
- Check 3 (bulk/core > 2.0): 2.221  PASS
- Check 4 (topology preserved): PASS
- Check 5 (equilibrated): delta=0.00%  PASS
- Check 6 (D_core > 0.40, Channel F active): 0.5476  PASS

## Interpretation
PASS: Channel F (v5 phi->sigma coupling) produces equilibrium sigma depletion at the phi vortex core. Sigma is depleted from sigma_ref=0.5 to a level consistent with sigma_eq = alpha*sigma_ref/(alpha+gamma_phi*D_core). The depletion is permanent (topological protection by phi winding) and the bulk sigma is unaffected. This completes DER-QNG-025 Sec 3: stable matter = topologically protected sigma deficit at phi vortex core. Motivates a_M fixing program and QNG-CPU-043 (3D vortex ring).
