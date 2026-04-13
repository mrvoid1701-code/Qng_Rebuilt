from __future__ import annotations

"""
QNG v7 observational proxy with toroidal source geometry.

Codex variant:
  - standalone file, does not modify existing OBS scripts
  - keeps ring/disk geometry from OBS-005
  - adds a second Yukawa-like response stage to reflect the v7 sigma_m -> sigma_g cascade

This is a pragmatic observational proxy for the latest theory direction:
    ring source geometry + v7 two-field response
It is not presented as the final theorem-level v7 galaxy formula.
"""

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-v7-ring-cascade-codex-v1"

AUTHOR = "Codex"
TEST_ID = "QNG-OBS-V7-CODEX-002"
MIN_POINTS = 5

# Reference baselines from the existing workspace
OBS001_RATIO = 38.870 / 17.166
OBS005_RATIO = 1.058
MOND_RATIO = 1.702

# Ring integration
N_GAUSS = 64
SOFTENING_KPC = 0.05

# Scan
LAM_RING_MIN = 0.1
LAM_RING_MAX = 50000.0
LAM_RING_N = 28

LAM_GRAV_MIN = 0.1
LAM_GRAV_MAX = 50000.0
LAM_GRAV_N = 36


def log_grid(x_min: float, x_max: float, n: int) -> list[float]:
    if n <= 1:
        return [x_min]
    return [x_min * (x_max / x_min) ** (i / (n - 1)) for i in range(n)]


def _gauss_u() -> tuple[list[float], float]:
    u = [2.0 * math.pi * k / N_GAUSS for k in range(N_GAUSS)]
    w = 1.0 / N_GAUSS
    return u, w


_U_VALS, _W_VAL = _gauss_u()


def load_data(path: Path) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            gid = row["system_id"].strip()
            grouped.setdefault(gid, []).append(row)

    galaxies: dict[str, list[dict]] = {}
    for gid, rows in grouped.items():
        if len(rows) < MIN_POINTS:
            continue
        pts: list[dict] = []
        for row in rows:
            v_obs = float(row["v_obs"])
            v_err = max(float(row["v_err"]), 1e-6)
            v2_obs = v_obs * v_obs
            v2_b = float(row["baryon_term"])
            v2_err = 2.0 * v_obs * v_err
            if v2_err <= 1e-12:
                continue
            pts.append(
                {
                    "r": float(row["radius"]),
                    "v2_obs": v2_obs,
                    "v2_b": v2_b,
                    "res": v2_obs - v2_b,
                    "w": 1.0 / (v2_err * v2_err),
                    "v2_err": v2_err,
                }
            )
        if len(pts) >= MIN_POINTS:
            galaxies[gid] = pts
    return galaxies


def k_vel(rho_obs: float, r_src: float, lam: float) -> float:
    """
    Same toroidal velocity kernel as OBS-005:
      contribution at rho_obs from a source ring at radius r_src.
    """
    eps2 = SOFTENING_KPC * SOFTENING_KPC
    total = 0.0
    for u in _U_VALS:
        cos_u = math.cos(u)
        d2 = rho_obs * rho_obs + r_src * r_src - 2.0 * rho_obs * r_src * cos_u + eps2
        if d2 < 1e-30:
            continue
        d = math.sqrt(d2)
        exp_d = math.exp(-d / lam) if d < 700.0 * lam else 0.0
        numerator = (rho_obs - r_src * cos_u) * (1.0 / lam + 1.0 / d)
        total += exp_d * numerator / d2
    return rho_obs * total * _W_VAL


def gravity_response_kernel(rho_obs: float, lam_grav: float) -> float:
    """
    v7 response proxy for sigma_m -> sigma_g cascade.

    Uses the same screened circular-velocity style factor as the old Yukawa lane,
    but now as a second stage that modulates the toroidal source response.
    """
    x = rho_obs / lam_grav
    if x > 700.0:
        return 0.0
    return (1.0 + x) * math.exp(-x)


def compute_ring_disk_kernel(galaxy_pts: list[dict], lam_ring: float) -> list[float]:
    """
    Geometry stage:
      sum over baryonic rings in the galaxy.
    """
    src_r = [p["r"] for p in galaxy_pts]
    src_w = [p["v2_b"] for p in galaxy_pts]

    total_w = sum(abs(w) for w in src_w)
    if total_w < 1e-30:
        total_w = 1.0

    values: list[float] = []
    for obs in galaxy_pts:
        rho_obs = obs["r"]
        accum = 0.0
        for r_src, w_b in zip(src_r, src_w):
            if abs(w_b) < 1e-30:
                continue
            accum += w_b * k_vel(rho_obs, r_src, lam_ring)
        values.append(accum / total_w)
    return values


def compute_v7_kernel_from_ring(galaxy_pts: list[dict], ring_kernel: list[float], lam_grav: float) -> list[float]:
    """
    v7 cascade stage:
      toroidal source geometry from sigma_m
      then extra sigma_g response scale.
    """
    return [k * gravity_response_kernel(p["r"], lam_grav) for p, k in zip(galaxy_pts, ring_kernel)]


