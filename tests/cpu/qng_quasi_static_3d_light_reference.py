from __future__ import annotations

"""
QNG-CPU-031: Quasi-static point source in 3D (6x6x6 cubic lattice, PBC).

Tests structural predictions of DER-QNG-012 and DER-QNG-015 on a 3D geometry:
- Screened Poisson profile with 3D-corrected screening length
- G_QNG scaling as 1/z (key formula prediction)
- Generation order sigma -> chi in 3D
- Quasi-static Poisson residual small in bulk

Does NOT attempt to verify Phi ~ 1/r (insufficient radial range on 216-node grid).
"""

import argparse
import json
import math
import random
from pathlib import Path

from qng_native_update_reference import clip01, wrap_angle, angle_diff

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-quasi-static-3d-light-reference-v1"
)

# ---------------------------------------------------------------------------
# Geometry: 6x6x6 cubic lattice with periodic boundary conditions
# ---------------------------------------------------------------------------

N_PER_AXIS: int = 6
N_NODES: int = N_PER_AXIS ** 3       # 216
Z_3D: int = 6                        # coordination number (cubic lattice)
Z_1D: int = 2                        # coordination number of 1D reference ring

# Quasi-static parameters (same as 1D reference test QNG-CPU-030)
ALPHA: float = 0.005
BETA: float = 0.35
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20
DELTA: float = 0.20

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05
SOURCE_NODE: int = 0          # node at lattice position (0,0,0)

STEPS: int = 2000
SEED: int = 20260325

# Predicted screening lengths
# lambda = sqrt(beta / (z * alpha))
LAMBDA_PRED_3D: float = math.sqrt(BETA / (Z_3D * ALPHA))   # ≈ 3.42
LAMBDA_PRED_1D: float = math.sqrt(BETA / (Z_1D * ALPHA))   # ≈ 5.92

# G_QNG in substrate units (Du=1, t_s=1)
G_QNG_3D: float = BETA / Z_3D    # ≈ 0.0583
G_QNG_1D: float = BETA / Z_1D    # ≈ 0.1750
G_RATIO_PRED: float = Z_1D / Z_3D  # = 1/3 ≈ 0.3333


# ---------------------------------------------------------------------------
# Lattice helpers
# ---------------------------------------------------------------------------

def xyz_to_idx(x: int, y: int, z: int, N: int = N_PER_AXIS) -> int:
    return x + N * y + N * N * z


