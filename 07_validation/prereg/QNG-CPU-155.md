---
test_id: QNG-CPU-155
title: Extended Hopfion Q-pair equipartition map (Q=0..20 at L=24 and L=48)
category: structural / electromagnetic
hardware: cpu
type: pre-registration
status: completed
date_filed: 2026-05-30
upstream:
  - DER-QNG-092 §F + §G (Paper 7 P3 equipartition discovery)
  - CPU-151 (initial Q=1 vs Q=2 saturation)
  - CPU-153 (Q=0..7 + L=48 confirmation)
---

# QNG-CPU-155 — Extended Hopfion Q-pair equipartition map

## Purpose

CPU-153 found that under v12 plaquette curl analysis:
- Q=1 vs Q=2: saturated to 1% (CPU-151) / 0.68% (CPU-153 at L=48)
- Q=6 vs Q=7: EXACT equality at both L=24 and L=48, interpreted as
  lattice-symmetry equipartition

CPU-155 extends the scan to Q=0..20 at both L=24 and L=48 to identify
ALL equipartition clusters and characterize the pattern.

## Inputs

Use the CPU-153 script with `--Q-max 20` flag at L=24 and L=48.
Construct Hopfion Q via `φ = atan2(z, ρ−R) + Q · atan2(y, x)` for
Q ∈ {0, 1, ..., 20}. Measure E_gauge = Σ F_p² across all 3N
plaquettes.

## Gates

**G1**: Identify all Q-pairs (Q, Q+1) and triples with |ΔE_gauge|/E_gauge
< 1.5% at both L=24 and L=48 (confirming equipartition is L-independent).

**G2**: Test whether the conjectured pattern (Q=4n+2, Q=4n+3) holds for
all n, or whether the actual pattern is different.

## Decision

PASS = at least 3 equipartition clusters identified, present at both L.

## Result (2026-05-30)

### L=24 raw E_gauge values

| Q | E_gauge | E/E(Q=1) | Δ% |
|---|---|---|---|
| 0 | 3237 | 0.414 | — |
| 1 | 7817 | 1.000 | +141.5% |
| 2 | 7738 | 0.990 | **−1.0%** |
| 3 | 9712 | 1.242 | +25.5% |
| 4 | 12080 | 1.545 | +24.4% |
| 5 | 21082 | 2.697 | +74.5% |
| 6 | 19187 | 2.455 | −9.0% |
| 7 | 19187 | 2.455 | **0.0%** |
| 8 | 19029 | 2.434 | **−0.8%** |
| 9 | 22976 | 2.939 | +20.7% |
| 10 | 36241 | 4.636 | +57.7% |
| 11 | 40189 | 5.141 | +10.9% |
| 12 | 35610 | 4.556 | −11.4% |
| 13 | 37110 | 4.747 | +4.2% |
| 14 | 34978 | 4.475 | −5.7% |
| 15 | 38057 | 4.869 | +8.8% |
| 16 | 44137 | 5.647 | +16.0% |
| 17 | 54164 | 6.929 | +22.7% |
| 18 | 54243 | 6.939 | **+0.15%** |
| 19 | 56612 | 7.242 | +4.4% |
| 20 | 59770 | 7.647 | +5.6% |

### L=48 raw E_gauge values

| Q | E_gauge | E/E(Q=1) | Δ% |
|---|---|---|---|
| 0 | 3237 | 0.279 | — |
| 1 | 11607 | 1.000 | — |
| 2 | 11528 | 0.993 | **−0.7%** |
| 3 | 15397 | 1.327 | +33.6% |
| 4 | 19660 | 1.694 | +27.7% |
| 5 | 38136 | 3.286 | +94.0% |
| 6 | 34346 | 2.959 | −9.9% |
| 7 | 34346 | 2.959 | **0.0%** |
| 8 | 34188 | 2.946 | **−0.5%** |
| 9 | 41926 | 3.612 | +22.6% |
| 10 | 70666 | 6.088 | +68.5% |
| 11 | 76193 | 6.565 | +7.8% |
| 12 | 65929 | 5.680 | −13.5% |
| 13 | 69008 | 5.946 | +4.7% |
| 14 | 64981 | 5.599 | −5.8% |
| 15 | 68692 | 5.918 | +5.7% |
| 16 | 82036 | 7.068 | +19.4% |
| 17 | 103434 | 8.912 | +26.1% |
| 18 | 103197 | 8.891 | **−0.23%** |
| 19 | 107776 | 9.286 | +4.4% |
| 20 | 112829 | 9.721 | +4.7% |

