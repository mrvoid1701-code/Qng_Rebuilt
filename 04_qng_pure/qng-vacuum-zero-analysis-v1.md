---
type: derivation
id: DER-QNG-065
title: Why E_vacuum = 0 may be natural in QNG — exploring derivation vs postulate
status: analytical investigation (Gabriel 2026-04-24 authorize)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - NOTE-QNG-026 (recap of 4 candidates, A = 0.233 preferred)
  - CPU-107 finite-lattice zero-point calculation
  - DER-QNG-062 (v10 axiomatization)
---

# DER-QNG-065 — E_vacuum = 0 analysis

## Statement

**Candidate A** (ℏ_QNG = 0.233) is derived from:
```
E_vacuum = -β_φ·N/2 + (ℏ/2)·Σ_k ω_k = 0
→ ℏ = β_φ·N / Σω_k
```

**Question**: is "E_vacuum = 0" a postulate we impose, or is it naturally
selected by QNG structure?

## Section 1: Structural formula for ℏ_QNG (under A)

Given QNG substrate parameters, ℏ_QNG is fully determined:

```
ℏ_QNG = β_φ·N / Σ_k ω_k
      = β_φ / ⟨ω_k⟩_lattice
      = β_φ / [√(β_φ/(z·μ_φ)) · ⟨√λ_k⟩_lattice]
      = √(β_φ·μ_φ·z) / ⟨√λ_k⟩
```

where `λ_k = 2[3 - cos(k_x) - cos(k_y) - cos(k_z)]` is the discrete
Laplacian eigenvalue on cubic lattice z=6.

**For thermodynamic limit** N → ∞: ⟨√λ_k⟩_BZ is a UNIVERSAL NUMBER
depending only on lattice type (cubic z=6):
```
⟨√λ_k⟩_BZ = 2·⟨√(3 - Σ_μ cos k_μ)⟩_BZ
```

Numerically (verified CPU-107): `⟨√λ_k⟩_L=28 = 2.389`

So:
```
ℏ_QNG = √(β_φ·μ_φ·z) / ⟨√λ_k⟩
      = √(0.06 · 0.857 · 6) / 2.389
      = √0.309 / 2.389
      = 0.556 / 2.389
      = 0.233 ✓
```

**This formula uses ONLY substrate quantities. No calibration.**

## Section 2: Is E_vacuum = 0 forced, or imposed?

### Approach 2.1: SUSY-like cancellation

SUSY forces E_vacuum = 0 via boson/fermion pairing. QNG has only
bosonic fields (Ψ complex, σ_g, σ_m real). **No fermions → no SUSY**.

SUSY argument does NOT apply to QNG directly.

**Alternative**: in QNG, maybe pair "gradient modes" with "kinetic modes"?

- Gradient potential: V = -(β_φ/(2z))·Σ_{<ij>} cos(Δφ) with classical
  minimum -β_φ·N/2
- Kinetic zero-point: T_ZP = (ℏ/2)·Σω_k

These are DIFFERENT structural objects, not related by any symmetry I
can identify. **No natural SUSY-like pairing**.

### Approach 2.2: Conformal / scale invariance

CFT can have vacuum energy protected by conformal anomaly = 0.

QNG has **lattice scale** (spacing `a` sets cutoff). Not scale-invariant.
**CFT argument doesn't apply**.

### Approach 2.3: Anomaly cancellation (genuine candidate)

Investigate: is there a "classical-quantum anomaly" that QNG cancels?

**Classical** ground state: `E_cl = -β_φ·N/2` — substrate's minimum-energy
configuration.

**Quantum** zero-point: `E_qm = (ℏ/2)·Σω_k` — quantum correction from
uncertainty principle.

**Hypothesis**: QNG may have a structural identity:
```
β_φ·N = ℏ·Σω_k   (exact, not imposed)
```

**Proof attempt**: compute both sides for generic N, z, β_φ, μ_φ, see if
relation is automatic.

