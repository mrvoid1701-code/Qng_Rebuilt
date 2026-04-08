# QNG v7 Gap 8 — Linear Stability Analysis of (sigma_g, chi) System

Type: `derivation`
ID: `DER-QNG-034`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-08`

---

## Problem Statement

CPU-061 (v7 two-field, T=2000) found that chi grows exponentially after T~1000,
collapsing sigma_g globally. This is Gap 8 (chi global instability). The goal here
is to derive the stability condition analytically.

---

## Setup: Linearized v7 equations (sigma_g sector)

Let s_i = sigma_g_i - sigma_g_ref (deviation from reference, small).
Let c_i = chi_i (small).
Fix sigma_m as an external source (sigma_m sector decoupled from sigma_g sector
at leading order by design of v7).

The v7 update equations for sigma_g and chi (linearized, dropping nonlinear terms):

  s_i(t+1) = s_i(t) + ALPHA*(0 - s_i) + BETA*(s_bar_i - s_i) + K_BACK*c_i - K_GM*m_dep_i

  c_i(t+1) = c_i(t)*(1 - CHI_DECAY) + CHI_REL*(s_bar_i - s_i) + DELTA*(0 - s_i)

where m_dep_i = sigma_m_ref - sigma_m_i >= 0 (fixed matter depletion source),
and s_bar_i = (1/z) * sum_{j ~ i} s_j (neighbor average, z=6 for cubic lattice).

---

## Fourier decomposition (Bloch modes)

For a uniform cubic lattice, write s_i = S_k * exp(i k · r_i) and c_i = C_k * exp(i k · r_i).

Define the discrete Laplacian eigenvalue for mode k:
  Lambda(k) = (1/z) * sum_mu [cos(k_mu * a)] - 1  (per lattice axis, a = lattice spacing)

For k=0 (uniform mode): Lambda(0) = 0.
For k ≠ 0:             Lambda(k) < 0.

The BETA*(s_bar - s) term becomes BETA*Lambda(k)*S_k for mode k.
Similarly CHI_REL*(s_bar - s) becomes CHI_REL*Lambda(k)*S_k.

---

## Stability matrix per mode k

Ignoring the forcing term K_GM*m_dep (homogeneous stability analysis):

  S_k(t+1) = [1 - ALPHA + BETA*Lambda(k)] * S_k(t) + K_BACK * C_k(t)

  C_k(t+1) = [DELTA*(Lambda(k)/... via CHI_REL) + (-DELTA)] * S_k(t) + (1-CHI_DECAY) * C_k(t)

More precisely, the DELTA cross-coupling gives -DELTA*s_i, and CHI_REL gives +CHI_REL*Lambda(k)*s_i:

  C_k(t+1) = [-DELTA + CHI_REL*Lambda(k)] * S_k(t) + (1 - CHI_DECAY) * C_k(t)

Define:
  a_k = 1 - ALPHA + BETA*Lambda(k)     (effective "survival" rate of sigma_g mode k)
  b   = 1 - CHI_DECAY                  (survival rate of chi, k-independent)
  d_k = -DELTA + CHI_REL*Lambda(k)     (coupling from sigma_g to chi for mode k)

The 2×2 transfer matrix for mode k:

  M_k = | a_k    K_BACK |
        | d_k    b      |

---

## Eigenvalues of M_k

char poly: (a_k - lambda)(b - lambda) - K_BACK * d_k = 0
lambda² - (a_k + b)*lambda + (a_k*b - K_BACK*d_k) = 0

The product of eigenvalues (determinant):
  |lambda_1 * lambda_2| = a_k*b - K_BACK*d_k
                        = (1-ALPHA+BETA*Lambda)(1-CHI_DECAY) - K_BACK*(-DELTA + CHI_REL*Lambda)
                        = (1-ALPHA+BETA*Lambda)(1-CHI_DECAY) + K_BACK*DELTA - K_BACK*CHI_REL*Lambda

For complex eigenvalues (oscillatory regime), both eigenvalues have modulus:
  |lambda|² = determinant of M_k
  (when discriminant < 0, i.e. (a_k + b)² < 4*(a_k*b - K_BACK*d_k))

Stability condition: |lambda|² < 1 for all modes k.

---

## Case 1: k = 0 (uniform mode)

Lambda(0) = 0, so a_0 = 1-ALPHA, d_0 = -DELTA:

  |lambda|² = (1-ALPHA)(1-CHI_DECAY) + K_BACK*DELTA

Stability requires |lambda|² < 1:

  (1-ALPHA)(1-CHI_DECAY) + K_BACK*DELTA < 1
  1 - ALPHA - CHI_DECAY + ALPHA*CHI_DECAY + K_BACK*DELTA < 1
  K_BACK*DELTA < ALPHA + CHI_DECAY - ALPHA*CHI_DECAY
  K_BACK*DELTA < ALPHA + CHI_DECAY*(1 - ALPHA)

**Stability criterion (k=0 mode):**

  K_BACK * DELTA < ALPHA + CHI_DECAY * (1 - ALPHA)           [STAB-0]

For small ALPHA, CHI_DECAY (as in QNG substrate):
  K_BACK * DELTA < ALPHA + CHI_DECAY   (approximately)

---

## Numerical evaluation at QNG v7 parameters

Parameters: ALPHA=0.005, CHI_DECAY=0.005, DELTA=0.20, K_BACK=0.10, BETA=0.35, CHI_REL=0.35

LHS: K_BACK * DELTA = 0.10 * 0.20 = 0.0200
RHS: ALPHA + CHI_DECAY*(1-ALPHA) = 0.005 + 0.005*0.995 = 0.00998 ≈ 0.010

  0.0200 > 0.010   →   CONDITION VIOLATED by factor 2.

The k=0 (uniform) mode is UNSTABLE at current parameters.

|lambda|² (k=0) = (0.995)(0.995) + 0.020 = 0.990 + 0.020 = 1.010
|lambda| = sqrt(1.010) ≈ 1.005

Growth rate per step: |lambda| - 1 ≈ 0.005 (5 per mille per step).
Doubling time: ln(2)/0.005 ≈ 139 steps.

Over 1000 steps: growth factor = 1.005^1000 = e^(0.005*1000) = e^5 ≈ 148×.

This is consistent with CPU-061: chi_rms grows from ~0.001 at T=1000 to ~0.38 at T=2000 (~380×,
but starting from a small-but-nonzero seed, exponential from ~T=800 onward).

---

## Case 2: k ≠ 0 (finite wavenumber modes)

For k ≠ 0, Lambda(k) < 0. In particular, Lambda(k) ≥ -2 (minimum eigenvalue of discrete Laplacian
per axis, for k = π/a). For a 3D cubic lattice, Lambda_min = -2 (in units where a=1).

Actually: Lambda(k) = (1/z)*sum_mu[cos(k_mu) - 1] ranges from 0 (k=0) to -1 (k=π for all axes, z=6).

Wait: for k = (π,0,0): Lambda = (1/6)*(cos(π)-1 + cos(0)-1 + cos(0)-1)*... 

Let me be precise: with z=6 for a 3D cubic lattice:
Lambda(k) = (1/6) * sum_{mu=±x,±y,±z} cos(k_mu) - 1
          = (cos(kx) + cos(ky) + cos(kz))/3 - 1

For k=(pi,pi,pi): Lambda = (cos(π)+cos(π)+cos(π))/3 - 1 = (-1-1-1)/3 - 1 = -1 - 1 = -2.

Hmm: Lambda(k) = (1/z) * sum_j (sigma_bar - sigma_i) per mode = eigenvalue of discrete Laplacian / sigma_i.

More carefully:
  s_bar_i = (1/6) * sum_{<ij>} s_j
  s_bar_i - s_i = (1/6)*sum_j s_j - s_i = (1/6)*sum_j(s_j - s_i)

For a Fourier mode s_j = exp(ik·r_j):
  s_bar - s = (1/6)*sum_mu [exp(ik_mu) + exp(-ik_mu)] * s - s
            = [(cos(kx)+cos(ky)+cos(kz))/3 - 1] * s
            = Lambda(k) * s

So Lambda(k) = (cos(kx)+cos(ky)+cos(kz))/3 - 1 ∈ [-2, 0].

For the smallest nonzero mode in an L=20 box: k_min = 2π/L = 2π/20 = π/10.
Lambda(k_min, 0, 0) = (cos(π/10) + 1 + 1)/3 - 1 = (0.951 + 2)/3 - 1 = 0.984 - 1 = -0.016.

For this mode:
  a_k = 1 - ALPHA + BETA*Lambda = 1 - 0.005 + 0.35*(-0.016) = 0.995 - 0.0056 = 0.989
  d_k = -DELTA + CHI_REL*Lambda = -0.20 + 0.35*(-0.016) = -0.20 - 0.0056 = -0.206

  |lambda|² = a_k*b - K_BACK*d_k
            = 0.989 * 0.995 - 0.10 * (-0.206)
            = 0.984 + 0.0206
            = 1.005

Still > 1! The smallest nonzero mode is also marginally unstable at L=20.

For larger k (shorter wavelengths), Lambda(k) becomes more negative, and a_k decreases,
eventually making |lambda|² < 1. The BETA term stabilizes short-wavelength modes.

**Crossover wavenumber k* (modes with |lambda|² = 1):**

Setting |lambda|² = 1:
(1-ALPHA+BETA*L)(1-CHI_DECAY) + K_BACK*(DELTA - CHI_REL*L) = 1
where L = -Lambda(k) ≥ 0.

Expanding:
(1-ALPHA)(1-CHI_DECAY) + (-BETA*L)(1-CHI_DECAY) + K_BACK*DELTA - K_BACK*CHI_REL*L = 1
[unstable condition from k=0] + L*[-BETA*(1-CHI_DECAY) - K_BACK*CHI_REL] = 0

Let R_0 = (1-ALPHA)(1-CHI_DECAY) + K_BACK*DELTA - 1  (= |lambda|²_k=0 - 1 > 0 for instability)

R_0 - L * [BETA*(1-CHI_DECAY) + K_BACK*CHI_REL] = 0

L_crit = R_0 / [BETA*(1-CHI_DECAY) + K_BACK*CHI_REL]

Numerically:
R_0 = 0.010
BETA*(1-CHI_DECAY) + K_BACK*CHI_REL = 0.35*0.995 + 0.10*0.35 = 0.348 + 0.035 = 0.383

L_crit = 0.010 / 0.383 = 0.026

So modes with -Lambda(k) > 0.026 are stable. In 3D cubic:
Lambda(k,0,0) = cos(k)/3 + 2/3 - 1 = (cos(k)-1)/3
|Lambda(k,0,0)| = (1-cos(k))/3 > 0.026
1 - cos(k) > 0.078
cos(k) < 0.922
k > arccos(0.922) = 0.395 rad

In units of lattice constant: k > 0.395. Physical wavelength: lambda < 2π/0.395 = 15.9 lattice units.

**Jeans length:** L_J ~ 16 lattice units (modes shorter than L_J = 16a are stable; longer modes are unstable).

For L=20 box: the only modes with wavelength > 16 are k=0 (uniform, λ=∞) and possibly
the lowest mode λ=L=20. Indeed, we found λ=20 mode has |lambda|²=1.005 (marginally unstable).
λ=10 mode: Lambda = (cos(2π/10)-1)/3 = (0.809-1)/3 = -0.064 > -0.026. Wait, that's less negative.

Let me recheck k=2π/10=π/5:
Lambda = (cos(π/5)+2)/3 - 1 = (0.809+2)/3 - 1 = 2.809/3 - 1 = 0.936 - 1 = -0.064

|lambda|² = (1-0.005+0.35*(-0.064))(1-0.005) + 0.10*(0.20 - 0.35*0.064)
           = (0.995 - 0.022)*0.995 + 0.10*(0.20 - 0.022)
           = 0.973*0.995 + 0.10*0.178
           = 0.968 + 0.018
           = 0.986 < 1  ✓ STABLE

So the λ=20 (k=2π/20=π/10) mode: |lambda|²=1.005 (barely unstable).
The λ=10 (k=2π/10=π/5) mode: |lambda|²=0.986 (stable). ✓

**Summary: the instability is confined to modes with wavelength λ > ~16 lattice units.**
In a L=20 box, only the k=0 mode and the longest-wavelength mode (λ=20) are unstable.
The instability is an INFRARED (long-wavelength) instability — a lattice-scale Jeans instability.

---

## Stability condition: summary

**[STAB-0]** k=0 mode stable iff:
  K_BACK * DELTA < ALPHA + CHI_DECAY * (1 - ALPHA)

**[STAB-k]** All modes stable iff additionally:
  L_J << L_box, equivalently L_box < L_J = 2π / arccos(1 - 3*L_crit)
  where L_crit = [(1-ALPHA)(1-CHI_DECAY) + K_BACK*DELTA - 1] / [BETA*(1-CHI_DECAY) + K_BACK*CHI_REL]

The Jeans length at current parameters:
  L_J ≈ 2π/0.395 ≈ 16 lattice units

For a stable simulation: need L_box << L_J.
At L=20: L_box > L_J → marginally unstable (confirmed by CPU-061).
At L=10: L_box < L_J → all modes stable (would not exhibit Gap 8 instability).

---

## Physical interpretation

This is a discrete-lattice analog of the **Jeans instability**: the gravitational field (sigma_g)
and its conjugate momentum (chi) form a system where the K_BACK*DELTA feedback loop
(KG wave mechanism) can overcome the damping terms (ALPHA + CHI_DECAY) for long wavelengths.

The same mechanism that produces Klein-Gordon waves (K_BACK*DELTA > 0) produces
Jeans instability for modes with wavelength > L_J.

This reveals a **structural tension in QNG v7:**
  - KG waves require: K_BACK * DELTA > 0 (and large enough for propagation above diffusion)
  - Jeans stability requires: K_BACK * DELTA < ALPHA + CHI_DECAY

These constraints are NOT mutually exclusive if ALPHA, CHI_DECAY are tuned appropriately,
but they compete: making KG waves stronger (larger K_BACK*DELTA) always shrinks L_J.

---

## Fixes

### Fix A: Reduce K_BACK*DELTA product

K_BACK_max = (ALPHA + CHI_DECAY) / DELTA = 0.010 / 0.20 = 0.05

With K_BACK=0.05 (and DELTA=0.20): K_BACK*DELTA = 0.01 ≤ threshold.
L_J → ∞ (k=0 mode exactly at stability boundary).

Consequence: wave speed v = sqrt(K_BACK*CHI_REL/6) = sqrt(0.05*0.35/6) = 0.054 (was 0.076).
KG mass² = K_BACK*DELTA = 0.01 (halved). Wave propagation becomes weaker.

### Fix B: Increase CHI_DECAY

New CHI_DECAY_min = K_BACK*DELTA - ALPHA = 0.020 - 0.005 = 0.015 (3× larger).
Consequence: KG mass² m² = k_back*delta (unchanged), but chi field damped 3× faster.
Wave propagation still works, but chi content per step is smaller.

### Fix C: Increase ALPHA

New ALPHA_min = K_BACK*DELTA - CHI_DECAY = 0.015 (3× larger).
Consequence: screening length lambda_screen = sqrt(BETA/(z*ALPHA)) decreases by sqrt(3).
Yukawa halo becomes shorter range.

### Fix D: Nonlinear chi saturation (Einstein suggestion)

Add: chi_i += -lambda_chi * chi_i^3
This saturates chi at chi_max ~ sqrt((K_BACK*DELTA - ALPHA - CHI_DECAY)/lambda_chi).
Avoids changing any linear parameters. Requires determining lambda_chi.
Not derivable from current gradient-flow action principle without modifying E[sigma,chi,phi].

**Recommended Fix B** (increase CHI_DECAY to 0.015):
- Preserves ALPHA (keeps lambda_screen unchanged)
- Preserves K_BACK (keeps wave speed and KG mass)
- Changes chi_rms at ring: smaller chi content (chi ~ K_BACK*delta_sg/CHI_DECAY, now 3× less)
- Stability: K_BACK*DELTA = 0.02, threshold = 0.005 + 0.015*0.995 = 0.020 → exactly at boundary
- For safety: CHI_DECAY = 0.020 gives margin: threshold = 0.005 + 0.020*0.995 = 0.025 > 0.020 ✓

---

## Impact on previous results

| Test | Impact |
|------|--------|
| CPU-060 (ring M=954.9) | Not affected (sigma_m decoupled, k=0 instability still in sigma_g but irrelevant for sigma_m) |
| CPU-061 (Yukawa profile) | Will be affected — with stable parameters, sigma_g profile will be genuine Yukawa |
| CPU-062 (k_gm scan) | Will be affected — dsg values change in sign (already fixed) and stability |
| CPU-063 (spectrum at T=1000) | Minimal impact — T=1000 is before instability onset at current params; E_ring unaffected |

---

## Cross-references

- Gap 8 identification: QNG-CPU-061 audit summary
- DER-QNG-033: v7 two-field substrate definition
- DER-QNG-028/030: KG wave equation (requires K_BACK*DELTA > 0)
- QNG-CPU-054: wave equation confirmed at K_BACK=0.10 (short run, instability not manifest)
- NOTE-QNG-013: Lorentz covariance gap (related structural gap)
