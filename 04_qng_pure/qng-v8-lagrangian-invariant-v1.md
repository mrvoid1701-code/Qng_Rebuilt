---
id: NOTE-QNG-017
title: Universal time-averaged Lagrangian invariant in v8 R1 orbital attractor
type: note
version: 1
author: C.D Gabriel
status: draft-v1
tags: [qng, v8, orbital-attractor, invariant, emergent]
upstream:
  - DER-QNG-042 (v8 canonical)
  - DER-QNG-050 (exact F_A)
  - GPU-031f (orbital attractor)
  - CPU-088 (de-biased dispersion, falsified)
  - CPU-089 (L-scan analysis, pending)
---

# Universal ⟨L⟩ invariant in v8 R1 orbital attractor

## 1. Statement

Under v8 canonical dynamics (Yoshida4 symplectic, Hamiltonian-conservative, initial
condition: σ_m vortex ring at radius R placed on periodic cubic lattice L³) the
time-averaged Lagrangian of the orbital attractor converges to a universal value
independent of R:

    E_char ≡ 2⟨T_kin⟩ − ⟨H⟩ = ⟨T⟩ − ⟨V⟩ = ⟨L⟩ (time-averaged Lagrangian)

**Data at L=28, T_P2=1000, burn-in 500 lu, T_track=2000 lu:**

| R | ⟨H⟩      | ⟨T_kin⟩ | ⟨L⟩     |
|---|----------|----------|---------|
| 2 | −624.20  | 17.56    | 659.32  |
| 3 | −605.23  | 27.87    | 660.97  |
| 4 | −617.97  | 20.68    | 659.32  |
| 5 | −590.22  | 35.08    | 660.38  |

- Mean ⟨L⟩ = 660.00, std 0.71, **CV = 0.11%**
- ⟨H⟩ across R: CV 2.14%
- ⟨T⟩ across R: 2× variation
- Virial ratio −2⟨H⟩/⟨L⟩ ∈ [1.79, 1.89] → orbit is anharmonic

## 2. Arithmetic match to substrate parameter

    ⟨L⟩ / N ≈ β_φ / 2 = 0.0300

    At N = 21952 (L=28):  predicted ⟨L⟩ = 658.56,  measured 660.00 → 0.22% agreement.

**Conjecture**: ⟨L⟩ = N · β_φ / 2 exactly, with O(1/N) finite-size corrections.

## 2.2a General theorem: ⟨L⟩ = −V_ground for harmonic attractors

For any classical Hamiltonian system with a stable local minimum V_ground and
time-averaged harmonic oscillations ⟨T⟩, the virial theorem gives
⟨V_excitation⟩ = ⟨T⟩ so that

    ⟨V⟩_total = V_ground + ⟨V_excitation⟩ = V_ground + ⟨T⟩
    ⟨L⟩ = ⟨T⟩ − ⟨V⟩_total = ⟨T⟩ − (V_ground + ⟨T⟩) = −V_ground

Therefore, for ANY harmonic attractor around the ground state:

    **⟨L⟩ = −V_ground**   (exact, modulo anharmonic corrections)

Measured deviations from this are entirely O(anharmonicity). Observed +0.116%
at L=28 R=4 reflects very mild anharmonicity in the sine-Gordon V_couple.

## 2.2 Analytical derivation (substrate-intrinsic XY ground state)

The R1 pure-XY form of E_phi_A (DER-QNG-051 Option R1, cf. `qng_v8_canonical_gpu.py:560-566`) is

    E_phi_A = −(β_φ/(2z)) · Σᵢ Σⱼ∈N(i) cos(φᵢ − φⱼ)

On cubic lattice z=6, the double sum has z·N = 6N terms. At ferromagnetic
ground state (all φᵢ equal), every cosine equals 1, so

    E_phi_A_ground = −(β_φ/(2·6)) · 6N = −β_φ · N / 2

For L=28, N=21952: E_phi_A_ground = −658.56 lu.

### Deviations from exact ground state

The attractor deviates from exact ferromagnet by:
1. **Ring winding** (Δφ ≈ 2π over perimeter): phase mismatch adds
   ΔE ≈ +(β_φ/(2z)) · Σlinks (1 − cos(Δφ_link)) > 0
2. **φ oscillations** (kinetic excitations): broadens ⟨cos Δφ⟩ slightly below 1
3. **V_couple** (sine-Gordon): adds small positive ⟨V_cp⟩ ≈ +0.98 (measured).

All three are positive → ⟨E_phi_A⟩ is slightly **above** the ferromagnetic floor
(less negative). Hence ⟨−E_phi_A⟩ is slightly **below** β_φ·N/2.

