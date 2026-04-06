from __future__ import annotations

"""
QNG-OBS-004: Galaxy rotation curves - QNG Yukawa radial profile.

Two global free parameters: lambda [kpc] and A [(km/s)^2].
For fixed lambda, A_opt is solved analytically (global WLS across all galaxies).
Lambda is scanned on a log grid to find the chi^2 minimum.

Compared against MOND (OBS-003 baseline: 1.702x improvement, 0 free params).
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-yukawa-reference-v1"

# OBS-003 MOND baseline
MOND_MED_BARYON = 38.870
MOND_RATIO      = 1.702
MOND_MED_MOND   = 38.870 / MOND_RATIO   # ~22.84

# Lambda scan parameters
LAM_MIN_KPC  = 0.1
LAM_MAX_KPC  = 10000.0
LAM_N_POINTS = 200

MIN_POINTS = 5


def ck(r_kpc: float, lam_kpc: float) -> float:
    """Yukawa kernel C_K(r, lambda) = (1 + r/lambda) * exp(-r/lambda)."""
    x = r_kpc / lam_kpc
    return (1.0 + x) * math.exp(-x)


def load_data(path: Path) -> list[dict]:
    """Load all data points as flat list."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        gal_rows: dict[str, list] = {}
        for row in reader:
            gid = row["system_id"].strip()
            gal_rows.setdefault(gid, []).append(row)
    # Keep only galaxies with >= MIN_POINTS
    for gid, grows in gal_rows.items():
        if len(grows) < MIN_POINTS:
            continue
        for row in grows:
            v_obs  = float(row["v_obs"])
            v_err  = max(float(row["v_err"]), 1e-6)
            v2_obs = v_obs * v_obs
            v2_b   = float(row["baryon_term"])
            v2_err = 2.0 * v_obs * v_err
            if v2_err < 1e-12:
                continue
            rows.append({
                "galaxy": gid,
                "r":      float(row["radius"]),
                "v2_obs": v2_obs,
                "v2_b":   v2_b,
                "res":    v2_obs - v2_b,   # residual = "missing" V^2
                "w":      1.0 / (v2_err * v2_err),
                "v2_err": v2_err,
            })
    return rows


def fit_lambda(rows: list[dict], lam: float) -> tuple[float, float, float]:
    """
    For fixed lambda, solve for A_opt analytically (global WLS).
    Returns (A_opt, chi2_total_baryon, chi2_total_yukawa).
    """
    # A_opt = sum(w * res * CK) / sum(w * CK^2)
    num = den = 0.0
    chi2_b = 0.0
    for r in rows:
        c = ck(r["r"], lam)
        num += r["w"] * r["res"] * c
        den += r["w"] * c * c
        chi2_b += (r["res"] / r["v2_err"]) ** 2

    A_opt = num / den if den > 1e-30 else 0.0

    chi2_q = 0.0
    for r in rows:
        c = ck(r["r"], lam)
        chi2_q += ((r["res"] - A_opt * c) / r["v2_err"]) ** 2

    return A_opt, chi2_b, chi2_q


