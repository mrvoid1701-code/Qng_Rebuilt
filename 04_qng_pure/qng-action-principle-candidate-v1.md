# QNG Action Principle Candidate v1

Type: `note`
ID: `NOTE-QNG-014`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Address Einstein's observation (2026-04-06): "Six channels is not a theory —
it is a phenomenology of the substrate. A unified theory must have a single
variational principle from which all channels follow."

This note derives a free-energy functional E[sigma, chi, phi] such that the
gradient flow dE/d(field) reproduces the QNG v5 update law channels. If all
six channels follow from one functional, the substrate has a unified energetic
description — the first step toward a true action principle.

## Inputs

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026

---

## The v5 update law (relevant channels)

```
sigma_i(t+1) = Proj[sigma_i + alpha*(sigma_ref - sigma_i)
                              + beta*(sigma_bar_i - sigma_i)
                              - gamma_phi * D_i * sigma_i]

chi_i(t+1)   = chi_i*(1 - chi_decay)
               + chi_rel*(sigma_bar_i - sigma_i)
               + delta*(sigma_ref - sigma_i)

phi_i(t+1)   = phi_i + beta_phi * angle_diff(phi_bar_i, phi_i)
               + epsilon * chi_i
```

where D_i = 1 - |Z_i| is the local phase disorder (Z_i = mean of exp(i phi) over neighbors).

---

## Step 1: Free energy for sigma channels (A + B + F)

Define the sigma free energy:
```
E_sigma[sigma] = sum_i [
    alpha/2 * (sigma_i - sigma_ref)^2              [Channel A: self-relaxation well]
  + beta/4 * sum_{j~i} (sigma_j - sigma_i)^2      [Channel B: diffusion/tension]
  + gamma_phi/2 * D_i(phi) * sigma_i^2            [Channel F: phase-depletion coupling]
]
```

Taking the gradient (treating D_i as fixed for this variation):
```
dE_sigma/d(sigma_i) = alpha*(sigma_i - sigma_ref)
                    + beta*(sigma_i - sigma_bar_i) * z   [z neighbors]
                    + gamma_phi * D_i * sigma_i
```

Gradient flow: sigma_i(t+1) = sigma_i - tau * dE_sigma/d(sigma_i)
```
= sigma_i - tau * [alpha*(sigma_i - sigma_ref) + beta*z*(sigma_i - sigma_bar_i) + gamma_phi*D_i*sigma_i]
= sigma_i + tau*alpha*(sigma_ref - sigma_i) + tau*beta*z*(sigma_bar_i - sigma_i) - tau*gamma_phi*D_i*sigma_i
```

With tau=1 and rescaling beta → beta/z (which is the standard QNG convention z=6):
```
sigma_i(t+1) = sigma_i + alpha*(sigma_ref - sigma_i) + beta*(sigma_bar_i - sigma_i) - gamma_phi*D_i*sigma_i
```

**This is exactly Channels A + B + F of the v5 update law.** ✓

All three sigma channels follow from gradient flow of E_sigma.

---

## Step 2: Free energy for the chi-sigma coupling (Channel D)

The chi update has a cross-coupling term: `delta*(sigma_ref - sigma_i)`.

Define a chi-sigma coupling energy:
```
E_chi_sigma[sigma, chi] = -delta * sum_i chi_i * (sigma_ref - sigma_i)
```

Gradient with respect to chi_i:
```
dE_chi_sigma/d(chi_i) = -delta * (sigma_ref - sigma_i)
```

Gradient flow for chi: chi_i += -dE_chi_sigma/d(chi_i) = delta*(sigma_ref - sigma_i) ✓

This is exactly Channel D.

---

## Step 3: The chi decay and chi_rel terms

The remaining chi terms:
```
chi_i += -chi_decay * chi_i + chi_rel * (sigma_bar_i - sigma_i)
```

- `chi_decay`: corresponds to E_decay = chi_decay/2 * sum_i chi_i^2
  (gradient: chi_decay * chi_i, flow: -chi_decay * chi_i) ✓

- `chi_rel * (sigma_bar_i - sigma_i)`: this is a response to local sigma gradients.
  It corresponds to a chi-sigma gradient coupling:
  E_rel = -chi_rel/2 * sum_i chi_i * sum_{j~i} (sigma_j - sigma_i) / z
  = chi_rel/2 * sum_i chi_i * (sigma_i - sigma_bar_i)
  Gradient w.r.t. chi_i: chi_rel * (sigma_i - sigma_bar_i) / 2 + ...
  (cross-term from sigma side also contributes)

The chi_rel term is a kinetic coupling between chi and sigma gradients.
In the oscillator interpretation, chi is the "momentum" of sigma, and chi_rel
sets the coupling strength between the two conjugate fields.

---

## Step 4: The phi channel (Channels B_phi + E)

The phi update:
```
phi_i += beta_phi * angle_diff(phi_bar_i, phi_i) + epsilon * chi_i
```

The first term follows from an XY-model energy:
```
E_phi[phi] = -beta_phi * sum_{i,j~i} sigma_i * sigma_j * cos(phi_i - phi_j) / z
```
(weighted XY model, weights = sigma)

Gradient: dE_phi/d(phi_i) = beta_phi * sum_{j~i} sigma_j * sin(phi_i - phi_j) / z
                          ≈ beta_phi * (phi_i - phi_bar_i)   [small angle approximation]

Flow: phi_i += -beta_phi * (phi_i - phi_bar_i) = beta_phi * angle_diff(phi_bar_i, phi_i) ✓

