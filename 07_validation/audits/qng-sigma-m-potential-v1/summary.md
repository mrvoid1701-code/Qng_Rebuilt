# QNG-GPU-018 Summary

- **Test**: V(σ_m) = (λ/4)(σ_m² - σ_ref²)² added to v5+Channel H
- **Committed λ**: 0.19 (from DER-QNG-040 marginal-stability saturation)
- **Gates**: A (halo ≥3.5) | B (FWHM 4.52) | C (ratio [1.25,1.40]) | D (r_eff 0.10)
- **Result**: FAIL_H3_STRUCTURAL — A/B/C FAIL, D PASS

## One-line verdict

V(σ_m) cannot cure a phi Goldstone halo; λ=0.19 over-suppresses σ_m
depletion; mass ratio collapses toward 1.00 at large L.

## Numbers

| Gate | Predicted | Observed | Err |
|---|---|---|---|
| A: α(L=80,R=5) | ≥3.5 | 2.49 | FAIL |
| B: FWHM | 4.52 lu | 1.00 lu | -78% |
| C: ratio(L=120) | in [1.25,1.40] | 1.031 | FAIL |
| D: r_eff | 0.100 | 0.1055 | +5.5% (PASS) |

## Downstream impact

- DER-QNG-040 status → **falsified_structural**
- NOTE-QNG-016 updated: quintuple-FAIL documented
- project_mass_identification memory updated
- project_der040_v_sigma_m memory updated

## Next candidate

σ_m·(1-cos phi) Yukawa coupling (pion-analog, DER-QNG-041 pending
3-agent synthesis).
