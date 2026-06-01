# 05 — Mass as a Resonance: trapped frequency that weighs

Type: `derivation` / `note`
Status: `conjecture DISFAVORED by E4 (2026-06-01) — 1/R cavity form excluded`
Author: `C.D Gabriel`
Depends on: `02` (dispersion gap), `04` (light gravitates)
Result: see `E4-RESULT-mass-is-volume.md`

---

> **⚠ UPDATE 2026-06-01 — E4 has run.** The baryon ladder (Δ/N = 1.313) is
> reproduced by the **volume charge `Σσ_m` alone** (1.310, 0.2% off); the
> product with a `1/R` cavity frequency gives 1.048 and **breaks** the match.
> **Mass tracks the volume/topological charge, not a `1/R` resonance.** The
> conjecture below is disfavored *in its `1/R` cavity form* (a constant-`ω`
> dressing is still compatible — see `E4-RESULT-mass-is-volume.md`).
> Net thread picture: **frequency/edges → light; node volume charge → mass.**

---

## 0. The idea in one line

If a freely-running frequency is light (page 04), then a frequency **trapped in
a loop** — a standing wave that cannot escape — is **mass**:

> **Mass = stored, self-trapped frequency.**   `m = ℏ ω₀ / c²`

This is the QNG version of the oldest dream in physics (Kelvin's vortex atoms,
Wheeler's "mass without mass," the photon-in-a-box rest mass). The substrate
gives it a concrete home: a vortex **ring** of radius `R` is a cavity, and a
phase wave running around its circumference is a standing mode.

## 1. The cavity argument (where `ω₀` comes from)

Two independent footholds both point at a rest frequency:

**(a) The dispersion gap (page 02).** The massive branch
`ω = √(c_φ²k² + m²)` has a minimum at `k=0`: `ω(0) = m`. A localized matter
mode therefore has an irreducible **rest frequency `ω₀ = m`** — it is still
turning even when standing still in space. *That zero-momentum turning is the
rest energy.* This is the cleanest statement of `E = mc²` in the substrate:
rest mass is the `k=0` frequency of the matter branch.

**(b) The toroidal cavity.** A ring of radius `R` (circumference `2πR`) supports
standing phase waves when an integer number of wavelengths fits around it. The
fundamental (one wavelength around the loop) has

```
        λ₁ = 2πR    ⟹    k₁ = 1/R    ⟹    ω₁ = c_φ k₁ = c_φ / R
```

Combine with page-00's `E = ℏω` and `E = mc²`:

```
        m  =  E/c²  =  ℏ ω₁ / c²  =  ℏ c_φ / (c² R)
```

— **a rest mass set by a trapped frequency, falling off as `1/R`.**

## 2. The hard tension (be honest, this is unresolved)

The cavity argument predicts **`m ∝ 1/R`**: bigger loop → lower frequency →
*lighter*. But the main-theory measurement points the **other way.**
`DER-QNG-038` found the conserved ring charge `M_ring` *rising* with radius —
roughly `M ∝ R^a` (`a > 0`), reproducing the baryon ladder
`R=4 → N(938)`, `R=5 → Δ(1232)`, `R=6 → N*(1520)`. Bigger loop → *heavier*.

```
        cavity frequency:   m ∝ 1/R        (lighter with R)
        measured M_ring:    M ∝ R^a        (heavier with R)
                                ↑ direct contradiction
```

Two numbers cannot both be "the mass." Something is being conflated.

⚠️ Compounding caution from the lab: `M_ring` was later shown
**lattice-dependent** (Gap 14 — matches hadron ratios at `L=20` but drifts ~7%
at `L=28`), and under v8 symplectic dynamics rings are **dynamic patterns, not
static solitons** (`DER-QNG-047`). So `M_ring` itself is on shaky ground as a
"rest mass." This makes the tension *more* interesting, not less.

## 3. The reconciliation candidate (→ Experiment E4)

The resolution is probably that **`M_ring` and the physical mass are different
quantities:**

- **`M_ring = Σ σ_m`** is a **volume/topological charge** — a *count of
  displaced amplitude*, like counting how many nodes are in the ring. It
  naturally grows with `R` (bigger ring, more nodes). It is **not** a frequency.
- **Physical mass** might be **energy = density × frequency**:

```
        m_phys  ~  (Σ σ_m) · ω₁  ~  M_ring · (c_φ/R)  ~  R^a · R^{-1}  =  R^{a-1}
```

The frequency factor `1/R` *corrects* the volume scaling `R^a`. Whether the
result rises, falls, or is flat depends on `a` — and **that** is the number the
experiment must measure, not assume.

This dissolves the paradox cleanly: the cavity intuition (`1/R`) and the
volume-charge measurement (`R^a`) were never the same observable. Mass is their
**product** — a density carrying a frequency — exactly as `04`'s two-ledger
picture demands (amplitude × phase-rate).

## 4. Experiment E4 (the decisive test)

For rings `R = 3, 4, 5, 6` on the v8 symplectic substrate, measure **two
things separately**:

1. `Σ σ_m` — the volume charge (the old `M_ring`).
2. `ω₁` — the **internal toroidal frequency**: track the phase circulating
   around the ring and extract its fundamental, or read the dominant peak of
   the time-FFT of a core observable.

Then test three hypotheses against the PDG ladder `938 / 1232 / 1520`:

| Hypothesis | Prediction | Verdict if it matches |
|---|---|---|
| `m ∝ Σσ_m` (pure volume) | `R^a`, rising | mass is just the charge (no frequency role) |
| `m ∝ ω₁` (pure frequency) | `1/R`, falling | mass is pure resonance (cavity wins) |
| **`m ∝ Σσ_m · ω₁`** (product) | `R^{a-1}` | **mass = density × frequency** (this page's thesis) |

Whichever scaling reproduces the measured baryon ratios is the physical mass.
**This single scan resolves the `1/R`-vs-`R^a` contradiction.**

## 5. If E4 confirms the product law

- Mass becomes **literally** "stored frequency × stored amount" — the deepest
  possible vindication of the frequency-first program.
- The baryon ladder gets a *physical* (not just numerological) explanation: the
  resonance ladder of a vibrating loop, like overtones of a string, modulated
  by how much amplitude the loop carries.
- It connects to the lab's universal invariants (⟨L⟩=660, |H|·T_cycle ≈ 40000):
  these may be the *action* `energy × period = (m c²)(1/ω)` held fixed across
  the ladder.

## 6. Honesty contract

- `m = ℏω₀/c²` is a **conjecture**, currently *contradicted* by the naive
  `M_ring` scaling. It is NOT to be written as established.
- The product-law reconciliation is **plausible and testable** but unconfirmed.
  **Gate: E4.** Do not write "mass is a resonance" until E4 selects the product
  law (or refutes it).
- Remember `M_ring`'s own lattice-dependence (Gap 14) and non-soliton status
  (`DER-QNG-047`): E4 should be run at ≥2 lattice sizes to avoid re-importing
  the `L=20` finite-size coincidence.

## 7. What we have after page 05

- **Conjecture:** mass = self-trapped frequency, `m = ℏω₀/c²`, with `ω₀` either
  the dispersion gap (`k=0` rest frequency) or the toroidal fundamental `c_φ/R`.
- **Tension:** cavity says `m ∝ 1/R`; measured `M_ring ∝ R^a`. Direct conflict.
- **Reconciliation:** `M_ring` is a *volume charge*, not a mass; physical mass
  `~ Σσ_m · ω₁ ~ R^{a-1}` — **density × frequency** (the two-ledger product).
- **Decisive test E4** measures `Σσ_m` and `ω₁` separately against the baryon
  ladder. Gated; not yet claimed.

**Next** (`06`): the full pre-registerable experiment set E1–E6 that turns this
whole thread from story into measurement.
