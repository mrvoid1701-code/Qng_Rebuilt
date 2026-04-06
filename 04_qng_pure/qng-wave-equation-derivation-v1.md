# QNG Wave Equation Derivation v1

Type: `derivation`
ID: `DER-QNG-028`
Status: `draft`
Author: `C.D Gabriel`
Date: `2026-04-06`

## Objective

Derive whether the linearized (sigma, chi) dynamics around the vacuum produce
a wave equation. A wave equation requires second-order time derivatives and
finite propagation speed — necessary for Lorentz covariance. If the linearized
system is purely diffusive (first-order in time), there is no wave equation
and Lorentz covariance cannot emerge from the (sigma, chi) sector alone.

## Inputs

- [qng-native-update-law-v5.md](qng-native-update-law-v5.md) — DER-QNG-026
- [qng-preferred-frame-analysis-v1.md](qng-preferred-frame-analysis-v1.md) — NOTE-QNG-013
- [qng-action-principle-candidate-v1.md](qng-action-principle-candidate-v1.md) — NOTE-QNG-014

---

## Step 1: Linearization around the vacuum

Vacuum state: sigma_i = sigma_ref, chi_i = 0, phi_i = uniform.

In the vacuum, phi is uniform → Z_i = 1 → D_i = 1 - |Z_i| = 0.
Channel F contribution: -gamma_phi * D_i * sigma_i = 0.

Perturbation: sigma_i = sigma_ref + s_i, chi_i = c_i, where |s_i| << sigma_ref.

sigma_bar_i = sigma_ref + s_bar_i where s_bar_i = mean of s over z neighbors.

**Linearized sigma update (Channels A + B, Channel F = 0):**
```
s_i(t+1) = s_i + alpha*(-s_i) + beta*(s_bar_i - s_i)
```

In continuum limit (Δt → 0, Δx → 0):
```
∂_t s = -alpha*s + beta*∇²s                    ... (1)
```

**Linearized chi update (Channels chi_decay, chi_rel, D):**
```
c_i(t+1) = c_i*(1 - chi_decay) + chi_rel*(s_bar_i - s_i) + delta*(-s_i)
```

In continuum limit:
```
∂_t c = -chi_decay*c + chi_rel*∇²s - delta*s   ... (2)
```

---

## Step 2: Is sigma autonomous?

Equation (1) contains ONLY sigma. Chi does not appear.

This means sigma evolves independently of chi in the linearized vacuum.
The sigma equation is:
```
∂_t s = -alpha*s + beta*∇²s
```

This is a **parabolic PDE** (reaction-diffusion). First-order in time.

Taking a second time derivative:
```
∂²_t s = -alpha*(∂_t s) + beta*∇²(∂_t s)
       = -alpha*(-alpha*s + beta*∇²s) + beta*∇²(-alpha*s + beta*∇²s)
       = alpha²*s - 2*alpha*beta*∇²s + beta²*∇⁴s
```

This is a fourth-order spatial operator (biharmonic) — NOT a wave equation
`∂²_t s = v²*∇²s`. The second time derivative of sigma does not produce
a d'Alembertian.

**Result: sigma alone gives NO wave equation in v5.**

---

## Step 3: Does the (sigma, chi) coupled system give an oscillator?

Chi is slaved to sigma via equation (2). Substituting:

In the long-wavelength limit (∇² → 0, ignore diffusion):
```
∂_t s = -alpha*s
∂_t c = -chi_decay*c - delta*s
```

The sigma equation is pure decay (exponential relaxation). The chi equation
is driven by sigma decay, but chi does not feed back into sigma.

For oscillatory dynamics, we would need:
```
∂_t s ~ +c  (chi drives sigma)
∂_t c ~ -s  (sigma drives chi, sign flip)
```

This IS a harmonic oscillator. But it requires chi to feed back into sigma —
which is ABSENT from the v5 update law.

**Result: (sigma, chi) in v5 is NOT an oscillator. No back-reaction chi → sigma.**

---

## Step 4: What is required for a wave equation

For a wave equation ∂²_t s = v²*∇²s to emerge from (sigma, chi), the system
needs a back-reaction channel: chi_i contributes to sigma_i's update.

**Candidate Channel G:**
```
sigma_i(t+1) += k_back * chi_bar_i    (chi Laplacian feedback)
or
sigma_i(t+1) += k_back * chi_i        (direct chi feedback)
```

With Channel G added (k_back * chi_i in sigma update), the linearized system becomes:
```
∂_t s = -alpha*s + beta*∇²s + k_back*c      ... (1')
∂_t c = -chi_decay*c + chi_rel*∇²s - delta*s  ... (2)
```

