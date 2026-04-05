# QNG Matter Sector Physical Motivation v1

Type: `derivation`
ID: `DER-QNG-022`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Address the physical motivation question raised by the geometry of the matter sector:
*Why should M_eff have a sigmoid form, and why should the argument be a combination of
L_eff and C_eff rather than some other substrate quantity?*

This document does not close the matter sector identification (Gap 3 is already closed
in the Newtonian limit by DER-QNG-013 + DER-QNG-015). It provides physical reasoning
for the functional form, identifies the minimum set of constraints M_eff must satisfy,
and shows those constraints are met by the sigmoid with the current argument.

## Inputs

- [qng-matter-sector-proxy-v1.md](qng-matter-sector-proxy-v1.md)
- [qng-matter-source-identification-v1.md](qng-matter-source-identification-v1.md)
- [qng-native-update-law-v3.md](qng-native-update-law-v3.md)
- [qng-primitives-v1.md](qng-primitives-v1.md)

---

## Section 1: Constraints M_eff must satisfy

From the Poisson equation requirements (DER-QNG-013, DER-QNG-018), M_eff must satisfy:

**C1 — Vacuum condition:** M_eff = 0 at the reference state (no matter, sigma = sigma_ref,
chi = 0, D = 0, P = 0). Required so that rho_eff = 0 in empty space.

**C2 — Sign consistency:** M_eff > 0 when matter is present. Matter depletes coherence
(sigma < sigma_ref) and increases chi tension. M_eff must track this.

**C3 — Boundedness:** M_eff must be bounded above and below to prevent the density
from diverging. Physical density is non-negative and finite.

**C4 — Linearity near vacuum:** For small perturbations, M_eff must be linear in the
substrate deviations (delta_chi, delta_sigma) so that the Poisson equation is linear
and the superposition principle holds.

**C5 — Monotone in depletion:** M_eff should increase as coherence decreases (more
matter = more depletion).

These five constraints are necessary conditions. They are not sufficient to fix the
functional form uniquely — many functions could satisfy all five.

---

## Section 2: Why the sigmoid satisfies all constraints

The current matter proxy (from DER-QNG-013 §2) is:
```
M_eff(i) = sigmoid(X_i) - 1/2
```
where:
```
X_i = a_M * L_eff(i) * (1 - C_eff(i)) + a_D * D_i + a_P * |sin(P_i)|
sigmoid(X) = 1 / (1 + exp(-X))
```

**C1:** At the reference state, L_eff = 0, C_eff = sigma_ref, D = 0, P = 0.
Therefore X = 0 and sigmoid(0) - 1/2 = 0. ✓

**C2:** When matter is present, chi > 0 (from generation order, DER-QNG-014) and
sigma < sigma_ref (coherence depleted). Therefore L_eff > 0 and (1 - C_eff) > (1 - sigma_ref).
The product L_eff * (1 - C_eff) > 0 makes X > 0, so sigmoid(X) > 1/2, giving M_eff > 0. ✓

**C3:** sigmoid(X) ∈ (0, 1), so M_eff = sigmoid(X) - 1/2 ∈ (-1/2, +1/2). Bounded. ✓

**C4:** Near vacuum (X ≈ 0): sigmoid(X) ≈ 1/2 + X/4 → M_eff ≈ X/4, which is
linear in X. And X is linear in L_eff and (1-C_eff), so M_eff is linear in small
substrate deviations near the reference state. ✓

**C5:** As coherence decreases, (1 - C_eff) increases, so X increases, so M_eff
increases monotonically (sigmoid is monotone increasing). ✓

The sigmoid is the unique differentiable, bounded, monotone function whose derivative
at X=0 is maximal (equals 1/4). This "maximal sensitivity near vacuum" property is
physically reasonable: the substrate should be most responsive to matter perturbations
precisely when it is closest to the reference state.

---

## Section 3: Physical motivation for the sigmoid — substrate binary statistics

The sigmoid arises naturally from a statistical mechanics argument on a two-state
substrate element.

**Premise:** Each QNG node can be modeled as a two-state system:
- State 0: coherent (energy = E_0 = 0, reference state)
- State 1: incoherent (energy = E_1 = X_i, driven by matter/tension)

If the node is in thermal/statistical equilibrium with its neighbors, the probability
of occupying the incoherent state follows the Fermi-Dirac distribution:
```
P(incoherent) = 1 / (1 + exp(-X_i / k_B T_eff))
```

