# QNG Matter Stability v1

Type: `derivation`
ID: `DER-QNG-025`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Show that the sigma channel alone is purely dissipative — it does not support stable
localized coherence deficits without external clamping or topological protection.
Identify the minimal additional structure needed for stable matter: winding number in
the phi channel (topological defects). Show this implies that matter and quantum phase
coherence in QNG are inseparable, and gives a structural constraint on a_M.

This document addresses Gap 4 (matter sector) at the level of identifying WHERE stable
matter can come from, without claiming to derive particle masses.

## Inputs

- [qng-native-update-law-v3.md](qng-native-update-law-v3.md)
- [qng-matter-sector-motivation-v1.md](qng-matter-sector-motivation-v1.md)
- [qng-rho0-constraint-v1.md](qng-rho0-constraint-v1.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)

---

## Section 1: The sigma channel is purely dissipative

The sigma update law (v3, no external source) is:
```
sigma_i(t+1) = sigma_i + alpha*(sigma_ref - sigma_i) + beta*(sigma_bar - sigma_i)
```

Defining delta_i = sigma_i - sigma_ref:
```
delta_i(t+1) = (1 - alpha)*delta_i + beta*(delta_bar - delta_i)
             = (1 - alpha - beta)*delta_i + beta*delta_bar
```

This is a linear, spatially coupled AR(1) process with a single fixed point: delta_i = 0
for all i (i.e., sigma_i = sigma_ref). The eigenvalue spectrum of the coupling matrix
lies in (-1, 1) for 0 < alpha < 1, 0 < beta < 1-alpha. Every initial perturbation
decays to zero.

**For a localized deficit** delta_i(0) = -A < 0 at one node, zero elsewhere: the
deficit diffuses outward (beta term) while decaying (alpha term). In the continuum limit:

```
dC/dt = -alpha * (C - C_ref) + D_diff * nabla^2 C
```

Solutions: delta_C(x,t) = -A * G(x,t) * exp(-alpha*t), where G is the 3D diffusion
Green's function. The deficit spreads and decays simultaneously.

**Decay rate:** At the origin, delta_C(0,t) ~ A * (4*pi*D_diff*t)^(-3/2) * exp(-alpha*t).
For alpha=0.005, after T=1000 steps: exp(-alpha*T) = exp(-5) ≈ 0.0067.
The deficit is effectively gone after ~200 steps (3 decay times = 3/alpha = 600 steps).

**Conclusion:** The sigma channel alone does not support stable matter. Any localized
coherence deficit dissipates on a timescale tau_decay = 1/alpha, regardless of how
localized or deep it is (in the linear regime).

---

## Section 2: The chi channel accumulates but does not stabilize

In v3, chi is slaved to sigma gradients:
```
chi_i(t+1) = chi_i * (1 - chi_decay) + chi_rel*(sigma_bar - sigma_i) + delta*(sigma_ref - sigma_i)
```

As sigma deficit forms, chi builds up. But chi does NOT feed back into sigma in v3.
The sigma channel is autonomous — it does not see chi.

In v4, chi→phi coupling exists (epsilon term), but phi does not feed back into sigma
either. The sigma channel remains autonomous and purely dissipative.

**To create matter from chi feedback, a hypothetical v5 update law would need:**
```
sigma_i(t+1) += gamma_chi * chi_i    [new term: chi feedback into sigma]
```

With this term, a stable equilibrium becomes possible: sigma deficit generates chi,
chi stabilizes sigma against further decay. This would be an internal source mechanism.

However, such a term would require physical motivation from first principles — it
represents a self-catalyzing coherence loop. It is not derived in the current framework.

---

## Section 3: Topological stabilization via phi winding numbers

The phi field is a circular variable: phi_i ∈ (-pi, pi], identifying phi ~ phi + 2pi.
In d >= 2 dimensions, the phi field can carry topological defects: regions where phi
is undefined (the vortex core) surrounded by a circulation that winds by 2pi.

**Vortex in 2D:**
A configuration with winding number n=1 has phi(r,theta) → theta as r → infinity.
The vortex core (r ≈ 0) is where phi is undefined — the update law forces sigma ≈ 0
in the core to accommodate the undefined phase.

