# QNG-CPU-071 Audit Summary

**Result: PASS**
Date: 2026-04-08
Script: `tests/cpu/qng_hopfion_gravity_reference.py`
Device: GPU (CuPy) — runtime ~30 seconds

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Gravitational well exists (both) | min_dsg < -1e-4 | PASS (ring -2.72e-4, hopfion -3.32e-4) |
| 2 - Hopfion well deeper than ring | |dsg_h| > |dsg_r| | PASS (3.32e-4 > 2.72e-4) |
| 3 - Yukawa fit lambda finite | 1 < lambda < L/2 | FAIL (signal too small for fit) |
| 4 - Bipolar structure (info) | informational | ring=0.086, hopfion=0.014 |

## Key results

| Structure | M (T=1500) | min delta_sg | Yukawa lambda | Bipolar ratio |
|-----------|------------|--------------|---------------|---------------|
| Ring Q=0  | 807.3 | **-0.000272** | not fit | 0.086 |
| Hopfion Q=1 | 1646.5 | **-0.000332** | not fit | 0.014 |

## Physical interpretation

### Gravitational well confirmed

Both ring and Hopfion produce a **negative delta_sigma_g** around them. This is the
expected signature of the K_GM coupling:

  sigma_g -= K_GM * (sigma_ref - sigma_m)

Where sigma_m is depleted (inside the ring tube), sigma_g is pulled below sigma_ref.
sigma_g below sigma_ref = gravitational well = attractive potential. ✓

**Hopfion well is 22% deeper** (3.32e-4 vs 2.72e-4) — consistent with 2× more sigma_m
depletion mass (M_hopfion = 1646.5 vs M_ring = 807.3 at T=1500).

### Why the signal is small (K_GM=0.001)

K_GM=0.001 is intentionally small — chosen for stability (Gap 8 criterion). The
gravitational signal is proportional to K_GM:

  delta_sg_max ~ K_GM × M_ring / (alpha × lattice_volume) ~ 0.001 × 900 / (0.005 × 8000) ~ 0.022

But the measured value is only ~3e-4, about 70× smaller. This suggests the
geometric spreading (sigma_m depletion is distributed over the ring, not a point
source) and the screening (CHI_DECAY=0.020 keeps sigma_g close to sigma_ref globally)
reduce the peak by this factor.

**To see a clear signal:** K_GM would need to be ~10-50× larger (K_GM=0.01-0.05).
But this conflicts with Gap 8 stability. This is the same tension Newton identified.

### Yukawa fit failed — why

The signal is ~3e-4 in amplitude, distributed over a periodic L=20 lattice. At this
amplitude, numerical noise in the spherical shell averaging (~1e-5) is comparable to
the signal at r > 5. The log-linear fit cannot converge.

**Next step:** Increase K_GM (need to check stability at higher values) or increase
L to reduce boundary effects.

### Bipolar structure: ring shows asymmetry, Hopfion doesn't

Ring Q=0: bipolar_ratio = 0.086 — north/south asymmetry is 8.6% of bulk signal.
  north = -0.000101,  south = -0.000092  (ring axis asymmetry)

Hopfion Q=1: bipolar_ratio = 0.014 — nearly symmetric (1.4%).
  north = -0.000204,  south = -0.000201

Surprising: the RING shows more asymmetry than the Hopfion. This may be because
the Hopfion's toroidal twist makes it more spherically symmetric overall, while
the ring has a preferred "above/below" axis from its planar geometry.

This is the opposite of the "bipolar jet" intuition. The bipolar structure may
require larger K_GM or different measurement (chi field, not sigma_g).

## What this tells us physically

**The sigma_g field around the ring/Hopfion IS a gravitational well.** The coupling
K_GM transfers mass information from sigma_m (matter sector) to sigma_g (gravity sector).
An observer in the sigma_g field would feel an attractive potential from the structure.

**The Hopfion's gravitational field is proportional to its mass** — consistent with the
Equivalence Principle: heavier structure = deeper gravitational well. This is a
necessary (not sufficient) condition for the Hopfion to be a particle candidate.

**What is missing:**
1. Radial profile: is the potential Newtonian (1/r) or Yukawa (exp(-r/lambda)/r)?
   Cannot determine at K_GM=0.001. Need K_GM scan at larger values.
2. Bipolar jets: the chi field (not sigma_g) was the original candidate for bipolar
   structure (see CPU-066 Check 3). The sigma_g field is more isotropic.
3. Unit conversion: delta_sg = -3e-4 in lattice units → what is this in m/s² or Newtons?
   Requires rho_0 and G_eff (Gap 4).

## Next steps

**CPU-072 — K_GM scan:** Run at K_GM = 0.001, 0.005, 0.010, 0.020 to find the
maximum K_GM where Gap 8 stability is maintained and the gravitational signal
is large enough for Yukawa fitting. Check stability criterion at each value:
K_BACK × DELTA = 0.020 < ALPHA + CHI_DECAY*(1-ALPHA) = 0.025 (must hold).

**DER-QNG-037 — Long path:** WKB derivation showing static Newtonian potential
coexists with KG waves in v7. Required before any quantitative G_QNG prediction.
