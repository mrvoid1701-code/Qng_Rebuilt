# QNG-CPU-074 Conservative M_ring Scan
- decision: `pass`

## Purpose
Canonical M_ring values for mass identification (DER-QNG-036 §6).
CPU-051 dissipative values are deprecated; Phase-3 conservative values used here.

## Results
| R | M_dissipative (Phase 2 end) | M_conservative (Phase 3, T=1000) | Ratio |
|---|---------------------------|----------------------------------|-------|
| 3 | 331.8 | 331.8 | 1.000x |
| 4 | 509.7 | 509.7 | 1.000x |
| 5 | 810.1 | 810.1 | 1.000x |

## Checks
- Check 1 (all rings survive Phase 3): PASS
- Check 2 (M_cons > 50% of M_diss):   PASS
- Check 3 (M_cons monotone in R):      PASS

## Key findings

**Finding 1 — M_ring exactly conserved in Phase 3 (ratio 1.000x for all R):**
Channel B (diffusion) conserves sum(sigma_m) on the periodic lattice (Laplacian sums to zero).
M = N×sigma_m_ref - sum(sigma_m) is an exact conserved quantity under Phase 3 dynamics.
The Phase 3 protocol confirms conservation but adds no new value beyond Phase 2 end.

**Finding 2 — CPU-067 value confirmed (R=5, T_P2=1000 → M=954.88 ≈ 954.9).**

**Canonical M_ring at T_P2=1000 (CPU-067 protocol convention):**
| R | M_ring(T_P2=1000) |
|---|------------------|
| 3 | 474.15 |
| 4 | 728.92 |
| 5 | 954.88 |

These replace CPU-051's 158.4 (R=4) for mass identification (DER-QNG-036 §6).

**Finding 3 — M_ring still decaying at T_P2=1500. T_P2=1000 is the canonical snapshot.**
