# REPORT — demo Phase-4a custodial symmetry audit

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase4a_custodial_audit.py`
Verdict: **NO_CUSTODIAL_SU2**

Operational test: does a rotation mixing (sigma_g, sigma_m) commute with the
dynamics?

| Case | commutator (relative) |
|---|---|
| real dynamics (Channel-F term on sigma_m only), theta=0.3 | 0.209 |
| theta=0.7 | 0.427 |
| theta=1.5 | 0.761 |
| control (gamma_f=0, matched fields), theta=0.7 | 1.3e-15 |

The physical channel asymmetry (Channel F acts on sigma_m, not sigma_g) BREAKS
the rotation. The control (matched, no Channel F) restores it, but only as
SO(2)=U(1) -- a rotation of two REAL fields, never SU(2) (which needs C^2).

tesla-mind's (sigma_g, sigma_m) = isospin-doublet conjecture fails at BOTH
levels: channel structure breaks even the U(1), and real fields cannot carry
SU(2) regardless. Confirms the professor. Non-abelian matter = new ontology v13.