def fit_amplitude(
    galaxies: dict[str, list[dict]],
    kernels: dict[str, list[float]],
) -> tuple[float, float, float]:
    num = den = chi2_b = 0.0
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        for p, k in zip(pts, ks):
            num += p["w"] * p["res"] * k
            den += p["w"] * k * k
            chi2_b += (p["res"] / p["v2_err"]) ** 2

    a_opt = num / den if den > 1e-30 else 0.0

    chi2_v7 = 0.0
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        for p, k in zip(pts, ks):
            chi2_v7 += ((p["res"] - a_opt * k) / p["v2_err"]) ** 2

    return a_opt, chi2_b, chi2_v7


def median_chi2_dof(
    galaxies: dict[str, list[dict]],
    kernels: dict[str, list[float]],
    amplitude: float,
) -> tuple[float, float]:
    vals_b: list[float] = []
    vals_v7: list[float] = []
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        n = len(pts)
        cb = cv7 = 0.0
        for p, k in zip(pts, ks):
            cb += (p["res"] / p["v2_err"]) ** 2
            cv7 += ((p["res"] - amplitude * k) / p["v2_err"]) ** 2
        vals_b.append(cb / n)
        vals_v7.append(cv7 / n)

    def med(values: list[float]) -> float:
        ordered = sorted(values)
        count = len(ordered)
        mid = count // 2
        if count % 2:
            return ordered[mid]
        return (ordered[mid - 1] + ordered[mid]) / 2.0

    return med(vals_b), med(vals_v7)