- LHS = β_φ·N (linear in N, linear in β)
- RHS = ℏ·N·⟨ω_k⟩ = ℏ·N·√(β_φ/(zμ))·⟨√λ_k⟩

For equality: ℏ·√(β_φ/(zμ)) · ⟨√λ_k⟩ = β_φ
→ ℏ = β_φ · √(zμ/β_φ) / ⟨√λ_k⟩
    = √(β_φ·z·μ) / ⟨√λ_k⟩

This is NOT automatic — it's a SPECIFIC VALUE of ℏ. Other values don't
satisfy the identity. So "anomaly cancellation" here means SELECTING ℏ
to cancel, not automatic cancellation.

**Verdict**: not a natural identity. ℏ value is CHOSEN to cancel, not
derived from deeper principle.

### Approach 2.4: Cosmological constant principle

In GR, vacuum energy contributes to cosmological constant:
```
Λ_cosmological ∝ E_vacuum · G_N
```

Observed: |Λ_obs| ≈ 10⁻⁵² m⁻² (SI). Very small.

If QNG is coupled to gravity (which v10 → v8 emergent GR shows), then
E_vacuum is PHYSICAL (not just arbitrary zero).

**Empirical principle**: if we POSTULATE that QNG predicts cosmological
constant ≈ 0 (consistent with observations), then E_vacuum = 0 is a
PREDICTION of QNG that matches reality.

**This is the strongest physical argument for Candidate A**. But it's
STILL a postulate (we choose ℏ to make Λ=0), not a derivation.

### Approach 2.5: Self-consistency with v10 dynamics

Could E_vacuum = 0 be required by v10 ground state stability?

If E_vacuum < 0, vacuum is unstable (runaway to more negative states).
If E_vacuum > 0, vacuum decays to lower state.
E_vacuum = 0 is the MARGINAL case — locally stable, no driving force.

**Hmm**: this is a STABILITY argument, not forced.

**Check**: for Candidate B (ℏ = 0.291 > 0.233):
E_vacuum = -658 + 0.291·5661/2 = +166 > 0
Can v10 "decay" from this state to lower energy? Depends on whether
lower states exist.

For Candidate D (ℏ = 0.194 < 0.233):
E_vacuum = -658 + 0.194·5661/2 = -109 < 0
Vacuum is bounded below (Hamiltonian has discrete spectrum, integer
filling). So this is stable, just negative.

**Stability doesn't uniquely select E_vacuum = 0.** All candidates are
stable under v10 dynamics (bounded spectrum).

### Approach 2.6: Naturalness / Occam's razor

"Zero" is SPECIAL. Among candidate vacuum energies (-∞, 0, +∞), zero
is unique.

Argument: absent specific reason for nonzero, zero is the minimal
assumption.

**This is philosophical, not derivation**. Many physical constants are
not zero (α, m_e, etc.). Occam doesn't force E_vacuum = 0.

## Section 3: Comparison with known physics

### 3.1 Standard QFT
Vacuum energy is UV divergent. Renormalization subtracts to make finite.
Specific finite value is RENORMALIZATION CHOICE (not derivation).

**QNG advantage**: discrete lattice = no UV divergence. Vacuum energy
finite from beginning. No renormalization needed.

**QNG disadvantage**: finite ≠ zero. Specific value needs justification.

### 3.2 Supersymmetry
SUSY cancels boson vs fermion contributions. If unbroken, E_vacuum = 0
exactly.

**QNG disadvantage**: no fermions → no SUSY cancellation.

**QNG novelty**: if QNG could achieve E_vacuum = 0 via DIFFERENT mechanism
(e.g., classical-quantum cancellation), it would be a new result.

### 3.3 Casimir-like arguments

In Casimir effect, boundary conditions select specific vacuum mode structure.
Finite vacuum energy depends on geometry.

