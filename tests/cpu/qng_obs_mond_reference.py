from __future__ import annotations

"""
QNG-OBS-003: MOND comparison on DS006 rotation curve sample.

MOND with simple interpolating function mu(x) = x/sqrt(1+x^2).
a_0 = 1.2e-10 m/s^2 from literature. Zero free parameters.
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-mond-reference-v1"

# Physical constants
A0 = 1.2e-10          # Milgrom constant [m/s^2]
KPC_TO_M = 3.0857e19  # 1 kpc in meters
KMS2_TO_M2S2 = 1e6    # 1 (km/s)^2 in m^2/s^2

# QNG-OBS-001 reference numbers for comparison
OBS001_MED_BARYON = 38.870
OBS001_MED_QNG    = 17.166
OBS001_RATIO      = 2.264

MIN_POINTS = 5


def v2_mond(baryon_term_kms2: float, r_kpc: float) -> float:
    """
    MOND prediction for V^2 at radius r.
    Returns V^2 in (km/s)^2.
    Simple interpolating function: mu(x) = x/sqrt(1+x^2).
    Analytic solution: t^2 = (x^2 + sqrt(x^4 + 4x^2)) / 2, a_MOND = sqrt(t^2)*a0.
    """
    if r_kpc <= 0 or baryon_term_kms2 <= 0:
        return 0.0
    a_N = baryon_term_kms2 * KMS2_TO_M2S2 / (r_kpc * KPC_TO_M)  # m/s^2
    x = a_N / A0
    x2 = x * x
    t2 = (x2 + math.sqrt(x2 * x2 + 4.0 * x2)) / 2.0
    a_m = math.sqrt(t2) * A0  # m/s^2
    return a_m * r_kpc * KPC_TO_M / KMS2_TO_M2S2  # back to (km/s)^2


def load_data(path: Path) -> dict[str, list[dict]]:
    galaxies: dict[str, list[dict]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row["system_id"].strip()
            galaxies.setdefault(gid, []).append({
                "radius":      float(row["radius"]),
                "v_obs":       float(row["v_obs"]),
                "v_err":       float(row["v_err"]),
                "baryon_term": float(row["baryon_term"]),
            })
    return galaxies


def fit_galaxy(rows: list[dict]) -> dict:
    n = len(rows)
    chi2_b = chi2_m = 0.0
    for r in rows:
        v_obs  = r["v_obs"]
        v_err  = max(r["v_err"], 1e-6)
        v2_obs = v_obs * v_obs
        v2_b   = r["baryon_term"]
        v2_m   = v2_mond(v2_b, r["radius"])
        v2_err = 2.0 * v_obs * v_err
        if v2_err < 1e-12:
            continue
        chi2_b += ((v2_obs - v2_b) / v2_err) ** 2
        chi2_m += ((v2_obs - v2_m) / v2_err) ** 2
    return {
        "chi2_baryon":     chi2_b,
        "chi2_mond":       chi2_m,
        "chi2_dof_baryon": chi2_b / n,
        "chi2_dof_mond":   chi2_m / n,
        "improved": chi2_m < chi2_b,
        "n": n,
    }


def median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid-1] + s[mid]) / 2.0


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    galaxies = load_data(DATA_FILE)
    print(f"Galaxies: {len(galaxies)}  |  a_0 = {A0:.1e} m/s^2  (zero free params)")

    results = []
    for gid, rows in sorted(galaxies.items()):
        if len(rows) < MIN_POINTS:
            continue
        fit = fit_galaxy(rows)
        results.append({"galaxy": gid, **fit})

    n_fit = len(results)
    med_b = median([r["chi2_dof_baryon"] for r in results])
    med_m = median([r["chi2_dof_mond"]   for r in results])
    ratio = med_b / med_m if med_m > 0 else 0.0
    frac  = sum(r["improved"] for r in results) / n_fit

    check1 = med_m < med_b
    check2 = ratio >= 2.0
    check3 = frac  > 0.60
    decision = check1 and check2 and check3

    # Comparison with OBS-001
    qng_ratio = OBS001_RATIO
    mond_beats_qng = ratio < qng_ratio  # lower ratio means MOND needs more fitting to beat baryon; higher = MOND is better
    # Actually: higher ratio = bigger improvement. So if ratio > qng_ratio, MOND beats per-galaxy QNG.

    print(f"\nResults (n={n_fit} galaxies, a_0={A0:.1e}):")
    print(f"  Median chi2/dof baryon-only : {med_b:.3f}")
    print(f"  Median chi2/dof MOND        : {med_m:.3f}")
    print(f"  MOND improvement ratio      : {ratio:.3f}x")
    print(f"  Fraction improved by MOND   : {frac:.3f}")
    print()
    print(f"  [Reference OBS-001] per-galaxy QNG ratio: {qng_ratio:.3f}x  (med_QNG={OBS001_MED_QNG:.3f})")
    print(f"  MOND vs QNG-OBS-001: {'MOND BETTER' if ratio > qng_ratio else 'QNG-OBS-001 BETTER (more variance absorbed)'}")
    print()
    print("Checks:")
    print(f"  Check 1 (MOND < baryon)   : {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (ratio >= 2.0x)   : {ratio:.3f}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (frac > 0.60)     : {frac:.3f}  {'PASS' if check3 else 'FAIL'}")
    print(f"\nqng_obs_mond_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-OBS-003",
        "decision": "pass" if decision else "fail",
        "a0_ms2": A0,
        "n_galaxies_fit": n_fit,
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_mond":   round(med_m, 4),
        "improvement_ratio":      round(ratio, 4),
        "fraction_improved":      round(frac, 4),
        "reference_obs001_ratio": qng_ratio,
        "mond_vs_qng_obs001": "mond_better" if ratio > qng_ratio else "qng_obs001_better",
        "checks": {
            "mond_lt_baryon_pass":          check1,
            "improvement_ratio_ge_2x_pass": check2,
            "fraction_improved_gt_0p60_pass": check3,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-003: MOND Comparison Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- a_0 = {A0:.1e} m/s^2  (zero free parameters)",
        "",
        "## Results",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof MOND | {med_m:.3f} |",
        f"| MOND improvement ratio | {ratio:.3f}x |",
        f"| Fraction improved | {frac:.3f} |",
        f"| OBS-001 QNG ratio (reference) | {qng_ratio:.3f}x |",
        f"| MOND vs QNG-OBS-001 | {'MOND better' if ratio > qng_ratio else 'QNG-OBS-001 better'} |",
        "",
        "## Checks",
        f"- Check 1 (MOND < baryon): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (ratio >= 2.0x): {'PASS' if check2 else 'FAIL'} ({ratio:.3f}x)",
        f"- Check 3 (frac > 0.60): {'PASS' if check3 else 'FAIL'} ({frac:.3f})",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
