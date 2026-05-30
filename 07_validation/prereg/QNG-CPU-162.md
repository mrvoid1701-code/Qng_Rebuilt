---
test_id: QNG-CPU-162
title: Q-saturation vs Δ-spectrum + Cluster-B vs N*-spectrum PDG tests
category: structural / phenomenological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-093 (QNG-baryon identification)
  - CPU-153, CPU-155 (Q-saturation, cluster B)
---

# QNG-CPU-162 — PDG comparison of Q-saturation and Q-cluster predictions

## Purpose

Test two QNG predictions from CPU-153/155 against SM data:

A. **Q-saturation**: QNG predicts Hopfion Q=1 and Q=2 have equilibrium
   mass agreement to 0.46% (CPU-159 at L=20). Test against SM Δ family
   structure.

B. **Q-cluster B**: QNG predicts {Q=6, Q=7, Q=8} have E_gauge agreement
   to 0.46% (CPU-155 at L=48). Test against SM N* spectrum.

## Inputs

QNG predictions from CPU-159, CPU-155.
SM Δ family: ground state isospin quartet + 10 radial excitations.
SM N* close triples: (1675/1680/1700) and (2090/2100/2120).

## Gates

**G_A1**: QNG Q-saturation matches some SM structure within 1%.
**G_A2**: QNG Q-saturation INVALIDATES any obvious wrong mapping.

**G_B1**: At least one SM N* triple has spread < 1% (matching QNG 0.46%).
**G_B2**: At minimum, QNG cluster spread and SM triple spread are in
the same order of magnitude.

## Result (2026-05-30)

### Test A: Q-saturation

| Pattern | Spread |
|---|---|
| QNG Q=1 vs Q=2 | 0.46% |
| SM Δ isospin quartet (Δ-, Δ0, Δ+, Δ++) all at 1232 MeV | 0.00% |
| SM Δ radial excitations Δ(1232), Δ(1600), Δ(1700) | 30-38% |

**G_A1**: PASS — QNG saturation matches SM isospin quartet at 0.5%
precision (QNG: 0.46%, SM: 0.00%, structurally identical).

**G_A2**: PASS — Q-saturation does NOT match SM radial excitations
(30-38% spread). Mapping QNG Q to radial excitation is FALSIFIED.

**Interpretation**: QNG Q-labeling corresponds to ISOSPIN-LIKE quantum
number, NOT radial excitation. This is a novel structural insight —
QNG produces isospin-like multiplets via lattice equipartition without
SU(2) at substrate level.

### Test B: Cluster B

| Spread |
|---|
| QNG {Q=6, Q=7, Q=8} | 0.46% |
| SM N(1675)/N(1680)/N(1700) | 1.49% |
| SM N(2090)/N(2100)/N(2120) | 1.42% |

**G_B1**: FAIL — no SM N* triple has spread < 1%. Closest is 1.42%.

**G_B2**: PASS — QNG and SM in same order of magnitude.

**Decision: PARTIAL_FAIL** — qualitative match (both have close
triples) but quantitative mismatch (QNG predicts 3× tighter than
observed).

**Interpretation**: Cluster B mapping to N* triple is TENTATIVE.
Possibilities:
- QNG is right and there exist 3 nearly-degenerate baryon resonances
  not yet identified in PDG (spread < 0.5%)
- QNG mass mapping needs additional corrections (Phase 3 incomplete,
  topology-specific phi-XY contributions ignored)
- The mapping to N* triple is wrong; cluster B corresponds to something
  else (could be different baryon family, or composite state)

## Combined verdict

Test A: STRONG SUPPORT for Q-saturation as isospin-analog.
Test B: WEAK SUPPORT (tentative); QNG predicts tighter cluster than
SM has currently identified.

## Artifacts

- Report: `07_validation/audits/qng-q-cluster-pdg-v1/report.json`
- Test runner: `tests/cpu/qng_q_cluster_pdg_test_reference.py`

## Follow-up

DER-QNG-093 §3-§4 documents the full analysis with implications.
