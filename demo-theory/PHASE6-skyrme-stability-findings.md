# Phase 6 — the v13 baryon is a stable object (Derrick + Skyrme term)

Type: `note` / `evidence`
Status: `RUN COMPLETE 2026-06-01`
Probe: `demo-theory/tests/t_phase6_skyrme_stability.py`
Artifact: `07_validation/audits/demo-phase6-skyrme-stability-v1/`

---

## Result

Phase 5 showed v13's SU(2) field hosts a B=1 baryon *topologically*. Phase 6 shows
it **exists dynamically** — a stable, finite-size soliton — via Derrick's theorem.

| Quantity | Value | Meaning |
|---|---|---|
| `E₂` (σ-model, 2-deriv) | 253.5 (>0) | scales as λ under x→λx |
| `E₄` (Skyrme, 4-deriv) | 17.6 (>0) | scales as 1/λ |
| σ-model alone min | λ→0.20 (edge) | **COLLAPSE** to zero size |
| with Skyrme term min | λ*≈0.26–0.30 | **STABLE** finite size |
| `M_cl = 2√(E₂E₄)` | 133.4 (natural units) | classical baryon mass |

## Verdict: **V13_BARYON_STABLE**

> Derrick's theorem confirmed. The pure 2-derivative chiral soliton collapses
> (`E(λ)=λE₂` → minimized at λ→0). The 4-derivative **Skyrme term** gives
> `E(λ)=λE₂ + E₄/λ`, a stable minimum at `λ*=√(E₄/E₂)` with classical mass
> `M_cl=2√(E₂E₄)`. **The v13 baryon is not just a topological label — it is a
> genuine stable object with a definite size and (natural-unit) mass.**

## Why the Skyrme term is natural in QNG, not an add-on

The 4-derivative Skyrme term is the leading higher-derivative piece of any chiral
Lagrangian — and in QNG it is exactly the kind of term the **edge gauge couplings**
and higher-order node interactions generate. The substrate's discreteness and the
`V_couple`/edge structure supply higher-derivative terms automatically; the Skyrme
term is their continuum image. So the stabilizer is expected, not imposed.

## The baryon sector is now structurally complete (modulo scale)

Combining Phases 4d + 5 + 6, the v13 baryon has:
- **topology**: B=1 in π₃(SU(2)) (Phase 5);
- **existence/size**: stable at `λ*` via the Skyrme term (Phase 6);
- **mass scaling**: `M_cl=2√(E₂E₄)` classical + `J(J+1)/2I` rotational band (4d);
- **partners**: the pion triplet as the 3 SU(2) generators (Phase 5).

This is a complete *structural* baryon — everything except the **absolute MeV
scale**, which remains blocked by the unresolved ℏ and the Gap-13 unit bridge.

## Honest scope

- `E₂`, `E₄` computed for the fixed hedgehog profile (not variationally relaxed);
  `λ*` is the Derrick scaling minimum, the standard first-pass stability proof.
  A full variational profile `F(r)` would refine `M_cl` but not the conclusion.
- `M_cl=133.4` is in lattice/natural units; converting to MeV needs ℏ + Gap-13.
- Stability shown against **scale** collapse (Derrick). Stability against
  arbitrary deformations (full Hessian) is the standard next refinement.
