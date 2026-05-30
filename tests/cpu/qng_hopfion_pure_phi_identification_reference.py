from __future__ import annotations

"""QNG-CPU-173: Hopfion Q-ladder identification from PURE PHI static data.

The pure phi sector (CPU-145) has well-defined static energies that
DO NOT depend on dissipative protocol equilibration. The Hopfion
ladder Q=1..5 has clean energies measured after 20000-step XY relaxation:

  Q=1: ΔE = 9.756
  Q=2: ΔE = 12.113
  Q=3: ΔE = 15.612
  Q=4: ΔE = 17.321
  Q=5: ΔE = 20.054

Hypothesis: map Hopfion Q=1 to lightest stable charged QNG soliton =
proton (938.27 MeV). Then compute predicted masses for Q=2..5 and
compare with PDG baryon spectrum.

Reference: CPU-145 pure phi data, DER-QNG-097 §"What QNG can do robustly"
"""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-pure-phi-id-v1"


# CPU-145 pure phi Hopfion ladder data (L=24, beta_phi=0.06, 20000 step relaxation)
HOPFION_LADDER = {
    1: 9.756,
    2: 12.113,
    3: 15.612,
    4: 17.321,
    5: 20.054,
}

# PDG baryons (mass in MeV, charge, J^P, strangeness)
BARYONS = [
    # name, mass MeV, charge, J^P, S
    ("p",          938.27,  +1, "1/2+", 0),
    ("n",          939.57,   0, "1/2+", 0),
    ("Lambda",    1115.68,   0, "1/2+", -1),
    ("Sigma+",    1189.37,  +1, "1/2+", -1),
    ("Sigma0",    1192.64,   0, "1/2+", -1),
    ("Sigma-",    1197.45,  -1, "1/2+", -1),
    ("Delta+",    1232.0,   +1, "3/2+", 0),
    ("Delta++",   1232.0,   +2, "3/2+", 0),
    ("Xi0",       1314.86,   0, "1/2+", -2),
    ("Xi-",       1321.71,  -1, "1/2+", -2),
    ("Sigma*+",   1382.8,   +1, "3/2+", -1),
    ("Sigma*0",   1383.7,    0, "3/2+", -1),
    ("Sigma*-",   1387.2,   -1, "3/2+", -1),
    ("N(1440)",   1430.0,   +1, "1/2+", 0),  # Roper
    ("N(1520)",   1515.0,   +1, "3/2-", 0),
    ("Xi*0",      1531.80,   0, "3/2+", -2),
    ("N(1535)",   1535.0,   +1, "1/2-", 0),
    ("Xi*-",      1535.0,   -1, "3/2+", -2),
    ("Delta(1600)",1600.0,  +1, "3/2+", 0),
    ("Delta(1620)",1620.0,  +1, "1/2-", 0),
    ("N(1650)",   1650.0,   +1, "1/2-", 0),
    ("Omega-",    1672.45,  -1, "3/2+", -3),
    ("N(1675)",   1675.0,   +1, "5/2-", 0),
    ("N(1680)",   1680.0,   +1, "5/2+", 0),
    ("N(1700)",   1700.0,   +1, "3/2-", 0),
    ("Delta(1700)",1700.0,  +1, "3/2-", 0),
    ("N(1710)",   1710.0,   +1, "1/2+", 0),
    ("N(1720)",   1720.0,   +1, "3/2+", 0),
    ("N(1875)",   1875.0,   +1, "3/2-", 0),
    ("Delta(1900)",1900.0,  +1, "1/2-", 0),
    ("Delta(1905)",1905.0,  +1, "5/2+", 0),
    ("Delta(1910)",1910.0,  +1, "1/2+", 0),
    ("N(1900)",   1900.0,   +1, "3/2+", 0),
    ("Delta(1920)",1920.0,  +1, "3/2+", 0),
    ("Delta(1930)",1930.0,  +1, "5/2-", 0),
    ("Delta(1950)",1950.0,  +1, "7/2+", 0),
    ("N(2090)",   2090.0,   +1, "1/2-", 0),
    ("N(2100)",   2100.0,   +1, "1/2+", 0),
    ("N(2120)",   2120.0,   +1, "3/2-", 0),
]


