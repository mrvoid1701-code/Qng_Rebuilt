# QNG-GPU-017 Interpretation — Hopfion Q=1 vs Ring Q=0 disorder L-scan

**Date:** 2026-04-18
**Verdict:** FAIL
**Test:** `tests/gpu/qng_hopfion_disorder_l_scan_gpu.py`
**Pre-registration:** `07_validation/prereg/QNG-GPU-017.md`

## Headline result

The hypothesis that Hopfion Q=1 topology gives faster IR decay of the phi
Goldstone halo than a vortex ring Q=0 (Faddeev-Niemi analog, savant
recommendation 2026-04-18) is **falsified**.

- **Ring control (q_twist=0):** power-law exponent alpha ≈ 2.39 at L=80,
  matches GPU-012 baseline 2.37 within 0.025 (Gate 1 PASS). L-scan 2.53,
  2.46, 2.39, 2.35 — slight decrease with L (consistent with halo reaching
  further at larger L).
- **Hopfion (q_twist=1):** alpha ≈ 1.89 at L=80. L-scan 1.77, 1.88, 1.89,
  1.89 — stabilizes by L=60 (Gate 3 PASS, spread 0.007 over L=60..100).
  Power-law fit R²=0.997; exponential fit R²=0.973 — power-law WINS
  (no mass gap).
- **Hopfion halo is SLOWER, not faster.** The extra toroidal winding
  (linking number 1) creates MORE phi disorder at large radius, not less.
  Topology does not cure the IR halo; it makes it worse.

## Physical interpretation

### Why topology doesn't help

The Faddeev-Niemi r^{-4} prediction assumes a Skyrme-stabilized Hopfion
in a non-linear sigma model with an additional fourth-order derivative
term. In QNG v5+Channel H, there is no Skyrme term and no non-linear
sigma constraint on phi — phi lives on (-π, π] with unbounded magnitude
modulo 2π. The Hopfion initial condition `phi = poloidal + q·toroidal`
adds a second Goldstone winding; in the linearized massless theory this
creates a second dipole-like contribution to dis(r) that falls more
slowly than the single winding.

Empirically: at L=100 the Hopfion dis(r) has exponent 1.89 ~ 2 (near
the linearized Goldstone 2D dipole value), while the ring has 2.39 ~ 2.5
(nearer the 3D dipole value). Both are **universal Goldstone behaviors**,
differing only by how much of the winding is "toroidal" vs "poloidal".

### Confirms einstein-mind diagnosis

Einstein-mind (2026-04-18) predicted:

> "You are weighing a soap film and calling it a proton. Give the
> substrate a vacuum to break, and you will have given it mass."

Root cause: sigma_m has no intrinsic mass scale in v5+Channel H. The
phi field is a massless Goldstone of a global U(1) symmetry. **No
topological dressing of phi can supply a length scale to sigma_m.**
The fix must come from the sigma_m sector itself — a potential V(σ_m)
that breaks the σ-shift symmetry and supplies a healing length.

### Refutes savant-physics-reviewer recommendation

Savant recommended Hopfion pivot over Option B (add V(σ_m)) on the
grounds that (a) the Faddeev-Niemi r^{-4} decay would localize the
object and (b) V(σ_m) would introduce a free parameter. GPU-017 shows
(a) is false in QNG's linearized substrate; therefore (b) must be
solved — dynamically-generated λ rather than imposed — but there is
no way around it via topology alone.

## Coincidence alert: xi ≈ λ_screen

The exponential fit reports xi_hopfion(L=80) = 8.59 lu, suspiciously
close to `λ_screen = sqrt(β/α) = 8.37 lu`. However, the exponential
R²=0.973 is *lower* than power-law R²=0.997 — the fit is worse. The
apparent coincidence is because over the fit domain `r ∈ [R+5, L/2-3]`
the exponential and a shallow power-law `r^{-1.9}` can mimic each other
reasonably. This is NOT evidence of a mass gap; it is the generic
degeneracy of log-log vs semilog fits over a finite range. Do not
interpret xi ≈ λ_screen as "Hopfion mass is the screening length".

## Gate-by-gate record

| Gate | Measured | Threshold | Result |
|------|----------|-----------|--------|
| G1 control (ring α L=80 vs 2.37) | 0.025 | < 0.20 | **PASS** |
| G2 Hopfion α at L=80 | 1.890 | ≥ 3.0 (PASS) / < 2.5 (FAIL) | **FAIL** |
| G3 L-independence of Hopfion α | 0.007 | < 0.25 | **PASS** |
| G4 exp vs power-law | ΔR² = -0.025 | exp wins if > +0.05 | power-law OK (no gap) |

G1 and G3 confirm the measurement is valid. G2 and G4 conclusively reject
the Hopfion pivot.

## Consequences

1. **Option C (different mass carrier via topology) falsified** at the
   structural level. Further Hopfion mass-scan tests are not warranted;
   the IR halo problem would reappear with the same pathology.
2. **Option B (new substrate term V(σ_m)) is FORCED** as the only
   remaining path to rescue the baryon identification program (if it is
   to be rescued at all).
3. **Einstein-mind recommendation** (2026-04-18): add a Ginzburg-Landau
   potential V(σ_m) = λ(σ_m² - σ_ref²)². This supplies a healing length
   ξ ~ 1/√λ independent of R, surface tension on the ring cross-section,
   and a true mass of the form `M = volume·bag + perimeter·tension`.
4. **Prerequisite before GPU-018**: theoretical derivation constraining
   λ from QNG principles (NOT imposed as a free parameter). Candidate
   approaches:
   - Derive λ from the DER-QNG-034 stability criterion (K_BACK·δ <
     α + χ_decay·(1-α)) extended to sigma_m.
   - Derive λ from the DER-QNG-037 G-reconciliation (consistency with
     β_g, α_g, k_gm relations).
   - Derive λ from chi-condensate back-reaction if ⟨χ⟩≠0 in ground state.

Any of these three routes would give a dynamically-generated mass scale.
Until ONE is worked out theoretically, no further GPU time is warranted
on the ring=baryon identification program.

## Additional note on Hopfion stability

Does the Q=1 Hopfion initial condition remain Q=1 after Phase 2? This
was not directly measured in GPU-017 (only dis(r) was recorded). The
stable L-independent alpha=1.89 across L ∈ {60, 80, 100} suggests the
configuration does reach a stable state (whatever its topology); it
does not confirm Q=1 topology is preserved. A Hopf-invariant
measurement (computed via linking number of preimage curves) would
settle this, but is not necessary for the IR halo question answered
here.

## Reproducibility

- Deterministic dynamics (no Xi noise in v5 + Channel H).
- Parameters frozen in `07_validation/prereg/QNG-GPU-017.md`.
- Raw data: `report.json`, `run.log`.
- Run time: ~7 minutes on GPU device 0 (L_max=100, N=1M sites).
