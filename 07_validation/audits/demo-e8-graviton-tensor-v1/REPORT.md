# REPORT — demo-E8 graviton tensor probe

Date: 2026-06-01
Probe: `demo-theory/tests/e8_graviton_tensor_probe.py`
Verdict: **SPIN2_EDGE_OK (kinematic)**

## Numbers

| Test | Result | Expected |
|---|---|---|
| E8a TT projector dof (symmetric 3x3, orthonormal basis) | 2.000000 +/- 4e-16 | 2 |
| E8b omega(+) | 0.15708 | >0, = omega(x) |
| E8b omega(x) | 0.15708 | = omega(+) |
| E8b two TT polarizations degenerate | True | True |

## Verdict

A symmetric rank-2 edge object carries exactly 2 transverse-traceless
polarizations propagating degenerately at c_phi -- the graviton's (h+, hx).
Confirms the 07-edges-carry-the-forces prediction: edge VECTOR = spin-1 photon
(E7b), edge RANK-2 = spin-2 graviton. Structural cure for Gap 12 (node scalar
sigma_g gives only spin-0).

KINEMATIC ONLY: shows the structure hosts spin-2 with the right polarization
count and lightcone; does NOT derive graviton dynamics from the substrate.
Gap 12 dynamics remain open.

## Bug fixed mid-run

First counting used the full 9-dim tensor-space trace einsum("ijij->") = 3
(double-counts off-diagonal symmetric components). Fixed to the trace over the
6-dim symmetric space in an orthonormal basis (off-diagonals weighted 1/sqrt2)
-> 2.000000 exactly, matching the known TT dof count (d+1)(d-2)/2 = 2 in d=3.
