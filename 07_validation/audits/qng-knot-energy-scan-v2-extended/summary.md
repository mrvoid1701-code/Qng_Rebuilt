# QNG-CPU-145 Knot Energy Spectrum
- decision: `pass`

## Purpose
First QNG test of Kelvin-Bilson-Thompson topological-knot
hypothesis for particle identification (DER-QNG-091 §7 Tier A.2,
DER-QNG-092). Measures relaxed phi-XY energy of distinct
topological configurations on identical lattice.

## Configurations tested
| Config | Description |
|---|---|
| ring_Q0     | Vortex ring, phi winding 1 around the loop |
| hopfion_Q1  | Q=1 Hopfion (poloidal + 1*toroidal) |
| hopfion_Q2  | Q=2 Hopfion (poloidal + 2*toroidal) |
| hopfion_Q3  | Q=3 Hopfion (poloidal + 3*toroidal) |
| trefoil     | Trefoil-knot phi vortex |

## Results
| Config | Delta_E (above vacuum) | Delta_E/Delta_E[Q0] | Delta_E/Delta_E[Q1] | Q_hopf proxy |
|---|---|---|---|---|
| ring_Q0 | 0.0346 | 1.000 | 0.004 | 0.000 |
| hopfion_Q1 | 9.7557 | 281.859 | 1.000 | 0.000 |
| hopfion_Q2 | 12.1134 | 349.976 | 1.242 | 0.000 |
| hopfion_Q3 | 15.6117 | 451.048 | 1.600 | -0.000 |
| hopfion_Q4 | 17.3210 | 500.432 | 1.775 | -0.000 |
| hopfion_Q5 | 20.0535 | 579.378 | 2.056 | 0.000 |
| trefoil | 0.0779 | 2.251 | 0.008 | 0.000 |

## Stability (first-order: Delta_E > 0.1)
- ring_Q0: COLLAPSED
- hopfion_Q1: OK
- hopfion_Q2: OK
- hopfion_Q3: OK
- hopfion_Q4: OK
- hopfion_Q5: OK
- trefoil: COLLAPSED

## Interpretation
Topological energy ratios are candidate analogs of particle mass ratios in the Kelvin-Bilson-Thompson hypothesis (DER-QNG-091 §7 Tier A.2). Compare to lepton ratios m_mu/m_e = 207 and m_tau/m_mu = 17 — exact match not expected at this level (missing matter sector and Wess-Zumino dressing).

## Honest caveats
- Energy measured at LOCAL minimum of XY gradient flow only.
  True ground state of each topology class may require longer relaxation
  or stronger optimizer (CG, simulated annealing).
- Trefoil init uses naive transverse-frame construction; may not yield
  exactly-tied trefoil under XY relaxation — could un-knot to unknot if
  topological protection fails.
- Q_hopf proxy is approximate; gauge-invariant Hopf number requires
  the n-field formulation (Faddeev-Skyrme), not pure phi.
- No matter (sigma_m) coupling — pure XY sector only. Real QNG energies
  include matter-sector and gravity-sector terms that may rescale ratios.
