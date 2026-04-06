from __future__ import annotations

"""
QNG-OBS-005: Galaxy rotation curves — ring Yukawa disk convolution.

Two global free parameters: lambda [kpc] and A [(km/s)^2].
For each galaxy, the chi-field at each observed radius rho_obs is the sum of
K_vel contributions from all baryonic rings at radii R_i in that galaxy,
weighted by V^2_baryon(R_i).

For fixed lambda, A_opt is solved analytically (global WLS across all galaxies).
Lambda is scanned on a log grid to find the chi^2 minimum.

Compared against:
  MOND  (OBS-003): 1.702x improvement, 0 free params
  Point Yukawa (OBS-004): FAIL (lambda -> inf, 2 free params)

Reference: DER-QNG-031 (qng-ring-yukawa-profile-v1.md)
"""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-ring-reference-v1"

# OBS-003 MOND baseline
MOND_RATIO = 1.702

# Lambda scan
LAM_MIN_KPC  = 0.1
LAM_MAX_KPC  = 50000.0
LAM_N_POINTS = 120

MIN_POINTS = 5

# Numerical integration
N_GAUSS = 64         # quadrature points for ring integral
SOFTENING_KPC = 0.05  # regularize ring singularity (r_source ~ r_obs)


def _gauss_u():
    """Precompute uniformly spaced u values and weights for ring integral."""
    u = [2.0 * math.pi * k / N_GAUSS for k in range(N_GAUSS)]
    w = 1.0 / N_GAUSS
    return u, w


_U_VALS, _W_VAL = _gauss_u()


def k_vel(rho_obs: float, R_src: float, lam: float) -> float:
    """
    Ring velocity kernel: circular velocity contribution at rho_obs (midplane)
    from a ring source at radius R_src, screening length lam. All in kpc.

    K_vel = rho_obs * (1/2pi) * integral_0^{2pi}
            exp(-d/lam) * (rho_obs - R_src*cos(u)) * (1/lam + 1/d) / d^2  du

    d(u) = sqrt(rho_obs^2 + R_src^2 - 2*rho_obs*R_src*cos(u) + eps^2)

    DER-QNG-031 §4, equation for K_ring_velocity.
    """
    eps2 = SOFTENING_KPC * SOFTENING_KPC
    total = 0.0
    for u in _U_VALS:
        cos_u = math.cos(u)
        d2 = rho_obs * rho_obs + R_src * R_src - 2.0 * rho_obs * R_src * cos_u + eps2
        if d2 < 1e-30:
            continue
        d = math.sqrt(d2)
        exp_d = math.exp(-d / lam) if d < 700.0 * lam else 0.0
        numerator = (rho_obs - R_src * cos_u) * (1.0 / lam + 1.0 / d)
        total += exp_d * numerator / d2
    return rho_obs * total * _W_VAL


def k_vel_far_field(r: float, lam: float) -> float:
    """Point-source limit (r >> R_src): (1 + r/lam) * exp(-r/lam)."""
    x = r / lam
    return (1.0 + x) * math.exp(-x) if x < 700.0 else 0.0


def load_data(path: Path) -> dict[str, list[dict]]:
    """Load rotation curve data, grouped by galaxy. Returns only galaxies with >= MIN_POINTS."""
    gal_rows: dict[str, list] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row["system_id"].strip()
            gal_rows.setdefault(gid, []).append(row)

    galaxies: dict[str, list[dict]] = {}
    for gid, grows in gal_rows.items():
        if len(grows) < MIN_POINTS:
            continue
        pts = []
        for row in grows:
            v_obs  = float(row["v_obs"])
            v_err  = max(float(row["v_err"]), 1e-6)
            v2_obs = v_obs * v_obs
            v2_b   = float(row["baryon_term"])
            v2_err = 2.0 * v_obs * v_err
            if v2_err < 1e-12:
                continue
            pts.append({
                "r":      float(row["radius"]),  # kpc
                "v2_obs": v2_obs,
                "v2_b":   v2_b,
                "res":    v2_obs - v2_b,
                "w":      1.0 / (v2_err * v2_err),
                "v2_err": v2_err,
            })
        if len(pts) >= MIN_POINTS:
            galaxies[gid] = pts
    return galaxies


def compute_disk_kernel(galaxy_pts: list[dict], lam: float) -> list[float]:
    """
    For each observation point in galaxy_pts, compute the disk-convolution kernel:

    K_disk(rho_obs) = sum_i V2_b(R_i) * K_vel(rho_obs, R_i, lam) / sum_i V2_b(R_i)

    This is the normalized ring-Yukawa prediction shape. Returns list of K_disk values,
    one per point in galaxy_pts.
    """
    # Source rings: all observed radii with their baryonic weights
    src_R  = [p["r"]    for p in galaxy_pts]
    src_w  = [p["v2_b"] for p in galaxy_pts]

    # Total baryonic weight for normalization
    w_total = sum(abs(w) for w in src_w)
    if w_total < 1e-30:
        w_total = 1.0

    k_disk = []
    for obs in galaxy_pts:
        rho_obs = obs["r"]
        val = 0.0
        for R_src, wb in zip(src_R, src_w):
            if abs(wb) < 1e-30:
                continue
            val += wb * k_vel(rho_obs, R_src, lam)
        k_disk.append(val / w_total)
    return k_disk