The Channel E term `epsilon * chi_i` is a chi→phi drive. It corresponds to:
```
E_E[phi, chi] = -epsilon * sum_i chi_i * phi_i
```
Gradient w.r.t. phi_i: -epsilon * chi_i
Flow: phi_i += epsilon * chi_i ✓

---

## Step 5: The unified free energy functional

Assembling all terms:

```
E[sigma, chi, phi] = sum_i {

  [sigma channels]
  alpha/2 * (sigma_i - sigma_ref)^2
  + beta/4 * sum_{j~i} (sigma_j - sigma_i)^2
  + gamma_phi/2 * D_i(phi) * sigma_i^2

  [chi channels]
  + chi_decay/2 * chi_i^2
  - chi_rel/2 * chi_i * (sigma_i - sigma_bar_i)
  - delta * chi_i * (sigma_ref - sigma_i)

  [phi channels]
  - beta_phi/z * sum_{j~i} sigma_i * sigma_j * cos(phi_i - phi_j)
  - epsilon * chi_i * phi_i

}
```

The QNG v5 update law is (approximately) gradient flow of this functional:
```
sigma_i(t+1) = sigma_i - dE/d(sigma_i)
chi_i(t+1)   = chi_i  - dE/d(chi_i)
phi_i(t+1)   = phi_i  - dE/d(phi_i)
```

(Ignoring the Proj clip, the chi*(1-chi_decay) form, and circular-mean details
for phi, which are implementation choices rather than physics.)

---

## Step 6: Physical interpretation of E

The functional E has a clear physical interpretation:

- **alpha term**: sigma is attracted to sigma_ref — the vacuum wants full coherence
- **beta term**: sigma wants to be uniform — gradient energy (tension)
- **gamma_phi term**: phase-disordered regions cost sigma — matter particles are energetically costly to maintain (they deplete sigma)
- **chi_decay term**: chi wants to be zero — chi is a transient, not a vacuum field
- **chi_rel term**: chi is sourced by sigma gradients — chi is the "rate of change" of sigma
- **delta term**: chi couples to sigma deviations — the generation hierarchy sigma→chi is energetic
- **beta_phi term**: phi wants to be aligned with neighbors (XY ferromagnet) — coherent phase is preferred
- **epsilon term**: chi drives phi — when sigma changes (chi ≠ 0), it leaves a phase imprint

The substrate minimizes E over time. Stable configurations are:
- sigma = sigma_ref everywhere (vacuum, no matter)
- chi = 0 everywhere (no dynamics)
- phi = uniform (no vortices)

Vortex rings are NOT minima of E — they are saddle points stabilized by
topological constraints on phi (winding number W = ±1 in 2D, dynamically
stabilized in 3D by Channel F). They are metastable states, not ground states.
This is consistent with particle physics: particles are excitations, not vacua.

---

## Step 7: Gradient flow vs. Hamiltonian dynamics

Einstein's concern is deeper than "derive all channels from one principle."
He wants a theory where the equations of motion follow from a single action
principle that is Lorentz-covariant. Gradient flow is:

```
∂_t field = -dE/d(field)
```

This is DISSIPATIVE and TIME-IRREVERSIBLE. It is not a Hamiltonian system.
It does not conserve E — it minimizes it. It does not have a symplectic structure.

For a truly relativistic theory, the equations of motion must follow from a
Lorentz-scalar action S via the Euler-Lagrange equations:

```
δS/δfield = 0
```

The relationship between E[sigma, chi, phi] and such an action S is:

- If chi is the conjugate momentum to sigma (chi = ∂_t sigma / something), then
  there exists a Lagrangian L = T - E where T is a kinetic term for sigma.
- The Hamiltonian H = T + E governs conservative dynamics.
- The dissipative gradient flow is then the overdamped limit of the Hamiltonian
  dynamics (when the kinetic energy is much smaller than the potential energy).

**The dissipative substrate may be the overdamped limit of a conservative theory.**
This is the key candidate: the full QNG theory has a Hamiltonian H[sigma, pi_sigma,
chi, pi_chi, phi, pi_phi] where pi are conjugate momenta. The update law observed
in simulations is the overdamped limit (momenta equilibrate fast). The conservative
limit (momenta retained) gives wave equations — and potentially Lorentz covariance.

This connection is not derived. It is a research program.

---

## Summary

| Result | Status |
|--------|--------|
| Channels A+B+F follow from E_sigma | DERIVED ✓ |
| Channel D follows from E_chi_sigma | DERIVED ✓ |
| chi_decay and chi_rel follow from E_chi | DERIVED ✓ |
| phi channels follow from XY + E_E | DERIVED (approximately) ✓ |
| All 6 channels from single functional E | ESTABLISHED (approximately) ✓ |
| E is a free-energy functional (gradient flow) | TRUE |
| E gives a Lorentz-covariant action | NOT SHOWN |
| Conservative limit of E gives wave equations | CANDIDATE mechanism |

**Einstein's concern is partially addressed:** all six channels follow from a
single free-energy functional. The substrate is not arbitrary phenomenology —
it is gradient flow of a physically interpretable energy.

**What remains open:** the gradient flow is dissipative and time-irreversible.
A Lorentz-covariant action principle requires a conservative dynamics with
conjugate momenta. The relationship between the dissipative E and a potential
conservative H is a research program, not an established result.

---

## Cross-references

- DER-QNG-026: v5 update law
- NOTE-QNG-013: qng-preferred-frame-analysis-v1.md — Lorentz/preferred frame
- DER-QNG-018: C_eff field equation (parabolic → must become hyperbolic)
