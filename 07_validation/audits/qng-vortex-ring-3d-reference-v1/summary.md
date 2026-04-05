# QNG 3D Vortex Ring Reference v1

- decision: `pass`
- L=20, R=5.0, beta_phi=0.02, gamma_phi=0.1
- Protocol: Phase1=300 steps (phi relax, no Channel F) + Phase2=700 steps (Channel F)
- pi_2(S^1)=0: ring NOT topologically protected (dynamic stability test)

## Phase 1 state (T=300, before Channel F)
- z_ring=0, core_sigma=0.5000, bulk_sigma=0.5000
- nonzero winding plaquettes: 72

## Ring evolution (Phase 2)

| T | z_ring | core_sigma | bulk_sigma | R_t | n_dep | n_ring |
|---|--------|------------|------------|-----|-------|--------|
| 500 | 19 | 0.2689 | 0.4478 | 5.29 | 917 | 840 |
| 1000 | 19 | 0.2747 | 0.4216 | 4.84 | 813 | 920 |

## Final state (T=1000)
- z_ring drift: 9 lattice units (self-induced ring velocity)
- Non-zero winding plaquettes: 56

## Summary checks
- Check 1 (core_sigma < 0.40): 0.27471  PASS
- Check 2 (bulk_sigma > 0.40): 0.42160  PASS
- Check 3 (R_t > 2.5): 4.843  PASS
- Check 4 (nonzero wind >= 4): 56  PASS
- Check 5 (ring nodes >= 10): 920  PASS
- Check 6 (persists T500+T1000 < 0.45): PASS

## Interpretation
PASS: 3D vortex ring is dynamically stable over 700 steps of Channel F (1000 total). With BETA_PHI=0.05 (slow phi diffusion), the ring does not collapse before Channel F builds sigma depletion. Despite pi_2(S^1)=0 (no topological protection), the ring maintains sigma depletion and ring radius > R/2. This confirms that 3D matter in QNG can take the form of a dynamically stable vortex ring. Motivates ring lifetime (QNG-CPU-044) and self-velocity (QNG-CPU-045).