def fit_amplitude(
    galaxies: dict[str, list[dict]],
    kernels: dict[str, list[float]],
) -> tuple[float, float, float]:
    """
    Analytically solve for global A_opt by WLS across all data points.
    Returns (A_opt, chi2_baryon, chi2_ring).
    """
    num = den = chi2_b = 0.0
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        for p, k in zip(pts, ks):
            num  += p["w"] * p["res"] * k
            den  += p["w"] * k * k
            chi2_b += (p["res"] / p["v2_err"]) ** 2

    A_opt = num / den if den > 1e-30 else 0.0

    chi2_r = 0.0
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        for p, k in zip(pts, ks):
            chi2_r += ((p["res"] - A_opt * k) / p["v2_err"]) ** 2

    return A_opt, chi2_b, chi2_r


def median_improvement(
    galaxies: dict[str, list[dict]],
    kernels: dict[str, list[float]],
    A: float,
) -> tuple[float, float]:
    """Per-galaxy median chi2/dof for baryon-only and ring model."""
    vals_b, vals_r = [], []
    for gid, pts in galaxies.items():
        ks = kernels[gid]
        n = len(pts)
        cb = cr = 0.0
        for p, k in zip(pts, ks):
            cb += (p["res"] / p["v2_err"]) ** 2
            cr += ((p["res"] - A * k) / p["v2_err"]) ** 2
        vals_b.append(cb / n)
        vals_r.append(cr / n)

    def med(v: list[float]) -> float:
        s = sorted(v); n = len(s); m = n // 2
        return s[m] if n % 2 else (s[m-1] + s[m]) / 2.0

    return med(vals_b), med(vals_r)


