---
id: AUDIT-QNG-V9A-001
type: audit
title: V9-A Berry-integral analysis — 14th ℏ program — MARGINAL (no topological ℏ)
version: v1
date: 2026-04-22
status: locked
scope: QNG-GPU-100 (R∈{3,4,5}, T_P2=5000 lu R1 protocol) + QNG-CPU-098 (Berry integrals)
---

# V9-A Berry-Integral Analysis — 2026-04-22

## Verdict: V9A-MARGINAL

**No topological ℏ emerges from the R1 orbital attractor.**
The 14th proposed mechanism for an intrinsic action scale inside v8
canonical is hereby closed as not-bearing, consistent with 13 prior
failures (DEC-QNG-006) and with the savant theorem-level argument
(Liouville + Noether: classical H cannot produce rigid action scale).

## Input: GPU-100 phase-space observables

| R | wall | ⟨M_ring⟩ | duty | H_drift | cycles |
|---|---|---|---|---|---|
| 3 | 42.1 min | +263.66 | 27.0% | 0.62% | 28 |
| 4 | 42.2 min | +309.45 | 38.5% | 0.20% | 27 |
| 5 | 42.4 min | +336.66 | 39.3% | 0.36% | 26 |

R=4 reproduces GPU-031f (⟨M⟩=309.45 exact) and R=5 reproduces GPU-031g
(⟨M⟩=336.66 exact) — corroborating the orbital attractor result and
the ladder-broken finding independently.

GPU-100 structural gates:
- G1 (all runs complete, H < 10%): **PASS**
- G2 (orbital attractor all R): **FAIL** — R=3 duty 27% below threshold
- G3 (snapshots written): **PASS**

## CPU-098 Berry-integral results

Four candidate loop integrals per orbital cycle, across R ∈ {3, 4, 5}:

| Candidate | R=3 mean ± std (CV) | R=4 mean ± std (CV) | R=5 mean ± std (CV) | Status |
|---|---|---|---|---|
| S1: `∮ P_M dM_ring` | +35.9 ± 23.4 (**0.651**) | +47.8 ± 17.8 (**0.372**) | +39.3 ± 12.9 (**0.327**) | **V9A-FAIL** |
| S2: `∫ Σπ_m dσ_m` | +680.9 ± 118.1 (**0.173**) | +757.3 ± 107.9 (**0.142**) | +771.3 ± 122.6 (**0.159**) | **V9A-MARGINAL** |
| S3: `∫ Σπ_φ dφ` | +668.5 ± 147.5 (**0.221**) | +657.5 ± 79.4 (**0.121**) | +650.1 ± 90.6 (**0.139**) | **V9A-FAIL** |
| S4: `∮ COM area` | ~1e-16 | ~1e-16 | ~1e-17 | **trivial** (COM pinned by periodic BC) |

## Analysis

### S1 — zero-mode action (FAIL)

P_M is the COM-conjugate mode of M_ring under R1. Within-R CV >33% at
every R. Means vary 35–48 (~35%). Not an adiabatic invariant.

### S2 — full σ_m sector action (MARGINAL)

Within-R CV 14–17% at all R. Means monotonically increase:
680.9 → 757.3 → 771.3 (ratio 1.13 from R=3 to R=5). Not integer-ratio.
Classical Hannay-Berry-type smooth R-dependence, as predicted by
savant's theorem.

### S3 — φ sector action (FAIL, but centroids near ⟨L⟩_universal)

R=3 CV = 22.1% triggers FAIL (>20% threshold). R=4 and R=5 have
CV 12–14% (marginal).

**Notable sub-finding**: the S3 centroids across R cluster near
**N·β_φ/2 = 660** (the XY ferromagnetic ground-state per NOTE-QNG-017):

| R | S3 mean | Deviation from 660 |
|---|---|---|
| 3 | 668.5 | +1.28% |
| 4 | 657.5 | −0.38% |
| 5 | 650.1 | −1.50% |

Monotonic decrease in R, spread ~2.8%. This is NOT a ℏ-quantization
but looks like a **new classical orbital-loop invariant** approximately
equal to the ⟨L⟩ time-averaged Lagrangian. Mechanism conjecture: for
a nearly-periodic Hamiltonian attractor, `∮ p dq ≈ 2 ⟨T⟩ · T_cycle`,
and `⟨L⟩ = 2⟨T⟩ − ⟨H⟩` is R-universal (NOTE-QNG-017). The two-pi-rotation
of φ pick up ≈ ⟨L⟩ action per cycle, independent of orbital period.

This sub-finding is **classical, not quantum** — to be followed up as
NOTE-QNG-017 §X addition if the conjecture survives a β_φ-scan
verification (test: at β_φ = 0.03, 0.06, 0.12, does S3 centroid scale
as N·β_φ/2?).

### S4 — COM action (trivial)

COM is pinned to the origin by 3D periodic BC and initial conditions;
the xy-plane loop area is at machine epsilon. No information.

## Verdict logic

Per CPU-098 prereg:
- V9A-PASS requires any candidate to reach within-R CV < 10% AND
  integer-theta_0 clustering with |err| < 5%
- No candidate achieves CV < 10% — S2 closest at 14–17%
- Overall verdict falls back to MARGINAL

## Decision flow

Per `project_v9_launch_2026_04_22.md` decision flow:

- V9A-PASS → topological ℏ → N/A
- V9A-MARGINAL / QUANTIZED_CONTINUOUS / FAIL → V9-C becomes the
  residual path; document as 14th failed ℏ program; lock v8 as
  classical substrate.

**V9A-MARGINAL triggers V9-C promotion**, because ℏ did NOT emerge
as a topological invariant of the orbital attractor. The MARGINAL
status reflects that the data is noisy-but-nonzero (classical smooth
dependence on R), not that a borderline quantum scale is present.

## Consequences

1. **Lock v8 as classical substrate.** v8 canonical Hamiltonian is the
   classical limit; ℏ does NOT emerge from any of the 14 programs
   tested inside v8 (13 prior via DEC-QNG-006, now 14 with V9-A).

2. **Promote V9-C (DER-QNG-052) to active residual path.** Weyl
   canonical quantization with external ℏ, Wallstrom-safe via
   Z-winding sector decomposition. Review issues in
   `qng-v8-comprehensive-audit-2026-04-22/DER-QNG-052-REVIEW.md`
   should be addressed before promoting to "locked".

3. **New classical invariant candidate.** The S3 centroid alignment
   with ⟨L⟩_universal = 660 across R is a standalone finding worth
   checking under β_φ scan (GPU-034 data) and β_φ ∈ {0.03, 0.12}
   new runs (GPU-042 queue). If confirmed, this extends NOTE-QNG-017
   from time-averaged ⟨L⟩ to loop-action ⟨S_φ⟩ invariant.

4. **DEC-QNG-007 pending** — decision record to formalize v8 classical
   lock + V9-C promotion.

## Artifacts

- Data: `07_validation/audits/qng-v9a-phase-space-v1/R{3,4,5}/`
- Analysis script: `tests/cpu/qng_v9a_berry_analysis.py`
- Per-R cycle details: `cycles_R{3,4,5}.json`
- Machine-readable summary: `report.json`
- Pre-check: `PRECHECK.md` (predictions confirmed)

## Closure

V9-A empirical branch closes with **V9A-MARGINAL**. ℏ is not
topological inside v8. V9-C analytic branch is the honest residual
path. 14th ℏ program documented.

Signed: autonomous assistant (main context)
Locked: 2026-04-22
