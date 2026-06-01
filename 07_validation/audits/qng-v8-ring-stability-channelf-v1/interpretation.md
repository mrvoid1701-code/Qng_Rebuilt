# GPU-024c interpretation — Channel F is NOT the sole driver

**Date**: 2026-04-20
**Script**: `tests/gpu/qng_v8_ring_stability_channelf.py`
**Run log**: `run.log`
**Verdict**: `H_NO_EQUILIBRIUM`

## Raw numbers

| config | v_couple | chi_decay | channel_f | M_ring range | rel drift | max RMS |
|---|---|---|---|---|---|---|
| D_ChF_off | True | 0.020 | **False** | [-402.27, +427.72] | 469.3% | 26.5% |
| E_all_off | False | 0.000 | **False** | [-389.38, +409.15] | 451.5% | 26.3% |

## What this rules out

GPU-024b had already ruled out:

- **V_couple as sole driver** (Config C: v_couple off, chaos persists)
- **chi_decay as driver** (Config A = Config B byte-identical due to k_gm=0)

GPU-024c adds:

- **Channel F as sole driver**. With channel_f=False, D and E still
  show ±400 M_ring oscillations within 50 lu. The non-linear sigma_m
  dynamics are chaotic with or without Channel F.

Note that D and E differ only in the `v_couple_on` + `chi_decay`
combination, and they agree at the 5% level on drift magnitude. This
confirms GPU-024b's finding that V_couple is not the bottleneck in
the Phase-2 regime probed here.

## What remains

After GPU-024c, the chain of ruled-out drivers is:

| candidate | status after |
|---|---|
| V_couple (single source) | ruled out (GPU-024b C) |
| chi_decay | ruled out (GPU-024b, k_gm=0) |
| Channel F | ruled out (GPU-024c D, E) |
| T_m kinetic + V_couple coupling | still possible |
| cached ring not a v8 fixed point | still possible (GPU-024d v1 confirms) |

## Connection to GPU-024d

GPU-024d (static ring search via gradient flow) uses the same
`channel_f=False` setting as GPU-024c and monotonically drives the
cached state toward vacuum. The chaos observed here in GPU-024c is
therefore not driven by "missing Channel F balance" — the ring has no
v8 stationary state in ANY accessible regime, and symplectic evolution
just makes the dissolution oscillatory instead of monotonic.

The unified reading:

- v7 ring is a gradient-flow equilibrium under Channel F.
- v8 V_couple (sine-Gordon) pulls phi back to the Z vacuum.
- The v7 ring is a basin flank on the v8 landscape, not a minimum.
- Under v8 symplectic evolution, the "ring" is a chaotic trajectory
  orbiting the vacuum with ±400 M_ring swings.
- Under v8 gradient flow, the same ring decays monotonically toward
  the vacuum with no intermediate fixed point.

## Consequences

- **item 2e** in THEORY_STATE §5.5 now reads: V_couple, chi_decay, and
  Channel F all ruled out as sole chaos drivers. The only remaining
  candidate is the kinetic structure (pi_m, pi_phi) coupled to
  V_couple, which is equivalent to saying "there is no static v8 ring."
- GPU-024d v2 (extended relaxation + V_couple-free variant) is the
  next step: does the cached ring survive with g=0 (V_couple off)? If
  yes, the sine-Gordon vacuum is the specific culprit; if no, v8 3D
  admits no ring soliton at all.
