# QNG 2.0 / 05 — the QM limit (Schrödinger + Born)

Type: `derivation`
Track: `qng-2.0`
Author: C.D Gabriel
Date: 2026-06-03

## Inputs

- [02-primitives.md](02-primitives.md) — the field ψ on the causet; `Z = Σ_C ∫Dψ e^{iS/ħ}`
- `qng-2.0` rung 0 — the field obeys a massive KG eqn on the causet (definite mass, CV=0.019)
- QNG 1.0 P102–105 — Schrödinger = NR limit of KG; Born rule as a dynamical attractor; decoherence

## The derivation

**Step 1 — the field is relativistic-quantum on the causet.** Rung 0 established that ψ on
the causet obeys `(B+m²)ψ=0` with `B→□`, i.e. the Klein–Gordon equation with dispersion
`ω² = c²k² + m²`, on a background-free, exactly-Lorentz substrate.

**Step 2 — Schrödinger as the NR limit.** Writing `ψ = e^{-imc²t/ħ} χ`, the slow envelope
`χ` obeys the free Schrödinger equation `iħ ∂_t χ = -(ħ²/2m)∇²χ` with `D = c²/2m`
(identical to QNG 1.0 P102; the KG→Schrödinger reduction is dimension- and
substrate-agnostic, so it transfers to the causet field verbatim).

**Step 3 — the measure gives QM.** In the regime where the dominant causet is
manifold-like, `Z = Σ_C ∫Dψ e^{iS/ħ}` reduces to the ordinary field path integral
`∫Dψ e^{iS_field/ħ}` on that manifold — the standard route to QFT and, in the
single-particle NR sector, to the Schrödinger propagator. Unitarity = conservation of the
field's Noether current (continuity). The **Born rule** transfers from QNG 1.0 P103–105:
it is a dynamical fixed-point + attractor (`|ψ|²` is equivariant and relaxed-to), and
substrate DECOHERENCE removes macroscopic superpositions (the causet itself is the
environment, even more naturally than QNG 1.0's lattice).

## The deep unification (stronger than QNG 1.0)

In QNG 1.0, GR and QM shared one **Hamiltonian** `H_v8`. In QNG 2.0 they share one
**path integral**: the SAME `Z = Σ_C ∫Dψ e^{iS_grav + iS_field}` produces gravity (vary
the order → Einstein, rung 2) AND quantum amplitudes (the `∫Dψ` measure → Schrödinger/Born,
this rung). One object, both pillars — the tightest expression of the synthesis.

## Honest status

- DERIVED/TRANSFERRED: Schrödinger as the NR limit of the causet KG field (clean, exact
  limit, demonstrated `tests/qng2_rung3_qm_limit.py`); unitarity from the field current.
- TRANSFERRED with caveat: the Born rule (attractor + decoherence) carries over from QNG
  1.0 P103–105 — but those used the guidance flow `v=∇S` (forced by unitarity, P104); the
  same Madelung argument applies to the causet field, so the transfer is sound, while a
  fully native causet-path-integral derivation of Born is the residual.
- OPEN (universal): single-outcome selection (interpretation) — same as everywhere.
- OPEN (the causet-specific risk): whether the manifold-like regime that makes `∫Dψ`
  reduce to QFT is generic, or needs the matter sector (rung 1) to be settled first.
- No numbers forced.
