# QNG-GPU-015 — Scientific interpretation (2026-04-18)

**Verdict: FAIL.** All three pre-registered gates fail. The Hamiltonian energy
functional does not produce an L-convergent mass observable either globally or
inside a ring-centered sphere window.

## Pre-registered gates — outcome

| Gate | Quantity | Value | Threshold | Result |
|------|----------|-------|-----------|--------|
| G1 | last-3-L spread of E_ring_global(R=5)/E_ring_global(R=4) | 0.2182 | < 0.03 | FAIL |
| G2 | last-3-L spread of E_ring_windowed(R=5)/E_ring_windowed(R=4) | 0.2155 | < 0.03 | FAIL |
| G3 global | |1.1265 - 1.3130| / 1.3130 | 14.2% | < 5% | FAIL |
| G3 windowed | |2.2447 - 1.3130| / 1.3130 | 71.0% | < 5% | FAIL |

## What the scan shows

### Global Hamiltonian energy is IR-divergent (same pathology as M_ring)

E_ring_global (the total Hamiltonian energy minus the vacuum energy on the same
L-box) grows without apparent saturation:

```
L:       20     30     40     60     80
R=4:   -60.8 -101.8 -145.5 -263.6 -424.2
R=5:  -114.3 -153.1 -195.7 -314.8 -477.8
```

Its R=5/R=4 ratio decays monotonically from 1.88 (L=20) through 1.50, 1.34, 1.19,
to 1.13 at L=80. The trend continues below SM=1.313 and heads toward ~1.0 — the
same geometric-volume pathology exhibited by M_ring (5/4 → 1.25 asymptotic).
The ring's excess Hamiltonian energy is not localized; it grows with box volume.

### Windowed energy asymptotes to ~2.2, not 1.313

E_ring_windowed uses a ring-centered sphere of radius R+5 with outer-shell
background subtraction. The ratio stabilizes at ~2.25 by L=80, but this is not
SM=1.313 and not the geometric 5/4. The windowed ratio plateaus at a value
determined by the window geometry and R choices, not particle physics.

### M_ring cross-check (unchanged from GPU-011)

M_ring ratio: 1.398 → 1.234 → 1.163 → 1.095 → 1.064. Same geometric pathology.

## Per-component analysis (Gate 4 — informational)

| Component | L=20 | L=30 | L=40 | L=60 | L=80 | Trend |
|-----------|------|------|------|------|------|-------|
| e_A (sigma^2 deviation) | 2.07 | 1.65 | 1.46 | 1.27 | 1.17 | → 1 (geometric) |
| **e_B (sigma gradient)** | 4.33 | 2.65 | 2.03 | 1.53 | **1.32** | → SM 1.313? |
| e_chi_dec (chi^2) | 2.09 | 1.66 | 1.47 | 1.27 | 1.18 | → 1 (geometric) |
| **e_chi_rel (chi·∇sm)** | 4.54 | 2.76 | 2.10 | 1.56 | **1.34** | → SM 1.313? |
| e_delta (chi·ds) | -2.08 | -1.66 | -1.47 | -1.27 | -1.17 | → -1 (geometric) |
| e_phi (phi alignment) | -1.15 | -1.13 | -1.10 | -1.06 | -1.05 | → -1 (geometric) |
| e_dis (disorder·sm^2) | 1.16 | 1.12 | 1.09 | 1.06 | 1.04 | → 1 (geometric) |

**Structural observation — not a rescue:** two components out of seven
(e_B and e_chi_rel) approach SM=1.313 monotonically rather than the bulk
geometric 1.0. At L=80 their ratios are 1.32 and 1.34 respectively — within
0.5% and 2.2% of SM 1.313. However, their last-3-L spreads (0.71 and 0.76)
are far above the 0.03 convergence threshold, so the approach is empirical
extrapolation, not demonstrated convergence.

Both components share the qualitative feature that they contain a sigma-gradient
or sigma-correlation factor that is localized at the ring surface rather than
spread through the bulk halo. This is a candidate mass-carrier, but the
demonstration requires:

1. L-scan extended to L >= 120–160 to check whether e_B and e_chi_rel plateau
   at SM or drift further below.
2. A justification for picking out e_B (or e_B + e_chi_rel) as the physical
   mass observable rather than the full Hamiltonian. A partial sum of
   Hamiltonian components is a priori ad-hoc unless it corresponds to a
   distinguished physical charge.

Without (1) and (2), no rehabilitation of DER-QNG-038 is warranted.

## Implications for DER-QNG-038

The candidate remedy proposed in the mass-identification document (§1.1,
2026-04-15) — "Hamiltonian energy H_v7 = T_g + E_v7 (energy, not depletion
integral)" — is **rejected at the full-Hamiltonian level**. Both the global
and the windowed Hamiltonian energy exhibit the same L-divergence pathology
as M_ring, and neither matches SM=1.313 at L=80.

DER-QNG-038 mass identification remains STRUCTURAL HINT. Three possible
next steps remain open, all requiring separate pre-registration:

- **(A) e_B single-component L-scan** — test whether the sigma-gradient energy
  alone converges to SM ratio at L=120/160/200. This is motivated but
  post-hoc; requires a theory-level justification for picking e_B.
- **(B) Different confinement mechanism** — Channel H confines phi but not
  sigma_m; a confinement mechanism for sigma_m (e.g., a sigma_m mass term
  or a self-interaction Vsm(sm)) might localize the full Hamiltonian.
- **(C) Give up fixed-R baryon identification** — accept that in v5/v7 a
  classical ring radius does not carry particle mass; search for a different
  mass carrier (Hopfion Q=1 Hamiltonian energy, bound state of phi-vortex
  and sigma depletion, quantized sigma_m field on the ring surface).

## Conclusion

The hypothesis of the pre-registration — that H_v7 evaluated on the final
ring state is L-convergent and matches SM — is falsified. The sigma-gradient
sub-component e_B shows an interesting asymptotic trend toward SM 1.313 but
is not itself convergent within the test range. No ad-hoc rehabilitation of
DER-QNG-038 is carried out; the STRUCTURAL HINT status is preserved, and a
tighter falsification programme (options A / B / C above) is deferred to
future pre-registrations.