Taking ∂_t of (1') and substituting (2) in the long-wavelength limit
(ignoring alpha, chi_decay, and second-order spatial terms for clarity):

```
∂²_t s = k_back * ∂_t c
       = k_back * (chi_rel*∇²s - delta*s)
       = k_back*chi_rel*∇²s - k_back*delta*s
```

This gives:
```
∂²_t s + k_back*delta*s = k_back*chi_rel*∇²s    ... (WAVE EQUATION)
```

This is a **Klein-Gordon equation**:
```
(∂²_t + m²) s = v²*∇²s
```
with:
```
m² = k_back * delta      [effective mass squared]
v² = k_back * chi_rel    [propagation speed squared]
```

For a massless wave (m = 0): requires delta = 0 (no Channel D coupling).
For c-speed propagation: requires k_back * chi_rel = c² (in lattice units).

---

## Step 5: Physical interpretation

If Channel G exists with coupling k_back:

1. **Oscillatory vacuum**: sigma fluctuations oscillate with frequency ω² = k_back*delta
   instead of decaying exponentially. The substrate vacuum is not static — it vibrates.

2. **Wave propagation**: disturbances in sigma propagate at speed v = sqrt(k_back*chi_rel).
   For this to equal c (speed of light), k_back must be chosen so that
   k_back = c²/chi_rel in physical units.

3. **Massive vs massless**: if delta > 0 (Channel D active), the wave is massive
   (Klein-Gordon). For massless gravitons, need delta = 0 or a mechanism to
   cancel the mass term.

4. **Lorentz covariance**: the Klein-Gordon equation IS Lorentz-covariant.
   Adding Channel G is the mechanism by which Lorentz invariance emerges.

---

## Step 6: Why Channel G is absent from v5

Channel G (chi → sigma back-reaction) would mean: the chi field, which accumulates
the "debt" of sigma deviations, pushes back on sigma. Physically: if chi has built
up a positive value (sigma has been depleted), it tries to restore sigma.

This is exactly what a restoring force does in an oscillator.

Currently, the update law has:
- sigma → chi: delta*(sigma_ref - sigma_i) in chi update (Channel D) — sigma drives chi
- chi → phi: epsilon*chi_i in phi update (Channel E) — chi drives phi
- phi → sigma: gamma_phi*D_i*sigma_i in sigma update (Channel F) — phase disorder depletes sigma

There is no chi → sigma back-reaction. The causal chain is:
```
sigma → chi → phi → sigma
```
(a cycle, but mediated through phi, not directly)

The indirect back-reaction through phi is nonlinear (requires vortex formation,
not present in the vacuum linearization). A direct linear chi → sigma channel
is not in the current ontology.

---

## Step 7: The sigma-chi-phi cycle and wave speed

The full cycle sigma → chi → phi → sigma has a characteristic time:
- sigma → chi: one update step (Channel D)
- chi → phi: one update step (Channel E, strength epsilon)
- phi → sigma: requires D_i ≠ 0 (phase disorder, requires vortices)

In the vacuum (uniform phi), the cycle is broken at the last step. The signal
from sigma that reaches phi through chi cannot feed back to sigma because D_i = 0.

The cycle only closes in the presence of phase disorder (near vortex cores).
This suggests the wave equation may only emerge near matter — not in the vacuum.

This is physically interesting: propagating modes may require matter to exist.
The vacuum may be genuinely dissipative (parabolic), and waves emerge only in
matter-containing regions. This is different from GR where gravitational waves
propagate through vacuum.

---

## Step 8: Summary and conclusion

| System | Dynamics | Wave equation? |
|--------|----------|----------------|
| sigma alone (v5 vacuum) | Parabolic: ∂_t s = -α s + β∇²s | NO |
| (sigma, chi) v5 vacuum | sigma autonomous, chi slaved | NO |
| (sigma, chi) with Channel G | Klein-Gordon: ∂²_t s = v²∇²s - m²s | YES |
| Full cycle sigma→chi→phi→sigma | Nonlinear, requires D_i≠0 | Only near matter |

**Main result:** The v5 update law does NOT produce a wave equation in the
linearized vacuum. The (sigma, chi) pair is a decay-diffusion system, not
an oscillator.

**For a wave equation:** Channel G (chi → sigma back-reaction with k_back)
must be added. This gives a Klein-Gordon equation with:
- m² = k_back × delta
- v² = k_back × chi_rel

Setting v = c fixes k_back = c²/chi_rel (one new parameter).

**Implication for Lorentz covariance:** The v5 substrate is not Lorentz-covariant
in its linearized vacuum dynamics. Adding Channel G is the minimal extension that
gives Lorentz-covariant wave propagation. This would be **v6 of the update law**.

---

## What needs to be done next

1. **Add Channel G as a candidate** (v6 update law, DER-QNG-029):
   sigma_i(t+1) += k_back * (chi_bar_i - chi_i)  [or direct chi_i]

2. **Test v6 numerically** (QNG-CPU-046 or new test):
   - Do sigma perturbations propagate as waves?
   - What is the measured speed v_prop?
   - Is v_prop = sqrt(k_back * chi_rel) as predicted?

3. **Check vortex ring stability under v6**: does adding Channel G destabilize
   the vortex rings that give us "particles"?

4. **Fix k_back from c**: k_back = c²/chi_rel in physical units requires the
   same unit conversion as the rotation curve program (needs rho_0).

---

## Cross-references

- NOTE-QNG-013: Lorentz preferred frame analysis
- NOTE-QNG-014: Action principle — E_sigma gradient flow gives Channels A+B+F
- DER-QNG-026: v5 update law
- DER-QNG-029 (planned): v6 update law with Channel G
