from __future__ import annotations

"""
QNG observational proxy for the latest v7 two-field theory.

Codex variant:
  - keeps all older observational scripts untouched
  - tests a v7-inspired double-Yukawa velocity kernel
  - uses two global screening lengths plus one global amplitude

Theory motivation:
  DER-QNG-035 suggests the v7 gravity lane is no longer a flat ether or a
  single Yukawa. The gravity response is a cascade from sigma_m into sigma_g,
  which motivates a double-Yukawa velocity kernel.
"""

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-v7-double-yukawa-codex-v1"

AUTHOR = "Codex"
TEST_ID = "QNG-OBS-V7-CODEX-001"
MIN_POINTS = 5

# Reference baselines from existing observational lane
OBS001_MED_BARYON = 38.870
OBS001_MED_QNG = 17.166
OBS001_RATIO = OBS001_MED_BARYON / OBS001_MED_QNG
MOND_RATIO = 1.702

# Scan configuration
LAM_MIN_KPC = 0.1
LAM_FAST_MAX_KPC = 300.0
LAM_SLOW_MAX_KPC = 50000.0
N_FAST = 36
N_SLOW = 48


def log_grid(x_min: float, x_max: float, n: int) -> list[float]:
    if n <= 1:
        return [x_min]
    return [x_min * (x_max / x_min) ** (i / (n - 1)) for i in range(n)]


def load_data(path: Path) -> list[dict]:
    """Load all DS006 points, keeping only galaxies with enough points."""
    grouped: dict[str, list[dict[str, str]]] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            gid = row["system_id"].strip()
            grouped.setdefault(gid, []).append(row)

    rows: list[dict] = []
    for gid, grows in grouped.items():
        if len(grows) < MIN_POINTS:
            continue
        for row in grows:
            v_obs = float(row["v_obs"])
            v_err = max(float(row["v_err"]), 1e-6)
            v2_obs = v_obs * v_obs
            v2_b = float(row["baryon_term"])
            v2_err = 2.0 * v_obs * v_err
            if v2_err <= 1e-12:
                continue
            rows.append(
                {
                    "galaxy": gid,
                    "r": float(row["radius"]),
                    "v2_obs": v2_obs,
                    "v2_b": v2_b,
                    "res": v2_obs - v2_b,
                    "v2_err": v2_err,
                }
            )
    return rows


def single_yukawa_velocity_kernel(r_kpc: float, lam_kpc: float) -> float:
    x = r_kpc / lam_kpc
    if x > 700.0:
        return 0.0
    return (1.0 + x) * math.exp(-x)


def equal_lambda_double_yukawa_kernel(r_kpc: float, lam_kpc: float) -> float:
    """
    Equal-lambda limit proxy for the v7 cascade.

    If the potential comes from a self-convolution of screened responses,
    the velocity contribution is softer than the single-Yukawa case.
    A simple positive proxy is x * exp(-x).
    """
    x = r_kpc / lam_kpc
    if x > 700.0:
        return 0.0
    return x * math.exp(-x)


def double_yukawa_velocity_kernel(r_kpc: float, lam_fast: float, lam_slow: float) -> float:
    """
    v7 proxy:
      V^2(r) ~ A * [mu_fast^2 * Y_fast(r) - mu_slow^2 * Y_slow(r)] / (mu_fast^2 - mu_slow^2)
    where Y(r) is the single-Yukawa circular-velocity kernel.

    This is a practical observational proxy extracted from DER-QNG-035, not a
    final theorem-level rotation formula.
    """
    if abs(lam_fast - lam_slow) / max(lam_fast, lam_slow) < 1e-3:
        return equal_lambda_double_yukawa_kernel(r_kpc, 0.5 * (lam_fast + lam_slow))

    mu_fast2 = 1.0 / (lam_fast * lam_fast)
    mu_slow2 = 1.0 / (lam_slow * lam_slow)
    y_fast = single_yukawa_velocity_kernel(r_kpc, lam_fast)
    y_slow = single_yukawa_velocity_kernel(r_kpc, lam_slow)
    denom = mu_fast2 - mu_slow2
    if abs(denom) < 1e-30:
        return equal_lambda_double_yukawa_kernel(r_kpc, 0.5 * (lam_fast + lam_slow))
    return (mu_fast2 * y_fast - mu_slow2 * y_slow) / denom


