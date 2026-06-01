# GPU-024d v2 interpretation — v8 admits no static 3D ring in either regime

**Date**: 2026-04-21
**Script**: `tests/gpu/qng_v8_static_ring_search_v2.py`
**Run log**: `run.log`
**Report**: `report.json`
**Verdict**: `H_NO_RING_IN_ANY_REGIME`

## What was tested

Extended gradient-flow relaxation (N_ITER=30000, dt_relax=0.05) of the
cached ring `ring_L28_R4_P1_300_P2_1000` under two configurations:

- **A — v8 full minus Channel F**: V_couple on (g=0.22), Channel F off
- **B — V_couple off**: Both V_couple and Channel F off. Pure E_v7
  minus coupling. Cleanest possible kinetic configuration.

Starting M_ring = 176.85 for both.

## Result

| config | iter | M_ring | ||F_sm|| | ||F_phi|| | verdict |
|---|---|---|---|---|---|
| A | 18000 | 0.05 | 2.18e-08 | 1.45e-04 | DISSOLVED |
| B | 30000 | 0.10 | 2.23e-08 | 9.28e-05 | DISSOLVED |

**Both configurations relax to vacuum monotonically.**

The V_couple-free run (B) is SLOWER (half-life ~6000 vs ~3000 iter for
A) but dissolves just as completely. The endpoint is the trivial
vacuum `(sigma_m = sigma_m_ref, phi = 0)` in both cases.

## What this rules out

- **V_couple is NOT the unique culprit.** Even with g=0 (sine-Gordon
  term completely removed), the cached ring dissolves. The previously
  suspected mechanism (V_couple = Z-vacuum attractor pulling phi to 0)
  is part of the story but not the whole story.
- **The chaotic oscillations in GPU-024c are NOT just "the v8 version
  of a stable v7 equilibrium".** The cached state has no equivalent
  v8 stationary configuration nearby — there is nowhere for the
  dynamics to settle.

## Why B also dissolves

Without V_couple, the only remaining phi dynamics are:
- phi diffusion via `BETA_PHI * wrap(phi_mean - phi)`.

This is a pure gradient-flow Laplacian on a compact field. It is
dissipative with no restoring potential. The 2π winding texture in the
phi channel is Goldstone-mode metastable under diffusion — in an
infinite continuous domain a vortex line cannot relax (topology is
protected), but on a finite lattice with periodic BCs and a core of
finite size, small-scale reconnection events dissolve the winding
diffusively.

Simultaneously, the sigma_m sector has:
- `ALPHA*(sigma_m_ref - sm)` pulling back to reference
- `BETA_M*(smb - sm)` diffusing the deficit

With no Channel F to pump deficit, the ring deficit just diffuses
away into the homogeneous background. Rate set by ALPHA + 6*BETA_M on
the k=0 mode.

A more careful statement: ring stability in v7 required Channel F
balancing diffusion. Without Channel F, v7 rings also dissolve (this
was the ALPHA>0 calibration setting in CPU-060). Run B confirms this
is still true in v8's kinetic sector.

## Combined with A (V_couple on)

With V_couple, both effects amplify each other:
- phi feels the sine-Gordon attractor → dissolves faster toward 0
- sigma deficit feels V_couple = 0 pull (once phi = 0) → faster
  return to sigma_m_ref

Run A dissolves in ~18k iter; Run B dissolves in ~30k iter. V_couple
**accelerates** dissolution but is not **required** for it.

## Structural implication

There is no regime of v8 on the 3D z=6 cubic lattice — among the axes
{Channel F, V_couple, chi_decay} we've explored — that admits the
cached vortex ring as a static soliton. The ring is metastable at
best under v7 gradient flow with active Channel F; it has no v8
analogue.

This is documented as `DER-QNG-047` with status upgraded from
*candidate* to **locked for v8 in 3D** based on v2's definitive
verdict.

## What GPU-024d v2 does NOT rule out

- Rings could still exist as dynamic orbits of the v8 Hamiltonian that
  do NOT correspond to equilibria. The 500-1000% oscillations in
  GPU-024 are plausibly such orbits — chaotic but bounded. Testing
  this requires Poincaré-section analysis on phase space; not yet done.
- A different v8 potential (e.g., gauge-invariant instead of
  sine-Gordon, or double-Yukawa) might admit a static ring. No
  candidate has been constructed yet.
- A higher-dimensional v8 substrate (4D cubic z=8, with rings as codim
  3 curves) might admit static rings. Tested at the linear level by
  GPU-026 (KG dispersion), not yet at the non-linear/topological level.

## Downstream actions

1. `DER-QNG-047` (qng-v8-no-static-ring-v1.md) → status **locked**
2. `THEORY_STATE.md` → item 2e closed with resolution "no v8 static
   ring in 3D". Gap 10 (dimension selection) promoted with explicit
   ring-failure evidence. GPU-022 saturation and GPU-021/023 residuals
   now read as dynamic-pattern phenomenology, not static-soliton
   phenomenology.
3. `DER-QNG-038` baryon mass identification: the R-scaling remains a
   valid v7 conservation statement, but the "rest mass" reading
   requires v8 stationary rings. Interpretation needs revision — the
   masses may be conserved quantities of v7 dynamics that do not
   directly correspond to v8 particle rest frames.
