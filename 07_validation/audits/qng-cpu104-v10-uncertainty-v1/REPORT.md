---
type: evidence
test_id: QNG-CPU-104
category: analytical_verification
hardware: CPU
status: completed
verdict: UR_PASS (Heisenberg uncertainty holds for all test states)
author: C.D Gabriel
date: 2026-04-24
upstream:
  - DER-QNG-062 (v10 foundational axioms)
  - QNG-CPU-103 (harmonic spectrum PASS)
---

# QNG-CPU-104 v10 uncertainty principle REPORT

## Verdict: **UR_PASS** — Heisenberg uncertainty verified

v10 axioms A3 (canonical algebra) produce the Heisenberg uncertainty
relation Δx·Δp ≥ ℏ/2 for all tested states.

## Results

### Ground state |0⟩ — minimum uncertainty
| ℏ | Δx | Δp | ΔxΔp | Saturation |
|---|---|---|---|---|
| 1.0 | 0.707 | 0.707 | 0.500 | 1.000 |
| 0.5 | 0.500 | 0.500 | 0.250 | 1.000 |
| 0.03 | 0.122 | 0.122 | 0.015 | 1.000 |

**Ground state saturates UR exactly** (DxDp = ℏ/2). Expected and verified.

### First excited |1⟩ — not minimum
| ℏ | ΔxΔp | Saturation |
|---|---|---|
| 1.0 | 1.500 | 3.000 |
| 0.5 | 0.750 | 3.000 |
| 0.03 | 0.045 | 3.000 |

**Factor 3 above minimum** (standard QM: |1⟩ gives DxDp = 3·ℏ/2).

### Coherent state |α=2⟩ — also minimum
| ℏ | Saturation |
|---|---|
| 1.0 | 1.000 |
| 0.5 | 1.000 |
| 0.03 | 26.647 (truncation artifact, N=100 too small for n=133) |

Coherent states saturate for hbar=1, 0.5. At hbar=0.03, mean n ≈ 133
but truncation N=100 causes state reconstruction issues. Physics still
holds (DxDp > ℏ/2 always).

### Superposition (|0⟩+|2⟩)/√2 — non-trivial
| ℏ | Saturation |
|---|---|
| 1.0 | 2.646 |
| 0.5 | 2.646 |
| 0.03 | 2.646 |

**Scale-invariant factor 2.646** = 7/e^(1/2) or similar — depends on
superposition structure, not hbar. Still > 1 so UR holds.

## Implications

v10 provides:
- **Requirement #1 (non-commutativity)**: Δx·Δp ≥ ℏ/2 — ✓ verified
- **Requirement #8 (discrete spectrum)**: via CPU-103 — ✓ verified

These are standard consequences of canonical quantization. v10 is
internally consistent with textbook QM at the single-site level.

## What this does NOT prove

Same caveat as CPU-103: this verifies that v10's truncated Fock
matrices correctly implement canonical commutation. It does NOT show:
- Classical limit recovery (needs CPU-105)
- ℏ derivation from substrate
- Multi-site physics (needs lattice implementation)

## Next critical tests

**CPU-105 classical limit**: take coherent state |α⟩ with large |α|,
evolve under Ĥ_v10, verify that ⟨Ψ̂(t)⟩ matches v8 Yoshida4 classical
trajectory. This is the REAL test of v10 as quantization of v8.

**CPU-106 ℏ identification**: compute ground state energy of v10 and
compare with classical v8 ground energy + zero-point sum. If
self-consistent with specific ℏ value, we have a numerical constraint
on ℏ_lattice.

## Files

- Script: `tests/cpu/qng_cpu104_v10_uncertainty.py`
- Report JSON: `report.json`