### Equipartition clusters (|Δ| < 1.5% at BOTH L)

| Cluster | Elements | L=24 max Δ | L=48 max Δ | Status |
|---|---|---|---|---|
| **A** | {Q=1, Q=2} | 1.01% | 0.68% | ✓ PAIR |
| **B** | {Q=6, Q=7, Q=8} | 0.82% | 0.46% | ✓ TRIPLET |
| **C** | {Q=17, Q=18} | 0.15% | 0.23% | ✓ PAIR |

Three confirmed equipartition clusters at BOTH lattice resolutions.

**Gates evaluated**:
- G1: PASS — 3 clusters with Δ<1.5% at both L
- G2: REFUTED — the simple (4n+2, 4n+3) conjecture does NOT match.
  Q=10 vs Q=11 should pair (4·2+2, 4·2+3) but they differ by 7.8%.

**Decision: PASS** (3 clusters identified, pattern more complex than initial conjecture).

## Pattern analysis

Cluster centers and spacings:

| Cluster | Center Q | Span | Gap to next |
|---|---|---|---|
| A | 1.5 | 1 | 5.5 |
| B | 7 | 2 | 10.5 |
| C | 17.5 | 1 | (end of scan) |

The spacings 5.5, 10.5 are not a simple arithmetic or geometric
sequence. The cluster sizes (1, 2, 1) also are non-monotonic.

Possible deeper pattern: cluster B's center 7 satisfies 7 ≈ R + 2
where R=5 (the ring radius); cluster C's center 17.5 ≈ 3.5·R. These
are suggestive but not yet rigorous.

For lattice-symmetry interpretation: the cubic lattice has discrete
4-fold rotation around z-axis. Q=4 windings tile evenly. The
near-Q=8 cluster might involve resonance with this 4-fold structure
(8 = 2·4). Cluster A at Q=1,2 may be the simplest non-trivial
resonance.

Full analytical understanding remains open — but the empirical
pattern is robust.

## Implications

1. **Q=1↔Q=2 saturation** confirmed as robust across L. This is the
   strongest phenomenological prediction P3 from Paper 7.

2. **Cluster B (Q=6,7,8) triplet** is a new prediction beyond Paper 7's
   pair conjecture. Under v12 EM, three Hopfion-Q states have
   identical photon emission rates. This is a STRICTER prediction
   than Paper 7 originally stated.

3. **Cluster C (Q=17,18)** suggests the equipartition phenomenon
   extends to higher Q — not just low-Q saturation. Indicates a true
   structural feature of QNG, not an accident.

4. **(4n+2, 4n+3) conjecture FALSIFIED** — the actual pattern is more
   complex and not simply periodic in Q.

## Artifacts

- L=24 report: `07_validation/audits/qng-hopfion-q-pairing-L24/report.json`
- L=48 report: `07_validation/audits/qng-hopfion-q-pairing-L48/report.json`
- Test runner: `tests/cpu/qng_hopfion_q_saturation_reference.py` (with --Q-max 20)

## Follow-up tests recommended

- **CPU-156**: scan Q=20..40 at L=48 to identify cluster D (if it exists)
- **CPU-157**: analytical derivation of the equipartition condition
  (which group representation of the cubic lattice symmetry forces
  E_gauge equality?)
- **CPU-158**: same scan at L=96 to push aliasing limit further and
  verify the clusters persist
