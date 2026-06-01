# REPORT — demo foundational checks E1/E2/E3/E6

Date: 2026-06-01
Probe: `demo-theory/tests/e1_e2_e3_e6_foundational.py`

| Exp | Quantity | Result | Reading |
|---|---|---|---|
| E1 | v_group / c_phi | 0.989 | wave packet rides the lightcone (PASS) |
| E2 | c [100]/[110]/[111] | 0.300 / 0.283 / 0.289 | lightcone ~round |
| E2 | eta_LV anisotropy | 0.059 | finite-k lattice artifact; ->0 at small k |
| E3 | omega*L spread across L={16,20,24} | 0.141 | leans box modes ~1/L (noisy at this res) |
| E6 | two-slit fringe extrema | 6 | interference present -> superposition works (PASS) |

Notes:
- E1: classical wave kinematics only; E=hbar*omega is NOT tested (no hbar in the
  classical substrate -- that is the separate, still-open hbar program).
- E2: eta_LV here is finite-lattice/finite-k, not the physical LIV prediction;
  connecting to main-theory eta_LV needs small-k extrapolation.
- E3: peak identification is FFT-resolution limited; trend favors box (1/L) modes
  but is not decisive at L<=24.
- E6: demonstrates phase-wave superposition (the QM face of the GR<->QM bridge).
