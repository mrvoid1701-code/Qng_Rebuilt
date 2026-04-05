# QNG-CPU-041

Type: `prereg`
Status: `locked`
Author: `C.D Gabriel`
test_class: `structural_prediction`

## Title

Phi vortex stability — confirming topological protection of sigma deficit in 2D

## Purpose

Test whether a phi vortex with winding number W=+1 in the 2D QNG substrate maintains
its winding number over 5000 steps (no decay), preserves a depleted sigma core, and
produces a screened exterior profile consistent with K_0(r/lambda) (2D Yukawa).

This is a POSITIVE result if the vortex survives: topological protection of sigma
deficit is confirmed. The winding number W is conserved by smooth evolution —
the vortex cannot annihilate unless it meets an anti-vortex.

A PASS directly supports DER-QNG-025 Section 3: stable matter in QNG requires phi
topology. It motivates the 3D vortex ring test (QNG-CPU-042) and the a_M fixing
program.

If the vortex decays: the substrate dynamics are destroying winding (should not
happen by topology — investigate for numerical phase wrapping artifacts or
update law with accidental W-violation).

## Inputs

- [qng-matter-stability-v1.md](../../04_qng_pure/qng-matter-stability-v1.md)
- [qng-native-update-law-v4.md](../../04_qng_pure/qng-native-update-law-v4.md)
- [qng_phi_vortex_reference.py](../../tests/cpu/qng_phi_vortex_reference.py)

## Experimental design

**Lattice:** 2D square grid, N=64×64=4096 nodes, periodic (torus) boundary conditions.

**Vortex initialization:** Vortex-antivortex pair (required: net W=0 on torus).
- Vortex W=+1 centered on plaquette at (L/4 + 0.5, L/2 + 0.5) = (16.5, 32.5)
- Anti-vortex W=-1 centered on plaquette at (3L/4 + 0.5, L/2 + 0.5) = (48.5, 32.5)
- phi_i = atan2(y_i - y_vortex, x_i - x_vortex) + atan2(y_i - y_antivortex, x_i - x_antivortex) + pi
  (superposition of vortex and anti-vortex phases, with anti-vortex contributing -1 winding)
- sigma initialized uniformly at sigma_ref = 0.5 (vortex core will self-organize)
- chi initialized uniformly at 0.0

**Parameters:** alpha=0.005, beta=0.35, delta=0.20, epsilon=0.0 (Channel E off for
clean topology test), chi_decay=0.005, chi_rel=0.35, sigma_ref=0.5.

**Protocol:**
1. Initialize phi with vortex-antivortex pair (centers on plaquettes, not nodes).
2. Initialize sigma=0.5 uniform, chi=0.0 uniform.
3. Run 5000 steps of the v4 update law (epsilon=0 reduces to v3 sigma/chi update,
   with phi evolving under wrapped phase diffusion toward sigma-weighted neighbors).
4. At each step: compute per-plaquette winding numbers for all 63×63=3969 plaquettes.
5. Record: W_plus (count of +1 plaquettes), W_minus (count of -1 plaquettes), max|W|
   per step. Record sigma profile at step 0, 1000, 2000, 5000.
6. At final step: locate vortex cores (connected region of plaquettes with W=+1 or
   W=-1), measure sigma at core center, fit sigma exterior to K_0(r/lambda).

**Winding number diagnostic (per plaquette, exact discrete formula):**
```
W_plaquette = round( (1/2pi) * sum of angle_diff around 4-node plaquette )
```
where `angle_diff(phi_next, phi_curr)` wraps the phase difference to (-pi, pi].
This is an exact integer for smooth configurations and detects vortex cores.

**Phi update law (v4, epsilon=0):**
```
phi_i(t+1) = phi_i(t) + alpha_phi * circular_mean_neighbors(phi) - phi_i
           + epsilon * chi_i(t)     [= 0 here since epsilon=0]
```
where the circular mean uses sigma-weighted neighbors.

Exact update: phi evolves by relaxation toward the weighted circular mean of
neighbors, subject to wrapped arithmetic (modulo 2pi). For epsilon=0:
```
phi_i(t+1) = angle( sum_j sigma_j * exp(i*phi_j) ) - driven by phase coherence
```
At each step: phi_i updates toward the argument of the weighted complex mean of
neighbor phases. This preserves winding number exactly (no smooth deformation can
change W).

