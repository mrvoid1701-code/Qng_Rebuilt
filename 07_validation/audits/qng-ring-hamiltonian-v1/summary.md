# QNG-CPU-056 Audit Summary

**Result: FAIL**
Date: 2026-04-07
Script: `tests/cpu/qng_ring_hamiltonian_reference.py`

## Check results

| Check | Gate | Result |
|-------|------|--------|
| 1 - Ring survives k_back=0 (v5 baseline) | M > 50 at T=1500 | PASS (M=810) |
| 2 - H increases with k_back at T=600 | H(k=0.05) > H(k=0) | PASS (H=-591 -> H=+4) |
| 3 - Ring survives k_back=0.10 (v6 stability) | M > 50 at T=1500 | FAIL (M=0) |

## Raw data at T=final (Phase-2 step 1500)

| k_back | T      | E       | H       | M     | ring |
|--------|--------|---------|---------|-------|------|
| 0.00   | 0.00   | -368.28 | -368.28 | 810.1 | OK   |
| 0.02   | 1.36   | +2.48   | +3.84   | 8.4   | DEAD |
| 0.05   | 0.59   | +2.32   | +2.91   | 1.2   | DEAD |
| 0.10   | 69.76  | +209.96 | +279.72 | 0.0   | DEAD |
| 0.20   | 37.51  | -87.26  | -49.75  | 0.0   | DEAD |

## Root cause of failure

Channel G is intrinsically incompatible with the v5 ring growth mechanism.

The v5 ring forms through Phase 2 Channel F depletion (gamma_phi x D_i x sigma_i).
Channel G adds +k_back x chi_core per step to sigma, directly opposing depletion.

At the ring core: chi_core ~ 10-12 (maintained by DELTA coupling).
Channel G sigma boost per step = k_back x chi_core ~ k_back x 10.

Stability threshold: gamma_phi x D_core x sigma_core > k_back x chi_core
  0.10 x 0.55 x 0.27 = 0.015 > k_back x 10
  -> k_back < 0.0015

All tested k_back values (>=0.02) are 10x above the stability threshold.
The ring never grows past M~15 when Channel G is active during Phase 2.

## H sign confirmation (Check 2 PASS)

H IS positive for k_back >= 0.02 wherever the ring briefly exists.
This confirms DER-QNG-032: for k_back > k_min, T > |E| and H > 0.
k_min ~ 0.02 (H first crosses zero between k_back=0.00 and k_back=0.02).

## Physical mass estimate (informational - ring not stable)

Using k_back=0.10 (ring dissolved, numbers from chaotic state):
  H_ring = 279.72 substrate units
  m_ring = 9.4e13 kg = 5.9e23 GeV
  (proton = 1.67e-27 kg = 0.938 GeV)
This is unphysical. Mass estimate requires a stable v6 ring.

## Key finding

The chi field that makes the ring massive (large chi_core -> large T) is the
same chi field that, through Channel G, destroys the ring's sigma depletion
structure. There is a fundamental tension:

  Large chi_core -> large T -> H > 0 (positive mass)  [wanted]
  Large chi_core -> Channel G -> sigma restored -> ring collapses  [unwanted]

## Next step (QNG-CPU-057 candidate)

Snapshot H measurement protocol:
1. Run full v5 ring to stable state (CPU-044/055 protocol)
2. Record final (sigma, chi, phi) state
3. Evaluate H = T(k_back) + E at that snapshot for each k_back
4. No v6 time evolution - purely evaluate the v6 Hamiltonian on the v5 ring state

This decouples the mass measurement from the stability problem.
