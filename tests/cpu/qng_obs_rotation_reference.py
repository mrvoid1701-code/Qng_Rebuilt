from __future__ import annotations

"""
QNG-OBS-001: Galaxy rotation curves - QNG flat-ether model vs baryon-only.

Tests whether the QNG flat chi-field contribution (a_M per galaxy) fits
175 rotation curves better than baryon-only, and whether a_M scales with
baryonic mass as predicted by DER-QNG-027.

Data: rotation_ds006_rotmod.csv
  Columns: system_id, radius, v_obs, v_err, baryon_term, history_term
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-rotation-reference-v1"

MIN_POINTS = 5  # minimum data points per galaxy for fitting


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(path: Path) -> dict[str, list[dict]]:
    """Load CSV; return dict galaxy_id -> list of row dicts."""
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
                "history_term":float(row["history_term"]),
            })
    return galaxies


# ---------------------------------------------------------------------------
# Per-galaxy fitting
# ---------------------------------------------------------------------------

def fit_galaxy(rows: list[dict]) -> dict:
    """
    Weighted least squares fit of a_M for the QNG flat model:
        V2_pred(r) = baryon_term(r) + a_M

    Weight = 1 / (V2_err)^2  where V2_err = 2 * v_obs * v_err.

    Returns dict with a_M, chi2_baryon, chi2_qng, dof, M_proxy.
    """
    n = len(rows)
    dof = max(1, n - 1)  # QNG has 1 free param per galaxy

    # Compute weights and residuals
    sum_w = 0.0
    sum_wx = 0.0  # x = history_term = v_obs^2 - baryon_term (= a_M target)
    sum_w_chi2_baryon = 0.0

    for r in rows:
        v_obs = r["v_obs"]
        v_err = max(r["v_err"], 1e-6)
        v2_obs = v_obs * v_obs
        v2_baryon = r["baryon_term"]
        v2_err = 2.0 * v_obs * v_err

        w = 1.0 / (v2_err * v2_err) if v2_err > 1e-12 else 0.0
        residual_baryon = v2_obs - v2_baryon

        sum_w += w
        sum_wx += w * residual_baryon
        sum_w_chi2_baryon += w * residual_baryon * residual_baryon

    # a_M = weighted mean of (v2_obs - baryon_term)
    a_M = sum_wx / sum_w if sum_w > 1e-30 else 0.0

    # chi2 for both models
    chi2_baryon = 0.0
    chi2_qng = 0.0
    for r in rows:
        v_obs = r["v_obs"]
        v_err = max(r["v_err"], 1e-6)
        v2_obs = v_obs * v_obs
        v2_baryon = r["baryon_term"]
        v2_err = 2.0 * v_obs * v_err
        w = 1.0 / (v2_err * v2_err) if v2_err > 1e-12 else 0.0

        res_b = v2_obs - v2_baryon
        res_q = v2_obs - (v2_baryon + a_M)

        chi2_baryon += w * res_b * res_b
        chi2_qng    += w * res_q * res_q

    # Normalize to proper chi2 (sum of (residual/sigma)^2 = sum w * res^2 / (sum w * something))
    # Actually chi^2 = sum_i (res_i / sigma_i)^2 = sum_i w_i * res_i^2 * (2*v_obs*v_err)^2
    # Let's recompute properly: chi2 = sum (res / sigma)^2 where sigma = v2_err
    chi2_baryon_proper = 0.0
    chi2_qng_proper = 0.0
    for r in rows:
        v_obs = r["v_obs"]
        v_err = max(r["v_err"], 1e-6)
        v2_obs = v_obs * v_obs
        v2_baryon = r["baryon_term"]
        v2_err = 2.0 * v_obs * v_err
        if v2_err < 1e-12:
            continue

        res_b = (v2_obs - v2_baryon) / v2_err
        res_q = (v2_obs - (v2_baryon + a_M)) / v2_err

        chi2_baryon_proper += res_b * res_b
        chi2_qng_proper    += res_q * res_q

    chi2_dof_baryon = chi2_baryon_proper / n       # baryon-only has 0 free params
    chi2_dof_qng    = chi2_qng_proper    / dof     # QNG has 1 free param

    # M_proxy: max baryon_term over all radii
    M_proxy = max(r["baryon_term"] for r in rows)

    return {
        "a_M":             a_M,
        "chi2_baryon":     chi2_baryon_proper,
        "chi2_qng":        chi2_qng_proper,
        "chi2_dof_baryon": chi2_dof_baryon,
        "chi2_dof_qng":    chi2_dof_qng,
        "n_points":        n,
        "dof":             dof,
        "M_proxy":         M_proxy,
    }


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx  = math.sqrt(sum((x - mx)**2 for x in xs))
    dy  = math.sqrt(sum((y - my)**2 for y in ys))
    if dx < 1e-30 or dy < 1e-30:
        return 0.0
    return num / (dx * dy)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="QNG-OBS-001: rotation curve fit.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from: {DATA_FILE}")
    galaxies = load_data(DATA_FILE)
    print(f"Galaxies loaded: {len(galaxies)}")

    # Fit each galaxy
    results = []
    skipped = 0
    for gid, rows in sorted(galaxies.items()):
        if len(rows) < MIN_POINTS:
            skipped += 1
            continue
        fit = fit_galaxy(rows)
        results.append({"galaxy": gid, **fit})

    n_fit = len(results)
    print(f"Galaxies fit: {n_fit}  (skipped {skipped} with <{MIN_POINTS} points)")
    print()

    # Extract arrays
    chi2_dof_b = [r["chi2_dof_baryon"] for r in results]
    chi2_dof_q = [r["chi2_dof_qng"]    for r in results]
    a_M_vals   = [r["a_M"]             for r in results]
    M_proxies  = [r["M_proxy"]         for r in results]

    med_b = median(chi2_dof_b)
    med_q = median(chi2_dof_q)

    frac_improved = sum(1 for r in results if r["chi2_qng"] < r["chi2_baryon"]) / n_fit
    pearson = pearson_r(a_M_vals, M_proxies)
    frac_positive = sum(1 for a in a_M_vals if a > 0) / n_fit

    # Check 5: mean M_proxy for negative vs positive a_M galaxies
    neg_proxies = [r["M_proxy"] for r in results if r["a_M"] <  0]
    pos_proxies = [r["M_proxy"] for r in results if r["a_M"] >= 0]
    mean_neg = sum(neg_proxies) / len(neg_proxies) if neg_proxies else 0.0
    mean_pos = sum(pos_proxies) / len(pos_proxies) if pos_proxies else 0.0

    # Checks
    check1 = med_q < med_b
    check2 = frac_improved > 0.60
    check3 = pearson > 0.40
    check4 = frac_positive > 0.60
    check5 = mean_neg > mean_pos  # informational

    decision = check1 and check2 and check3 and check4

    print("=" * 60)
    print("Results:")
    print(f"  Galaxies fit:           {n_fit}")
    print(f"  Median chi2/dof (baryon-only): {med_b:.3f}")
    print(f"  Median chi2/dof (QNG):         {med_q:.3f}")
    print(f"  Improvement ratio:      {med_b/med_q:.2f}x")
    print(f"  Fraction improved:      {frac_improved:.3f}")
    print(f"  Pearson r(a_M, M_proxy):{pearson:.4f}")
    print(f"  Fraction a_M > 0:       {frac_positive:.3f}")
    print(f"  Mean M_proxy (a_M < 0): {mean_neg:.1f}")
    print(f"  Mean M_proxy (a_M >= 0):{mean_pos:.1f}")
    print()
    print("Checks:")
    print(f"  Check 1 (med chi2/dof QNG < baryon): {'PASS' if check1 else 'FAIL'}")
    print(f"    {med_q:.3f} < {med_b:.3f}")
    print(f"  Check 2 (frac improved > 0.60): {'PASS' if check2 else 'FAIL'}")
    print(f"    {frac_improved:.3f}")
    print(f"  Check 3 (Pearson r > 0.40): {'PASS' if check3 else 'FAIL'}")
    print(f"    r = {pearson:.4f}")
    print(f"  Check 4 (frac a_M > 0 > 0.60): {'PASS' if check4 else 'FAIL'}")
    print(f"    {frac_positive:.3f}")
    print(f"  Check 5 [info] (mean M_proxy neg > pos): {'PASS' if check5 else 'FAIL'}")
    print(f"    neg={mean_neg:.1f}  pos={mean_pos:.1f}")
    print()
    print(f"qng_obs_rotation_reference: {'PASS' if decision else 'FAIL'}")

    checks = {
        "chi2_dof_qng_lt_baryon_pass":    check1,
        "fraction_improved_gt_0p60_pass": check2,
        "pearson_r_gt_0p40_pass":         check3,
        "fraction_positive_aM_pass":      check4,
        "check5_neg_more_baryon_rich_info":check5,
    }

    report = {
        "test_id": "QNG-OBS-001",
        "decision": "pass" if decision else "fail",
        "n_galaxies_fit": n_fit,
        "n_skipped": skipped,
        "median_chi2_dof_baryon":  round(med_b, 4),
        "median_chi2_dof_qng":     round(med_q, 4),
        "improvement_ratio":       round(med_b / med_q, 4) if med_q > 0 else 0.0,
        "fraction_improved":       round(frac_improved, 4),
        "pearson_r_aM_Mproxy":     round(pearson, 4),
        "fraction_positive_aM":    round(frac_positive, 4),
        "mean_Mproxy_neg_aM":      round(mean_neg, 2),
        "mean_Mproxy_pos_aM":      round(mean_pos, 2),
        "checks": checks,
        "per_galaxy": [
            {
                "galaxy":          r["galaxy"],
                "a_M":             round(r["a_M"], 2),
                "chi2_dof_baryon": round(r["chi2_dof_baryon"], 4),
                "chi2_dof_qng":    round(r["chi2_dof_qng"], 4),
                "M_proxy":         round(r["M_proxy"], 2),
                "n_points":        r["n_points"],
            }
            for r in results
        ],
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-001: Rotation Curve Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- galaxies fit: {n_fit}",
        "",
        "## Summary Statistics",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof QNG | {med_q:.3f} |",
        f"| Improvement ratio | {med_b/med_q:.2f}x |",
        f"| Fraction improved | {frac_improved:.3f} |",
        f"| Pearson r(a_M, M_proxy) | {pearson:.4f} |",
        f"| Fraction a_M > 0 | {frac_positive:.3f} |",
        "",
        "## Checks",
        f"- Check 1 (chi2/dof QNG < baryon): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (frac improved > 0.60): {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (Pearson r > 0.40): {'PASS' if check3 else 'FAIL'}",
        f"- Check 4 (frac a_M > 0 > 0.60): {'PASS' if check4 else 'FAIL'}",
        f"- Check 5 [info] (neg a_M galaxies more baryon-rich): {'PASS' if check5 else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