def pearson_r(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n; my = sum(ys) / n
    sx = math.sqrt(sum((x - mx)**2 for x in xs) / n)
    sy = math.sqrt(sum((y - my)**2 for y in ys) / n)
    if sx < 1e-30 or sy < 1e-30:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--lam-n",   type=int, default=LAM_N_POINTS)
    parser.add_argument("--lam-min", type=float, default=LAM_MIN_KPC)
    parser.add_argument("--lam-max", type=float, default=LAM_MAX_KPC)
    args = parser.parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    galaxies = load_data(DATA_FILE)
    n_gal  = len(galaxies)
    n_pts  = sum(len(v) for v in galaxies.values())
    print(f"Galaxies: {n_gal}  Points: {n_pts}")

    # Lambda scan (log-uniform)
    lam_grid = [
        args.lam_min * (args.lam_max / args.lam_min) ** (i / (args.lam_n - 1))
        for i in range(args.lam_n)
    ]

    best_lam  = lam_grid[0]
    best_A    = 0.0
    best_chi2 = 1e30
    scan_results = []

    for idx, lam in enumerate(lam_grid):
        if idx % 20 == 0:
            print(f"  lambda={lam:.1f} kpc  ({idx+1}/{args.lam_n})")
        # Build per-galaxy disk kernels
        kernels: dict[str, list[float]] = {}
        for gid, pts in galaxies.items():
            kernels[gid] = compute_disk_kernel(pts, lam)

        A_opt, _, chi2_r = fit_amplitude(galaxies, kernels)
        scan_results.append({"lambda": lam, "A_opt": A_opt, "chi2_ring": chi2_r})
        if chi2_r < best_chi2:
            best_chi2 = chi2_r
            best_lam  = lam
            best_A    = A_opt

    # Final evaluation at best lambda
    print(f"\nBest lambda: {best_lam:.2f} kpc  A: {best_A:.2f} (km/s)^2")
    best_kernels: dict[str, list[float]] = {}
    for gid, pts in galaxies.items():
        best_kernels[gid] = compute_disk_kernel(pts, best_lam)

    med_b, med_r = median_improvement(galaxies, best_kernels, best_A)
    ratio = med_b / med_r if med_r > 0 else 0.0

    # Per-galaxy A for Check 6 (a_M correlation)
    per_gal_A: list[float] = []
    per_gal_mass_proxy: list[float] = []
    for gid, pts in galaxies.items():
        ks = best_kernels[gid]
        num = den = 0.0
        for p, k in zip(pts, ks):
            num += p["w"] * p["res"] * k
            den += p["w"] * k * k
        A_gal = num / den if den > 1e-30 else 0.0
        # Mass proxy: max V^2_obs * r_max (rough virial mass indicator)
        m_proxy = max(p["v2_obs"] * p["r"] for p in pts)
        per_gal_A.append(A_gal)
        per_gal_mass_proxy.append(m_proxy)

    r_pearson = pearson_r(per_gal_A, per_gal_mass_proxy)

    # Fraction improved
    n_improved = 0
    for gid, pts in galaxies.items():
        ks = best_kernels[gid]
        cb = sum((p["res"] / p["v2_err"])**2 for p in pts)
        cr = sum(((p["res"] - best_A * k) / p["v2_err"])**2 for p, k in zip(pts, ks))
        if cr < cb:
            n_improved += 1
    frac_improved = n_improved / n_gal

    # Checks
    check1 = med_r < med_b
    check2 = ratio > MOND_RATIO
    check3 = 1.0 <= best_lam <= 5000.0
    check4 = best_A > 0
    check6_info = r_pearson > 0.40

    decision = check1 and check2 and check3 and check4

    print(f"\nMedian chi2/dof baryon-only : {med_b:.3f}")
    print(f"Median chi2/dof ring model  : {med_r:.3f}")
    print(f"Ring improvement ratio      : {ratio:.3f}x")
    print(f"MOND improvement ratio [ref]: {MOND_RATIO:.3f}x")
    print(f"Fraction galaxies improved  : {frac_improved:.3f}")
    print(f"Pearson r(A_gal, M_proxy)   : {r_pearson:.3f}")
    print()
    print("Checks:")
    print(f"  Check 1 (ring < baryon)          : {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (ratio > MOND 1.702)     : {ratio:.3f}  {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (1 < lambda < 5000 kpc)  : {best_lam:.2f} kpc  {'PASS' if check3 else 'FAIL'}")
    print(f"  Check 4 (A_opt > 0)              : {best_A:.2f}  {'PASS' if check4 else 'FAIL'}")
    print(f"  Check 6 [info] Pearson r > 0.40  : {r_pearson:.3f}  {'PASS' if check6_info else 'FAIL'}")
    print(f"\nqng_obs_ring_reference: {'PASS' if decision else 'FAIL'}")

    # Top 5 lambda values
    scan_sorted = sorted(scan_results, key=lambda x: x["chi2_ring"])[:5]
    print("\nTop 5 lambda values by chi^2:")
    for s in scan_sorted:
        print(f"  lambda={s['lambda']:8.2f} kpc  A={s['A_opt']:8.1f}  chi2={s['chi2_ring']:.1f}")

    # Save report
    report = {
        "test_id": "QNG-OBS-005",
        "decision": "pass" if decision else "fail",
        "best_lambda_kpc":  round(best_lam, 4),
        "best_A_kms2":      round(best_A, 4),
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_ring":   round(med_r, 4),
        "improvement_ratio":      round(ratio, 4),
        "mond_ratio_reference":   MOND_RATIO,
        "fraction_improved":      round(frac_improved, 4),
        "pearson_r_A_mass":       round(r_pearson, 4),
        "n_galaxies": n_gal,
        "n_points":   n_pts,
        "lambda_scan_n": args.lam_n,
        "softening_kpc": SOFTENING_KPC,
        "n_gauss": N_GAUSS,
        "checks": {
            "ring_lt_baryon_pass":        check1,
            "ratio_gt_mond_pass":         check2,
            "lambda_in_range_pass":       check3,
            "A_opt_positive_pass":        check4,
            "pearson_r_gt_040_info":      check6_info,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-005: Ring Yukawa Disk Convolution Reference",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- best-fit lambda = {best_lam:.2f} kpc",
        f"- best-fit A = {best_A:.2f} (km/s)^2",
        "",
        "## Results",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof ring model | {med_r:.3f} |",
        f"| Ring improvement ratio | {ratio:.3f}x |",
        f"| MOND improvement ratio (OBS-003) | {MOND_RATIO:.3f}x |",
        f"| Fraction galaxies improved | {frac_improved:.3f} |",
        f"| Pearson r(A_gal, M_proxy) | {r_pearson:.3f} |",
        f"| Best-fit lambda | {best_lam:.2f} kpc |",
        f"| Best-fit A | {best_A:.2f} (km/s)^2 |",
        "",
        "## Checks",
        f"- Check 1 (ring < baryon): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (ratio > MOND): {'PASS' if check2 else 'FAIL'} ({ratio:.3f}x vs {MOND_RATIO:.3f}x)",
        f"- Check 3 (lambda in range): {'PASS' if check3 else 'FAIL'} ({best_lam:.2f} kpc)",
        f"- Check 4 (A_opt > 0): {'PASS' if check4 else 'FAIL'} ({best_A:.2f})",
        f"- Check 6 [info] Pearson r: {'PASS' if check6_info else 'FAIL'} ({r_pearson:.3f})",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
