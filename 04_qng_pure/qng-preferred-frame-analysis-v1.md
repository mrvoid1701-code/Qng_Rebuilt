# QNG Preferred Frame Analysis v1

Type: `note`
ID: `NOTE-QNG-013`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Address Einstein's question (2026-04-06 review): does the synchronous update
law define a physically preferred time foliation, and if so, does it survive
into the continuum limit? If yes, the theory predicts Lorentz violation —
which is experimentally constrained to parts in 10^23 or better.

This is not a minor issue. It is the question of whether QNG is consistent
with special relativity at all.

## Inputs

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026
- [qng-ceff-field-equation-v1.md](qng-ceff-field-equation-v1.md) — C_eff dynamics
- [qng-lorentzian-4d-resolution-v1.md](qng-lorentzian-4d-resolution-v1.md) — NOTE-QNG-012

---

## Step 1: The preferred foliation at the substrate level

The update law maps `(sigma_i(t), chi_i(t), phi_i(t))` → `(sigma_i(t+1), ...)`.
The index `t` is a discrete global counter. All nodes advance simultaneously.

This defines a preferred foliation:
```
F_t = {all nodes at substrate time t}
```

The leaves F_t are spacelike surfaces in any continuum embedding. The update
law distinguishes "before" and "after" for every node at every step. This is
a preferred notion of simultaneity — exactly what special relativity forbids
as a physical observable.

**Is this a problem?** Only if the foliation leaves an observable trace at
accessible energy scales. If it is sub-Planckian, it is unobservable in
practice. If it produces measurable asymmetry in propagation speeds or
cross-sections, it conflicts with experiment.

---

## Step 2: Does the foliation survive in the C_eff continuum limit?

The coarse-grained field equation for C_eff derived in DER-QNG-018 is:

```
∂_t C_eff = α(C_ref - C_eff) + β ∇² C_eff
```

This is a **parabolic PDE** — a diffusion equation with a preferred time
direction `∂_t`. It is not Lorentz-covariant. Under a Lorentz boost, `∂_t`
mixes with `∂_x`, and the equation changes form.

**The preferred foliation DOES survive into the continuum limit** at the
level of the C_eff equation. The coarse-grained theory is not Lorentz-covariant
by construction.

This is not an oversight. It is a structural feature:

1. QNG gravity in the Newtonian limit is instantaneous action-at-a-distance
   (screened Poisson equation, no retardation). This is consistent with
   Newtonian mechanics, which is non-relativistic.

2. For GR to emerge, the dynamical QNG theory must produce a wave equation
   for perturbations of C_eff — not just the static screened Poisson equation.
   That wave equation must propagate at c, not at beta (the diffusion speed).

3. The Lorentz symmetry of GR must emerge at the level of the effective metric
   dynamics, not at the substrate level. This is analogous to how phonons in
   a crystal have approximate Lorentz symmetry even though the crystal lattice
   breaks translation symmetry — the symmetry is emergent, not fundamental.

---

## Step 3: What is required for Lorentz-emergent QNG

For QNG to be consistent with special relativity, the following must hold:

**Condition L1 (Emergent Lorentz covariance):** The effective field equations
for perturbations of C_eff around the background must reduce to a Lorentz-
covariant wave equation in the limit `r >> a_lattice`, `t >> tau_lattice`.

Specifically, the linearized perturbation `δC_eff` must satisfy:
```
□ δC_eff = source
```
where `□ = ∂²_t/c² - ∇²` is the d'Alembertian with speed c.

Currently, the linearized equation is:
```
∂_t δC_eff ≈ -α δC_eff + β ∇² δC_eff
```
This is parabolic (diffusion), not hyperbolic (wave). The speed of propagation
is `v_prop ~ sqrt(β/τ_lattice)` per unit lattice spacing — not c by construction.

**Condition L2 (Planck-scale suppression):** If Lorentz covariance is only
approximate, the violation must be suppressed by at least (E/E_Planck)^n for
some n ≥ 1. Current LIV constraints from astrophysical photons and gravitational
waves require n ≥ 1 with suppression below E_Planck.

For QNG: if a_lattice ~ l_Planck = 1.6e-35 m and tau_lattice ~ t_Planck =
5.4e-44 s, then any Lorentz violation is suppressed by (E/E_Planck). At
accessible energies E << E_Planck, the violation is unobservable.

This is the Planck-scale safety argument. It is a plausibility argument,
not a derivation.

---

## Step 4: Current status

**What is established:**
- The substrate update law has a preferred foliation (by construction)
- The C_eff diffusion equation is parabolic, not hyperbolic

**What is NOT established:**
- That the substrate-level foliation is suppressed at observable scales
- That the C_eff dynamics produce a Lorentz-covariant wave equation in any limit
- That the effective metric `g_μν ~ C_eff` field equations are hyperbolic

**What is assumed:**
- a_lattice ~ l_Planck (the Planck-scale safety assumption)
- Lorentz symmetry is emergent from the coarse-grained dynamics

---

## Step 5: The C_eff diffusion vs. wave equation gap

The specific technical gap is: the current C_eff equation has first-order
time derivative `∂_t C_eff`. A Lorentz-covariant wave equation has second-order
`∂²_t C_eff`. To get a wave equation from the substrate, one needs:

Either (a) a second discrete time step in the update law (introducing `C_eff(t-1)`),
or (b) a chi-mediated back-reaction term that turns the dissipative equation
into a conservative one.

The chi field `chi_i` plays the role of a "momentum" conjugate to `sigma_i`
in some interpretations of the update law. If `∂_t sigma ∝ chi` and
`∂_t chi ∝ -σ source + β ∇² sigma`, then together they give a second-order
wave equation. This is the oscillator structure.

**This has not been derived from the v5 update law.** It is a candidate
mechanism. Checking whether channels A+B+D produce oscillatory dynamics
in the (sigma, chi) pair — and whether those oscillations have speed c —
is an open computation.

---

## Summary

| Claim | Status |
|-------|--------|
| Substrate has preferred foliation | TRUE by construction |
| Preferred foliation survives into C_eff equation | TRUE (parabolic PDE) |
| Lorentz covariance is emergent at observable scales | ASSUMED, not derived |
| Planck-scale suppression applies | ASSUMED (requires a_lattice ~ l_Planck) |
| C_eff dynamics produce wave equation in any limit | NOT SHOWN |
| (sigma, chi) pair gives oscillator/wave structure | CANDIDATE mechanism, unverified |

**The Lorentz question is OPEN.** The theory is consistent with Lorentz
invariance by assumption (Planck-scale substrate), but the emergence of
Lorentz covariance from the coarse-grained C_eff dynamics has not been
demonstrated. This is the most important structural gap in QNG for consistency
with known physics.

**What needs to be done:**
1. Derive the linearized dynamics of (delta_C, delta_chi) around the
   vacuum background and check whether they produce a wave equation.
2. If yes: identify the propagation speed and check c-consistency.
3. If no: identify the mechanism by which Lorentz symmetry emerges.

---

## Cross-references

- NOTE-QNG-012: qng-lorentzian-4d-resolution-v1.md (4D structure question)
- DER-QNG-018: C_eff field equation
- DER-QNG-026: v5 update law (Channel F)
- 04_qng_pure/qng-action-principle-candidate-v1.md — energy functional and
  whether (sigma, chi) pair gives oscillator structure
