# REPORT — demo Phase-2 v12 lattice photon

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase2_v12_lattice_photon.py`
Verdict: **V12_PHOTON_CONFIRMED**

Implements the ACTUAL v12 structure (DER-QNG-076): A_a link variables, F_p
plaquette field strength, lattice Maxwell EOM (not the idealized spectral
curl-curl of E7).

| Quantity | Result |
|---|---|
| transverse pol z omega | 0.54978 |
| transverse pol y omega | 0.54978 (degenerate) |
| longitudinal x omega | 0.0 (frozen, Gauss) |
| 2 transverse + frozen longitudinal | True |

The real v12 edge gauge structure carries the photon: 2 degenerate transverse
polarizations propagating, longitudinal frozen. Validates demo-E7 in the
original theory's actual formulation. Edge gauge field = light, dynamically on
the lattice.
