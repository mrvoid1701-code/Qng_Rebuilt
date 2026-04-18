# QNG-GPU-016 Interpretation — e_B Extended L-Scan

**Date:** 2026-04-18
**Verdict:** FAIL_GEOMETRIC
**Test:** `tests/gpu/qng_e_b_l_scan_gpu.py`
**Pre-registration:** `07_validation/prereg/QNG-GPU-016.md`

## Headline result

The soliton rest-energy (Bogomolny / bag-model) hypothesis for QNG vortex-ring
mass, via the sigma-gradient sub-component `e_B = (beta/4)·sum_nb(Δσ_m)²`, is
**falsified**.

- **Global e_B ratio** (R=5/R=4) drifts monotonically from 4.33 (L=20) through
  1.319 (L=80) to **1.154 at L=120**, below the 1.28 geometric threshold and
  clearly heading toward the geometric asymptote a ≈ 0.36 (Model A best fit).
- Fit competition: **Model A (a+b/L) preferred over Model B (a+b·log L) by
  ΔAIC=12.5**. Model A asymptote `a = 0.356` (threshold was > 1.28 for PASS).
- Model A coefficient `b ≈ 77` — this `b/L` decay is the same IR pathology
  observed for M_ring (DER-QNG-038) and full Hamiltonian energy (GPU-015).

## What the test rules out

1. **SM baryon match for e_B_global is coincidental.** The value 1.319 at
   L=80 was passage through SM on the way to the geometric limit, not a
   plateau. Same story as the original M_ring 0.24% coincidence at L=20.
2. **Bogomolny identification fails numerically.** A Bogomolny-saturated
   soliton would have mass fixed by topology (winding Q); the R-dependence
   should come only from integrating around the ring (perimeter ~ R, ratio
   5/4 = 1.25). Observed asymptote 0.36 is below even that geometric bound —
   global e_B is dominated by halo contributions that vanish more strongly
   for small rings.
3. **The baryon resonance ladder (DER-QNG-038) lacks dynamical grounding.**
   No L-convergent QNG observable matches the SM baryon ratio. Absolute
   masses at L=20/T_P2=1000 remain a protocol convention, not a prediction.

## Partial structural finding (NOT a rescue)

Gate 2 **passed**: the windowed e_B (sphere of radius R+3 around ring center)
is L-converged to <0.5% spread across L=80,100,120. Core-tube e_B is
similarly converged (spread 0.006). Converged values:

- `e_B_windowed_R=4` = 0.0802, `e_B_windowed_R=5` = 0.3577, ratio **4.459**
- `e_B_core_R=4`     = 0.0432, `e_B_core_R=5`     = 0.2095, ratio **4.844**

**Interpretation:**

- The sigma-gradient IS localized at the ring tube — the local depletion
  profile stabilizes by L ≥ 60 and is independent of box size. This confirms
  the physical intuition of a localized soliton rest-energy.
- However, the R=5/R=4 ratio at the localized level is ~4.5–4.8, nowhere
  near SM 1.313 and also nowhere near the linear-in-R geometric limit 1.25.
- Power-law fit: `r_c ≈ (R5/R4)^n` gives `n ≈ 7` — a very strong
  R-dependence of core-energy density that does NOT correspond to any
  obvious topological or geometric invariant of a torus.
- `M_ring(R=5)/M_ring(R=4) ≈ 1.04` at L=120 (nearly equal total depletion),
  while e_B_core ratio is 4.84. This means R=5 has the same sigma
  deficit as R=4 but packs it into a sharper gradient — suggesting the
  ring cross-section sharpens with R, not a fixed-profile ansatz.

## Global-vs-windowed reconciliation

Why does global e_B drift while windowed converges?

- Windowed mask (sphere radius R+3) captures only the ring neighborhood.
- Global sum includes the entire box, which at larger L contains more
  low-amplitude Goldstone-halo gradient. For R=4 rings the Goldstone
  amplitude is slightly smaller per volume than for R=5 (smaller source),
  but the available volume grows faster than the R=5/R=4 ring asymmetry,
  so `e_B_global(R=4)` grows faster than `e_B_global(R=5)` with L, dragging
  the ratio down toward the geometric floor.
- The windowed mask is blind to this halo growth — that is precisely why
  it converges.

## Consequences

1. **DER-QNG-038 status unchanged**: baryon resonance ladder
   (R=4→N, R=5→Δ, etc.) remains a numerical coincidence at L=20/T_P2=1000
   protocol convention; no scale-converged dynamical mass ratio matches SM.
2. **Gap 4 (ρ₀ / mass identification)** stays OPEN. All three paths —
   M_ring, Hamiltonian energy (GPU-015), e_B sub-component (GPU-016) — have
   been falsified as SM-compatible mass observables.
3. **New open question**: what physical quantity has R=5/R=4 ratio ≈ 4.5 in
   v5+Channel H? Candidates: integrated |∇φ|² (phi winding density),
   cross-section sharpness R^3 scaling, or some product of Hopf-like
   topological invariants. This is speculative and unrelated to SM matching.
4. **Mass identification options remaining**:
   - **Option B** (previously listed): sigma_m confinement mechanism
     (current Channel H confines only phi). Would require a new channel
     analogous to H for sigma_m — no theoretical motivation yet.
   - **Option C** (previously listed): abandon fixed-R baryon identification;
     search for a different mass carrier (e.g. Hopfion Q=1, excited-state
     modes, two-ring composites).

## Gate-by-gate record

| Gate | Measured | Threshold | Result |
|------|----------|-----------|--------|
| G1: e_B global L-spread (L=80..120) | 0.1644 | < 0.05 | FAIL |
| G2: e_B windowed L-spread           | 0.0043 | < 0.05 | **PASS** (structural hint) |
| G3: SM match at L=120 (global/windowed) | 12.1% / 239.6% | < 3% | FAIL |
| G4: fit competition (Model A asymptote + ΔAIC) | a=0.356, ΔAIC=12.5 | a>1.28 & ΔAIC>4 | FAIL |
| G5: geometric rejection (ratio > 1.28) | 1.155 | > 1.28 | FAIL |

Four of five gates fail; the one pass (G2) is consistent with a locally
convergent observable but the converged value disagrees with SM. Verdict
FAIL_GEOMETRIC is decisive.

## Reproducibility

- Seed: deterministic (no Xi noise in v5 + Channel H).
- Parameters frozen before execution in `07_validation/prereg/QNG-GPU-016.md`.
- Raw data: `report.json`, `run.log`.
- Run time: ~10 minutes on GPU device 0 (L_max=120, N=1.728M sites).