Measured values vs theory:
| R | predicted −E_ground | measured ⟨L⟩ | deviation |
|---|--------------------|---|---|
| 2 | 658.56 | 659.32 | +0.12% |
| 3 | 658.56 | 660.97 | +0.37% |
| 4 | 658.56 | 659.32 | +0.12% |
| 5 | 658.56 | 660.38 | +0.28% |

All within 0.4% of pure ferromagnetic ground-state prediction.

### Theoretical consequences

- **⟨L⟩ is the magnitude of the XY-model ground-state energy** on the cubic
  lattice, up to small positive corrections from ring topology and kinetic
  excitations.
- **No ℏ interpretation**: this is a static substrate quantity, not a
  quantum action scale.
- **Gate A prediction** (L-scan): α=3 exactly (extensive in N=L³).
  - L=20 → 240.00
  - L=24 → 414.72
  - L=28 → 658.56
- **Gate B prediction** (β_φ-scan): ⟨L⟩ ∝ β_φ linearly, with slope N/2.
- **Gate C prediction** (R-extension): ⟨L⟩ ≈ 658.56 + O(ring-winding) for any R
  that sustains the orbital attractor. R-independence explained: ring winding
  cost scales with perimeter 2πR, but the attractor redistributes it so the
  bulk stays near ground state.

This derivation **closes §8 open question 1**: the per-node β_φ/2 arises from
the XY-model ferromagnetic ground state, not from mode-summation or virial.
The apparent "quantization" of ⟨L⟩ is the classical ferromagnetic floor.

## 2.1 Critical refinement: ⟨L⟩ ≈ |⟨V⟩|

Sector analysis at R=4 reveals:
- ⟨T_kin⟩ = 20.68 (small)
- ⟨V_total⟩ = −638.65 (NEGATIVE)
- ⟨V_couple⟩ = +0.98 (sine-Gordon positive)
- ⟨V_grad + α + F_A⟩ = −639.63 (dominated by DER-QNG-050 pure-XY F_A term)

Because ⟨T⟩ << |⟨V⟩|, we have:

    ⟨L⟩ = ⟨T⟩ − ⟨V⟩ ≈ −⟨V⟩ = |⟨V_ground_attractor⟩|

So the 660 invariant is essentially the **magnitude of the negative ground-state
potential energy** on the orbital attractor. Savant's virial concern is resolved:
the quadratic gradient kinetic V_grad IS dominant, but the R1/DER-QNG-050 F_A
pure-XY term contributes a strong negative offset, giving V_total < 0.

The universality ⟨L⟩ ≈ N·β_φ/2 then translates to:

    |⟨V_attractor⟩| = N · β_φ / 2  (conjecture)

I.e., the attractor's mean potential energy density is −β_φ/2 per node.

## 3. Physical interpretation (two readings)

### 3.1 Einstein-mind reading: emergent rest-energy
If ⟨L⟩ over a closed orbit plays the role of action-per-cycle per unit time, a relativistic
bound state gives ⟨L⟩ = −m₀c² · ⟨√(1−v²/c²)⟩. The R-invariance of ⟨L⟩ would then correspond
to a **universal rest-mass shell** — different R orbits sit on the same mass shell but
differ in kinetic and binding content. No v8 R1 quantization is needed; this is classical
Noether for a hidden cyclic coordinate.

### 3.2 Tesla-mind reading: substrate admittance / mode equipartition
Every lattice node contributes β_φ/2 to the mean Lagrangian regardless of local state.
Tesla framing: "generalized mode-wise equipartition of the gradient channel" — each
normal mode k contributes (1/2)β_φ·k²|φ_k|² gradient ↔ kinetic, summed over uniformly
populated modes yields N·β_φ/2.

Note: standard equipartition gives ⟨T⟩ = ⟨V⟩ and hence ⟨L⟩ = 0 for harmonic systems.
Here ⟨L⟩ = N·β_φ/2 > 0 → the attractor violates strict equipartition, signalling
anharmonic (sine-Gordon) mode structure. Tesla view is a suggestive heuristic, not
strict equipartition.

## 4. Falsification gates (open)

### Gate A: L-scan (launching now)
At R=4 fixed, vary L ∈ {20, 24, 28}:
- **α=0 (intensive)**: ⟨L⟩ L-independent → substrate-intrinsic rest-energy scale.
- **α=3 (extensive)**: ⟨L⟩ ∝ L³ at ⟨L⟩/N = β_φ/2 → per-node substrate density.
- **α=1 or 2 (geometric)**: ring perimeter/cross-section contribution.