For T_eff = 1 (substrate units), this is exactly sigmoid(X_i). The centered form
M_eff = sigmoid(X_i) - 1/2 is the excess incoherence beyond the vacuum baseline.

**This is not a thermodynamic claim about temperature** — it is a structural observation:
the sigmoid is the natural occupancy function for a two-state substrate element with
energy bias X_i. The same functional form arises in:
- Fermi-Dirac statistics (quantum gases)
- Ising model magnetization (mean-field)
- Logistic population dynamics (bounded growth)
- Neural network activation functions (McCulloch-Pitts)

In each case, the sigmoid encodes the same physical fact: a system with two competing
tendencies (order vs disorder, coherence vs incoherence) in the presence of an external
bias X_i naturally occupies states according to P(incoherent) = sigmoid(X_i).

---

## Section 4: Physical motivation for the argument X_i = a_M * L_eff * (1 - C_eff)

The argument X_i must represent the "energy bias toward incoherence" at node i.

**Why L_eff * (1 - C_eff)?**

L_eff is the chi-sector effective field — it represents local substrate tension or load.
In the generation-order limit, chi_i > 0 near matter (DER-QNG-014). A substrate node
under tension (L_eff > 0) is energetically biased toward incoherence.

(1 - C_eff) is the coherence deficit from the maximum value. A node that is already
depleted (sigma close to 0, far from sigma_ref) has little remaining coherence to lose;
its marginal susceptibility to further incoherence is high.

The product L_eff * (1 - C_eff) therefore represents:
```
X_i ~ (tension at node i) * (remaining susceptibility to incoherence)
```

This is structurally analogous to elastic strain energy density:
```
u_elastic ~ sigma_stress * epsilon_strain
          ~ L_eff * (1 - C_eff)
```

where the tension (chi / L_eff) plays the role of stress and the coherence deficit
(1 - sigma) plays the role of strain. The product stress × strain is the local elastic
energy density — the energy "stored" in the deformation.

**The history terms a_D * D_i + a_P * |sin(P_i)|:**

D_i (mismatch accumulator) captures the history of node mismatch — accumulated
departure from the local consensus. A node that has been mismatched repeatedly has
had persistent exposure to a disturbed environment.

P_i (phase coherence) captures the alignment of the node with its phase neighbors.
Phase incoherence (large |sin(P_i)|) indicates the node is dynamically disturbed.

Both terms contribute to the "incoherence bias" X_i, representing different timescales
(D_i: slow history; P_i: instantaneous phase). Together they make the matter proxy
responsive to both the instantaneous state and its history.

---

## Section 5: What remains open

The above motivation is necessary but not sufficient to fix the coefficients a_M, a_D, a_P.
These are currently free parameters of the matter sector.

**To fix the coefficients requires one of:**

1. **Matching to a specific particle:** For a proton at rest, the substrate equilibrium
   profile is unique (up to rho_0). The coefficients a_M, a_D, a_P determine how the
   proton's energy is distributed between the three terms in X_i. Matching to the observed
   proton mass-to-charge ratio (or proton-to-electron mass ratio) would fix their relative
   values.

2. **Variational principle:** Require that M_eff be the unique matter proxy that minimizes
   some substrate free energy under the constraint of reproducing the Poisson equation with
   the correct G_SI. This would fix a_M in terms of alpha, beta, delta.

3. **QM-facing constraint:** The phase sector (phi, P_i) is connected to quantum coherence.
   If the matter proxy must also reproduce the QM dephasing time T_2* (DER-QNG-017), the
   coefficient a_P is constrained by the ratio of gravitational to quantum effects.

**Current status:** The sigmoid form and the argument structure are physically motivated
and satisfy all five necessary constraints. The coefficients are free parameters, and the
matter sector is not closed beyond the Newtonian limit.

This document does not constitute a derivation of the matter sector from first principles.
It demonstrates that the chosen form is the minimum physically motivated choice consistent
with the existing substrate structure.

---

## Cross-references

- Matter proxy original: `DER-QNG-008` (`qng-matter-sector-proxy-v1.md`)
- Matter source ID: `DER-QNG-013` (`qng-matter-source-identification-v1.md`)
- Generation order: `DER-QNG-014` (`qng-generation-order-v1.md`)
- v3 update law: `DER-QNG-015` (`qng-native-update-law-v3.md`)
- rho_0 constraint: `DER-QNG-021` (`qng-rho0-constraint-v1.md`)