def median_chi2_dof(rows: list[dict], lam: float, A: float) -> tuple[float, float]:
    """Per-galaxy median chi2/dof for baryon-only and Yukawa."""
    from collections import defaultdict
    gal: dict[str, list] = defaultdict(list)
    for r in rows:
        gal[r["galaxy"]].append(r)

    vals_b, vals_q = [], []
    for gid, pts in gal.items():
        n = len(pts)
        cb = cq = 0.0
        for r in pts:
            c = ck(r["r"], lam)
            cb += (r["res"] / r["v2_err"]) ** 2
            cq += ((r["res"] - A * c) / r["v2_err"]) ** 2
        vals_b.append(cb / n)
        vals_q.append(cq / n)

    def med(v):
        s = sorted(v); n = len(s); m = n // 2
        return s[m] if n % 2 else (s[m-1] + s[m]) / 2.0

    return med(vals_b), med(vals_q)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_data(DATA_FILE)
    n_points = len(rows)
    n_galaxies = len(set(r["galaxy"] for r in rows))
    print(f"Points: {n_points}  Galaxies: {n_galaxies}")

    # Lambda scan (log-uniform)
    lam_grid = [LAM_MIN_KPC * (LAM_MAX_KPC / LAM_MIN_KPC) ** (i / (LAM_N_POINTS - 1))
                for i in range(LAM_N_POINTS)]

    best_lam = lam_grid[0]
    best_A   = 0.0
    best_chi2 = 1e30
    scan_results = []

    print(f"Scanning lambda from {LAM_MIN_KPC} to {LAM_MAX_KPC} kpc ({LAM_N_POINTS} points)...")
    for lam in lam_grid:
        A_opt, chi2_b, chi2_q = fit_lambda(rows, lam)
        scan_results.append({"lambda": lam, "A_opt": A_opt, "chi2_yukawa": chi2_q})
        if chi2_q < best_chi2:
            best_chi2 = chi2_q
            best_lam  = lam
            best_A    = A_opt

    _, chi2_baryon_total = fit_lambda(rows, best_lam)[1], fit_lambda(rows, best_lam)[1]
    _, chi2_b_total, _   = fit_lambda(rows, 1.0)  # just need chi2_b
    chi2_b_total         = scan_results[0]["chi2_yukawa"]  # recompute properly
    # Recompute chi2_baryon once
    chi2_baryon = sum((r["res"] / r["v2_err"]) ** 2 for r in rows)

    med_b, med_q = median_chi2_dof(rows, best_lam, best_A)
    ratio = med_b / med_q if med_q > 0 else 0.0

    # AIC: n * ln(chi2/n) + 2k
    n = n_points
    aic_yukawa = n * math.log(best_chi2 / n) + 2 * 2   # k=2
    aic_mond_chi2 = MOND_MED_MOND * n_galaxies          # approximate
    aic_mond = n * math.log(best_chi2 / n * (ratio / MOND_RATIO)) + 2 * 0 if ratio > 0 else 0
    # Simpler: just report AIC difference

    # Fraction of galaxies improved
    from collections import defaultdict
    gal: dict[str, list] = defaultdict(list)
    for r in rows: gal[r["galaxy"]].append(r)
    n_improved = 0
    for gid, pts in gal.items():
        cb = sum((r["res"] / r["v2_err"]) ** 2 for r in pts)
        cq = sum(((r["res"] - best_A * ck(r["r"], best_lam)) / r["v2_err"]) ** 2 for r in pts)
        if cq < cb: n_improved += 1
    frac_improved = n_improved / n_galaxies

    check1 = med_q < med_b
    check2 = ratio > MOND_RATIO
    check3 = 1.0 <= best_lam <= 500.0
    check4 = best_A > 0
    # AIC informational
    aic_diff = (n * math.log(best_chi2 / n)) - (n * math.log(best_chi2 / n * ratio / MOND_RATIO)) + 2*2
    check5_info = aic_diff < 0

    decision = check1 and check2 and check3 and check4

    print(f"\nBest-fit lambda: {best_lam:.2f} kpc")
    print(f"Best-fit A:      {best_A:.2f} (km/s)^2")
    print(f"Total chi^2 (Yukawa): {best_chi2:.1f}")
    print(f"Total chi^2 (baryon): {chi2_baryon:.1f}")
    print()
    print(f"Median chi^2/dof baryon-only : {med_b:.3f}")
    print(f"Median chi^2/dof Yukawa      : {med_q:.3f}")
    print(f"Yukawa improvement ratio     : {ratio:.3f}x")
    print(f"MOND improvement ratio [ref] : {MOND_RATIO:.3f}x")
    print(f"Fraction galaxies improved   : {frac_improved:.3f}")
    print()
    print(f"Yukawa vs MOND: {'YUKAWA BETTER' if ratio > MOND_RATIO else 'MOND BETTER'}")
    print()
    print("Checks:")
    print(f"  Check 1 (Yukawa < baryon)   : {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (ratio > MOND 1.702): {ratio:.3f}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (1 < lambda < 500)  : {best_lam:.2f} kpc  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 (A_opt > 0)         : {best_A:.2f}  {'PASS' if check4 else 'FAIL'}")
    print(f"  Check 5 [info] AIC Yukawa < MOND: {'PASS' if check5_info else 'FAIL'}")
    print(f"\nqng_obs_yukawa_reference: {'PASS' if decision else 'FAIL'}")

    # Top 5 lambda scan near minimum
    scan_sorted = sorted(scan_results, key=lambda x: x["chi2_yukawa"])[:5]
    print("\nTop 5 lambda values by chi^2:")
    for s in scan_sorted:
        print(f"  lambda={s['lambda']:8.2f} kpc  A={s['A_opt']:8.1f}  chi2={s['chi2_yukawa']:.1f}")

    report = {
        "test_id": "QNG-OBS-004",
        "decision": "pass" if decision else "fail",
        "best_lambda_kpc": round(best_lam, 4),
        "best_A_kms2":     round(best_A, 4),
        "chi2_baryon_total":  round(chi2_baryon, 2),
        "chi2_yukawa_total":  round(best_chi2, 2),
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_yukawa": round(med_q, 4),
        "improvement_ratio":      round(ratio, 4),
        "mond_ratio_reference":   MOND_RATIO,
        "fraction_improved":      round(frac_improved, 4),
        "n_points": n_points,
        "n_galaxies": n_galaxies,
        "lambda_scan_n": LAM_N_POINTS,
        "checks": {
            "yukawa_lt_baryon_pass":       check1,
            "ratio_gt_mond_pass":          check2,
            "lambda_in_galactic_range_pass": check3,
            "A_opt_positive_pass":         check4,
            "aic_yukawa_lt_mond_info":     check5_info,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-004: Yukawa Radial Profile Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- best-fit lambda = {best_lam:.2f} kpc",
        f"- best-fit A = {best_A:.2f} (km/s)^2",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof Yukawa | {med_q:.3f} |",
        f"| Yukawa improvement ratio | {ratio:.3f}x |",
        f"| MOND improvement ratio (OBS-003) | {MOND_RATIO:.3f}x |",
        f"| Fraction galaxies improved | {frac_improved:.3f} |",
        f"| Best-fit lambda | {best_lam:.2f} kpc |",
        f"| Best-fit A | {best_A:.2f} (km/s)^2 |",
        "",
        "## Checks",
        f"- Check 1 (Yukawa < baryon): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (ratio > MOND): {'PASS' if check2 else 'FAIL'} ({ratio:.3f}x vs {MOND_RATIO:.3f}x)",
        f"- Check 3 (lambda in galactic range): {'PASS' if check3 else 'FAIL'} ({best_lam:.2f} kpc)",
        f"- Check 4 (A_opt > 0): {'PASS' if check4 else 'FAIL'} ({best_A:.2f})",
        f"- Check 5 [info] AIC: {'PASS' if check5_info else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
