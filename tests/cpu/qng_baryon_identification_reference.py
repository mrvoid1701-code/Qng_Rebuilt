from __future__ import annotations

"""QNG-CPU-161: Systematic QNG knot mass-ratio identification with baryons.

Inputs:
- QNG knot masses from CPU-159 (v12 enhanced, e=3.0): trefoil, figure_8,
  cinquefoil, ring, hopfion_Q1, hopfion_Q2.
- PDG baryon octet (J=1/2+) and decuplet (J=3/2+) masses.

Constraints:
- v12 charge-topology link (DER-QNG-082) forbids neutral elementary
  particles. So only charged baryons (q=±1) are eligible candidates.
- Excludes: neutron (q=0), Λ (q=0), Σ0 (q=0), Ξ0 (q=0), Δ0 (q=0),
  Δ++ (q=+2, requires winding 2), Ω- (s=3, multi-strange).

Method:
- Use trefoil as reference (lightest in QNG class).
- Identify trefoil with proton (lightest stable charged baryon).
- Compute all QNG mass ratios to trefoil.
- Compute all baryon mass ratios to proton.
- For each QNG topology, find best baryon match by minimum |ratio_QNG - ratio_SM|.
- Output identification table with errors.

Reference: Paper 7 §4 (refined), DER-QNG-093.
"""

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-baryon-identification-v1"


# QNG masses from CPU-159 enhanced v12 at e=3.0, L=20 (M_ring at P3 end)
QNG_MASSES = {
    "trefoil":    1902.16,
    "cinquefoil": 1981.45,
    "figure_8":   2132.69,
    "ring_Q0":    2167.99,
    "hopfion_Q2": 2445.25,
    "hopfion_Q1": 2456.50,
}


# PDG baryon masses (MeV). Charge q=+1 or -1 only (v12 constraint).
# J=1/2+ octet (J^P assignment):
# J=3/2+ decuplet:
BARYONS = [
    # (name, mass_MeV, charge, J, P, strangeness, label)
    ("p",        938.27,  +1, 0.5, +1, 0,  "proton (J=1/2+, S=0)"),
    ("Sigma+",  1189.37,  +1, 0.5, +1, -1, "Sigma+ (J=1/2+, S=-1)"),
    ("Sigma-",  1197.45,  -1, 0.5, +1, -1, "Sigma- (J=1/2+, S=-1)"),
    ("Xi-",     1321.71,  -1, 0.5, +1, -2, "Xi- (J=1/2+, S=-2)"),
    ("Delta+",  1232.0,   +1, 1.5, +1, 0,  "Delta+ (J=3/2+, S=0)"),
    ("Delta-",  1232.0,   -1, 1.5, +1, 0,  "Delta- (J=3/2+, S=0)"),
    ("SigmaStar+", 1382.8, +1, 1.5, +1, -1, "Sigma*+ (J=3/2+, S=-1)"),
    ("SigmaStar-", 1387.2, -1, 1.5, +1, -1, "Sigma*- (J=3/2+, S=-1)"),
    ("XiStar-", 1535.0,   -1, 1.5, +1, -2, "Xi*- (J=3/2+, S=-2)"),
    # N excitations (J^P varies)
    ("N1440",   1430.0,   +1, 0.5, +1, 0,  "N(1440) Roper (J=1/2+)"),
    ("N1535",   1535.0,   +1, 0.5, -1, 0,  "N(1535) (J=1/2-)"),
    ("N1520",   1515.0,   +1, 1.5, -1, 0,  "N(1520) (J=3/2-)"),
    ("N1650",   1650.0,   +1, 0.5, -1, 0,  "N(1650) (J=1/2-)"),
    ("N1675",   1675.0,   +1, 2.5, -1, 0,  "N(1675) (J=5/2-)"),
    ("N1680",   1680.0,   +1, 2.5, +1, 0,  "N(1680) (J=5/2+)"),
    ("N1700",   1700.0,   +1, 1.5, -1, 0,  "N(1700) (J=3/2-)"),
    ("N1710",   1710.0,   +1, 0.5, +1, 0,  "N(1710) (J=1/2+)"),
    ("N1720",   1720.0,   +1, 1.5, +1, 0,  "N(1720) (J=3/2+)"),
]


