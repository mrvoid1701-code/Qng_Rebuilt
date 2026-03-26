# DER-BRIDGE-033 — QM→GR 6-Channel Coupling Large-N Probe

**Status**: LOCKED (pre-registration)
**Depends on**: DER-BRIDGE-032 (CPU-050), DER-BRIDGE-029 (CPU-047)

---

## Motivation

CPU-050 confirmed the QM→GR 6-channel bridge is Tier-1 at N=16:
- 5/5 seeds improve (P1 PASS)
- sign(e_mis_ett) = −1 on 4/5 seeds (P3 PASS)
- mean e_mis = −0.175 (universal coupling at N=16)

CPU-047 established the **sparse-graph law** for the QM continuity sector:
- R²_multi-channel decreases monotonically with N: 0.586 → 0.405 → 0.269
- Cause: denser graphs (mean_deg 3.2→4.3→6.9) → more divergence cancellation
- phi channel disappears at N=32 (|α_phi| < 0.0004 universally)

**Open question**: Does the sparse-graph law also apply to the GR coupling?
Specifically:
1. Does the 6-channel improvement (Δratio_split) shrink with N?
2. Does the coupling amplitude |e_mis| decrease with N?
3. Does the coupling direction (sign of e_mis) remain stable across N?

---

## Theoretical claim

The mismatch divergence current div_J_mis is a **local operator** — it depends
only on node i's neighborhood. The GR tensor E_μν = Laplacian(h) is also local
in the linear approximation. Therefore, the coupling constant e_mis should be:

- **Amplitude**: N-dependent (weaker in denser graphs — sparse-graph law extends)
- **Direction**: N-independent (sign determined by physics, not topology density)
- **Improvement**: Persistent (OLS monotonicity + non-zero signal at any N)

**Hypothesis**: The sparse-graph law applies to both QM and GR sectors:
- GR coupling improvement Δratio shrinks with N
- |e_mis| decreases from N=8 to N=32
- But 6-channel remains better than 4-channel at all N (improvement doesn't reverse)

---

## Mathematical structure

For each (N, seed), define:
- Δratio(N,s) = ratio6_split(N,s) − ratio4_split(N,s)
- e_mis(N,s) = coefficient of div_J_mis in 6-ch E_tt fit
- sign_e_mis(N,s) = sign(e_mis(N,s))

N-scaling laws to test:
- mean_N(Δratio) as function of N
- mean_N(|e_mis|) as function of N
- consistency of sign_e_mis across N

---

## Predictions (pre-registered)

**P1 — Large-N improvement persists**:
    Δratio_split(N=32,s) < 0 on ≥ 4/5 seeds
    (6-channel still beats 4-channel at N=32)

**P2 — Coupling weakens with N (sparse-graph law)**:
    |e_mis_ett(N=32,s)| < |e_mis_ett(N=8,s)| on ≥ 3/5 seeds
    (consistent with QM sparse-graph law from CPU-047)

**P3 — Sign is N-stable**:
    sign(e_mis_ett) consistent across all 3 N values on ≥ 4/5 seeds
    (coupling direction is structural, not scale-dependent)

**P4 — Mean improvement shrinks with N**:
    mean_seeds(Δratio_split) at N=32 > mean_seeds(Δratio_split) at N=8
    (i.e., the absolute value of the mean improvement decreases;
    Δ is negative so: |mean Δ at N=32| < |mean Δ at N=8|)

Pass: ≥ 3/4 — Partial: 2/4 — Fail: ≤ 1/4

---

## Tier classification (post-test)

- P1 + P3 pass → Tier-1 large-N (coupling universal across N)
- P1 pass, P3 fail → Tier-1.5 (improvement persists but direction N-dependent)
- P1 fail → Tier-2 (coupling collapses at large N)

---

## Connection to open problems

This test is part of Problem 4 (exact QM recovery) and Problem 3 (exact GR recovery):
- Finding the N-scaling of the QM→GR coupling is necessary before taking the
  continuum limit (N→∞)
- If coupling weakens with N, the continuum theory needs a renormalized coupling
- If coupling direction is N-stable, the physical interpretation is robust