def fraction_improved(
    galaxies: dict[str, list[dict]],
    kernels: dict[str, list[float]],
    amplitude: float,
) -> float:
    improved = 0
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        cb = cv7 = 0.0
        for p, k in zip(pts, ks):
            cb += (p["res"] / p["v2_err"]) ** 2
            cv7 += ((p["res"] - amplitude * k) / p["v2_err"]) ** 2
        if cv7 < cb:
            improved += 1
    return improved / len(galaxies)


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG v7 toroidal cascade observational proxy by Codex.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--lam-ring-n", type=int, default=LAM_RING_N)
    parser.add_argument("--lam-grav-n", type=int, default=LAM_GRAV_N)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    galaxies = load_data(DATA_FILE)
    n_gal = len(galaxies)
    n_pts = sum(len(v) for v in galaxies.values())
    print(f"Author: {AUTHOR}")
    print(f"Galaxies: {n_gal}  Points: {n_pts}")

    lam_ring_grid = log_grid(LAM_RING_MIN, LAM_RING_MAX, args.lam_ring_n)
    lam_grav_grid = log_grid(LAM_GRAV_MIN, LAM_GRAV_MAX, args.lam_grav_n)

    best = {
        "lam_ring": lam_ring_grid[0],
        "lam_grav": lam_grav_grid[0],
        "A": 0.0,
        "chi2_total": float("inf"),
    }
    scan_results: list[dict] = []

    ring_kernel_cache: dict[float, dict[str, list[float]]] = {}

    for idx_ring, lam_ring in enumerate(lam_ring_grid, start=1):
        print(f"  ring geometry scan {idx_ring}/{len(lam_ring_grid)}: lam_ring={lam_ring:.3f} kpc")
        ring_kernel_cache[lam_ring] = {
            gid: compute_ring_disk_kernel(pts, lam_ring)
            for gid, pts in galaxies.items()
        }

        for lam_grav in lam_grav_grid:
            kernels = {
                gid: compute_v7_kernel_from_ring(galaxies[gid], ring_kernel_cache[lam_ring][gid], lam_grav)
                for gid in galaxies
            }
            a_opt, chi2_b, chi2_v7 = fit_amplitude(galaxies, kernels)
            scan_results.append(
                {
                    "lam_ring": lam_ring,
                    "lam_grav": lam_grav,
                    "A": a_opt,
                    "chi2_total": chi2_v7,
                }
            )
            if chi2_v7 < best["chi2_total"]:
                best = {
                    "lam_ring": lam_ring,
                    "lam_grav": lam_grav,
                    "A": a_opt,
                    "chi2_total": chi2_v7,
                    "chi2_baryon": chi2_b,
                }

    best_kernels = {
        gid: compute_v7_kernel_from_ring(galaxies[gid], ring_kernel_cache[best["lam_ring"]][gid], best["lam_grav"])
        for gid in galaxies
    }
    med_b, med_v7 = median_chi2_dof(galaxies, best_kernels, best["A"])
    ratio = med_b / med_v7 if med_v7 > 0 else 0.0
    frac_imp = fraction_improved(galaxies, best_kernels, best["A"])

    checks = {
        "v7_lt_baryon_pass": med_v7 < med_b,
        "v7_beats_mond_pass": ratio > MOND_RATIO,
        "v7_beats_obs001_pass": ratio > OBS001_RATIO,
        "v7_beats_obs005_pass": ratio > OBS005_RATIO,
        "lam_grav_positive_pass": best["lam_grav"] > 0.0,
        "amplitude_positive_pass": best["A"] > 0.0,
        "majority_improved_pass": frac_imp > 0.60,
    }
    decision = (
        checks["v7_lt_baryon_pass"]
        and checks["lam_grav_positive_pass"]
        and checks["amplitude_positive_pass"]
        and checks["majority_improved_pass"]
    )

    print()
    print(f"Best lam_ring : {best['lam_ring']:.4f} kpc")
    print(f"Best lam_grav : {best['lam_grav']:.4f} kpc")
    print(f"Best A        : {best['A']:.4f} (km/s)^2")
    print(f"Median chi2/dof baryon-only : {med_b:.3f}")
    print(f"Median chi2/dof v7 cascade  : {med_v7:.3f}")
    print(f"v7 cascade improvement      : {ratio:.3f}x")
    print(f"Fraction galaxies improved  : {frac_imp:.3f}")
    print()
    print("Checks:")
    print(f"  v7 < baryon         : {'PASS' if checks['v7_lt_baryon_pass'] else 'FAIL'}")
    print(f"  v7 > MOND 1.702x    : {'PASS' if checks['v7_beats_mond_pass'] else 'FAIL'}")
    print(f"  v7 > OBS-001 2.264x : {'PASS' if checks['v7_beats_obs001_pass'] else 'FAIL'}")
    print(f"  v7 > OBS-005 1.058x : {'PASS' if checks['v7_beats_obs005_pass'] else 'FAIL'}")
    print(f"  lam_grav > 0        : {'PASS' if checks['lam_grav_positive_pass'] else 'FAIL'}")
    print(f"  A > 0               : {'PASS' if checks['amplitude_positive_pass'] else 'FAIL'}")
    print(f"  frac improved > 0.60: {'PASS' if checks['majority_improved_pass'] else 'FAIL'}")
    print()
    print(f"qng_obs_v7_ring_cascade_reference_codex: {'PASS' if decision else 'FAIL'}")

    top5 = sorted(scan_results, key=lambda item: item["chi2_total"])[:5]
    print("\nTop 5 fits:")
    for item in top5:
        print(
            f"  lam_ring={item['lam_ring']:9.3f}  lam_grav={item['lam_grav']:9.3f}  "
            f"A={item['A']:10.3f}  chi2={item['chi2_total']:.3f}"
        )

    report = {
        "test_id": TEST_ID,
        "author": AUTHOR,
        "decision": "pass" if decision else "fail",
        "theory_variant": "v7 toroidal cascade proxy",
        "n_galaxies": n_gal,
        "n_points": n_pts,
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_v7_cascade": round(med_v7, 4),
        "improvement_ratio": round(ratio, 4),
        "fraction_improved": round(frac_imp, 4),
        "best_lam_ring_kpc": round(best["lam_ring"], 6),
        "best_lam_grav_kpc": round(best["lam_grav"], 6),
        "best_A_kms2": round(best["A"], 6),
        "checks": checks,
        "reference_ratios": {
            "obs001_ratio": OBS001_RATIO,
            "obs005_ratio": OBS005_RATIO,
            "mond_ratio": MOND_RATIO,
        },
        "top5": [
            {
                "lam_ring": round(item["lam_ring"], 6),
                "lam_grav": round(item["lam_grav"], 6),
                "A": round(item["A"], 6),
                "chi2_total": round(item["chi2_total"], 6),
            }
            for item in top5
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG v7 Ring Cascade Rotation Reference (Codex)",
        f"- author: `{AUTHOR}`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof v7 cascade | {med_v7:.3f} |",
        f"| v7 cascade improvement ratio | {ratio:.3f}x |",
        f"| OBS-001 ratio (reference) | {OBS001_RATIO:.3f}x |",
        f"| OBS-005 ratio (reference) | {OBS005_RATIO:.3f}x |",
        f"| MOND ratio (reference) | {MOND_RATIO:.3f}x |",
        f"| Best lam_ring | {best['lam_ring']:.4f} kpc |",
        f"| Best lam_grav | {best['lam_grav']:.4f} kpc |",
        f"| Best A | {best['A']:.4f} (km/s)^2 |",
        f"| Fraction galaxies improved | {frac_imp:.3f} |",
        "",
        "## Checks",
        f"- v7 < baryon: {'PASS' if checks['v7_lt_baryon_pass'] else 'FAIL'}",
        f"- v7 > MOND: {'PASS' if checks['v7_beats_mond_pass'] else 'FAIL'}",
        f"- v7 > OBS-001: {'PASS' if checks['v7_beats_obs001_pass'] else 'FAIL'}",
        f"- v7 > OBS-005: {'PASS' if checks['v7_beats_obs005_pass'] else 'FAIL'}",
        f"- lam_grav > 0: {'PASS' if checks['lam_grav_positive_pass'] else 'FAIL'}",
        f"- A > 0: {'PASS' if checks['amplitude_positive_pass'] else 'FAIL'}",
        f"- fraction improved > 0.60: {'PASS' if checks['majority_improved_pass'] else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