```
Winding number W = (1/2pi) * loop_integral d_phi
```

W is a topological invariant: it cannot be changed by smooth evolution. The vortex
cannot annihilate unless it meets an anti-vortex (W=-1). Therefore:

- **Sigma deficit at core is permanent** — topology protects it
- **The sigma profile is Yukawa-like outside** — screened by substrate relaxation
- **M_eff integral is finite** — determined by vortex size and profile

This is structurally analogous to:
- Abrikosov vortices in type-II superconductors (quantized magnetic flux)
- BEC vortices (quantized circulation, persistent hole in density)

**In 2D QNG substrate:** stable matter = topologically protected sigma deficit at
the core of a phi vortex. The particle is not a point — it is the vortex core region.
The particle's "size" is the vortex core radius r_core (where sigma ≈ 0).

**Critical caveat for 3D:** Since phi ∈ S¹ (a scalar phase), the relevant homotopy
groups are π_1(S¹) = ℤ (stable vortex lines in 3D, not point defects) and
π_2(S¹) = 0 (NO topologically stable point defects of S¹ in 3D). This means:

- Vortex LINES threading 3D space are stable (π_1 = ℤ, supported by infinite or
  closed vortex strings)
- Vortex RINGS (closed vortex lines) are dynamically stable but NOT topologically
  protected — they can shrink and annihilate
- "Hedgehog monopoles" (phi pointing radially outward from a point) require a
  field valued in S², not S¹. These are NOT present in QNG with phi ∈ S¹.

Three resolution paths for 3D matter stability:
- (A) Vortex rings are dynamically stable on substrate timescales despite no
  topological protection — requires numerical confirmation (QNG-CPU-042)
- (B) Enrich phi to S² or SU(2)-valued field — would require ontological revision
- (C) Physical matter is quasi-2D at the substrate scale, with effective 2D topology

The current simulation program (QNG-CPU-041) tests 2D vortex stability first —
this establishes the baseline topological mechanism before addressing the 3D case.

---

## Section 4: What topological matter implies for a_M

For a phi vortex of core radius r_core (in substrate units), the sigma profile is:
```
sigma(r) ≈ 0                           for r < r_core   [depleted core]
sigma(r) ≈ sigma_ref + delta_C(r)      for r >> r_core  [screened exterior]

2D vortex: delta_C(r) ~ -A_vortex * K_0(r/lambda)      [2D Yukawa / K_0 Bessel]
3D case:   delta_C(r) ~ -A_vortex * exp(-r/lambda) / r  [3D Yukawa — applies to
                                                          3D vortex ring exterior]
```
Note: K_0(r/lambda) ~ sqrt(pi*lambda/(2r)) * exp(-r/lambda) for r >> lambda, so
both profiles are exponentially screened; the prefactor differs between 2D and 3D.

The matter proxy integral:
```
rho_0 * integral(M_eff dV) = rho_0 * a_M * integral( L_eff * (1-C_eff) dV )
```

In the generation-order limit (DER-QNG-014), chi_eff is slaved to delta_C:
```
chi_eff ≈ -(delta/alpha) * delta_C
```

So M_eff ≈ a_M * L_eff * (1 - C_eff) ≈ a_M * (delta/alpha) * (-delta_C) * (1 - sigma_ref)

For the Yukawa profile outside the core:
```
integral(M_eff dV) ≈ a_M * kappa * integral(|delta_C| dV)
                   ≈ a_M * kappa * A_vortex * 4*pi * lambda^2
```

where kappa = (delta/alpha) * (1 - sigma_ref) and the integral of |A*exp(-r/lambda)/r|
over all space = 4*pi*lambda^2 * A (standard Yukawa integral).

Setting this equal to m_particle/rho_0:
```
a_M * kappa * A_vortex * 4*pi*lambda^2 = m_particle / rho_0
```

This gives ONE constraint on a_M given:
- kappa (from substrate parameters, known)
- lambda (from substrate parameters, known)
- A_vortex (from vortex dynamics, to be computed)
- m_particle (observed, e.g., m_proton)
- rho_0 (from CODATA G constraint)