**QNG analog**: Σω_k depends on lattice structure (cubic z=6). ℏ·Σω_k/2
is the Casimir-like contribution from the lattice "box" (periodic T³).

The value is LATTICE-DEPENDENT, not universal in continuum limit.
Doesn't force E_vacuum = 0.

## Section 4: What we actually have

### Observation: E_vacuum = 0 is NOT strictly derivable in QNG

All attempts (SUSY, CFT, anomaly, stability, naturalness) give partial
arguments but not hard derivation.

### Observation: E_vacuum = 0 IS physically consistent

No contradiction with any QNG structural property. No symmetry FORCES
it, but nothing VIOLATES it either.

### Observation: E_vacuum = 0 IS cosmologically privileged

Matches observed Λ ≈ 0. If we demand QNG predict observed universe,
E_vacuum ≈ 0 is quasi-required.

## Section 5: Honest status

**Candidate A (ℏ = 0.233) IS MORE NATURAL than B, C, D** because:

1. **Uses only structural substrate quantities** (β_φ, μ_φ, z, lattice)
2. **Produces E_vacuum = 0** matching observed cosmology
3. **Simplest possible assumption** (zero is special)
4. **No arbitrary "excitation level" choice** (unlike B, C, D which
   require picking n)

**But it's NOT strictly derived** — requires postulating E_vacuum = 0.

**Philosophical status**: "ℏ_QNG = √(βμz)/⟨√λ⟩ = 0.233 is the unique
value consistent with QNG substrate parameters + observed Λ ≈ 0 cosmology".

This is publishable as: "QNG predicts ℏ = 0.233 natural units, under
the assumption of zero cosmological constant, which matches observations".

## Section 6: Deeper question — is there a symmetry we missed?

Let me try one more angle. In v10, the Hamiltonian is:
```
Ĥ_v10 = T̂ + V̂
T̂ = (1/(2μ)) Σ|Π̂|²
V̂ = -(β/(2z))Σ cos(Δφ̂)
```

Zero-point energy from kinetic: `⟨T̂⟩_0 = (ℏ/2)·Σω_k`
Classical minimum of V̂: `⟨V̂⟩_min = -β·N/2`

Their sum = E_vacuum.

Is there a relation `⟨T̂⟩_0 + ⟨V̂⟩_min = 0` that follows from
canonical structure?

For harmonic oscillator (single mode):
⟨T⟩_0 = ℏω/4 (kinetic zero-point)
⟨V⟩_0 = ℏω/4 (potential zero-point)
E_0 = ℏω/2 (total zero-point)

Both kinetic and potential contribute EQUALLY to zero-point (virial). 
But classical minimum of V is 0 (at equilibrium), not -V_max.

In QNG, the situation is DIFFERENT because the potential has a non-zero minimum:
V_min = -β·N/2 (at ferromagnetic ground state)

The "non-zero V_min" is structural feature — classical binding energy. It doesn't have a direct harmonic-oscillator analog.

**Key question**: is there a symmetry that makes the substrate treat
`V_min` and `⟨T̂⟩_0` as dual?

Let me think... In XY model, the virial theorem says:
⟨T⟩ = -⟨V⟩ (for harmonic oscillator), so total = 0 at ground.

BUT for XY model the ground state is at V_min = -β·N/2, not at V = 0.
The EXCITATION energy is relative to V_min.

So "zero-point" in QNG is around V_min, and total = V_min + ZP.

For V_min + ZP = 0: ZP must equal -V_min = +β·N/2.
Which gives ℏ = β_φ·N/Σω_k.

This is just Candidate A formula.

**Is there a reason for ZP = -V_min?**

Hmm... physically this would require specific fine-tuning. There's no
obvious principle.

BUT — here's a thought: if we DEMAND that QNG ground state is "flat"
(zero energy density), then cosmological Λ=0 naturally.

This is actually SIMILAR to asymptotic flatness in GR: the natural
boundary condition at infinity is g_μν → Minkowski (flat), which implies
vacuum energy density → 0 at infinity.

