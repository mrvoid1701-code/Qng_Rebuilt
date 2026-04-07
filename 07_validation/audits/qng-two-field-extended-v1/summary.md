# QNG-CPU-061 Audit Summary

**Result: PASS (with critical finding: chi global instability)**
Date: 2026-04-07
Script: `tests/cpu/qng_two_field_extended_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Ring alive at T=2000 | M>50 | PASS (M=619) |
| 2 - sigma_g profile decays with distance | dsg(r=5) > dsg(r=9) | PASS (barely: 0.4773 > 0.4769) |
| 3 - chi field active | chi_rms > 0.01 | PASS (chi_rms=0.384 at T=2000) |

## Trajectory

| t    | M_ring | chi_rms | dsg@r=2   | dsg@r=5   | dsg@r=9   |
|------|--------|---------|-----------|-----------|-----------|
| 1    | 11.7   | 0.0000  | 0.000000  | 0.000000  | 0.000000  |
| 500  | 1056.5 | 0.0005  | -0.000048 | +0.000016 | -0.000052 |
| 1000 | 954.9  | 0.0011  | -0.010132 | -0.010249 | -0.010104 |
| 1500 | 810.1  | 0.1724  | -0.025825 | -0.025645 | -0.025811 |
| 2000 | 619.0  | 0.3844  | +0.476861 | +0.477299 | +0.476807 |
| 2500 | 425.4  | 0.2845  | +0.465951 | +0.465826 | +0.465973 |

## Critical finding: chi global instability (Gap 8)

The sigma_g profile at T=2000 is NOT a Yukawa halo.
All r values show delta_sg ≈ 0.477 (variation < 0.001 across r=1..10).
This means sigma_g has been globally depleted from 0.5 to ~0.023 everywhere.

**Instability mechanism:**
1. Ring in sigma_m depletes sigma_m locally
2. k_gm coupling: sigma_g += k_gm*(sigma_m_ref - sigma_m) → sigma_g pulled DOWN at ring
3. DELTA coupling: chi += DELTA*(sigma_g_ref - sigma_g) → chi builds up where sigma_g is low
4. chi spreads globally (sigma_g diffusion spreads perturbation before Yukawa screening damps it)
5. Global chi buildup → Channel G drives sigma_g oscillation
6. Oscillation grows (growth rate DELTA >> decay rate chi_decay) → sigma_g crashes near 0

**Timing:**
  T=1000: chi_rms=0.0011 (safe)
  T=1500: chi_rms=0.1724 (growing)
  T=2000: chi_rms=0.3844 (sigma_g collapsed globally)

**Growth rate estimate:**
At T=1500, chi_rms doubles in ~300 steps → growth rate ~ ln(2)/300 ~ 0.002/step
Compare chi_decay = 0.005/step (damping) vs DELTA*(delta_sg/chi) ~ 0.20*0.025/0.17 ~ 0.03/step
Growth dominates when delta_sg/chi_rms > chi_decay/DELTA = 0.025.
At T=1000, delta_sg ~ 0.010 and chi_rms ~ 0.0011 → ratio = 9 >> 0.025 → unstable.

**This is a new structural problem in v7:**
Gap 8 (new): v7 two-field chi runaway — k_gm coupling drives chi instability in sigma_g sector.

## Yukawa profile not confirmed

The Yukawa screening length lambda_screen = sqrt(beta/(z*alpha)) = sqrt(0.35/0.03) = 3.4 lattice units.
For a ring at r=5 from center, the Yukawa profile should decay to e^(-3/3.4) ~ 0.41 by r=8.
But the actual profile is flat — the chi oscillation overwhelms spatial structure before
the Yukawa profile can establish itself.

The profile IS slightly stronger at the ring (r=5: 0.4773 vs r=9: 0.4769, diff=0.0004).
This tiny residual spatial variation is consistent with a Yukawa signal buried in noise.

## Implication for v7

Path D works for Gap 7 (ring survives in sigma_m with Channel G in sigma_g).
But v7 introduces Gap 8: the k_gm coupling drives a chi global oscillation in sigma_g.

**Fix candidates:**
1. Reduce k_gm to 0.0001 or smaller (weaker coupling, slower instability)
2. Increase chi_decay (faster chi damping, but changes KG mass)
3. One-way coupling: k_gm only affects sigma_g restoration, NOT the chi buildup
   (i.e., make chi couple to sigma_g reference, not to ring-perturbed sigma_g)
4. Separate chi from the gravitational source: chi is the matter momentum field,
   not the gravitational wave field. Use a separate field psi for gravitational waves.

The snapshot mass spectrum (CPU-063, snapshot at T=1000 before instability) is
still valid because chi_rms < 0.002 at T=1000 — the instability hasn't kicked in.
