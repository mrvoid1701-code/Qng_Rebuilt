---
id: PRECHECK-CPU-098
type: note
title: V9-A Berry-integral pre-check on R=3 + R=4 (R=5 still running)
date: 2026-04-22
status: provisional (R=5 pending)
---

# V9-A Berry-Integral Pre-Check — 2026-04-22

GPU-100 R=3 and R=4 complete; R=5 in Phase 2. This pre-check ran
`qng_v9a_berry_analysis.analyze_R(R)` on the available data only, to
catch script bugs and see early within-R CV signals before committing
to the full verdict.

## Raw numbers

| R | n_cycles | S1 mean ± std (CV) | S2 mean ± std (CV) | S3 mean ± std (CV) | S4 mean |
|---|---|---|---|---|---|
| 3 | 28 | +35.9 ± 23.4 (**0.651**) | +680.9 ± 118.1 (**0.173**) | +668.5 ± 147.5 (**0.221**) | ~1e-17 (zero) |
| 4 | 27 | +47.8 ± 17.8 (**0.372**) | +757.3 ± 107.9 (**0.142**) | +657.5 ± 79.4 (**0.121**) | ~1e-17 (zero) |

## Within-R CV interpretation per CPU-098 thresholds

- `V9A-PASS`: within-R CV < 10% AND integer-theta clustering <5% error
- `V9A-MARGINAL`: 10% < CV < 20%
- `V9A-FAIL`: CV > 20%

| Candidate | R=3 CV | R=4 CV | Leading verdict (pre-R=5) |
|---|---|---|---|
| **S1** `∮ P_M dM_ring` | 0.651 | 0.372 | **V9A-FAIL** (both > 20%) |
| **S2** `∫ Σ π_m dσ_m` | 0.173 | 0.142 | **V9A-MARGINAL** (both in 10–20%) |
| **S3** `∫ Σ π_φ dφ` | 0.221 | 0.121 | **V9A-MARGINAL / borderline FAIL** (R=3 > 20%) |
| **S4** `∮ COM area` | ~ε | ~ε | **trivial zero** (COM pinned by periodic BC) |

## Notable observation: S3 centroids ≈ ⟨L⟩_universal = 660

S3(R=3) = 668.5 and S3(R=4) = 657.5 straddle **660.0** (= N·β_φ/2,
the XY ferromagnetic ground state from NOTE-QNG-017) within ±1.3%.
Even though within-R scatter is 12–22%, the centroids of both R cluster
near the same value.

This is interesting but ambiguous — it could mean:

- **A**: the φ-sector loop action per cycle equals the time-averaged
  Lagrangian ⟨L⟩·T_cycle/T_cycle = 660 by some virial identity on the
  periodic attractor → *classical emergent invariant*, not ℏ.
- **B**: accidental agreement at R ∈ {3, 4} driven by the ring not
  being topologically separate from the vacuum (rings = local patterns
  in XY ferromagnet ground state, so loop integral inherits ground-state
  energy scale).
- **C**: the apparent agreement is coincidence; R=5 will break it.

If R=5 S3 is also near 660 ± 2%, interpretation (A) becomes plausible
and this is a *new* classical invariant (emergent quantity), not ℏ.
If R=5 is far from 660, coincidence.

## Impact on overall V9-A verdict

None of S1, S2, S3 will reach the `V9A-PASS` gate (within-R CV < 10%).
The most likely overall verdicts, in order of decreasing probability:

1. **V9A-MARGINAL** (S2 and possibly S3 land in 10–20% band uniformly)
2. **V9A-QUANTIZED_CONTINUOUS** (if within-R tightens at R=5 and integer
   theta_0 doesn't fit, this is the savant-predicted Hannay-Berry
   classical analogue)
3. **V9A-FAIL** (if R=5 S3 CV > 20%)

**V9A-PASS (topological ℏ) is structurally ruled out** by the current
pre-check. The savant theorem-level argument (Liouville + Noether:
classical H cannot produce rigid action scale) is now empirically
consistent with the observation.

## Consequence for v9 decision flow

Per `project_v9_launch_2026_04_22.md` decision flow:

- V9A-FAIL or V9A-QUANTIZED_CONTINUOUS → V9-C becomes the residual
  path; document as 14th failed ℏ program; lock v8 as classical
  substrate underlying quantum mechanics.

V9-C (DER-QNG-052 Weyl + path integral) is already drafted. If the
full CPU-098 confirms the pre-check direction, the next action is:

1. Lock v8 classical (DEC-QNG-007 decision record)
2. Promote V9-C to active: `ℏ` enters as external canonical
   quantization, Wallstrom-safe via Z-winding sector sum
3. Document 14th failure with this audit as evidence

## Pending

Full CPU-098 verdict awaits R=5 (~40 min at 2026-04-22 14:12 local).

## Also notable: `⟨L⟩` identity candidate

The coincidence S3(R=3) ≈ S3(R=4) ≈ 660 ≈ N·β_φ/2 warrants a
standalone classical follow-up (independent of V9-A): **is
`∮ Σ π_φ dφ` per orbital period always equal to N·β_φ/2 (the XY
ground-state energy) on the R1 attractor?** If so, this is a new
conserved quantity of the orbital attractor — classical, not
quantum, but previously unsuspected. Consider this a research byproduct
worth checking at R=5 and at new β_φ values (reusing GPU-034 L-scan
data if available).
