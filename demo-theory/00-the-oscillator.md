# 00 — The Oscillator: frequency is the first thing

Type: `definition` / `note`
Status: `foundational draft`
Author: `C.D Gabriel`
Depends on: nothing (this is the starting point)

---

## 0. Strip everything away

Forget the lattice. Forget gravity. Forget mass. Take **one node** and ask:
what is the simplest non-trivial thing it can do?

A QNG node carries, among its state, a **phase** `φ ∈ [-π, π]`. A phase is a
point on a circle. The simplest thing a point on a circle can do is **turn**:

```
        φ(t) = φ₀ + ω t
```

The rate of turning, `ω = dφ/dt`, is a **frequency**. That is the entire
content of this page, and it is the seed of everything downstream:

> **The most primitive dynamical fact in QNG is that a node has a phase, and
> a phase turns. Frequency is not derived. It is there at the start.**

This is why this whole thread is called "frequency and light": we are not
adding frequency to QNG. We are noticing it was the foundation all along, and
following it.

## 1. Give the oscillator inertia: the v8 canonical form

A free phase that turns forever at constant `ω` is too simple — nothing
restores it, nothing stores energy. v8 gives `φ` a **conjugate momentum**
`π_φ` and an **effective inertia** `μ_φ`. The single-node energy is then

```
        H_node = π_φ² / (2 μ_φ)   +   V(φ)
```

- `π_φ² / (2 μ_φ)` is the **kinetic term** — energy of *turning*.
- `V(φ)` is a potential on the circle (in the substrate it is the
  sine-Gordon-like `1 − cos φ` coupling).

The equations of motion are Hamilton's:

```
        dφ/dt   = ∂H/∂π_φ = π_φ / μ_φ          (so  ω = π_φ / μ_φ)
        dπ_φ/dt = −∂H/∂φ   = −V'(φ)
```

Two readings of the first equation, both important:

1. **Frequency is momentum.** `ω = π_φ / μ_φ`. The faster the phase turns, the
   more momentum it carries. `μ_φ` is the "flywheel": large `μ_φ` → hard to
   spin up → low frequency for given push.
2. **Energy is stored frequency.** Substitute back:
   `T = π_φ²/(2μ_φ) = ½ μ_φ ω²`. The kinetic energy of a node is literally the
   energy stored in its rate of vibration. Hold this thought — at the wave
   level it becomes `E = ℏω`, the photon.

## 2. Small oscillations: the harmonic heart

Near the bottom of `V(φ)` (call it `φ = 0`), expand `V(φ) ≈ ½ k φ²` with
stiffness `k = V''(0)`. The node is then a **simple harmonic oscillator**:

```
        μ_φ φ̈ = −k φ        ⟹        φ(t) = A cos(ω₀ t + δ),    ω₀ = √(k/μ_φ)
```

The **natural frequency** `ω₀ = √(stiffness / inertia)` is the single most
important number an oscillator has. Every result later in this thread —
the speed of light `c`, the lightcone, mass-as-resonance — is a descendant of
this one square root. Memorize the shape: **frequency = √(restoring / inertia).**

## 3. Where do the amplitude fields (`σ`) sit?

A node also has amplitude-like fields `σ_g, σ_m ∈ [0,1]`. Are *they* primitive
too, or are they downstream of the phase?

**Honest answer (flagged):** they are *co-primitive* but **dynamically
subordinate** — the amplitudes relax toward whatever configuration the phase
coherence dictates. The evidence is Channel F in the substrate: the matter
amplitude is depleted by *phase incoherence*,

```
        Δσ_m  ∝  −(1 − |Z|) σ_m ,       Z = local phase coherence (order param)
```

so where phases disagree, amplitude drains; where phases lock, amplitude
survives. **Amplitude is enslaved to coherence.** This is the precise sense in
which *"phase organizes the amplitudes."*

⚠️ **Do not over-claim.** The strong statement *"frequency is the sole
primitive, σ is fully derived"* requires an **adiabatic / slow-manifold
theorem** (σ instantaneously tracks φ) that is **not proven**. Treat it as an
open program (see `06-experiments.md`, and the main-theory Gap on χ
canonicalization). The defensible claim is the weaker one above.

## 4. What we have after page 00

- A node is an oscillator. **Frequency `ω = dφ/dt` is primitive.**
- v8 gives it inertia `μ_φ` and momentum `π_φ`; **`ω = π_φ/μ_φ`**.
- **Energy is stored frequency:** `T = ½ μ_φ ω²`.
- Natural frequency `ω₀ = √(stiffness/inertia)` — the template for `c` later.
- Amplitudes `σ` follow the phase (Channel F evidence); the strong "frequency
  is everything" claim is an open adiabatic conjecture, not a result.

**Next** (`01`): connect two oscillators. Out come beats, synchronization, and
the coherence field `C_eff` — the Kuramoto order parameter that becomes
geometry.
