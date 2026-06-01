# 02 — Phase Waves and the Lightcone: c = √(stiffness / inertia)

Type: `derivation`
Status: `foundational draft`
Author: `C.D Gabriel`
Depends on: `00-the-oscillator.md`, `01-coupled-oscillators.md`
Reuses (not re-derived): substrate dispersion `ω² = c_φ²k² + m²`, `c_φ² = β_φ/(z·μ_φ)`

---

## 0. Let the agreement travel

Page 01 had oscillators *locking in place*. Now let a disturbance in the phase
**move**: node `i` nudges `i+1`, which nudges `i+2`. A travelling pattern of
phase is a **wave**. The question is the relation between its frequency `ω`
(how fast it turns in time) and its wavenumber `k = 2π/λ` (how fast it turns in
space). That relation — the **dispersion** `ω(k)` — is the DNA of the medium.

## 1. The chain calculation (the heart of it)

Take a 1-D chain of the page-00 oscillators (inertia `μ`, neighbor coupling of
stiffness `β`, spacing `a`). Small-phase EOM at node `n`:

```
        μ φ̈ₙ = β (φₙ₊₁ − 2φₙ + φₙ₋₁)  −  m_loc² φₙ
                 └────── discrete Laplacian ──────┘    └ on-site restoring ┘
```

Plug in a travelling wave `φₙ = A e^{i(k n a − ω t)}`. The discrete Laplacian
gives `−(4/a²)·... ` but in the long-wavelength limit `ka ≪ 1` it reduces to
`−k²`, and you get the **dispersion relation**:

```
        μ ω² = β k²  +  m_loc²
   ⟹    ω² = (β/μ) k²  +  m_loc²/μ
```

On a lattice with coordination number `z` (number of neighbors; `z=6` for a
cubic 3-D lattice) the stiffness is shared over the `z` links, giving the
substrate form already established in the main theory:

```
   ┌─────────────────────────────────────────┐
   │   ω² = c_φ² k² + m²,    c_φ² = β_φ/(z μ_φ) │
   └─────────────────────────────────────────┘
```

Two limits, two kinds of light-and-matter:

- **`m = 0` (massless):** `ω = c_φ k`. A straight line through the origin —
  **the lightcone.** All wavelengths travel at the same speed `c_φ`. This is
  the *light-like* mode. No dispersion: a wave packet keeps its shape.
- **`m ≠ 0` (massive):** `ω = √(c_φ²k² + m²)`. Curved; there is a minimum
  frequency `ω(0) = m` — a **gap**. Long waves cannot go below it. This is the
  *matter-like* mode, and `m` is a rest energy (page 05).

> **The speed of light is born here as a slope.** `c_φ` is the slope of the
> massless branch. Nothing about "light" yet — just that the substrate has a
> universal propagation speed for phase disturbances.

## 2. `c = √(stiffness / inertia)` — the same law as every wave in nature

Look at `c_φ² = β_φ/(z μ_φ)` and recognize the page-00 template
`ω₀ = √(stiffness/inertia)`. It is the **same square root**, now for waves:

| Medium | speed | stiffness | inertia |
|---|---|---|---|
| String | `v = √(T/ρ)` | tension `T` | mass density `ρ` |
| Sound | `v = √(K/ρ)` | bulk modulus `K` | density `ρ` |
| EM (vacuum) | `c = 1/√(μ₀ε₀)` | `1/ε₀` (elastic) | `μ₀` (inertial) |
| **QNG phase** | `c_φ = √(β_φ/(z μ_φ))` | `β_φ` (phase rigidity) | `z μ_φ` (phase inertia) |

So `c` in QNG is not a postulate dropped into the theory. It is the
**transmission speed of the oscillator network**, fixed by how stiff the
phase-coupling is (`β_φ`) against how heavy the phase-flywheel is (`μ_φ`). This
is the cleanest physical reading of the constant.

## 3. Lorentz invariance = impedance matching (the new framing)

Here is the idea worth keeping from this page. The substrate has **three**
sectors that each carry waves: `σ_g` (gravity), `σ_m` (matter), `φ` (phase).
Each has its own speed `c_g, c_m, c_φ`. The main theory **requires** them
equal — `c_g = c_m = c_φ` — to get a single, sector-independent lightcone
(this is what makes emergent Lorentz invariance work; the inertias
`μ_m = 10.0`, `μ_φ = 0.857` were *derived* from exactly this matching).

Read it as a **transmission-line / impedance** statement:

- A medium has a **characteristic impedance** `Z₀ ~ √(stiffness · inertia)`
  (geometric-mean form).
- When two media have **equal impedance**, a wave crosses the boundary with
  **no reflection** — the join is invisible.
- `c_g = c_m = c_φ` is the condition that the three sectors form a **matched
  transmission line.** A wave passing from the phase sector into the matter
  sector into the gravity sector is not reflected; there is one universal
  light-cone for all of them.

```
   matched impedance  ⟺  one universal c  ⟺  one lightcone  ⟺  Lorentz invariance
   mismatch           ⟺  multiple cones   ⟺  Lorentz violation (LIV, η_LV)
```

This is, physically, **why Lorentz invariance is special and fragile**: it is
the knife-edge of perfect impedance matching across sectors. Mismatch is the
generic case and produces a measurable LIV signature `η_LV`.

⚠️ **Honesty flag.** This is a *reframe*, not a derivation. It explains the
*meaning* of `c_g = c_m = c_φ` beautifully, but it does **not** explain *why*
the substrate parameters take the matched values. That "why" is still the open
cosmological-α problem (Gap 5). Do not write "Lorentz invariance is derived
from impedance matching" — write "Lorentz invariance *is* impedance matching;
why the impedances match is Gap 5."

## 4. What we have after page 02

- A chain of page-00 oscillators carries **phase waves** with
  `ω² = c_φ²k² + m²`.
- The **massless branch is the lightcone**; `c_φ` is its slope, fixed by
  `c_φ = √(β_φ/(z μ_φ)) = √(stiffness/inertia)` — the same law as strings,
  sound, and EM.
- The massive branch has a **frequency gap `ω(0)=m`** — the seed of rest mass
  (page 05).
- **Lorentz invariance = impedance matching** across the three sectors; LIV =
  impedance mismatch. (Reframe, not derivation — `why` is Gap 5.)

**Next** (`03`): a single scalar phase wave is *longitudinal* and cannot be EM
light. We find the honest photon in the **transverse** part of the edge field
`θ_ij = φ_i − φ_j` — no gauge field required.