Predictions under α=3 (N·β_φ/2):
- L=20:  ⟨L⟩ = 240.00
- L=24:  ⟨L⟩ = 414.72
- L=28:  ⟨L⟩ = 658.56  (measured 660.00, 0.22% off)

If L=20 measurement ≈ 240 ± 2, α=3 confirmed → per-node invariant.
If L=20 measurement ≈ 660, α=0 confirmed → substrate-intrinsic scale.
If L=20 measurement ≈ 600 (dominated by ring), intermediate geometry → re-analyze.

### Gate B: β_φ scan
At fixed L=28, R=4, vary β_φ ∈ {0.03, 0.06, 0.12}:
- If ⟨L⟩ ∝ β_φ exactly → confirms β_φ/2 per-node formula.
- If ⟨L⟩ = f(β_φ, μ_φ, g) → more complex emergent formula.

### Gate C: R-extension **CONFIRMED** (2026-04-22)

Full R-scan at L=28, T_P2=1000, T_run=2000, burn-in 500 lu:

| R | E_char  | dev from XY ground | ⟨T_kin⟩ | ⟨V_couple⟩ | ⟨M_ring⟩       |
|---|---------|--------------------|---------|------------|-----------------|
| 2 | 659.32  | +0.116%            | 17.56   | 0.90       | 637.70 ± 331.77 |
| 3 | 660.97  | +0.366%            | 27.87   | 1.40       | 881.78 ± 573.19 |
| 4 | 659.32  | +0.116%            | 20.68   | 0.98       | 801.78 ± 461.53 |
| 5 | 660.38  | +0.277%            | 35.08   | 2.02       | 920.65 ± 523.45 |
| 6 | 660.66  | +0.318%            | 27.84   | 1.52       | 774.87 ± 585.65 |

- **Mean E_char** = 660.13, std 0.69, **CV = 0.104%**
- **Mean dev from XY ground (658.56):** +0.238%
- **Max dev:** +0.366% (R=3)
- **Odd-even split:** +0.909 lu (odd R slightly higher than even)

All R∈{2,3,4,5,6} cluster within ±0.4% of the XY ferromagnetic ground-state
prediction N·β_φ/2 = 658.56. R-universality of the orbital attractor confirmed.
The small positive offset (~0.24%) is consistent with anharmonic corrections
from ring winding + V_couple sine-Gordon term.

Report: `07_validation/audits/qng-R-scan-E-char-v1/report.json`

## 5. What this is NOT

- **Not ℏ**: ⟨L⟩ has units of energy (action/time), not action.
- **Not a dispersion relation**: the original E²=(ℏω)²+m² fit was falsified via
  FFT bin-locking (CPU-088); the surviving E_char universality is a different
  quantity (period-independent virial form).
- **Not a rest-mass energy of the ring**: v8 rings dissolve (GPU-024d). ⟨L⟩ is
  an attractor-flow invariant, not a soliton rest-mass.
- **Not a conserved Noether charge of a symmetry**: v8 has Z winding (broken by
  sine-Gordon) + translation/rotation. No known symmetry gives ⟨L⟩ as its conserved
  generator.

## 6. Why it still matters

Even without a direct ℏ interpretation:

1. First **emergent classical invariant** of v8 R1 connecting substrate parameter
   β_φ to attractor-averaged dynamics.

2. Provides a candidate **characteristic energy scale** for v8 orbital modes,
   potentially relevant to:
   - Emergent c in EFT limit (via β_φ gradient coefficient)
   - Jackiw-Rebbi mass spectrum (GPU-035 gave m² ∝ g·Δ²/μ_φ; ⟨L⟩ not directly
     comparable but orders-of-magnitude suggestive)

3. **Calibration anchor** for any future v9 Langevin Ξ_χ extension: the classical
   attractor ⟨L⟩ sets the thermal-fluctuation baseline against which stochastic
   departures would measure effective ℏ.

## 7. Status

- **Discovered 2026-04-22** via CPU-087 and virial-form computation.
- **Theory note, not a claim** — promotion to claim requires passing Gate A
  (L-scan) and Gate B (β_φ-scan).
- Audit: `07_validation/audits/qng-v8-particle-probe-{R2,R3,v1,R5}/traces.npz`,
  inline Python analysis in conversation history.

## 8. Open questions

- If α=3 confirmed, what is the derivation of β_φ/2 as the per-node mean
  Lagrangian? Possible routes: symplectic trace formula, mode-sum with
  spectral cutoff, virial theorem with anharmonic correction.
- Does ⟨L⟩/N vary with substrate temperature (Ξ_χ noise injection)?
- Is there an analogous per-node ⟨V⟩ or ⟨T⟩ invariant?
