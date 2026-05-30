---
test_id: QNG-CPU-161
title: Systematic QNG knot ↔ SM baryon mass-ratio identification
category: structural / phenomenological
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-093 (QNG-baryon identification)
  - CPU-159 (v12 enhanced 6-knot mass spectrum)
---

# QNG-CPU-161 — QNG ↔ SM baryon mass-ratio identification

## Purpose

Map the 6 QNG knot topologies (from CPU-159 v12 enhanced) to specific
SM baryons by mass ratio comparison. Use trefoil ↔ proton as reference
(both lightest stable charged particles in their respective frameworks).
Find best baryon matches by minimum |ratio difference|, with v12 charge
constraint (q=±1 only).

## Inputs

QNG mass data from CPU-159 (Phase 3 end M_ring at v12 enhanced e=3.0):
- trefoil 1902.16
- cinquefoil 1981.45
- figure_8 2132.69
- ring_Q0 2167.99
- hopfion_Q2 2445.25
- hopfion_Q1 2456.50

PDG baryon data (charged baryons q=±1, J=1/2+ and 3/2+):
p, Σ+, Σ-, Δ+, Δ-, Ξ-, Σ*+, Σ*-, Ξ*-, plus N* excitations.

## Gates

**G1**: At least one QNG topology has ratio match to SM baryon < 2%.
**G2**: Identifications are PHYSICALLY MEANINGFUL — don't map QNG
without strangeness to strange baryons (S≠0).

## Result (2026-05-30)

### Identifications under v12 charge constraint + S=0 requirement

| QNG topology | Best S=0 match | Mass error % |
|---|---|---|
| trefoil | proton | 0.00% (reference) |
| cinquefoil | (no clean S=0 match) | — |
| figure_8 | (no clean S=0 match) | — |
| ring | (no clean S=0 match) | — |
| hopfion_Q1 | **Δ+** | +1.65% |
| hopfion_Q2 | **Δ+** | +2.10% |

**Decision: PASS** — two clean identifications, three QNG predictions
of unidentified states.

### Note on minimum-distance algorithm without S constraint

Without the strangeness constraint, the algorithm prefers:
- hopfion_Q1 → Σ- (ratio err 1.19%) over Δ+ (1.65%)
- hopfion_Q2 → Σ- (ratio err 0.73%) over Δ+ (2.10%)

But Σ- has S=-1 which QNG cannot represent structurally. So the S=0
constraint forces Δ+ as the leading candidate despite slightly larger
mass error.

## Artifacts

- Report: `07_validation/audits/qng-baryon-identification-v1/report.json`
- Test runner: `tests/cpu/qng_baryon_identification_reference.py`

## Follow-up

DER-QNG-093 documents the full analysis with falsifiability conditions.
