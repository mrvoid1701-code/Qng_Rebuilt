# REPORT — demo-E5 transverse-light probe

Date: 2026-06-01
Probe: `demo-theory/tests/e5_transverse_light_probe.py`
Verdict: **ROUTE_A_INSUFFICIENT** (Route A falsified for pure scalar φ)

## Numbers

| Test | Result | Expected |
|---|---|---|
| E5a transverse fraction (smooth single-valued φ) | 9.44e-32 | ~0 (machine eps) |
| E5b transverse fraction (vortex, winding 2π) | 0.256 | > 0 (topological) |
| E5b transverse energy within r<=4 of core | 19.6% | localized-ish |
| E5c rms-radius growth / c_φ | -0.30 | >0.5 if radiating |
| reference c_φ (meas / small-k theory) | 0.303 / 0.265 | consistent |

E5c radius series collapses 12.73 -> ~3e-7 after the first sampled step:
transverse content is not dynamically sustained, let alone propagating.

## Verdict

A single scalar phase field cannot host a propagating transverse photon
(2 polarizations). The transverse edge sector is identically zero for
single-valued φ (Hodge: θ=dφ is purely exact/longitudinal) and topological
transverse content is bound to defects and not sustained. A genuine photon
requires a SECOND dynamical edge degree of freedom:
- Route B (primary): coupled φ–χ transverse mode (χ-circulation = B-analog) → test E7.
- Route C (axiomatic fallback): v12 edge gauge field A_ij.

Mirrors Gap 12 (scalar σ_g → spin-0, not spin-2 graviton) and the ℏ-edge
finding (scalar edges structurally insufficient). Consistent structural lesson:
node-scalars are not enough; the missing object lives on edges as an
independent vector/tensor.

No derived-photon claim is made. QNG retains only the axiomatic v12 photon
until E7 (or successor) passes.
