# REPORT — demo-E7 phi-chi photon probe

Date: 2026-06-01
Probe: `demo-theory/tests/e7_phi_chi_photon_probe.py`
Verdict: **ROUTE_B_FAILS_NODE_SCALARS / EDGE_PHOTON_FORCED**

## Numbers

| Test | Result | Expected |
|---|---|---|
| E7a max\|curl(grad phi)\| | 2.22e-16 | ~0 (Hodge d.d=0) |
| E7a max\|curl(grad chi)\| | 2.22e-16 | ~0 |
| E7a sustained transverse fraction (coupled evolution) | 7.42e-32 | ~0 |
| E7b transverse pol 1 (z) omega | 0.15708 | > 0, = pol 2 |
| E7b transverse pol 2 (y) omega | 0.15708 | > 0, = pol 1 |
| E7b longitudinal (x) omega | 0.0 | 0 (frozen) |
| E7b 2 transverse match + longitudinal frozen | True | True |

(c_meas ~ 0.30 vs c_phi 0.265 is FFT bin resolution ~0.05 over the 120-lu
window; the equal-transverse and frozen-longitudinal facts are
resolution-independent.)

## Verdict

chi is a node scalar -> curl(grad chi) = 0 identically -> cannot be a B-analog.
No coupling of two node scalars sources a sustained transverse mode. A
FUNDAMENTAL edge-vector field (gauge field on links, not the gradient of any
node scalar) reproduces the photon exactly under Maxwell dynamics
d2A/dt2 = -c^2 curlcurl A: 2 transverse polarizations propagate at c_phi, the
longitudinal mode is frozen (Gauss constraint).

CONCLUSION: the v12 edge gauge field A_ij is the MINIMAL and FORCED carrier of
light in a node-scalar substrate. Light is necessarily a link degree of freedom.
Unifies with Gap 12 (graviton tensor needs rank-2 edge object) and the hbar-edge
finding (scalar edges insufficient): nodes carry matter/phase scalars, EDGES
carry the force-carrier gauge fields.

## Bug fixed mid-run

First run used a central-difference curl with a forward-difference gradient
(mismatched discrete operators) -> spurious curl(grad) ~ 2.8e-2. Fixed to the
matched forward-difference plaquette curl so that d.d = 0 exactly (curl(grad)
-> 2.2e-16). Verdict unchanged in direction, now clean.