def fit_amplitude(rows: list[dict], lam_fast: float, lam_slow: float) -> tuple[float, float]:
    """Solve A_opt analytically for fixed lambdas; return (A_opt, chi2_total)."""
    num = 0.0
    den = 0.0
    for row in rows:
        kernel = double_yukawa_velocity_kernel(row["r"], lam_fast, lam_slow)
        weight = 1.0 / (row["v2_err"] * row["v2_err"])
        num += weight * row["res"] * kernel
        den += weight * kernel * kernel

    a_opt = num / den if den > 1e-30 else 0.0

    chi2 = 0.0
    for row in rows:
        kernel = double_yukawa_velocity_kernel(row["r"], lam_fast, lam_slow)
        chi2 += ((row["res"] - a_opt * kernel) / row["v2_err"]) ** 2
    return a_opt, chi2


def median_chi2_dof(rows: list[dict], lam_fast: float, lam_slow: float, amplitude: float) -> tuple[float, float]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["galaxy"], []).append(row)

    vals_b: list[float] = []
    vals_v7: list[float] = []
    for galaxy_rows in grouped.values():
        n = len(galaxy_rows)
        chi2_b = 0.0
        chi2_v7 = 0.0
        for row in galaxy_rows:
            kernel = double_yukawa_velocity_kernel(row["r"], lam_fast, lam_slow)
            chi2_b += (row["res"] / row["v2_err"]) ** 2
            chi2_v7 += ((row["res"] - amplitude * kernel) / row["v2_err"]) ** 2
        vals_b.append(chi2_b / n)
        vals_v7.append(chi2_v7 / n)

    def med(values: list[float]) -> float:
        ordered = sorted(values)
        count = len(ordered)
        mid = count // 2
        if count % 2:
            return ordered[mid]
        return (ordered[mid - 1] + ordered[mid]) / 2.0

    return med(vals_b), med(vals_v7)


