# QNG v7 Gravitational Potential: Double-Yukawa Green's Function

Type: `derivation`
ID: `DER-QNG-035`
Status: `candidate`
Author: `C.D Gabriel`
Date: `2026-04-08`

---

## Motivation

In the single-sigma substrate (v5/v6), the gravitational potential Phi ∝ delta_sigma satisfies
a screened Poisson equation (DER-QNG-012/018) with a single Yukawa kernel:
  Phi(r) ~ G_QNG * M_ring * exp(-r/lambda_screen) / r

In the v7 two-field substrate, matter (sigma_m) sources gravity (sigma_g) through the K_GM
coupling. Newton's review (2026-04-07) identified this as a double-Yukawa convolution structure.
This derivation makes that explicit.

---

## Continuum limit of v7 sigma_g equation (static/quasi-static case)

In the quasi-static limit (dsg/dt ≈ 0), the sigma_g update equation (from DER-QNG-033)
with Channel G and K_GM coupling becomes:

  0 ≈ -ALPHA*s_g + BETA*∇²s_g - K_BACK*chi - K_GM*m_dep

where:
  s_g = delta_sigma_g = sigma_g - sigma_g_ref
  m_dep = sigma_m_ref - sigma_m = -delta_sigma_m

and in the quasi-static chi limit (chi slaved to sigma_g, no K_BACK back-reaction dominance):
  chi ≈ -DELTA/CHI_DECAY * s_g  (from chi equation at equilibrium, see DER-QNG-028 §2)

Substituting:
  0 ≈ -ALPHA*s_g + BETA*∇²s_g + K_BACK*DELTA/CHI_DECAY * s_g - K_GM*m_dep

Define effective restoration:
  alpha_eff = ALPHA - K_BACK*DELTA/CHI_DECAY

For stable system (DER-QNG-034 Fix B: CHI_DECAY ≥ 0.020):
  alpha_eff = 0.005 - 0.10*0.20/0.020 = 0.005 - 1.0 = -0.995 (negative → unstable quasi-static!)

This confirms DER-QNG-034: quasi-static approximation for chi is invalid when K_BACK*DELTA > ALPHA*CHI_DECAY.

**Corrected approach for unstable parameters:** chi is NOT quasi-static; we must use the
full time-dependent system. Below we treat the STATIC limit only with reduced K_BACK
(Fix A or Fix B of DER-QNG-034), so that alpha_eff > 0.

With Fix A (K_BACK = 0.05):
  alpha_eff = 0.005 - 0.05*0.20/0.005 = 0.005 - 2.0   (still negative for current CHI_DECAY=0.005!)

With Fix B (CHI_DECAY = 0.020, K_BACK = 0.10):
  alpha_eff = 0.005 - 0.10*0.20/0.020 = 0.005 - 1.0 = -0.995  (still negative)

Observation: for the quasi-static approximation to hold with alpha_eff > 0, need:
  ALPHA > K_BACK*DELTA/CHI_DECAY
  0.005 > K_BACK*0.20/CHI_DECAY

This requires either very small K_BACK (< 0.005*CHI_DECAY/0.20 = 0.00125 for CHI_DECAY=0.005)
or very large CHI_DECAY (> K_BACK*DELTA/ALPHA = 0.10*0.20/0.005 = 4.0).

**Conclusion for quasi-static path:** The quasi-static approximation for chi is NOT compatible
with the KG-wave parameter regime. The Newtonian limit requires a separate analysis that
averages over the fast KG oscillations (WKB/secular approximation).

---

## Double-Yukawa in the STATIC source limit (chi → 0, K_BACK → 0)

In the limit where KG waves are negligible (K_BACK → 0, or equivalently T → T_Yukawa << T_wave),
the sigma_g equation becomes:

  -ALPHA*s_g + BETA*∇²s_g = K_GM * delta_sigma_m    [Eq. 1]

  -ALPHA_m*s_m + BETA_m*∇²s_m = source_m(r)        [Eq. 2 -- sigma_m, driven by ring/phi]

where delta_sigma_m = sigma_m - sigma_m_ref = s_m, and source_m is the phi-vortex depletion term.

This is a CASCADE of two screened Poisson equations:
  Phi ∝ s_g, sourced by s_m
  s_m sourced by matter (phi vortex ring)

---

## Solving the cascade: Green's functions

**Step 1:** sigma_m field from matter source.