## Checks

**Check 1 — Winding number W=+1 vortex persists:**
```
Count of plaquettes with W=+1 >= 1 at all T in {1000, 2000, 3000, 4000, 5000}
```
The vortex should not annihilate (it has no anti-vortex nearby — they are separated
by L/2 = 32 lattice spacings).

**Check 2 — Winding number W=-1 anti-vortex persists:**
```
Count of plaquettes with W=-1 >= 1 at all T in {1000, 2000, 3000, 4000, 5000}
```

**Check 3 — Phi gradient concentrated at topological defect plaquettes:**
```
mean |angle_diff| on 4 edges of W=+1 plaquettes > 3 * global mean |angle_diff|
```
Measured at T=5000: mean |angle_diff| on the 4 edges of each W=+1 plaquette must
be at least 3× the global mean edge gradient. Under strong beta diffusion, W=+1
plaquettes can MOVE from their initial position (co-charge vortices repel on the
torus), so the gradient check uses actual W=+1 plaquette locations, not the initial
center coordinates. Expected: vortex edges ~π/2 each, global background ~0.07 rad,
ratio ~22.

Note: sigma is autonomous in v3/v4 (no phi→sigma coupling). Sigma stays at
sigma_ref throughout — sigma depletion at the vortex core requires a new coupling
term not yet in the update law. This test checks phi topology only.

**Check 4 — Vortex-antivortex separation maintained:**
```
|center_plus - center_minus| > 20 at T=5000
```
(Centers measured as centroid of plaquettes with |W|=1.) The pair must not have
drifted together and annihilated — 20 lattice spacings is half the initial separation.

**Check 5 — Net winding number zero throughout (torus constraint):**
```
|W_plus_count - W_minus_count| <= 2 at all recorded steps
```
On a torus: net W must be 0. Small deviations (≤2) allowed for numerical boundary
effects, but persistent asymmetry indicates a winding error.

**Check 6 — Winding count stable (no diffusion or proliferation of topological charge):**
```
std(W_plus_count over {1000, 2000, 3000, 4000, 5000}) <= 1
```
The count of W=+1 plaquettes must be stable over time — winding does not
diffuse away or proliferate. std ≤ 1 over the 5 recorded steps.

## Decision rule

**Overall PASS** if all six checks pass.

**Interpretation of PASS:**
The phi vortex is topologically protected in the v3/v4 QNG substrate. Winding number
W=+1 is conserved over 5000 steps with no decay. The phase gradient is concentrated
at the vortex core. The winding count is stable. This confirms the structural mechanism
of DER-QNG-025 Section 3: phi topology provides stable, conserved defects that cannot
annihilate without an anti-vortex encounter.

IMPORTANT: This test confirms phi topology only. Sigma depletion at the vortex core
(sigma < sigma_ref at the vortex center) requires a phi→sigma coupling term not present
in v3/v4. The matter stability program requires a new coupling term (v5, future program).

This motivates:
- Design of v5 phi→sigma coupling (e.g., sigma penalized by local phase disorder)
- QNG-CPU-042: test phi→sigma coupling term that produces sigma depletion at vortex core
- QNG-CPU-043: 3D vortex ring stability test

**Interpretation of FAIL:**
- Check 1/2 fail: winding number destroyed — investigate phase wrapping in update law
  or numerical pi-crossing artifacts. Winding destruction by smooth dynamics is
  topologically impossible — failure indicates a numerical artifact.
- Check 3 fails: phi gradient not concentrated near core — vortex has diffused into
  a uniform phase distribution. Check initialization and beta parameter.
- Check 4 fails: pair annihilated — separation was too small or dynamics too fast.
  Increase initial separation and re-test.
- Check 5 fails: torus constraint violated — initialization has wrong net W.
  Re-check vortex + anti-vortex superposition formula.
- Check 6 fails: winding count drifting — unexpected topological charge creation.
  Check for numerical phase wrapping errors.

## Artifact paths

- `07_validation/audits/qng-phi-vortex-reference-v1/report.json`
- `07_validation/audits/qng-phi-vortex-reference-v1/summary.md`
