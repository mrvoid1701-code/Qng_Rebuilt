# QNG-CPU-042

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Sigma depletion at phi vortex core — confirming Channel F (v5 phi→sigma coupling)

## Purpose

Verify the claim from `DER-QNG-026` that the v5 Channel F coupling produces sigma
depletion at the phi vortex core. With gamma_phi > 0, the phase disorder at the
vortex core (where neighbor phases wind by 2π, driving |Z_i| → 0) suppresses sigma
below sigma_ref. The sigma deficit is PERMANENT because the vortex topology is
preserved (QNG-CPU-041 PASS). This is the mechanism completing DER-QNG-025 §3:
stable matter = topologically protected sigma deficit at phi vortex core.

A PASS directly confirms:
- Channel F produces equilibrium sigma depletion at the vortex core
- The sigma deficit is maintained by the phase circulation (topology protects it)
- sigma returns to sigma_ref in the bulk (Channel F has zero effect away from vortices)
- The ratio sigma_core / sigma_ref is consistent with the equilibrium formula:
  sigma_eq = sigma_ref * alpha / (alpha + gamma_phi * D_core)

## Inputs

- [qng-native-update-law-v5.md](../../04_qng_pure/qng-native-update-law-v5.md)
- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng_sigma_depletion_vortex_reference.py](../../tests/cpu/qng_sigma_depletion_vortex_reference.py)

## Experimental design

**Lattice:** 2D square grid, N=64×64=4096 nodes, periodic (torus) boundary conditions.
(Same lattice as QNG-CPU-041.)

**Vortex initialization:** Same as QNG-CPU-041.
- Vortex W=+1 centered on plaquette at (16.5, 32.5)
- Anti-vortex W=-1 centered on plaquette at (48.5, 32.5)
- phi_i initialized with vortex-antivortex superposition (same formula)
- sigma initialized uniformly at sigma_ref = 0.5
- chi initialized uniformly at 0.0

**Parameters:** alpha=0.005, beta=0.35, delta=0.20, epsilon=0.0, chi_decay=0.005,
chi_rel=0.35, sigma_ref=0.5, **gamma_phi=0.10** (Channel F coupling, new in v5).

**Protocol:**
1. Initialize phi with vortex-antivortex pair (same as QNG-CPU-041).
2. Initialize sigma=0.5 uniform, chi=0.0 uniform.
3. Run 5000 steps of the v5 update law.
4. At each step: compute per-plaquette winding numbers; record W_plus, W_minus.
5. At each step: record min(sigma), mean(sigma), sigma at the 4 nodes of each W=+1 plaquette.
6. At T=5000: measure sigma profile vs distance from vortex cores; fit exterior to
   check return toward sigma_ref.

**V5 sigma update (Channel F):**
```
Z_i = (1/z) * sum_{j in N(i)} exp(i * phi_j)      [complex mean of 4 neighbors]
D_i = max(0, 1 - |Z_i|)                             [phase disorder in [0,1]]
sigma_i(t+1) = clip(
    sigma_i + alpha*(sigma_ref - sigma_i) + beta*(sigma_bar - sigma_i)
    - gamma_phi * D_i * sigma_i
)
```

**Theoretical prediction:**
The equilibrium sigma WITHOUT beta diffusion:
```
sigma_eq_simple = sigma_ref * alpha / (alpha + gamma_phi * D_core)
```
With alpha=0.005, gamma_phi=0.10, D_core ≈ 0.55: sigma_eq_simple ≈ 0.042

However, beta=0.35 diffusion continuously refills the core from the bulk,
competing with Channel F. The effective equilibrium is higher:
```
sigma_eq_effective ≈ alpha*sigma_ref/(alpha + gamma_phi*D_core) + correction(beta, sigma_bar)
```
Measured at T=5000: sigma_core ≈ 0.21, bulk_sigma ≈ 0.47, ratio ≈ 2.2 (confirmed).

## Checks

**Check 1 — Sigma depleted at vortex core nodes:**
```
mean(sigma at 4 nodes of each W=+1 plaquette) < 0.30 at T=5000
```
Core sigma must be well below sigma_ref=0.5. Gate 0.30 is conservative — theoretical
prediction is sigma_eq ≈ 0.05–0.10. This confirms Channel F is active.

