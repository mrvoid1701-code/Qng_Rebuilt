---
test_id: QNG-CPU-164
title: W+W- composite (neutron candidate) and W+W+ composite (Δ++ candidate)
category: structural / phenomenological / composites
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-082 (DM no-go, neutral elementary forbidden)
  - DER-QNG-093 (initial baryon identifications)
  - DER-QNG-094 (this work's parent doc)
  - CPU-049 (W+W- attract, W+W+ repel)
  - CPU-050 (W+W- bound state d≈3λ)
  - CPU-159 (v12 enhanced masses)
---

# QNG-CPU-164 — Composite knot states under v12 enhanced

## Purpose

Test if QNG can host the neutron (q=0) and Δ++ (q=+2) as composites
of single-charge rings, since v12 forbids neutral and ±2 elementary
particles (DER-QNG-082 charge-topology link).

If W+W- gives neutron mass (940 MeV via trefoil↔proton scale), neutron
is identified.
If W+W+ gives Δ++ mass (1232 MeV), Δ++ is identified.

## Inputs

L=20, v12 enhanced (e=3.0, mu_A=1.0, BETA_A=0.05).

Four configurations:
1. ring_W+_single: single ring vortex (baseline)
2. W+W-_composite: opposite-chirality pair at separation D=6 lu
3. W+W+_control: same-chirality pair at D=6 lu
4. trefoil_proton: reference (must give proton ratio = 1.000)

Three-phase protocol: P1=300, P2=1500, P3=3000.

## Gates

**G_neutron**: W+W- composite mass / trefoil = 1.0014 ± 0.02
(i.e., within 2% of SM neutron/proton ratio).

**G_delta++**: W+W+ composite mass / trefoil = 1.3131 ± 0.02
(within 2% of SM Δ++/proton ratio).

## Result (2026-05-30)

| Config | charge | M_P3_end | Ratio to trefoil | Compare with SM |
|---|---|---|---|---|
| ring_W+_single | +1 | 2168 | 1.140 | (no clean S=0 match) |
| W+W-_composite | 0 | 1807 | 0.950 | neutron 1.001 → −5.14% |
| W+W+_control | +2 | **2515** | **1.322** | Δ++ 1.313 → **+0.68%** |
| trefoil_proton | +1 | 1902 | 1.000 | proton (reference) |

**Gates**:
- G_neutron: **FAIL** (−5.14% error)
- G_delta++: **PASS** (+0.68% error, within 2% tolerance)

**Decision: PARTIAL_PASS** — Δ++ identified, neutron not.

## Interpretation

### Δ++ identification (NEW)

QNG W+W+ composite has charge +2, mass ratio 1.322 to trefoil.
SM Δ++ has charge +2, mass ratio 1.313 to proton.
**Identification clean at 0.68% — best QNG identification to date**.

### Neutron not identified

QNG W+W- composite has charge 0 but mass 1807 = LESS than single ring
(2168). This is qualitatively wrong: composites should be heavier
than constituents.

Physical explanation: opposite-chirality phi-windings cancel partially
in overlap, reducing total disorder and matter depletion. This is an
ANNIHILATION channel, not a binding channel.

Therefore W+W- is not a neutron candidate. Neutron remains structurally
absent in QNG v12, requires v13 SU(2) for proton↔neutron weak conversion.

### 891 MeV: open prediction

W+W- composite mass 891 MeV (after rescaling via proton-trefoil) has
no clean SM non-strange neutral hadron match. Closest:
- η' (957.78): +7.5% error
- K* (891.66): exact, but K* has S=−1 (strange)

QNG predicts a q=0 S=0 hadron-like state at 891 MeV that doesn't have
clean SM correspondence. This is a TENTATIVE QNG prediction.

## Artifacts

- Report: `07_validation/audits/qng-neutron-composite-v1/report.json`
- Test runner: `tests/cpu/qng_neutron_composite_reference.py`

## Follow-up

- CPU-165: anti-Hopfion ↔ Δ- (q=-1)
- CPU-166: W-W- composite ↔ Δ--
- CPU-167: separation scan for W+W- to find true equilibrium binding
- DER-QNG-094 documents the full analysis