In QNG discrete context: "flat boundary" = classical + quantum exactly
cancel for bulk vacuum. This is a STRUCTURAL BOUNDARY CONDITION, not
imposed by symmetry but by "natural embedding in empty space".

## Section 7: Provisional principle

**Provisional "QNG Vacuum Principle"**:

> For a QNG substrate embedded in asymptotically flat space-time,
> the total vacuum energy density (classical + quantum zero-point)
> must vanish:
> 
> E_classical_ground + E_quantum_zero_point = 0
> 
> This fixes ℏ_QNG uniquely via ℏ = β_φ·N/Σω_k.

**Status**: PROVISIONAL — motivated by flat cosmology but not derived
from first principles.

**Consequence**: ℏ_QNG = 0.233 in natural units, Λ = 0 predicted.

**Falsifiable**: if Λ_observed ≠ 0 (cosmological constant nonzero),
the principle fails. Currently Λ_obs ≈ 10⁻⁵² m⁻² — consistent with 0
but not demonstrably zero.

## Section 8: Next analytical steps

### α1 verdict: E_vacuum = 0 is PROVISIONAL principle, not derivation

### α2: Formalize "QNG Vacuum Principle" (next step)

Write formal axiom: QNG + asymptotic flatness → E_vacuum = 0.

### α3: v10 numerical test

With v10 framework, COMPUTE E_vacuum for small system and verify ℏ = 0.233
gives E_total = 0. This is a CONSISTENCY CHECK, not derivation.

### α4: Cosmological prediction

If ℏ_QNG = 0.233 natural, what SI value does this map to? Requires
unit-bridge (still problematic per DER-QNG-064). 

## Section 9: Status summary

```
╔══════════════════════════════════════════════════════════════╗
║  CANDIDAT A: hbar_QNG = 0.233                                ║
║                                                              ║
║  NATURAL because:                                            ║
║   - Uses only substrate params (β, μ, z, lattice)            ║
║   - Produces E_vacuum = 0 consistent with observed Λ ≈ 0    ║
║   - Simplest assumption (zero is special)                    ║
║   - No arbitrary excitation level choice                     ║
║                                                              ║
║  BUT not strictly DERIVED - requires postulate               ║
║   "QNG Vacuum Principle": E_classical + E_ZP = 0             ║
║                                                              ║
║  FORMULA (substrate-only):                                   ║
║   hbar_QNG = sqrt(β·μ·z) / <sqrt(λ_k)>_BZ                    ║
║                                                              ║
║  PREDICTION if confirmed:                                    ║
║   Cosmological constant Λ = 0 exactly                        ║
║   Resolves "cosmological constant problem"                   ║
║                                                              ║
║  Classification: PRIVILEGED CANDIDATE                        ║
║   Not fully derived, but uniquely selected                   ║
║   by minimal physical assumptions                            ║
╚══════════════════════════════════════════════════════════════╝
```

## Section 10: Ce rezultă

**Dacă Candidat A e corect**, QNG v10 devine:

1. **Prima teorie substrat-discret care fixează ℏ din structură**
2. **Rezolvă cosmological constant problem natural**
3. **Are predicție falsificabilă**: Λ = 0 exact
4. **Mecanism nou**: cancelare clasic-cuantic (nu SUSY)

**Publicabilitate**: dacă numerele reprezintă argumentele riguroase,
paper în PRL sau Physical Review D e realistic.

**Riscul**: postulatul "E_vacuum = 0" e critique-abil. Un reviewer ar
putea spune "de ce zero? De ce nu 10⁻⁵²?". Răspunsul onest: consistent
cu observații dar nu derivabil.

**Comparație**: QNG ar fi ca Einstein 1917 care a INTRODUS Λ pentru a
face universul static. Acum noi IDENTIFICĂM Λ = 0 cu o specifică ℏ, 
diferit de Einstein dar comparabil ca impact teoretic.