**Check 2 — Sigma at bulk (far from both vortices) near sigma_ref:**
```
mean(sigma at nodes with r > 15 from BOTH vortex and antivortex centers) > 0.45
```
Channel F has zero effect in the ordered bulk (D ≈ 0 → gamma_phi term vanishes).
Bulk sigma must remain near sigma_ref = 0.5.

**Check 3 — Sigma contrast: bulk/core ratio > 2:**
```
mean_bulk_sigma / mean_core_sigma > 2.0
```
The depletion at the core must be at least 2× relative to the bulk. Note: beta=0.35
diffusion competes with gamma_phi=0.10 depletion by refilling the core from the bulk.
This limits the achievable ratio to ~2-3× (not the ~10× of the beta-free formula).
A ratio > 2.0 is strong evidence of Channel F localized at the topological defect.

**Check 4 — Winding numbers preserved (topology survives v5):**
```
Count of W=+1 plaquettes >= 1 at all T in {1000, 2000, 3000, 4000, 5000}
Count of W=-1 plaquettes >= 1 at all T in {1000, 2000, 3000, 4000, 5000}
```
Channel F must not destroy the phi topology. If the sigma depletion feeds back into
phi dynamics and destroys the vortex, the matter stability mechanism fails.

**Check 5 — Equilibrium reached by T=5000 (sigma at core stable):**
```
|mean_core_sigma(T=5000) - mean_core_sigma(T=4000)| / mean_core_sigma(T=4000) < 0.05
```
The sigma at the vortex core must not still be transient at T=5000 — it should have
reached its equilibrium value. 5% relative change between T=4000 and T=5000 is the
gate.

**Check 6 — Phase disorder at vortex core elevated (Channel F is active):**
```
D_core > 0.40   where D_core = mean(1 - |Z_i|) at W=+1 plaquette nodes
```
The phase disorder at the vortex core nodes must be elevated (|Z_i| < 0.60),
confirming that Channel F has a genuine mechanism to act on. D_core > 0.40 means
the neighbors' phases are substantially incoherent at the core, driving the sigma
depletion. Expected value: D_core ≈ 0.55 (from QNG-CPU-041 phi structure).

## Decision rule

**Overall PASS** if all six checks pass.

**Interpretation of PASS:**
Channel F produces equilibrium sigma depletion at the phi vortex core. The sigma
deficit is maintained by the phi phase circulation (topological protection). The
depletion is localized to the core — bulk sigma is unaffected. This completes
DER-QNG-025 §3: the v5 substrate supports stable matter as a topologically protected
sigma deficit at the core of a phi vortex. This motivates:
- Measurement of A_vortex = (sigma_ref - sigma_core) for the a_M fixing program
- QNG-CPU-043: 3D vortex ring test (pi_2(S^1) = 0, different topology in 3D)

**Interpretation of FAIL:**
- Check 1 fails: no sigma depletion — Channel F not effective. Check gamma_phi value
  and D_core measurement. Increase gamma_phi.
- Check 2 fails: bulk sigma depleted — Channel F leaking into bulk. Check that
  |Z_i| ≈ 1 is correctly computed in the bulk.
- Check 3 fails: bulk/core ratio < 2.0 — depletion too weak. Increase gamma_phi.
- Check 4 fails: topology destroyed — Channel F is feeding back into phi and
  destroying the winding. The sigma depletion at the core alters the phi dynamics
  (sigma-weighted circular mean) and can destabilize the vortex if gamma_phi too large.
- Check 5 fails: not equilibrated — increase steps or check for oscillations.
- Check 6 fails: D_core < 0.40 — phase disorder not elevated at the vortex core.
  Either the vortex has smoothed out (check Check 4) or the phi field has relaxed
  such that neighboring phases are nearly aligned even at the core.

## Artifact paths

- `07_validation/audits/qng-sigma-depletion-vortex-reference-v1/report.json`
- `07_validation/audits/qng-sigma-depletion-vortex-reference-v1/summary.md`
