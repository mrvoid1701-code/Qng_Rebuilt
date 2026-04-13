# QNG-CPU-073 Back-Reaction Test
- decision: `pass`

## Physics tested
DER-QNG-036 predicts back-reaction term (B):
  sigma_m_i += K_GM * (sigma_g_i - SIGMA_REF)  (matter falls into gravity wells)
This term is absent from current v7 (DER-QNG-033).
Test: ring centroid drifts toward static sigma_g depletion pin when (B) is active.

## Results
| Metric | Value |
|--------|-------|
| z_centroid initial       | 9.6170 |
| Drift original v7        | +0.1408 lu |
| Drift symmetric v7       | +1.1529 lu |
| Extra drift (back-rxn)   | +1.0121 lu |
| M_final original         | 120.0 |
| M_final symmetric        | 512.5 |

## Checks
- Check 1 drift_sym > 0.5 lu : PASS
- Check 2 extra_drift > 0.5 lu: PASS
- Check 3 rings alive         : PASS

## Additional findings

1. **Back-reaction confirmed:** The symmetric term produces 1.0 lu extra drift vs. original v7.
   The ring centroid moves from z=9.62 to z=8.46 (1.15 lu toward pin at z=3).

2. **Ring mass asymmetry:** M_final_symmetric (512.5) >> M_final_original (120.0).
   The back-reaction counteracts the natural sigma_m restoration near the gravity well,
   deepening and sustaining the ring depletion. The ring lives longer in the symmetric case.

3. **v7-original also drifts slightly (0.14 lu):** Small indirect drift via K_GM → sigma_g
   gradient → chi → sigma_g Laplacian bias. 7× smaller than back-reaction signal.

4. **Signal is monotone:** z_symmetric decreases continuously throughout Phase 2,
   confirming steady gravitational drift, not oscillation.
