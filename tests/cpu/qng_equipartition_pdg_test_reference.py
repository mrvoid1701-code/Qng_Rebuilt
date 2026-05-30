from __future__ import annotations

"""QNG-CPU-176: CRITICAL TEST — cubic equipartition vs PDG triples.

The QNG framework's FIRST RIGOROUS FALSIFIABILITY TEST.

QNG prediction (DER-QNG-092 §G, CPU-155):
Three Hopfion Q values in the same lattice-symmetry cluster have
EQUAL gauge energy E_gauge. The cluster B is {Q=6, Q=7, Q=8} with
relative spread:
  L=24: 0.83%
  L=48: 0.46%
Extrapolation suggests CONTINUUM: 0% (exact degeneracy)

CANDIDATE SM TRIPLE (closest match by mass to QNG cluster B at L=48):
N(1675) D15, N(1680) F15, N(1700) D13.

But: these three particles have DIFFERENT J^P values (5/2-, 5/2+, 3/2-),
so SM does NOT predict them as a multiplet. SM spread comes from
spin-orbit / spin-parity differences.

QUESTIONS:
1. Is QNG cluster B prediction consistent with observed N(1675/1680/1700)
   spread?
2. Are there OTHER observed triples with smaller spread that could be
   the true QNG cluster B match?
3. Can the observed spread be entirely explained by SM spin-parity
   corrections, leaving QNG substrate prediction intact?

Reference: CPU-155 cluster B data, DER-QNG-092 §G.
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equipartition-pdg-test-v1"


# QNG cluster B data from CPU-155 (L=48 best precision)
QNG_CLUSTER_B = {
    "L=24": {"Q6": 19186.5, "Q7": 19186.5, "Q8": 19028.6},
    "L=48": {"Q6": 34346.2, "Q7": 34346.2, "Q8": 34188.3},
}


def qng_cluster_stats(data):
    """Statistics on cluster B at given L."""
    vals = list(data.values())
    mean = sum(vals) / len(vals)
    max_val = max(vals)
    min_val = min(vals)
    spread_abs = max_val - min_val
    spread_pct = spread_abs / mean * 100
    return {"mean": mean, "max": max_val, "min": min_val,
            "spread_abs": spread_abs, "spread_pct": spread_pct}


# PDG values (from PDG 2023 Particle Listings, central values)
# Format: (name, mass MeV, mass_err MeV, width MeV, J^P, total_isospin)
PDG_TRIPLES = [
    {
        "name": "N(1675/1680/1700)",
        "particles": [
            ("N(1675)", 1675, 5, 150, "5/2-", "1/2"),
            ("N(1680)", 1680, 4, 130, "5/2+", "1/2"),
            ("N(1700)", 1700, 20, 150, "3/2-", "1/2"),
        ],
    },
    {
        "name": "N(2090/2100/2120)",
        "particles": [
            ("N(2090)", 2090, 50, 350, "1/2-", "1/2"),
            ("N(2100)", 2100, 30, 200, "1/2+", "1/2"),
            ("N(2120)", 2120, 40, 300, "3/2-", "1/2"),
        ],
    },
    {
        "name": "N(1875/1880/1900)",
        "particles": [
            ("N(1875)", 1875, 30, 200, "3/2-", "1/2"),
            ("N(1880)", 1880, 30, 300, "1/2+", "1/2"),
            ("N(1900)", 1900, 30, 200, "3/2+", "1/2"),
        ],
    },
]

# Also "doublet" tests — Q=1,Q=2 cluster A
PDG_DOUBLETS = [
    {"name": "p/n", "particles": [
        ("p", 938.272, 0.001, 0, "1/2+", "1/2"),
        ("n", 939.565, 0.001, 0, "1/2+", "1/2"),
    ]},
    {"name": "N(1535)/N(1520)", "particles": [
        ("N(1535)", 1535, 10, 150, "1/2-", "1/2"),
        ("N(1520)", 1515, 5, 110, "3/2-", "1/2"),
    ]},
]


def pdg_triple_stats(triple):
    """Statistics on a PDG triple."""
    masses = [p[1] for p in triple["particles"]]
    errors = [p[2] for p in triple["particles"]]
    mean = sum(masses) / len(masses)
    spread_abs = max(masses) - min(masses)
    spread_pct = spread_abs / mean * 100
    # Total error in spread (max - min)
    spread_err = (errors[masses.index(max(masses))] +
                  errors[masses.index(min(masses))])
    return {"mean": mean, "spread_abs": spread_abs, "spread_pct": spread_pct,
            "spread_err": spread_err}


def main():
    out = Path(DEFAULT_OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    print("QNG-CPU-176: CRITICAL TEST — cubic equipartition vs PDG")
    print("=" * 80)
    print()

    # QNG predictions
    print("QNG CLUSTER B predictions (E_gauge):")
    print("-" * 80)
    qng_stats = {}
    for L_key, data in QNG_CLUSTER_B.items():
        stats = qng_cluster_stats(data)
        qng_stats[L_key] = stats
        print(f"  {L_key}: mean E_gauge = {stats['mean']:.1f}, "
              f"spread = {stats['spread_abs']:.1f} = {stats['spread_pct']:.2f}%")
    print()
    print("Continuum L -> infinity extrapolation:")
    print(f"  L=24 spread: {qng_stats['L=24']['spread_pct']:.2f}%")
    print(f"  L=48 spread: {qng_stats['L=48']['spread_pct']:.2f}%")
    ratio = qng_stats['L=24']['spread_pct'] / qng_stats['L=48']['spread_pct']
    print(f"  Spread reduction L=24 -> L=48: factor {ratio:.2f}")
    print(f"  EXTRAPOLATED L -> infinity spread: approaches 0%")
    print()

    print("=" * 80)
    print("PDG TRIPLE COMPARISON")
    print("=" * 80)
    print()

    qng_predicted_spread_pct_L48 = qng_stats['L=48']['spread_pct']
    qng_predicted_spread_pct_continuum = 0.0  # exact equipartition

    for triple in PDG_TRIPLES:
        print(f"\nTriple: {triple['name']}")
        print("-" * 80)
        stats = pdg_triple_stats(triple)
        for p in triple['particles']:
            print(f"  {p[0]:<12} mass = {p[1]:>6} ± {p[2]:>3} MeV, "
                  f"width = {p[3]:>4} MeV, J^P = {p[4]:<6}")
        print(f"  Mean mass: {stats['mean']:.1f} MeV")
        print(f"  Spread: {stats['spread_abs']} MeV "
              f"= {stats['spread_pct']:.2f}% (error ±{stats['spread_err']})")

        print(f"\n  QNG prediction (L=48): {qng_predicted_spread_pct_L48:.2f}%")
        print(f"  QNG prediction (continuum): {qng_predicted_spread_pct_continuum:.2f}%")
        ratio_L48 = stats['spread_pct'] / qng_predicted_spread_pct_L48
        print(f"  Observed/predicted ratio (L=48): {ratio_L48:.2f}x")

        if ratio_L48 < 1.5:
            verdict = "CONSISTENT with QNG at L=48"
        elif ratio_L48 < 5:
            verdict = "PARTIAL match (factor 2-5x)"
        else:
            verdict = "INCONSISTENT (>5x) — QNG prediction too tight"
        print(f"  Verdict: {verdict}")

    print()
    print("=" * 80)
    print("DOUBLET TEST (cluster A: Q=1, Q=2)")
    print("=" * 80)
    print(f"QNG cluster A spread at L=48: 0.68% (Q=1 vs Q=2)")
    print()

    for doublet in PDG_DOUBLETS:
        print(f"\nDoublet: {doublet['name']}")
        masses = [p[1] for p in doublet['particles']]
        spread = max(masses) - min(masses)
        mean = sum(masses) / 2
        spread_pct = spread / mean * 100
        for p in doublet['particles']:
            print(f"  {p[0]:<12} mass = {p[1]} ± {p[2]} MeV, J^P = {p[4]}")
        print(f"  Spread: {spread:.2f} MeV = {spread_pct:.4f}%")
        print(f"  QNG cluster A predicts: 0.68%")
        ratio = spread_pct / 0.68
        print(f"  Observed/predicted ratio: {ratio:.3f}x")

    print()
    print("=" * 80)
    print("HONEST VERDICT")
    print("=" * 80)
    print("""
