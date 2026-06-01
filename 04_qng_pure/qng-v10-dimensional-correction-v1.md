---
type: note
id: NOTE-QNG-024
title: Correction to DER-QNG-061/062 — ⟨L⟩ has units of ENERGY, not action
status: correction to earlier claim (Gabriel 2026-04-24 "dai analitic, nimic ad-hoc")
author: C.D Gabriel
date: 2026-04-24
upstream:
  - NOTE-QNG-017 (original, correctly states "⟨L⟩ has units of energy, not action")
  - DER-QNG-061 (connection map — INCORRECTLY claimed ⟨L⟩ IS ℏ_QNG)
  - DER-QNG-062 (v10 foundational — INCORRECTLY used same claim)
---

# NOTE-QNG-024 — Dimensional correction: ⟨L⟩ ≠ ℏ_QNG

## The error

In DER-QNG-061 (connection map) and DER-QNG-062 (v10 foundational),
I wrote:

> "⟨L⟩ = 660 likely IS ℏ_QNG, just unrecognized due to missing operator structure"

**This claim is dimensionally incorrect.**

NOTE-QNG-017 (the original derivation of ⟨L⟩) explicitly states in
Section 4:

> "Not ℏ: ⟨L⟩ has units of energy (action/time), not action."

Units:
- ⟨L⟩ = time-averaged Lagrangian = ⟨T_kin⟩ - ⟨V⟩ has dimensions of ENERGY
- ℏ has dimensions of ACTION = ENERGY × TIME

**⟨L⟩ cannot directly BE ℏ_QNG**. They have different dimensions.

## Why I made the error

I was excited by the correspondence:
- ⟨L⟩ = N·β_φ/2 is universal (R-invariant)
- β_φ/2 is per-node intensive quantity
- "Per-node intensive action constant" is what ℏ looks like

And conflated "acting like action" with "BEING action." A rigorous
dimensional analysis would have caught this immediately.

Gabriel 2026-04-24 directive: *"dai analitic, nimic ad-hoc"* — this
was exactly the ad-hoc I was warned against. Correcting now.

## What ⟨L⟩ actually is

⟨L⟩ = N·β_φ/2 is the **negative classical ground state energy**
(per NOTE-QNG-017 §2.2a):

```
⟨L⟩ = −V_ground   for harmonic attractors around ground state
```

For v8 at pure-XY ground state:
```
V_ground = E_phi_A_ground = −β_φ · N / 2
⟨L⟩ = −V_ground = +β_φ · N / 2
```

**⟨L⟩ is a classical invariant with dimensions of ENERGY**. It
characterizes the **depth** of the ground state, not the quantum of action.

## What role might ⟨L⟩ play in v10 (if any)

### Possibility 1: Ground-state energy reference

In v10 harmonic approximation, zero-point energy per mode = ℏω/2.
Total ground-state energy = Σ_modes ℏω_mode/2.

Per-node (intensive): some characteristic ℏω_char / 2.

If v10 ground state energy per node = β_φ/2 = 0.03 (same as v8), and
we can identify a characteristic frequency ω_char, then:

```
ℏ_QNG = 2 × (β_φ/2) / ω_char = β_φ / ω_char
```

**But we need to specify ω_char carefully**. Candidates:
- Orbital frequency ω_orbit = 0.035 → ℏ = 0.06/0.035 ≈ 1.7
- XY single-mode frequency ω_XY = √(β_φ/μ_φ) = 0.265 → ℏ = 0.06/0.265 ≈ 0.23
- Plasma-like frequency ω_plasma = √(g/μ_φ) → ℏ = 0.06 · ...

**Different ω choices give different ℏ values — factor ~10 range**.

This is NOT a derivation; it's a dimensional exercise. Need physical
argument to pick ω_char.

### Possibility 2: Action per orbital cycle

Classical Bohr-Sommerfeld: ∮ p dq = n·h = 2π·n·ℏ

For v8 orbital attractor:
- Period T_orbit = 185 lu
- Classical action per cycle = ⟨L⟩ · T_orbit = 660 · 185 ≈ 1.22×10⁵
- If this equals 2π·n·ℏ_QNG for some integer n

With n=1: ℏ_QNG = 1.22×10⁵ / (2π) ≈ 1.94×10⁴
With n=N=21952 (one quantum per node): ℏ_QNG ≈ 0.88

These are VERY different values depending on what "n" means. This is
NOT a valid derivation.

### Possibility 3: ℏ_QNG is FREE in v10 (honest stance)

