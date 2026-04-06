from __future__ import annotations

"""
QNG-OBS-002: Galaxy rotation curves - QNG global fixed a_M (zero free parameters).

a_M = A_VORTEX = 0.225 fixed from QNG-CPU-043 vortex ring simulation.
No fitting to galaxy data. Pure prediction.
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-rotation-global-reference-v1"

A_VORTEX = 0.225   # sigma deficit from QNG-CPU-043 — fixed, not fitted
MIN_POINTS = 5


def load_data(path: Path) -> dict[str, list[dict]]:
    galaxies: dict[str, list[dict]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row["system_id"].strip()
            galaxies.setdefault(gid, []).append({
                "v_obs":       float(row["v_obs"]),
                "v_err":       float(row["v_err"]),
                "baryon_term": float(row["baryon_term"]),
            })
    return galaxies


def chi2_galaxy(rows: list[dict], a_M: float) -> tuple[float, float, int]:
    """Returns chi2_baryon, chi2_qng, n_points."""
    cb = cq = 0.0
    for r in rows:
        v_obs = r["v_obs"]
        v_err = max(r["v_err"], 1e-6)
        v2_obs = v_obs * v_obs
        v2_b   = r["baryon_term"]
        v2_err = 2.0 * v_obs * v_err
        if v2_err < 1e-12:
            continue
        cb += ((v2_obs - v2_b)        / v2_err) ** 2
        cq += ((v2_obs - v2_b - a_M)  / v2_err) ** 2
    return cb, cq, len(rows)


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
    print(f"Galaxies: {len(galaxies)}  |  A_VORTEX (fixed) = {A_VORTEX}")

    results = []
    skipped = 0
    for gid, rows in sorted(galaxies.items()):
        if len(rows) < MIN_POINTS:
            skipped += 1
            continue
        cb, cq, n = chi2_galaxy(rows, A_VORTEX)
        results.append({
            "galaxy": gid,
            "chi2_baryon": cb,
            "chi2_qng":    cq,
            "chi2_dof_baryon": cb / n,
            "chi2_dof_qng":    cq / max(1, n),
            "improved": cq < cb,
            "n": n,
        })

    n_fit = len(results)
    chi2_dof_b = [r["chi2_dof_baryon"] for r in results]
    chi2_dof_q = [r["chi2_dof_qng"]    for r in results]

    med_b = median(chi2_dof_b)
    med_q = median(chi2_dof_q)
    ratio = med_b / med_q if med_q > 0 else 0.0
    frac_improved = sum(r["improved"] for r in results) / n_fit

    # Check 4: median residual bias
    # median of (v2_obs - v2_baryon) across all points, compared to A_VORTEX
    all_residuals = []
    all_v2obs = []
    for gid, rows in sorted(galaxies.items()):
        if len(rows) < MIN_POINTS:
            continue
        for r in rows:
            all_residuals.append(r["v_obs"]**2 - r["baryon_term"])
            all_v2obs.append(r["v_obs"]**2)
    med_residual = median(all_residuals)
    med_v2obs    = median(all_v2obs)
    bias = abs(med_residual - A_VORTEX) / med_v2obs if med_v2obs > 0 else 1.0

    check1 = med_q < med_b
    check2 = ratio >= 1.5
    check3 = frac_improved > 0.50
    check4 = bias < 0.30  # informational

    decision = check1 and check2 and check3

    print(f"\nResults (a_M = {A_VORTEX} fixed, n={n_fit} galaxies):")
    print(f"  Median chi2/dof baryon-only : {med_b:.3f}")
    print(f"  Median chi2/dof QNG global  : {med_q:.3f}")
    print(f"  Improvement ratio           : {ratio:.3f}x")
    print(f"  Fraction improved           : {frac_improved:.3f}")
    print(f"  Median residual bias        : {bias:.3f}  (med_resid={med_residual:.1f}, A_VORTEX={A_VORTEX})")
    print()
    print("Checks:")
    print(f"  Check 1 (med QNG < baryon)  : {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (ratio >= 1.5x)     : {ratio:.3f}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (frac > 0.50)       : {frac_improved:.3f}  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 [info] (bias < 0.30): {bias:.3f}  {'PASS' if check4 else 'FAIL'}")
    print(f"\nqng_obs_rotation_global_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-OBS-002",
        "decision": "pass" if decision else "fail",
        "a_vortex_fixed": A_VORTEX,
        "n_galaxies_fit": n_fit,
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_qng":    round(med_q, 4),
        "improvement_ratio":      round(ratio, 4),
        "fraction_improved":      round(frac_improved, 4),
        "median_residual_bias":   round(bias, 4),
        "checks": {
            "chi2_dof_qng_lt_baryon_pass":   check1,
            "improvement_ratio_ge_1p5_pass": check2,
            "fraction_improved_gt_0p50_pass":check3,
            "bias_lt_0p30_info":             check4,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-002: Global Fixed a_M Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- a_M fixed = {A_VORTEX} (from QNG-CPU-043, zero free parameters)",
        "",
        "## Results",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof QNG global  | {med_q:.3f} |",
        f"| Improvement ratio           | {ratio:.3f}x |",
        f"| Fraction improved           | {frac_improved:.3f} |",
        f"| Median residual bias        | {bias:.3f} |",
        "",
        "## Checks",
        f"- Check 1 (QNG < baryon): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (ratio >= 1.5x): {'PASS' if check2 else 'FAIL'} ({ratio:.3f}x)",
        f"- Check 3 (frac > 0.50): {'PASS' if check3 else 'FAIL'} ({frac_improved:.3f})",
        f"- Check 4 [info] (bias < 0.30): {'PASS' if check4 else 'FAIL'} ({bias:.3f})",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
