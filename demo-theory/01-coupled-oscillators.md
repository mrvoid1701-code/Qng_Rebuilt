# 01 — Coupled Oscillators: beats, synchronization, and where C_eff comes from

Type: `derivation` / `note`
Status: `foundational draft`
Author: `C.D Gabriel`
Depends on: `00-the-oscillator.md`

---

## 0. Two is where physics begins

One oscillator just turns. **Two coupled oscillators** already contain almost
the whole story: interference, beats, and the choice between agreeing
(in-phase) and disagreeing (anti-phase). The lattice is just "two" repeated.

Take nodes `1` and `2` with phases `φ₁, φ₂` and a coupling that wants them to
agree. The minimal QNG-flavored coupling is sinusoidal (it must be `2π`-periodic
in each phase, and the substrate's vacuum is sine-Gordon):

```
        V_couple = −κ cos(φ₁ − φ₂)
```

This is minimized when `φ₁ = φ₂` (phases locked). The force on the phase
difference `ψ = φ₁ − φ₂` is `∝ −sin ψ` — a pendulum equation for the
*difference*. Two regimes:

- **Weak drive, near-equal natural frequencies →** the phases **lock**
  (synchronize): `ψ → const`. They turn together as one.
- **Stronger frequency mismatch →** they **beat**: the difference itself
  oscillates at the **beat frequency** `ω_beat = |ω₁ − ω₂|`. This is the
  acoustic "wah-wah" of two slightly-detuned strings — and the same math as a
  two-level quantum system's Rabi oscillation.

> **Beats are the substrate's most primitive clock.** Any two regions at
> slightly different frequency produce a slow modulation `|ω₁ − ω₂|` that is
> observable in amplitude even though each oscillator is fast. Keep this: slow
> physics (matter, mass scales) can emerge as *beat envelopes* of fast phase.

## 1. Many oscillators → Kuramoto, and the birth of coherence

Now `N` nodes, each with natural frequency `ωᵢ`, each coupled to its lattice
neighbors. In mean-field form this is the **Kuramoto model**:

```
        φ̇ᵢ = ωᵢ + (K/N) Σⱼ sin(φⱼ − φᵢ)
```

Kuramoto's central object is the **complex order parameter**:

```
        r e^{iΨ} = (1/N) Σⱼ e^{iφⱼ}
```

- `r ∈ [0,1]` measures **how aligned the phases are**. `r = 0`: total disorder
  (phases scattered around the circle). `r = 1`: perfect synchronization (all
  phases equal).
- There is a **critical coupling** `K_c`: below it `r = 0` (incoherent); above
  it `r > 0` (a synchronized cluster nucleates). A genuine **phase transition**.

## 2. The QNG identification: `C_eff` IS the Kuramoto order parameter

This is the structural payoff of page 01. The coarse-grained **coherence
field** `C_eff` that QNG uses to build geometry is *exactly* the local Kuramoto
order parameter:

```
        C_eff(x)  ≡  | (1/N_x) Σ_{j∈ neighborhood of x} e^{iφⱼ} |   =   r_local
```

Consequences, each load-bearing for the bigger theory:

1. **Geometry is synchronization.** In the main theory the Newtonian potential
   is `Φ ∝ δ_C` (deviation of `C_eff` from reference; convention GRAV-C1). Read
   through Kuramoto: **a gravitational well is a region where phases are
   *more* synchronized (or less) than the background.** Matter curves space by
   changing the local degree of phase agreement.
2. **The local coherence `|Z|` that drives Channel F** (page 00 §3) is the same
   `r_local`. So "amplitude drains where phases disagree" = "amplitude drains
   where `r` is low." Amplitude tracks the order parameter.
3. **Mass condenses out of a sync transition.** A stable matter structure is a
   region that has crossed `K_c` locally — a self-sustaining synchronized
   cluster. This reframes "particle formation" as a *nucleation of coherence*,
   and connects to the substrate's observed critical coupling `e*`
   (CPU-160 universal phase transition in the main lab).

## 3. In-phase vs anti-phase = the two faces of force

For two clusters, locking **in-phase** (`ψ=0`) and **anti-phase** (`ψ=π`) are
different energy minima of `−κ cos ψ`. The main theory already sees this:
CPU-049 found `W⁺W⁺` rings **repel** and `W⁺W⁻` rings **attract** — a
chirality/relative-phase-sensitive force. Through page 01 that is natural:

> **Like phases and unlike phases sit in different wells of the coupling
> potential. The "force" between two structures is the gradient of their
> phase-locking energy.** Under v12 this is read as the Coulomb force; here it
> is simply two coupled oscillators choosing how to align.

## 4. What we have after page 01

- Two oscillators → **beats** at `|ω₁ − ω₂|` (the primitive clock; slow physics
  as beat envelopes) and **locking** when the drive wins.
- Many oscillators → **Kuramoto**, with order parameter `r` and a genuine
  **synchronization phase transition** at `K_c`.
- **`C_eff = r_local`**: the coherence field that builds geometry is the
  Kuramoto order parameter. Gravity = spatial variation of phase agreement;
  Channel F amplitude depletion = low `r`; particle = nucleated sync cluster.
- Attractive/repulsive force = in-phase vs anti-phase wells.

**Next** (`02`): let the synchronized phase *propagate*. A chain of oscillators
carries phase waves with a dispersion relation — and out of it falls the
lightcone and the speed of light as `√(stiffness/inertia)`.
