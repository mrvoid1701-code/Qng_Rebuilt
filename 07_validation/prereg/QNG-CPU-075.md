# QNG-CPU-075

Type: `prereg`
Status: `pass`
Author: `C.D Gabriel`
Date: `2026-04-13`
test_class: `mass_identification`

## Title

Extended M_ring scan — R=3,4,5,6,7 for baryon resonance ladder test

## Purpose

DER-QNG-038 establishes the candidate identification:
```
R = 4  →  Nucleon N (938.27 MeV)
R = 5  →  Delta Δ(1232 MeV)
```

With a_M = 1.373×10^-3 (m_u = m_proton convention), the theory predicts:

```
M_ring(R) = m_particle(R) / (a_M × m_proton)
```

If the baryon resonance ladder continues (N*, Δ*, ...):
```
N*(1440) Roper:        M_ring_predicted ≈ 1119 substrate units
Δ*(1600):              M_ring_predicted ≈ 1240 substrate units
```

This test measures M_ring for R=6 and R=7 using the same CPU-074 conservative
protocol (T_P2=1000 snapshot) and checks whether the predicted values are reproduced.

Additionally, R=3 is re-examined: with a_M fixed, the QNG-predicted mass is 611 MeV.
No SM particle is known at 611 MeV, but the scan establishes M_ring(R=3) cleanly
as a reference.

## Upstream

- DER-QNG-038: N/Δ identification, a_M = 1.373×10^-3
- QNG-CPU-074: PASS — conservative M_ring protocol confirmed for R=3,4,5
- QNG-CPU-067: PASS — Phase-3 conservation confirmed at R=5

## Predicted M_ring values (DER-QNG-038 §8)

```
M_ring(R) = m_particle / (a_M × m_proton)
           = m_particle / (1.373×10^-3 × 938.27 MeV)
           = m_particle / 1.2882 MeV
```

| R | Candidate particle | m_particle (MeV) | M_ring predicted |
|---|-------------------|-----------------|-----------------|
| 3 | unknown (611 MeV) | 611  | 474 (from CPU-074, not a prediction) |
| 4 | Nucleon N         | 938.27 | 728.9 (CPU-074 anchor) |
| 5 | Delta Δ(1232)     | 1232  | 954.9 (CPU-074 anchor) |
| 6 | N*(1440) Roper    | 1440  | 1118 |
| 7 | Δ*(1600)          | 1600  | 1242 |

Tolerances: ±30 substrate units (±3%) on each predicted M_ring value.

## Experimental design

Same protocol as CPU-074 for each R ∈ {3, 4, 5, 6, 7}:

  **Phase 1** (300 steps): dissipative v7, no Channel F, no Channel G.
  Purpose: phi vortex formation.

  **Phase 2** (1500 steps): dissipative v7-symmetric, Channel F active,
  CHI_DECAY=0.020. No Channel G (k_back=0 in Phase 2).
  Purpose: form stable sigma_m ring.

  **Snapshot at T_P2=1000**: record M_ring = sum_i max(0, sigma_m_ref - sigma_m_i).
  This is the canonical value per CPU-074 convention.

Note: L=20 box limits maximum ring radius. For R=6 and R=7, the ring fits comfortably
in L=20 (diameter 12 and 14 lattice units vs box size 20). Verify no boundary collision.

## Checks

**Check 1 — CPU-074 anchors reproduced:**
|M_ring(R=4, T_P2=1000) - 728.92| < 5 and
|M_ring(R=5, T_P2=1000) - 954.88| < 5
(Confirms protocol consistency across runs.)

**Check 2 — M_ring monotone in R:**
M_ring(R=3) < M_ring(R=4) < M_ring(R=5) < M_ring(R=6) < M_ring(R=7)

**Check 3 — N*(1440) Roper prediction:**
|M_ring(R=6) - 1118| < 60   (±5% gate, more conservative due to extrapolation)

**Check 4 — Δ*(1600) prediction:**
|M_ring(R=7) - 1242| < 75   (±6% gate)

## Decision rule

PASS if Check 1, Check 2, and at least one of Check 3 or Check 4 passes.

FAIL if Check 1 fails (protocol inconsistency) or Check 2 fails (non-monotone).

PARTIAL if Checks 1+2 pass but both Check 3 and Check 4 fail — M_ring continues
growing but not on the baryon resonance ladder.

## Artifact paths

- `07_validation/audits/qng-extended-mring-scan-v1/report.json`
- `07_validation/audits/qng-extended-mring-scan-v1/summary.md`