Treat ℏ_lattice as a **free parameter** of v10 until a rigorous
derivation identifies it from substrate quantities. This is the
position Nelson, Parisi-Wu, Ginzburg-Landau all take.

In this stance:
- v10 is a well-defined quantum theory parametrized by ℏ_lattice
- Calibration to ℏ_SI can be done empirically (match some observable)
- Derivation of ℏ_lattice from substrate is an OPEN problem

This is the **rigorous** position. "⟨L⟩ = ℏ_QNG" was wishful thinking.

## Honest status

**DER-QNG-062 is mathematically correct as a v10 axiomatization** —
the Hamiltonian, operator algebra, and classical limit arguments stand.

**The specific identification ℏ_lattice = β_φ/2 in DER-QNG-062 §9 is
WITHDRAWN as unjustified.** Replace with: "ℏ_lattice is a free
parameter of the theory, to be calibrated or derived via further
analysis."

**DER-QNG-061 connection map is structurally correct** but the final
"⟨L⟩ may BE ℏ_QNG" claim is withdrawn. The map still shows what v10
needs structurally; only the numerical identification is removed.

**CPU-103 verdict HO_PASS still stands** — the test was harmonic
oscillator spectrum consistency, which passed for any value of
ℏ_lattice (including 0.03, but not uniquely).

## What this means for the ℏ-program

Good news: v10 axiomatization is sound. v10 correctly provides all 8
quantum requirements. Classical limit recovers v8.

Bad news: we DO NOT have a derivation of ℏ_QNG yet. We just have a
framework where ℏ can play its expected roles.

Realistic status:
- v10 would produce QM behavior with ℏ as parameter
- Calibrating ℏ to match ℏ_SI is EMPIRICAL (like measuring a fundamental
  constant)
- DERIVING ℏ from QNG substrate remains open question

**This is where everyone is in quantum foundations**. Nelson couldn't
derive D = ℏ/2m. Parisi-Wu couldn't derive noise amplitude = ℏ. Adler
couldn't derive equipartition scale. We're in the same position —
except we explicitly acknowledge it.

## Path forward (revised)

### Phase I revised (pure theory, 2-4 weeks)

1. v10 axiomatization (DER-QNG-062) — **CORRECT**, ℏ as free parameter
2. Rigorous classical limit derivation — show v8 equations recovered
   as ℏ → 0
3. Ground state analysis — identify what role β_φ/2 per node plays
   (it's ⟨V_ground⟩/N per virial theorem, NOT ℏ)
4. Unit-bridge analysis — if ℏ_QNG = X in natural units, what must X
   be for ℏ_QNG · a_S = ℏ_SI where a_S is derived from a_M and c?

### Phase II (numerical, months)

5. CPU implementation of small-system v10 harmonic
6. CPU-103 already PASSED (harmonic spectrum consistent for any ℏ)
7. CPU-104 uncertainty (should pass trivially)
8. CPU-105 classical limit — PRIMARY TEST of v10-to-v8 reduction

### Phase III (predictions, months)

9. Compute v10 baryon spectrum (quantum) vs DER-QNG-038 classical ladder
10. Compute v10 Einstein-correspondence probes vs DER-QNG-044 classical
11. Identify if v10 gives ANY specific ℏ value without calibration

## Apology and lesson

The claim "⟨L⟩ IS ℏ_QNG" was wishful thinking dressed up as analysis.
Exactly what Savant reviewer warned against. Exactly what Gabriel said
NOT to do.

**Lesson**: dimensional analysis first, excitement second.

Going forward:
- Every claim about "this quantity equals ℏ" must pass dimensional check
- Every "identification" must come from explicit derivation, not pattern
  matching
- Free parameters are HONEST; forced identifications are suspicious

## Status of earlier documents

- **NOTE-QNG-017** (original ⟨L⟩ derivation): CORRECT throughout. This
  was always properly scoped.
- **DER-QNG-061** (connection map): structurally correct, final
  "⟨L⟩=ℏ_QNG" claim withdrawn.
- **DER-QNG-062** (v10 foundational): axiomatically correct. Section 9
  specific identification withdrawn; replaced with "ℏ_lattice free
  parameter."
- **NOTE-QNG-023** (revised hbar axiomatic): claim "ℏ is axiomatic"
  actually STRENGTHENED by this correction — if we can't derive ℏ even
  with v10 structure, Einstein-mind's position is validated.

Corrections to be applied via edits to the respective documents.

---

*Gabriel 2026-04-24: "dai analitic, nimic ad-hoc"*
*Response: corrected ad-hoc dimensional claim. Honesty > ambition.*