def find_best_match(predicted_mass, prefer_S=0, prefer_charge=None):
    """Find best PDG match for predicted mass with structural preferences."""
    candidates = []
    for name, mass, q, jp, s in BARYONS:
        err = (predicted_mass - mass) / mass * 100
        score = abs(err)
        # Structural penalties
        if prefer_S is not None and s != prefer_S:
            score += 10  # S=0 preference (QNG without strangeness)
        candidates.append((name, mass, q, jp, s, err, score))
    candidates.sort(key=lambda c: c[6])
    return candidates[:3]  # top 3


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--reference", default="proton",
                    choices=["proton", "delta", "roper"],
                    help="Which SM particle Q=1 maps to")
    args = ap.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    ref_masses = {"proton": 938.27, "delta": 1232.0, "roper": 1430.0}
    ref_mass = ref_masses[args.reference]
    ref_name = args.reference

    print(f"QNG-CPU-173: Hopfion ladder identification")
    print(f"Pure phi sector (CPU-145, L=24, beta_phi=0.06)")
    print(f"Reference: Q=1 maps to {ref_name} ({ref_mass} MeV)")
    print()

    print("Hopfion Q values:")
    Q1_energy = HOPFION_LADDER[1]
    for Q, dE in HOPFION_LADDER.items():
        ratio = dE / Q1_energy
        predicted = ratio * ref_mass
        print(f"  Q={Q}: dE={dE:.3f}, ratio vs Q=1 = {ratio:.4f}, "
              f"predicted m = {predicted:.1f} MeV")
    print()

    # Per Q, find best PDG match
    identifications = []
    print("=" * 100)
    print(f"{'Q':<4} {'pred MeV':>10} {'best match':<18} {'mass':>10} {'q':>4} "
          f"{'J^P':>6} {'S':>4} {'err %':>8}")
    print("-" * 100)
    for Q, dE in HOPFION_LADDER.items():
        ratio = dE / Q1_energy
        predicted = ratio * ref_mass
        if Q == 1:
            # Reference
            ref_baryon = next(b for b in BARYONS if b[0] == ref_name[0]) if ref_name == "proton" \
                         else next(b for b in BARYONS if "p" == b[0]) if ref_name == "proton" \
                         else None
            ref_baryon = next(b for b in BARYONS if b[0] == "p") if ref_name == "proton" \
                         else next(b for b in BARYONS if b[0] == "Delta+") if ref_name == "delta" \
                         else next(b for b in BARYONS if b[0] == "N(1440)") if ref_name == "roper" \
                         else None
            name, mass, q, jp, s, err, _ = (ref_baryon[0], ref_baryon[1],
                                             ref_baryon[2], ref_baryon[3],
                                             ref_baryon[4], 0.0, 0.0)
            identifications.append({
                "Q": Q, "predicted_mass": predicted, "sm_name": name,
                "sm_mass": mass, "sm_charge": q, "sm_JP": jp, "sm_S": s,
                "error_pct": err
            })
            print(f"{Q:<4} {predicted:>10.1f} {name:<18} {mass:>10.1f} "
                  f"{q:>+4} {jp:>6} {s:>4} {err:>+8.2f}")
        else:
            # Find best with S=0 preference
            best3 = find_best_match(predicted, prefer_S=0)
            best = best3[0]
            name, mass, q, jp, s, err, _ = best
            identifications.append({
                "Q": Q, "predicted_mass": predicted, "sm_name": name,
                "sm_mass": mass, "sm_charge": q, "sm_JP": jp, "sm_S": s,
                "error_pct": err, "top3": [(b[0], b[5]) for b in best3]
            })
            print(f"{Q:<4} {predicted:>10.1f} {name:<18} {mass:>10.1f} "
                  f"{q:>+4} {jp:>6} {s:>4} {err:>+8.2f}")
            # Show alternatives
            print(f"     alternatives: " + ", ".join(
                f"{b[0]}({b[5]:+.2f}%)" for b in best3[1:]))
    print("=" * 100)

    # Summary statistics
    n_clean = sum(1 for i in identifications if abs(i["error_pct"]) < 2.0)
    n_very_clean = sum(1 for i in identifications if abs(i["error_pct"]) < 1.0)

    print()
    print(f"Identifications with error < 1.0%: {n_very_clean} / {len(identifications)}")
    print(f"Identifications with error < 2.0%: {n_clean} / {len(identifications)}")

    # Identify the pattern
    print()
    print("PATTERN OBSERVED:")
    s0_count = sum(1 for i in identifications if i["sm_S"] == 0)
    print(f"  S=0 (no strangeness) identifications: {s0_count} / {len(identifications)}")
    print(f"  (QNG cannot represent strangeness without v13)")

    report = {
        "test_id": "QNG-CPU-173_hopfion_pure_phi_id",
        "reference": ref_name,
        "reference_mass_MeV": ref_mass,
        "hopfion_ladder_data": HOPFION_LADDER,
        "identifications": identifications,
        "n_very_clean": n_very_clean,
        "n_clean": n_clean,
        "note": (
            "Hopfion Q-ladder energies from CPU-145 pure phi sector are "
            "STATIC, protocol-independent (no equilibrium issue). "
            "Identifications here therefore avoid the equilibrium problem "
            "diagnosed in DER-QNG-096."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