def identify():
    """Match QNG knots to baryons by mass ratio."""
    # Reference: lightest QNG topology -> proton
    M_QNG_ref = QNG_MASSES["trefoil"]
    M_SM_ref  = 938.27  # proton

    print("=" * 80)
    print("QNG mass ratios (relative to trefoil = proton candidate)")
    print(f"Reference: trefoil M_QNG = {M_QNG_ref:.2f}; proton M_SM = {M_SM_ref:.2f} MeV")
    print("=" * 80)

    qng_ratios = {}
    for name, M in QNG_MASSES.items():
        qng_ratios[name] = M / M_QNG_ref
        print(f"  {name:<14} M_QNG = {M:>8.2f}  ratio = {qng_ratios[name]:.4f}")
    print()

    # SM ratios to proton
    sm_ratios = {b[0]: b[1]/M_SM_ref for b in BARYONS}

    # For each QNG topology, find best SM match
    print("=" * 100)
    print("Best baryon match per QNG topology (minimum |ratio difference|)")
    print("=" * 100)
    identifications = []
    for qng_name, qng_ratio in qng_ratios.items():
        # Find min difference (use SM ratios)
        best_match = None
        best_err = float('inf')
        candidates = []
        for b in BARYONS:
            sm_name = b[0]
            sm_ratio = sm_ratios[sm_name]
            err = abs(qng_ratio - sm_ratio)
            candidates.append((sm_name, sm_ratio, err, b[2], b[3], b[6]))
            if err < best_err:
                best_err = err
                best_match = (sm_name, sm_ratio, err, b)

        # Sort candidates by error and pick top 3
        candidates.sort(key=lambda c: c[2])
        top3 = candidates[:3]

        bm_name, bm_ratio, bm_err, bm_full = best_match
        bm_pred_M_MeV = qng_ratio * M_SM_ref
        actual_M = bm_full[1]
        m_err_pct = (bm_pred_M_MeV - actual_M) / actual_M * 100

        identifications.append({
            "qng_topology": qng_name,
            "qng_mass_substrate": QNG_MASSES[qng_name],
            "qng_ratio_to_trefoil": qng_ratio,
            "predicted_mass_MeV": bm_pred_M_MeV,
            "best_SM_match": bm_full[6],
            "best_SM_name": bm_name,
            "best_SM_mass_MeV": actual_M,
            "best_SM_ratio": bm_ratio,
            "ratio_error_abs": bm_err,
            "ratio_error_pct": bm_err / bm_ratio * 100 if bm_ratio > 0 else 0,
            "mass_error_pct": m_err_pct,
            "best_SM_J": bm_full[3],
            "best_SM_P": bm_full[4],
            "top3_candidates": [(c[0], c[2]/c[1]*100 if c[1] > 0 else 0) for c in top3],
        })

        print(f"\n  {qng_name:<14} ratio={qng_ratio:.4f}")
        print(f"    -> Predicted m = {bm_pred_M_MeV:.1f} MeV")
        print(f"    Best match: {bm_full[6]}")
        print(f"      actual m = {actual_M:.1f} MeV  ratio = {bm_ratio:.4f}")
        print(f"      mass error: {m_err_pct:+.2f}%  ratio error: {bm_err / bm_ratio * 100:+.2f}%")
        print(f"    Top 3 candidates by error:")
        for c in top3:
            print(f"      {c[0]:<12} ratio={c[1]:.4f} err={c[2]/c[1]*100:+.2f}%")

    print()
    print("=" * 100)
    print("Summary table")
    print("=" * 100)
    print(f"{'QNG topology':<14} {'pred. m (MeV)':>14} {'SM match':<20} "
          f"{'actual m':>10} {'mass err %':>11}")
    print("-" * 100)
    for ident in identifications:
        print(f"{ident['qng_topology']:<14} {ident['predicted_mass_MeV']:>14.1f} "
              f"{ident['best_SM_name']:<20} {ident['best_SM_mass_MeV']:>10.1f} "
              f"{ident['mass_error_pct']:>+11.2f}")

    return identifications


def export(identifications, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "test_id": "QNG-CPU-161",
        "qng_input_masses": QNG_MASSES,
        "proton_reference_MeV": 938.27,
        "qng_reference_topology": "trefoil",
        "identifications": identifications,
        "method": (
            "Use trefoil (lightest QNG topology with charge +e) as proton "
            "candidate. Compute mass ratios to proton in both QNG and SM. "
            "For each QNG topology, find baryon with minimum |ratio "
            "difference|. v12 charge constraint q=±1 enforced (neutral "
            "baryons excluded)."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    identifications = identify()
    export(identifications, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