(-ALPHA_m + BETA_m*∇²) s_m = source_m(r)

In Fourier space: s_m(k) = source_m(k) / (-ALPHA_m - BETA_m*k²)

Real-space Green's function (solution for point source at origin):
  G_m(r) = - (1/BETA_m) * exp(-r/lambda_m) / (4π*r)
  lambda_m = sqrt(BETA_m/(z*ALPHA_m))   [screening length for sigma_m]

For alpha_m = alpha = 0.005, beta_m = beta = 0.35, z=6:
  lambda_m = sqrt(0.35/(6*0.005)) = sqrt(11.67) ≈ 3.4 lattice units

**Step 2:** sigma_g field sourced by sigma_m depletion.

(-ALPHA_g + BETA_g*∇²) s_g = K_GM * s_m(r) = K_GM * (G_m * source_m)(r)

Real-space: s_g = (K_GM / BETA_g) * G_g * (G_m * source_m)
           = (K_GM / BETA_g) * (G_g * G_m) * source_m

where G_g is the sigma_g Green's function:
  G_g(r) = - (1/BETA_g) * exp(-r/lambda_g) / (4π*r)
  lambda_g = sqrt(BETA_g/(z*ALPHA_g)) ≈ 3.4 lattice units   (same as lambda_m if alpha_g=alpha_m)

