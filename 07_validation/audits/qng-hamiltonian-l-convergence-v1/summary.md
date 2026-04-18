# Hamiltonian Energy L-Convergence (QNG-GPU-015)

Protocol: v5 dynamics + Channel H (Phase 1 and 2), K_GM=0.0
bp_min=0.0005  bp_ring=0.06
SM ratio Delta/N = 1.3130

## Results -- global and windowed energy ratios

| L | E_glob(R4) | E_glob(R5) | ratio_g | E_win(R4) | E_win(R5) | ratio_w | M_R4 | M_R5 | ratio_M |
|---|-----------|-----------|---------|-----------|-----------|---------|------|------|--------|
| 20 | -6.082e+01 | -1.143e+02 | 1.8800 | -7.706e+00 | -3.090e+01 | 4.0098 | 605.7 | 846.6 | 1.3978 |
| 30 | -1.018e+02 | -1.531e+02 | 1.5047 | -1.004e+01 | -2.642e+01 | 2.6317 | 1249.6 | 1542.2 | 1.2342 |
| 40 | -1.455e+02 | -1.957e+02 | 1.3447 | -1.255e+01 | -3.088e+01 | 2.4602 | 1978.6 | 2300.3 | 1.1626 |
| 60 | -2.636e+02 | -3.148e+02 | 1.1945 | -1.521e+01 | -3.513e+01 | 2.3093 | 3810.8 | 4174.0 | 1.0953 |
| 80 | -4.242e+02 | -4.778e+02 | 1.1265 | -1.643e+01 | -3.687e+01 | 2.2447 | 6195.3 | 6594.2 | 1.0644 |

## Gates

- **Gate 1** (E_global L-spread): 0.2182  threshold < 0.03  -> FAIL
- **Gate 2** (E_windowed L-spread): 0.2155  threshold < 0.03  -> FAIL
- **Gate 3** (SM match at L=80):
   - global:   ratio=1.1265  dev=14.20%  (gate < 5%)
   - windowed: ratio=2.2447  dev=70.96%  (gate < 5%)
   -> FAIL

## Per-component L-behaviour (informational, Gate 4)

Component ratio E_comp(R=5)/E_comp(R=4) at each L:

| comp | L=20 | L=30 | L=40 | L=60 | L=80 |
|---|---|---|---|---|---|
| e_A | 2.0725 | 1.6547 | 1.4632 | 1.2653 | 1.1715 |
| e_B | 4.3278 | 2.6505 | 2.0303 | 1.5258 | 1.3189 |
| e_chi_dec | 2.0853 | 1.6645 | 1.4720 | 1.2714 | 1.1757 |
| e_chi_rel | 4.5397 | 2.7621 | 2.1022 | 1.5638 | 1.3422 |
| e_delta | -2.0780 | -1.6589 | -1.4671 | -1.2681 | -1.1734 |
| e_phi | -1.1526 | -1.1288 | -1.1004 | -1.0641 | -1.0450 |
| e_dis | 1.1634 | 1.1158 | 1.0885 | 1.0576 | 1.0414 |

## Verdict: **FAIL**

Energy observable does not converge (G1 or G2 failed). Channel H insufficient for energy localization. Report shows which component dominates divergence.