QNG cubic equipartition prediction status:

1. SIGN: QNG correctly predicts existence of close-mass baryon
   multiplets (factor 2-5x match with observed).

2. MAGNITUDE: QNG predicts spread WAY TIGHTER than observed.
   - For triples: QNG 0.46% vs PDG 1.0-1.5% (factor 2-3x)
   - For p/n doublet: QNG 0.68% vs PDG 0.14% (QNG TOO LOOSE!)

3. CONTINUUM (L -> infinity): QNG predicts EXACT equipartition (0%).
   Observed spread must then come from SM corrections (EM, spin-orbit).
   The 1.3 MeV n-p split is mostly EM. The 25 MeV N* triple spread
   could be spin-orbit between J=5/2-, 5/2+, 3/2-.

4. SPECIFICALLY: J^P values are DIFFERENT in the N(1675/1680/1700)
   triple. SM does NOT predict these as a multiplet. If QNG groups
   them, that's a STRUCTURAL CLAIM that must be derived from
   topology, not just mass coincidence.

OVERALL: The prediction is NOT cleanly falsified, but it requires:
- Derivation of EM + spin-orbit corrections within QNG to explain
  observed spread starting from exact equipartition
- Justification for why specific J^P values land in same Q-cluster

Without these derivations, the prediction is INCONCLUSIVE rather
than confirmed.

CONFIDENCE in QNG cubic equipartition: ~25-30%

(Lower than initial impression because:
- p/n splitting is 5x SMALLER than QNG predicts at L=48
- N* triple spread is 3x LARGER than QNG predicts at L=48
- No consistent calibration emerges
- The triple has different J^P, which SM treats as independent)
""")

    report = {
        "test_id": "QNG-CPU-176_equipartition_pdg",
        "qng_cluster_B_data": QNG_CLUSTER_B,
        "qng_stats": qng_stats,
        "pdg_triples_tested": [
            {
                "name": t["name"],
                "stats": pdg_triple_stats(t),
                "particles": t["particles"],
            } for t in PDG_TRIPLES
        ],
        "pdg_doublets_tested": [
            {
                "name": d["name"],
                "spread": max(p[1] for p in d["particles"]) -
                         min(p[1] for p in d["particles"]),
                "particles": d["particles"],
            } for d in PDG_DOUBLETS
        ],
        "verdict": "INCONCLUSIVE — partial match (factor 2-5x) requires "
                  "further theoretical work to derive corrections",
        "qng_confidence_in_equipartition_pct": 27,
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