**Conclusion:** a_M is fixed once A_vortex is computed from a vortex simulation.
The coefficient a_M is not a free parameter of the substrate — it is determined by
matching the vortex sigma amplitude to the observed particle mass.

---

## Section 5: Discrete mass spectrum — topological structure

In 2D, the topological classification is sharp:
- π_1(S¹) = ℤ: vortices classified by integer winding number W ∈ ℤ
- W is conserved: it cannot change under smooth dynamics
- The mass spectrum is discrete: each winding sector W has a different core size
  and different A_vortex amplitude

Different winding numbers W give different core sizes and different A_vortex values:
```
A_vortex(W) = f_W * A_vortex(W=1)
```

If f_W is determined by the substrate dynamics, the mass ratios m(W)/m(W=1) are
predicted without free parameters. This would be a structural prediction of QNG.

**3D note — homotopy constraint (not resolved):**
For phi ∈ S¹ in 3D:
- π_1(S¹) = ℤ → stable vortex LINES (strings) threading 3D space
- π_2(S¹) = 0 → NO topologically stable point defects
- "Hedgehog monopoles" require an S²-valued field — not applicable here

The identification of discrete mass spectrum in 3D requires either:
- A vortex ring stability analysis (QNG-CPU-042, future)
- An enriched phi field (ontological revision, beyond current framework)

The 3D mass spectrum question is left open pending the 2D vortex confirmation
(QNG-CPU-041) and the 3D vortex ring stability test (QNG-CPU-042).

---

## Section 6: What remains open (honest assessment)

This section derives the STRUCTURE of the solution, not the solution itself.

**Derived:**
1. Sigma channel is purely dissipative — stable matter cannot come from sigma alone ✓
2. Chi feedback would require a new coupling term (v5) — not derived, not required yet ✓
3. Phi vortex topology can stabilize matter — structural mechanism identified ✓
4. a_M fixing condition: requires A_vortex from vortex simulation ✓

**Remaining open:**
1. Does the v3/v4 QNG substrate support stable phi vortex solutions in 2D?
   (QNG-CPU-041: 2D square lattice, vortex-antivortex pair, winding number persistence)
2. Are the stable vortices discrete (quantized) or do they diffuse continuously?
3. What determines A_vortex — is it fixed by alpha, beta, epsilon alone?
4. Do vortex RINGS in 3D have sufficient dynamic stability for matter purposes?
   (QNG-CPU-042, future: 3D ring initialized, check ring radius shrinkage rate)
5. π_2(S¹) = 0: point defects not topologically stable in 3D. Resolution requires
   either quasi-2D structure, ring stability, or enriched phi ∈ S² ontology.
6. Connection to Standard Model quantum numbers (baryon number, charge, spin) is not
   addressed here — this is a future program.

**What this document achieves:** Gap 4 status moves from "coefficients a_M, a_D, a_P
are free" to "a_M is determined by A_vortex, which requires a vortex simulation."
The path is identified. The destination (particle spectrum) is not yet reached.

---

## Numerical tests

**QNG-CPU-040** (complete): Sigma deficit stability test on 1D ring.
- Confirms sigma channel is purely dissipative (deficit decays as predicted)
- Decay rate matches exp(-alpha*t) envelope
- PASS confirms: stable matter requires topology beyond sigma channel

**QNG-CPU-041** (proposed): Phi vortex stability test on 2D grid.
- Initialize phi with winding number W=1 around center node
- Initialize sigma with deficit at core
- Run dynamics with v4 (epsilon > 0)
- Check: does winding number persist? Does sigma deficit at core survive?
- PASS would confirm: phi topology stabilizes matter in QNG

---

## Cross-references

- v3 update law: `DER-QNG-015` (`qng-native-update-law-v3.md`)
- v4 update law: `DER-QNG-016` (`qng-native-update-law-v4.md`)
- rho_0 constraint: `DER-QNG-021` (`qng-rho0-constraint-v1.md`)
- Matter motivation: `DER-QNG-022` (`qng-matter-sector-motivation-v1.md`)
- Test sigma stability: `QNG-CPU-040` (`07_validation/prereg/QNG-CPU-040.md`)
- Test phi vortex: `QNG-CPU-041` (proposed — not yet registered)