**Convolution G_g * G_m:**

  (G_g * G_m)(r) = integral d³r' G_g(|r-r'|) G_m(r')

This integral of two Yukawa kernels has a known closed-form result in 3D:

For exp(-r/lambda_g)/(4π*r) * exp(-r/lambda_m)/(4π*r):

  (Y_g * Y_m)(r) = [exp(-r/lambda_g) - exp(-r/lambda_m)] / (4π*(lambda_g² - lambda_m²)*r)
                                                       [if lambda_g ≠ lambda_m]

  (Y * Y)(r) = exp(-r/lambda) / (4π*lambda² * r) * (r/lambda + 1) * ...  
               (more complex form for equal screening lengths)
               = r * exp(-r/lambda) / (8π*lambda²)  ... 
               Actually the convolution of two identical Yukawa propagators is:
               (Y * Y)(r) = exp(-r/lambda)/(8π*lambda) 
               (the convolution of 1/(4πr)*e^{-mr} with itself in 3D)

**General result (lambda_g ≠ lambda_m):**

  (G_g * G_m)(r) = [1/(4π*(BETA_g*BETA_m))] * 
                   [exp(-r/lambda_g) - exp(-r/lambda_m)] / [(1/lambda_m² - 1/lambda_g²) * r]

Simplifying: define mu_g = 1/lambda_g, mu_m = 1/lambda_m:

  (G_g * G_m)(r) = 1/(4π*BETA_g*BETA_m*(mu_m² - mu_g²)) * 
                   [mu_m² * exp(-mu_m*r)/r - mu_g² * exp(-mu_g*r)/r]

  = 1/(4π*BETA_g*BETA_m) * [exp(-r/lambda_g)/(r*(1/lambda_g² - 1/lambda_m²)) 
                            - exp(-r/lambda_m)/(r*(1/lambda_g² - 1/lambda_m²))]

---

## Special case: lambda_g = lambda_m = lambda (equal screening lengths)

When alpha_g = alpha_m (same for both fields), lambda_g = lambda_m = lambda = sqrt(BETA/(z*ALPHA)).

The convolution of two identical Yukawa kernels:
  (Y * Y)(r) = integral d³r' [e^{-|r-r'|/lambda}/(4π|r-r'|)] * [e^{-r'/lambda}/(4π*r')]

This is the standard Yukawa self-convolution in 3D. Result:

  (Y * Y)(r) = e^{-r/lambda} * (1 + r/lambda) / (8π*lambda)   × (1/lambda²)
  
  [More precisely: the convolution of exp(-mu*r)/(4π*r) with itself in 3D gives
   exp(-mu*r)/(4π) * (1/2mu) = exp(-mu*r)/(8π*mu), where mu = 1/lambda]

So the gravitational potential for equal screening lengths:

  Phi(r) ∝ s_g(r) ∝ K_GM/(BETA_g*BETA_m) * (G_g * G_m * source_m)(r)
                   ∝ K_GM/(BETA²) * [e^{-r/lambda}/(8π*lambda)] * source_m_total

For a RING source at radius R (integrating over the ring):
  source_m_total = integral over ring of source_m dA ~ 2π*R * M_line (linear depletion density)

  Phi(r_center) ∝ K_GM/(8π*BETA²*lambda) * 2π*R * M_line * e^{-r/lambda}

The equal-lambda case gives a SINGLE Yukawa with the SAME screening length lambda,
but with an EXTRA factor of r from the self-convolution. This makes the profile
decay faster than pure Yukawa at r > lambda, and slower at r < lambda.

---

## Physical implications

1. **Two screening lengths:** If alpha_g ≠ alpha_m (different restoration rates for the two fields),
   the gravitational potential is a DIFFERENCE of two Yukawa terms with different ranges:
     Phi(r) ~ A*exp(-r/lambda_g)/r - B*exp(-r/lambda_m)/r

   This produces:
   - A potential that goes through ZERO at some radius r* (attractive inside, repulsive outside,
     or vice versa)
   - This is qualitatively similar to a Lennard-Jones potential structure
   - Consistent with the non-monotonic force profile found in QNG-CPU-050

2. **Equal screening length (alpha_g = alpha_m):** Phi falls faster than Yukawa for r >> lambda.
   This is a SOFTER gravitational profile than single-sigma v5. May help rotation curves.

3. **K_GM as gravitational coupling constant:**
   The amplitude of the gravitational potential scales as K_GM/(BETA²). Together with the
   matter source integral, this gives:
     G_eff ∝ K_GM * lambda² / BETA
   (since lambda² = BETA/(z*ALPHA), so G_eff ∝ K_GM/(z*ALPHA) -- independent of BETA!)
   This is a new formula for G_QNG in the two-field case.

4. **Observational implication:** The double-Yukawa profile is qualitatively DIFFERENT from
   single-Yukawa. At galactic scales (if lambda ≈ kpc-scale), this could produce:
   - Inner region (r < lambda_m): roughly Newtonian, dominated by near field
   - Outer region (r > lambda_g): exponential fall-off of gravitational enhancement
   - The transition region may mimic MOND-like behavior IF lambda is tuned correctly

---

## New prediction vs single-sigma

| Property | Single-sigma (v5) | Two-field (v7) |
|----------|------------------|----------------|
| Gravitational source | delta_sigma | delta_sigma_m (matter field only) |
| Potential profile | Y_lambda(r) = exp(-r/lambda)/r | (Y_g * Y_m)(r) — double-Yukawa |
| Profile for lambda_g=lambda_m | exp(-r/lambda)/r | exp(-r/lambda)*(1+r/lambda)/r² |
| Profile for lambda_g≠lambda_m | single exponential | difference of two exponentials |
| G_QNG formula | beta/z | k_gm/(z*alpha) |
| Free parameters | lambda (= lambda_screen) | lambda_g, lambda_m, k_gm |

---

## Condition for derivation validity

This derivation is valid when:
1. Chi is quasi-static (K_BACK*DELTA << ALPHA*CHI_DECAY) — see discussion above.
   At current QNG parameters, this requires either very small K_BACK or very large CHI_DECAY.
   The full time-dependent analysis (Section above) must be used for the KG-wave regime.

2. The sigma_m depletion profile is approximately static (ring is long-lived).
   Confirmed: T_lifetime = 2400 steps (CPU-044). Valid for T < 2400.

3. The screened Poisson equation applies (linear regime, small perturbations).
   Valid for K_GM << ALPHA (K_GM=0.001 << ALPHA=0.005 marginally, ratio 5×).

---

## Next step (CPU-064)

Run v7 k_gm scan with:
- Corrected K_GM sign (done, 2026-04-08 commit)
- CHI_DECAY = 0.020 (Fix B from DER-QNG-034) for stability
- Verify: dsg at ring is now POSITIVE (attractive potential)
- Verify: spatial profile decays with distance (Yukawa structure)
- Measure: effective screening length of sigma_g profile

---

## Cross-references

- DER-QNG-033: v7 two-field substrate
- DER-QNG-034: Gap 8 stability analysis (k=0 instability criterion)
- DER-QNG-012: screened Poisson equation (single-sigma)
- GRAV-C1: Phi ∝ delta_sigma (unchanged, now delta_sigma_g)
- QNG-CPU-050: non-monotonic force profile (may be double-Yukawa artifact)
- QNG-CPU-061: sigma_g profile (currently flat due to instability + wrong sign)
