# REPORT — demo Phase-4c fermion doubling / chirality wall

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase4c_fermion_doubling.py`
Verdict: **CHIRALITY_WALL_CONFIRMED**

| Quantity | Result |
|---|---|
| naive lattice Dirac zeros | k = {0, +/-pi} -> 2 species/dim |
| doublers in 3+1D | 2^4 = 16 |
| Wilson term M(k=0) | 0 (physical fermion massless) |
| Wilson term M(k=pi) | 2r (doubler decouples) |
| chiral symmetry under Wilson term | broken explicitly |

A naive lattice Dirac fermion has 16 doublers (Nielsen-Ninomiya). The Wilson
term decouples them but breaks chiral symmetry. The parity-violating weak sector
therefore needs a lattice-chiral solution (Ginsparg-Wilson / overlap /
domain-wall) -- a v14-level construction, the same one every lattice-QCD program
solves. Edges host forces (easy); chiral fermions are hard (solved technology).
