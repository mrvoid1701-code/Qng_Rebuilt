# e_B Extended L-Scan (QNG-GPU-016)

Protocol: v5 + Channel H (Phase 1 and 2), K_GM=0.0
bp_min=0.0005  bp_ring=0.06
SM ratio Delta/N = 1.3130

## e_B ratios vs L

| L | eB_g(R4) | eB_g(R5) | r_g | eB_w(R4) | eB_w(R5) | r_w | eB_c(R4) | eB_c(R5) | r_c |
|---|---------|---------|-----|---------|---------|-----|---------|---------|----|
| 20 | 1.085e-01 | 4.695e-01 | 4.3278 | 3.411e-02 | 2.339e-01 | 6.8573 | 2.110e-02 | 1.316e-01 | 6.2400 |
| 40 | 5.476e-01 | 1.112e+00 | 2.0303 | 7.144e-02 | 3.491e-01 | 4.8861 | 3.859e-02 | 2.063e-01 | 5.3468 |
| 60 | 1.086e+00 | 1.657e+00 | 1.5258 | 7.803e-02 | 3.572e-01 | 4.5779 | 4.189e-02 | 2.093e-01 | 4.9965 |
| 80 | 1.778e+00 | 2.345e+00 | 1.3189 | 8.012e-02 | 3.576e-01 | 4.4637 | 4.319e-02 | 2.095e-01 | 4.8495 |
| 100 | 2.646e+00 | 3.213e+00 | 1.2145 | 8.021e-02 | 3.577e-01 | 4.4594 | 4.324e-02 | 2.095e-01 | 4.8440 |
| 120 | 3.695e+00 | 4.266e+00 | 1.1545 | 8.021e-02 | 3.577e-01 | 4.4593 | 4.324e-02 | 2.095e-01 | 4.8440 |

## Gates

- **Gate 1** (e_B global L-spread, L=80..120): 0.1644  threshold < 0.05  -> FAIL
- **Gate 2** (e_B windowed L-spread): 0.0043  threshold < 0.05  -> PASS
- **Gate 3** (SM match at L=120):
   - global:   ratio=1.1545  dev=12.07%
   - windowed: ratio=4.4593  dev=239.62%
   - core:     ratio=4.8440  (informational)
   -> FAIL
- **Gate 4** (fit competition):
   - Model A (a+b/L):  a=0.3555, AIC=-19.32
   - Model B (a+b*log L): a=8.9254, AIC=-6.80
   - Delta-AIC (B-A) = 12.52  (A preferred if > 4)
   - A asymptote > 1.28 required: a=0.3555
   -> FAIL
- **Gate 5** (geometric rejection): ratio(L=120)=1.1545 > 1.28  -> FAIL

## Verdict: **FAIL_GEOMETRIC**

e_B exhibits geometric drift (ratio < 1.28 or Model B preferred). Soliton rest-energy hypothesis falsified.