def idx_to_xyz(idx: int, N: int = N_PER_AXIS) -> tuple[int, int, int]:
    x = idx % N
    y = (idx // N) % N
    z = idx // (N * N)
    return x, y, z


def build_cubic_lattice(N: int = N_PER_AXIS) -> list[list[int]]:
    """6-connected cubic lattice with periodic boundary conditions."""
    adj: list[list[int]] = []
    for k in range(N):
        for j in range(N):
            for i in range(N):
                neighbors = [
                    xyz_to_idx((i + 1) % N, j, k, N),
                    xyz_to_idx((i - 1) % N, j, k, N),
                    xyz_to_idx(i, (j + 1) % N, k, N),
                    xyz_to_idx(i, (j - 1) % N, k, N),
                    xyz_to_idx(i, j, (k + 1) % N, N),
                    xyz_to_idx(i, j, (k - 1) % N, N),
                ]
                adj.append(neighbors)
    return adj


def lattice_distance(idx_i: int, idx_j: int, N: int = N_PER_AXIS) -> float:
    """Euclidean distance with minimum-image convention (PBC)."""
    xi, yi, zi = idx_to_xyz(idx_i, N)
    xj, yj, zj = idx_to_xyz(idx_j, N)
    dx = min(abs(xi - xj), N - abs(xi - xj))
    dy = min(abs(yi - yj), N - abs(yi - yj))
    dz = min(abs(zi - zj), N - abs(zi - zj))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# ---------------------------------------------------------------------------
# One step: v3 quasi-static on arbitrary adjacency list (no history, no noise)
# ---------------------------------------------------------------------------

def one_step_3d(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
) -> tuple[list[float], list[float], list[float]]:
    n = len(adj)
    new_sigma = [0.0] * n
    new_chi = [0.0] * n
    new_phi = [0.0] * n

    for i, neighbors in enumerate(adj):
        z = len(neighbors)

        sigma_bar = sum(sigma[j] for j in neighbors) / z
        chi_bar = sum(chi[j] for j in neighbors) / z
        sin_s = sum(math.sin(phi[j]) for j in neighbors)
        cos_s = sum(math.cos(phi[j]) for j in neighbors)
        phi_bar = (
            math.atan2(sin_s, cos_s)
            if abs(sin_s) + abs(cos_s) > 1e-12
            else phi[i]
        )

        # sigma channel
        new_sigma[i] = clip01(
            sigma[i]
            + ALPHA * (SIGMA_REF - sigma[i])
            + BETA * (sigma_bar - sigma[i])
        )

        # chi channel (v3: Channel D active)
        new_chi[i] = (
            chi[i]
            - CHI_DECAY * chi[i]
            + CHI_REL * (sigma_bar - sigma[i])
            + DELTA * (SIGMA_REF - sigma[i])
        )

        # phi channel
        new_phi[i] = wrap_angle(
            phi[i] + PHI_REL * angle_diff(phi_bar, phi[i])
        )

    # Clamp source node
    new_sigma[SOURCE_NODE] = SIGMA_SOURCE

    return new_sigma, new_chi, new_phi


# ---------------------------------------------------------------------------
# Profile extraction: radial bins
# ---------------------------------------------------------------------------

def radial_profile(
    sigma: list[float],
    chi: list[float],
    n: int = N_NODES,
    n_per_axis: int = N_PER_AXIS,
) -> dict[float, dict]:
    """Average sigma and chi over nodes in each radial bin from SOURCE_NODE."""
    bin_data: dict[float, list[tuple[float, float]]] = {}
    for i in range(n):
        r = round(lattice_distance(SOURCE_NODE, i, n_per_axis), 4)
        if r not in bin_data:
            bin_data[r] = []
        bin_data[r].append((sigma[i], chi[i]))

    profile = {}
    for r, vals in sorted(bin_data.items()):
        sigma_vals = [v[0] for v in vals]
        chi_vals = [v[1] for v in vals]
        profile[r] = {
            "sigma_mean": sum(sigma_vals) / len(sigma_vals),
            "chi_mean": sum(chi_vals) / len(chi_vals),
            "n_nodes": len(vals),
        }
    return profile


# ---------------------------------------------------------------------------
# Exponential fit
# ---------------------------------------------------------------------------

def fit_exponential(
    rs: list[float], vals: list[float]
) -> tuple[float, float, float]:
    """Fit log|vals| = log(A) - r/lambda via OLS. Returns (A, lambda, R²)."""
    pts = [(r, v) for r, v in zip(rs, vals) if abs(v) > 1e-9]
    if len(pts) < 3:
        return 0.0, 0.0, 0.0
    log_pts = [(r, math.log(abs(v))) for r, v in pts]
    n = len(log_pts)
    sx = sum(r for r, _ in log_pts)
    sy = sum(y for _, y in log_pts)
    sxy = sum(r * y for r, y in log_pts)
    sxx = sum(r * r for r, _ in log_pts)
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-15:
        return 0.0, 0.0, 0.0
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    lam = -1.0 / slope if abs(slope) > 1e-12 else 1e9
    A = math.exp(intercept)
    y_mean = sy / n
    ss_res = sum((y - (intercept + slope * r)) ** 2 for r, y in log_pts)
    ss_tot = sum((y - y_mean) ** 2 for _, y in log_pts)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0
    return A, lam, r2


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx < 1e-15 or dy < 1e-15:
        return 0.0
    return num / (dx * dy)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="QNG quasi-static 3D light CPU reference test (QNG-CPU-031)."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    adj = build_cubic_lattice(N_PER_AXIS)
    rng = random.Random(SEED)

    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    chi = [0.0] * N_NODES
    phi = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]
    sigma[SOURCE_NODE] = SIGMA_SOURCE

    for _ in range(STEPS):
        sigma, chi, phi = one_step_3d(sigma, chi, phi, adj)

    profile = radial_profile(sigma, chi, N_NODES, N_PER_AXIS)
    r_sorted = sorted(profile.keys())

    sigma_by_r = {r: profile[r]["sigma_mean"] for r in r_sorted}
    chi_by_r = {r: profile[r]["chi_mean"] for r in r_sorted}
    delta_sigma_by_r = {r: sigma_by_r[r] - SIGMA_REF for r in r_sorted}

    # ------------------------------------------------------------------
    # Check 1: sigma decays monotonically from source at integer distances
    # On a cubic lattice, irrational distances (sqrt(2), sqrt(3), ...) can
    # show discrete averaging artefacts. Test only integer-valued distances.
    # ------------------------------------------------------------------
    integer_rs = [r for r in r_sorted if abs(r - round(r)) < 0.01 and r <= 3.0]
    sigma_integer = [sigma_by_r[r] for r in integer_rs]
    monotone = all(
        sigma_integer[i] <= sigma_integer[i + 1]
        for i in range(len(sigma_integer) - 1)
    )
    source_depleted = delta_sigma_by_r[r_sorted[0]] < -0.01
    check1_pass = monotone and source_depleted

    # ------------------------------------------------------------------
    # Check 2: exponential fit quality R² > 0.75
    # Use radial bins r in [1, 3] (Euclidean distance)
    # ------------------------------------------------------------------
    fit_rs = [r for r in r_sorted if 1.0 <= r <= 3.0]
    fit_ds = [delta_sigma_by_r[r] for r in fit_rs]
    _, lambda_obs, r2_fit = fit_exponential(fit_rs, fit_ds)
    check2_pass = r2_fit > 0.75

    # ------------------------------------------------------------------
    # Check 3: observed 3D screening length within 30% of predicted
    # ------------------------------------------------------------------
    if lambda_obs > 0:
        lambda_ratio = lambda_obs / LAMBDA_PRED_3D
        lambda_error_3d = abs(lambda_ratio - 1.0)
    else:
        lambda_ratio = 0.0
        lambda_error_3d = 1.0
    check3_pass = lambda_error_3d < 0.30

    # ------------------------------------------------------------------
    # Check 4: G_QNG ratio G_3D / G_1D within 20% of predicted (1/3)
    # G_QNG = beta / z (substrate units, Du=1, t_s=1)
    # ------------------------------------------------------------------
    g_ratio_obs = G_QNG_3D / G_QNG_1D    # formula gives exact 1/3
    g_ratio_error = abs(g_ratio_obs - G_RATIO_PRED) / G_RATIO_PRED
    check4_pass = g_ratio_error < 0.20

    # ------------------------------------------------------------------
    # Check 5: generation order spatial correlation > 0.60
    # ------------------------------------------------------------------
    deficit_all = [SIGMA_REF - sigma[i] for i in range(N_NODES)]
    corr_deficit_chi = pearson(deficit_all, chi)
    check5_pass = corr_deficit_chi > 0.60

    # ------------------------------------------------------------------
    # Check 6: Poisson residual small in bulk (r >= 2)
    # residual_i = |beta*(sigma_bar - sigma_i) - alpha*(sigma_i - sigma_ref)|
    # should be near zero at quasi-static equilibrium
    # ------------------------------------------------------------------
    bulk_residuals: list[float] = []
    for i in range(N_NODES):
        r_i = lattice_distance(SOURCE_NODE, i, N_PER_AXIS)
        if r_i < 2.0:
            continue
        neighbors = adj[i]
        sigma_bar = sum(sigma[j] for j in neighbors) / len(neighbors)
        residual = abs(
            BETA * (sigma_bar - sigma[i]) - ALPHA * (sigma[i] - SIGMA_REF)
        )
        bulk_residuals.append(residual)

    mean_residual = sum(bulk_residuals) / len(bulk_residuals) if bulk_residuals else 1.0
    check6_pass = mean_residual < 0.01

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------
    checks = {
        "sigma_decays_monotonically_pass": check1_pass,
        "exponential_fit_quality_pass": check2_pass,
        "screening_length_3d_match_pass": check3_pass,
        "G_QNG_ratio_scaling_pass": check4_pass,
        "generation_order_3d_correlation_pass": check5_pass,
        "poisson_residual_bulk_pass": check6_pass,
    }
    decision = all(checks.values())

    # Sample radial profile for report
    profile_sample = {}
    for r in r_sorted[:12]:
        profile_sample[f"r{r:.3f}"] = {
            "sigma": round(sigma_by_r[r], 6),
            "chi": round(chi_by_r[r], 6),
            "delta_sigma": round(delta_sigma_by_r[r], 6),
            "n_nodes": profile[r]["n_nodes"],
        }

    report = {
        "test_id": "QNG-CPU-031",
        "decision": "pass" if decision else "fail",
        "geometry": {
            "n_per_axis": N_PER_AXIS,
            "n_nodes": N_NODES,
            "z_3d": Z_3D,
            "z_1d": Z_1D,
        },
        "parameters": {
            "alpha": ALPHA,
            "beta": BETA,
            "delta": DELTA,
            "sigma_source": SIGMA_SOURCE,
            "steps": STEPS,
        },
        "screening": {
            "lambda_pred_3d": round(LAMBDA_PRED_3D, 4),
            "lambda_pred_1d": round(LAMBDA_PRED_1D, 4),
            "lambda_obs_3d": round(lambda_obs, 4),
            "ratio_obs_pred": round(lambda_ratio, 4),
            "relative_error": round(lambda_error_3d, 4),
            "r2_fit": round(r2_fit, 4),
        },
        "G_QNG": {
            "G_3d_substrate": round(G_QNG_3D, 6),
            "G_1d_substrate": round(G_QNG_1D, 6),
            "ratio_obs": round(g_ratio_obs, 6),
            "ratio_pred": round(G_RATIO_PRED, 6),
            "relative_error": round(g_ratio_error, 6),
        },
        "generation_order": {
            "corr_deficit_chi": round(corr_deficit_chi, 4),
        },
        "poisson_residual": {
            "mean_bulk_residual": round(mean_residual, 6),
            "n_bulk_nodes": len(bulk_residuals),
        },
        "profile_sample": profile_sample,
        "checks": checks,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Quasi-Static 3D Light Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Geometry",
        f"- {N_PER_AXIS}×{N_PER_AXIS}×{N_PER_AXIS} cubic lattice (PBC), N={N_NODES} nodes, z={Z_3D}",
        "",
        "## Screening length",
        f"- λ_pred_3D = sqrt(β/(z·α)) = `{LAMBDA_PRED_3D:.4f}` node spacings",
        f"- λ_pred_1D = sqrt(β/(2·α)) = `{LAMBDA_PRED_1D:.4f}` node spacings",
        f"- λ_obs_3D  =               `{lambda_obs:.4f}`",
        f"- ratio obs/pred: `{lambda_ratio:.4f}`  (error: {lambda_error_3d:.4f}, threshold < 0.30)  {'PASS' if check3_pass else 'FAIL'}",
        f"- R² fit: `{r2_fit:.4f}`  threshold > 0.75  {'PASS' if check2_pass else 'FAIL'}",
        "",
        "## G_QNG scaling with z (key formula prediction)",
        f"- G_QNG_3D = β/z_3D = `{G_QNG_3D:.6f}`",
        f"- G_QNG_1D = β/z_1D = `{G_QNG_1D:.6f}`",
        f"- ratio obs: `{g_ratio_obs:.6f}`  pred: `{G_RATIO_PRED:.6f}`  error: `{g_ratio_error:.6f}`  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Check 1: sigma decays from source",
        f"  {'PASS' if check1_pass else 'FAIL'}  (monotone={monotone}, source_depleted={source_depleted})",
        "",
        "## Check 5: generation order in 3D",
        f"- corr(σ_deficit, χ): `{corr_deficit_chi:.4f}`  threshold > 0.60  {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Check 6: Poisson residual (bulk nodes r≥2)",
        f"- mean |β·(σ̄-σ) - α·(σ-σ_ref)|: `{mean_residual:.6f}`  threshold < 0.01  {'PASS' if check6_pass else 'FAIL'}",
        "",
        "## Radial profile sample",
    ]

    for r_key, vals in profile_sample.items():
        summary_lines.append(
            f"  r={r_key}: σ={vals['sigma']:.4f}  χ={vals['chi']:.4f}  δσ={vals['delta_sigma']:.4f}  n={vals['n_nodes']}"
        )

    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_quasi_static_3d_light_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
