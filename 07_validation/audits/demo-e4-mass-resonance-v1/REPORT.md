# REPORT — demo-E4 mass-resonance probe

Date: 2026-06-01
Probe: `demo-theory/tests/e4_mass_resonance_probe.py`
Verdict: **MASS_IS_VOLUME_CHARGE** (page-05 1/R resonance disfavored)

## Decisive analysis (canonical M_ring CPU-074 + cavity omega~1/R)

| Hypothesis | R5/R4 | PDG Delta/N target | match |
|---|---|---|---|
| H_volume  m ~ Sigma sigma_m | 1.310 | 1.313 | YES (0.2%) |
| H_freq    m ~ omega~1/R | 0.800 | 1.313 | no |
| H_product m ~ Sigma sigma_m * omega | 1.048 | 1.313 | no |

Canonical M_ring: R3=474.15, R4=728.92, R5=954.88.

## Verdict

The baryon ladder tracks the conserved volume/topological charge Sigma sigma_m
alone; multiplying by a 1/R cavity frequency BREAKS the match. The "mass = 1/R
resonance" conjecture (page 05) is DISFAVORED. Division of labor: frequency/edges
set LIGHT (E5/E7), node volume-charge sets MASS.

## Caveats (honest)

- The self-contained ring sim in this probe is CRUDE and UNRELIABLE: its
  Channel-F carve depletes sigma_m globally (deficit ~2300-2700, not canonical
  ~474-955), and its omega_1=0.134 is R-INDEPENDENT (a global phi mode, not the
  toroidal cavity mode). The quantitative verdict uses canonical M_ring, not the
  sim.
- Loophole: 1/R is excluded; if a FAITHFUL omega_1(R) were R-independent then
  product == volume and the match survives. Needs real v8 ring infra
  (E4-faithful follow-up).
- M_ring is lattice-dependent (Gap 14); v8 rings are dynamic not static
  (DER-QNG-047); MeV scale is Gap 13. No absolute-mass claim is made.
