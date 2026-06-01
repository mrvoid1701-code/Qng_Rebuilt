# QNG-GPU-034

Type: `prereg`
Status: `pending`
Author: `C.D Gabriel`
Date: `2026-04-21`
test_class: `falsifier`
hardware: `GPU`
upstream: `QNG-GPU-031f` (H_ORBITAL_ATTRACTOR, <M>_t = 309.45 at L=20 R=4);
          `QNG-GPU-031g` (R=3+R=5 ladder DEAD, universal basin R-insensitive);
          `DER-QNG-051` (v8 vacuum instability, R1 pure-XY cure)

## Title

L-scaling of v8 R1 single-ring orbital attractor — falsify cavity-mode hypothesis.

## Purpose

GPU-031f established that under v8 R1 (pure-XY E_phi), a single R=4 ring at
L=20 settles into an **oscillating attractor** with mean topological charge
<M>_t = 309.45 and dominant period T_dom = 185 lu. GPU-031g showed the same
mean holds for R=3 (308.9) and R=5 (351.1), confirming the attractor basin
is **R-insensitive** — which *weakens* the DER-QNG-038 baryon-ladder
interpretation (where M is supposed to track ring radius).

A cheap but decisive falsifier remains open:

> Is T_dom = 185 lu a **cavity k=1 eigenmode** — T = L / c_φ at L=20 with
> c_φ = √0.01167 = 0.1080 — or a genuinely particle-intrinsic oscillation?

At L=20, L/c_φ = 185.2 lu — coincident with measurement to within rounding.

## Prediction

If the attractor is box-locked (cavity mode):

- T_dom(L) = L / c_φ
- T_dom(L=32) = 296.3 lu
- T_dom(L=16) = 148.1 lu

If the attractor is an intrinsic ring property:

- T_dom(L) ≈ 185 lu independent of L

## Configuration

- Integrator: Yoshida4, DT=0.025
- exact_a='r1' (DER-QNG-051 Option R1, pure-XY E_phi)
- Phase 1: v_couple_on=False, T_P1=300 lu (ring formation)
- Phase 2: v_couple_on=True, T_P2=5000 lu (orbital dynamics + sampling)
- k_gm=0 (no gravitational back-reaction, matches GPU-031f baseline)
- Ring init: R=4, single vortex ring at z = L/2
- Box sizes to test: L=32 (primary), L=16 (if time permits)

## Gates

- **BOX_LOCKED**: |T_meas / (L/c_φ) - 1| < 0.10 → basin is cavity k=1 eigenmode.
  DER-QNG-038 baryon ID becomes definitively void; <M>_t is NOT a rest-mass
  analog; ring is a box-size artifact of the simulation.
- **INTRINSIC_RING**: |T_meas / 185 - 1| < 0.10 → T_dom is L-independent.
  Multi-vortex hypothesis revived as L-independent. Pivot to stability
  (Floquet) analysis and N=3+ ring probes.
- **INCONCLUSIVE**: T_meas matches neither — could be k=2 (L/(2c_φ)) or
  k=3 (L/(3c_φ)) modes, or novel physics. Requires further scans.

## Expected wall time

~22 minutes (L=32, 5000 lu, Yoshida4) based on GPU-031f scaling.

## Artifacts

- Script: `tests/gpu/qng_v8_r1_L_scan.py`
- Audit: `07_validation/audits/qng-v8-r1-L-scan-v1-L32/`
- Memory hook: `project_gpu034_L_scaling.md` (write only after completion).