def fraction_improved(rows: list[dict], lam_fast: float, lam_slow: float, amplitude: float) -> float:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["galaxy"], []).append(row)

    improved = 0
    for galaxy_rows in grouped.values():
        chi2_b = 0.0
        chi2_v7 = 0.0
        for row in galaxy_rows:
            kernel = double_yukawa_velocity_kernel(row["r"], lam_fast, lam_slow)
            chi2_b += (row["res"] / row["v2_err"]) ** 2
            chi2_v7 += ((row["res"] - amplitude * kernel) / row["v2_err"]) ** 2
        if chi2_v7 < chi2_b:
            improved += 1
    return improved / len(grouped)


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG v7 double-Yukawa observational proxy by Codex.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--fast-n", type=int, default=N_FAST)
    parser.add_argument("--slow-n", type=int, default=N_SLOW)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_data(DATA_FILE)
    n_points = len(rows)
    n_galaxies = len({row["galaxy"] for row in rows})
    print(f"Author: {AUTHOR}")
    print(f"Galaxies: {n_galaxies}  Points: {n_points}")

    baryon_chi2_total = sum((row["res"] / row["v2_err"]) ** 2 for row in rows)
    fast_grid = log_grid(LAM_MIN_KPC, LAM_FAST_MAX_KPC, args.fast_n)
    slow_grid = log_grid(LAM_MIN_KPC, LAM_SLOW_MAX_KPC, args.slow_n)

    best = {
        "lam_fast": fast_grid[0],
        "lam_slow": slow_grid[0],
        "A": 0.0,
        "chi2": float("inf"),
    }
    scan: list[dict] = []

    total_pairs = 0
    for lam_fast in fast_grid:
        for lam_slow in slow_grid:
            if lam_slow < lam_fast:
                continue
            total_pairs += 1

    pair_idx = 0
    for lam_fast in fast_grid:
        for lam_slow in slow_grid:
            if lam_slow < lam_fast:
                continue
            pair_idx += 1
            if pair_idx % 100 == 1:
                print(f"  scan {pair_idx}/{total_pairs}: lam_fast={lam_fast:.3f} kpc, lam_slow={lam_slow:.3f} kpc")

            amplitude, chi2_total = fit_amplitude(rows, lam_fast, lam_slow)
            scan.append(
                {
                    "lam_fast": lam_fast,
                    "lam_slow": lam_slow,
                    "A": amplitude,
                    "chi2_total": chi2_total,
                }
            )
            if chi2_total < best["chi2"]:
                best = {
                    "lam_fast": lam_fast,
                    "lam_slow": lam_slow,
                    "A": amplitude,
                    "chi2": chi2_total,
                }

    med_b, med_v7 = median_chi2_dof(rows, best["lam_fast"], best["lam_slow"], best["A"])
    ratio = med_b / med_v7 if med_v7 > 0 else 0.0
    frac_imp = fraction_improved(rows, best["lam_fast"], best["lam_slow"], best["A"])

    checks = {
        "v7_lt_baryon_pass": med_v7 < med_b,
        "v7_beats_mond_pass": ratio > MOND_RATIO,
        "v7_beats_obs001_pass": ratio > OBS001_RATIO,
        "lambdas_ordered_pass": best["lam_slow"] >= best["lam_fast"],
        "amplitude_positive_pass": best["A"] > 0.0,
        "majority_improved_pass": frac_imp > 0.60,
    }
    decision = (
        checks["v7_lt_baryon_pass"]
        and checks["lambdas_ordered_pass"]
        and checks["amplitude_positive_pass"]
        and checks["majority_improved_pass"]
    )

    print()
    print(f"Best lam_fast : {best['lam_fast']:.4f} kpc")
    print(f"Best lam_slow : {best['lam_slow']:.4f} kpc")
    print(f"Best A        : {best['A']:.4f} (km/s)^2")
    print(f"Median chi2/dof baryon-only : {med_b:.3f}")
    print(f"Median chi2/dof v7 proxy    : {med_v7:.3f}")
    print(f"v7 improvement ratio        : {ratio:.3f}x")
    print(f"Fraction galaxies improved  : {frac_imp:.3f}")
    print()
    print("Checks:")
    print(f"  v7 < baryon         : {'PASS' if checks['v7_lt_baryon_pass'] else 'FAIL'}")
    print(f"  v7 > MOND 1.702x    : {'PASS' if checks['v7_beats_mond_pass'] else 'FAIL'}")
    print(f"  v7 > OBS-001 2.264x : {'PASS' if checks['v7_beats_obs001_pass'] else 'FAIL'}")
    print(f"  lam_slow >= lam_fast: {'PASS' if checks['lambdas_ordered_pass'] else 'FAIL'}")
    print(f"  A > 0               : {'PASS' if checks['amplitude_positive_pass'] else 'FAIL'}")
    print(f"  frac improved > 0.60: {'PASS' if checks['majority_improved_pass'] else 'FAIL'}")
    print()
    print(f"qng_obs_v7_double_yukawa_reference_codex: {'PASS' if decision else 'FAIL'}")

    top5 = sorted(scan, key=lambda item: item["chi2_total"])[:5]
    print("\nTop 5 fits:")
    for item in top5:
        print(
            f"  lam_fast={item['lam_fast']:8.3f}  lam_slow={item['lam_slow']:9.3f}  "
            f"A={item['A']:10.3f}  chi2={item['chi2_total']:.3f}"
        )

    report = {
        "test_id": TEST_ID,
        "author": AUTHOR,
        "decision": "pass" if decision else "fail",
        "theory_variant": "v7 double-Yukawa observational proxy",
        "n_galaxies": n_galaxies,
        "n_points": n_points,
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_v7": round(med_v7, 4),
        "improvement_ratio": round(ratio, 4),
        "fraction_improved": round(frac_imp, 4),
        "baryon_chi2_total": round(baryon_chi2_total, 4),
        "best_lam_fast_kpc": round(best["lam_fast"], 6),
        "best_lam_slow_kpc": round(best["lam_slow"], 6),
        "best_A_kms2": round(best["A"], 6),
        "checks": checks,
        "reference_ratios": {
            "obs001_ratio": OBS001_RATIO,
            "mond_ratio": MOND_RATIO,
        },
        "top5": [
            {
                "lam_fast": round(item["lam_fast"], 6),
                "lam_slow": round(item["lam_slow"], 6),
                "A": round(item["A"], 6),
                "chi2_total": round(item["chi2_total"], 6),
            }
            for item in top5
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG v7 Double-Yukawa Rotation Reference (Codex)",
        f"- author: `{AUTHOR}`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof v7 proxy | {med_v7:.3f} |",
        f"| v7 improvement ratio | {ratio:.3f}x |",
        f"| OBS-001 ratio (reference) | {OBS001_RATIO:.3f}x |",
        f"| MOND ratio (reference) | {MOND_RATIO:.3f}x |",
        f"| Best lam_fast | {best['lam_fast']:.4f} kpc |",
        f"| Best lam_slow | {best['lam_slow']:.4f} kpc |",
        f"| Best A | {best['A']:.4f} (km/s)^2 |",
        f"| Fraction galaxies improved | {frac_imp:.3f} |",
        "",
        "## Checks",
        f"- v7 < baryon: {'PASS' if checks['v7_lt_baryon_pass'] else 'FAIL'}",
        f"- v7 > MOND: {'PASS' if checks['v7_beats_mond_pass'] else 'FAIL'}",
        f"- v7 > OBS-001: {'PASS' if checks['v7_beats_obs001_pass'] else 'FAIL'}",
        f"- lam_slow >= lam_fast: {'PASS' if checks['lambdas_ordered_pass'] else 'FAIL'}",
        f"- A > 0: {'PASS' if checks['amplitude_positive_pass'] else 'FAIL'}",
        f"- fraction improved > 0.60: {'PASS' if checks['majority_improved_pass'] else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
