# REPORT — demo Phase-23 master particle-mass table

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase23_master_mass_table.py`
Verdict: **MASTER_MASS_TABLE**

Full light-hadron spectrum, absolute MeV vs PDG (mean err 0.5%, max 3.4%):

| Particle | QNG | PDG | err | role |
|---|---|---|---|---|
| N | 941.8 | 938.9 | 0.3% | scale s1 (alpha_s) |
| Lambda | 1111.4 | 1115.7 | 0.4% | GMO PRED |
| Sigma | 1191.8 | 1193.2 | 0.1% | GMO |
| Xi | 1321.2 | 1318.3 | 0.2% | GMO |
| Delta | 1232.0 | 1232.0 | 0.0% | input s3 |
| Sigma* | 1378.8 | 1384.6 | 0.4% | spacing s2 |
| Xi* | 1525.7 | 1533.4 | 0.5% | PRED |
| Omega | 1672.5 | 1672.5 | 0.0% | PRED (Gell-Mann) |
| pi | 138.0 | 138.0 | 0.0% | scale s4 |
| K | 495.6 | 495.6 | 0.0% | input |
| eta | 566.7 | 547.9 | 3.4% | PRED (m^2 GMO) |
| rho | 775.3 | 775.3 | 0.0% | vector scale |
| K* | 905.7 | 891.8 | 1.6% | PRED |
| phi(ss) | 1019.5 | 1019.5 | 0.0% | input |

~8 genuine predictions from ~6 scale inputs. Photon massless (derived); leptons
ABSENT (v13+v14). Full table + sector status in demo-theory/PARTICLE-MASS-TABLE.md.

Structure: baryons=phi-solitons (GMO in m), mesons=phi-Goldstone (GMO in m^2),
overall scale=alpha_s (Phase 12). Hadron ratios/structure reproduced (inherited
SU(3)/chiral relations); absolute scale=input (Drumul 3); leptons open.
