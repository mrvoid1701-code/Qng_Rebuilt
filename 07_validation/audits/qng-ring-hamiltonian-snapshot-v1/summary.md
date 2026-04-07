# QNG-CPU-057 Audit Summary

**Result: PASS**
Date: 2026-04-07
Script: `tests/cpu/qng_ring_hamiltonian_snapshot_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Ring survives, M > 50 at T=1000 | M > 50 | PASS (M=954.9) |
| 2 - H > 0 at k_back=0.05, T=1000 | H > 0 | PASS (H=5190.25) |
| 3 - k_min < 0.10 at T=1000 | k_min < 0.10 | PASS (k_min=0.00442) |

## Snapshot H(k_back) at T=1000

State: M=954.9, E_ring=-503.64, chi_rms=5.34, sum_chi2=227755

| k_back | T_snap    | H_snap     |
|--------|-----------|------------|
| 0.000  | 0.00      | -503.64    |
| 0.005  | 569.39    | +65.75     |
| 0.010  | 1138.78   | +635.14    |
| 0.020  | 2277.56   | +1773.91   |
| 0.050  | 5693.89   | +5190.25   |
| 0.100  | 11387.78  | +10884.13  |
| 0.200  | 22775.55  | +22271.91  |
| 0.500  | 56938.88  | +56435.22  |
| 1.000  | 113877.75 | +113374.09 |

k_min = 2 x |E_ring| / sum_chi2 = 2 x 503.64 / 227755 = 0.00442

## Key findings

**Finding 1: k_min is very small (0.0044)**
The ring has positive Hamiltonian energy for ANY k_back >= 0.005.
The threshold is much lower than the k_back=0.05 estimate in the prereg.
This is because chi_core is very large (chi_rms~5.3) relative to |E_ring|=503.

**Finding 2: H scales linearly with k_back**
For large k_back: H ~ k_back/2 * sum_chi2 (T dominates).
For small k_back: H ~ k_back/2 * sum_chi2 + E_ring (E partially cancels T).
The transition is around k_back = 0.005.

**Finding 3: Physical mass with C4 (m_u=Planck) is 10^25 x proton mass**
  H_ring(k_back=1) = 113374 substrate units
  m_ring = H x m_u / v_meas^2 = 113374 x 2.18e-8 / 0.0523 = 0.047 kg
  proton = 1.67e-27 kg
  ratio: m_ring / m_proton ~ 2.8e25

This is the C4 tension identified in NOTE-QNG-016 (Interpretation A/B/C),
now confirmed numerically:
  IF C4 holds (m_u ~ Planck mass) AND IF the ring is the proton,
  the substrate energy scale is ~25 orders of magnitude too large.

**Finding 4: What m_u would give m_proton?**
  m_u_needed = m_proton x v_meas^2 / H_substrate
             = 1.67e-27 x 0.0523 / 113374
             = 7.7e-34 kg   (~0.5 electron masses)

This is NOT Planck mass. The C4 constraint (m_u ~ Planck) and the
proton identification require completely different m_u values.
This is the core open problem in the matter source identification program.

## Resolution paths (per NOTE-QNG-016)

**Path A (C4 revised):** Find a weaker quantum of action constraint
that gives m_u ~ 10^-33 kg instead of Planck mass. This requires
revisiting what "quantum of action" means at the node level.

**Path B (Energy rescaling):** The substrate H is a sum over N=8000 nodes.
Physical ring energy may require a coarse-graining factor: only a fraction
of nodes are in the "ring core" and contribute to the particle mass.
If only ~ring_nodes ~ 868 nodes count (from CPU-055), the effective H is
still ~12000 x too large. Need additional per-node normalization.

**Path C (Different ring):** R=5 ring on L=20 lattice is not the proton.
Physical proton may correspond to a much smaller or different excitation
(minimum topological excitation, not the classical L=20 ring).

## Next step

The matter source identification program requires one of:
1. Derive m_u from first principles (not just C4 dimensional argument)
2. Identify the correct volume/normalization factor for physical energy
3. Compute m_ring for multiple ring sizes (R=2,3,4,5) to see if any
   gives proton mass for reasonable m_u, and determine the mass spectrum

Mass spectrum across ring radii (CPU-058 candidate):
  Run snapshot H for R=2,3,4,5 at fixed Phase-2 T=1000.
  If m_ring(R) ratios match hadron mass ratios, C4 is empirically motivated
  even without the absolute scale being correct.
