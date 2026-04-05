from __future__ import annotations

"""
QNG-CPU-037: Gap 1 -- 3D isotropy on a cubic lattice.

Tests Assumption D2 (AX-QNG-004): the QNG discrete graph Laplacian on a cubic lattice
(z=6) produces an isotropic screened Poisson equation in 3D.

Protocol:
  - 20x20x20 cubic lattice (8000 nodes), z=6 neighbors
  - Source clamped at center node (10,10,10): sigma_source = 0.05
  - 3000 equilibration steps (v3 quasi-static update law)
  - Fit 3D Yukawa: delta_C(r) ~ A * exp(-r/lambda) / r
  - Check: lambda_sphere ~= lambda_pred = sqrt(beta/(z*alpha)) ~= 3.416
  - Check: isotropy -- same lambda in (1,0,0), (1,1,0), (1,1,1) directions
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-3d-isotropy-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N: int = 20            # lattice dimension per axis (20^3 = 8000 nodes)
EQ_STEPS: int = 3000
SEED: int = 20260405

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05

ALPHA: float = 0.005
BETA: float = 0.35
Z: int = 6             # cubic lattice: 6 neighbors
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20
DELTA: float = 0.20

SRC_X: int = N // 2   # source node coordinates
SRC_Y: int = N // 2
SRC_Z: int = N // 2

SPHERE_R_MIN: float = 1.5
SPHERE_R_MAX: float = 7.5
SPHERE_BIN_WIDTH: float = 0.5

DIR_R_MAX_100: int = 8    # along (1,0,0): up to r=8
DIR_R_MAX_110: int = 6    # along (1,1,0): up to r=6 (actual dist r*sqrt(2) ~= 8.5)
DIR_R_MAX_111: int = 5    # along (1,1,1): up to r=5 (actual dist r*sqrt(3) ~= 8.7)


# ---------------------------------------------------------------------------
# Lattice construction
# ---------------------------------------------------------------------------

def idx(x: int, y: int, z: int) -> int:
    return x + N * y + N * N * z


def build_cubic_adj() -> list[list[int]]:
    adj: list[list[int]] = []
    for z in range(N):
        for y in range(N):
            for x in range(N):
                adj.append([
                    idx((x + 1) % N, y, z),
                    idx((x - 1) % N, y, z),
                    idx(x, (y + 1) % N, z),
                    idx(x, (y - 1) % N, z),
                    idx(x, y, (z + 1) % N),
                    idx(x, y, (z - 1) % N),
                ])
    return adj


def node_coords() -> list[tuple[int, int, int]]:
    """Returns (x,y,z) for each node index."""
    coords = []
    for z in range(N):
        for y in range(N):
            for x in range(N):
                coords.append((x, y, z))
    return coords


def ring_dist_1d(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, N - d)


def dist3d(x: int, y: int, z: int) -> float:
    dx = ring_dist_1d(x, SRC_X)
    dy = ring_dist_1d(y, SRC_Y)
    dz = ring_dist_1d(z, SRC_Z)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def wrap_angle(x: float) -> float:
    y = (x + math.pi) % (2.0 * math.pi) - math.pi
    return y if y > -math.pi else y + 2.0 * math.pi


def angle_diff(a: float, b: float) -> float:
    return wrap_angle(a - b)


# ---------------------------------------------------------------------------
# v3 equilibration step (quasi-static, no channel E)
# ---------------------------------------------------------------------------

def eq_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    src_idx: int,
) -> tuple[list[float], list[float], list[float]]:
    n_nodes = len(adj)
    z_eff = Z  # all nodes have z=6 neighbors
    new_sigma: list[float] = []
    new_chi: list[float] = []
    new_phi: list[float] = []

    for i, neighbors in enumerate(adj):
        sigma_i = sigma[i]
        chi_i = chi[i]
        phi_i = phi[i]

        sigma_neigh = sum(sigma[j] for j in neighbors) / z_eff
        sin_sum = sum(math.sin(phi[j]) for j in neighbors)
        cos_sum = sum(math.cos(phi[j]) for j in neighbors)
        phi_neigh = (
            math.atan2(sin_sum, cos_sum)
            if abs(sin_sum) + abs(cos_sum) > 1e-12
            else phi_i
        )

        sigma_new = clip01(
            sigma_i
            + ALPHA * (SIGMA_REF - sigma_i)
            + BETA * (sigma_neigh - sigma_i)
        )
        chi_new = (
            chi_i
            - CHI_DECAY * chi_i
            + CHI_REL * (sigma_neigh - sigma_i)
            + DELTA * (SIGMA_REF - sigma_i)
        )
        phi_new = wrap_angle(phi_i + PHI_REL * angle_diff(phi_neigh, phi_i))

        new_sigma.append(sigma_new)
        new_chi.append(chi_new)
        new_phi.append(phi_new)

    new_sigma[src_idx] = SIGMA_SOURCE
    return new_sigma, new_chi, new_phi


# ---------------------------------------------------------------------------
# Yukawa fit in 3D: fit log(r * |delta_C(r)|) = log(A) - r/lambda
# Returns (lambda_fit, A_fit, r_squared)
# ---------------------------------------------------------------------------

def fit_yukawa_3d(
    rs: list[float], delta_c_vals: list[float]
) -> tuple[float, float, float]:
    """
    Fit 3D Yukawa profile: delta_C(r) ~ A * exp(-r/lambda) / r.
    Input: list of (r, delta_C) pairs.
    """
    xs: list[float] = []
    ys: list[float] = []
    for r, dc in zip(rs, delta_c_vals):
        if r > 1e-9 and abs(dc) > 1e-10:
            val = r * abs(dc)
            if val > 1e-15:
                xs.append(r)
                ys.append(math.log(val))

    n = len(xs)
    if n < 3:
        return 0.0, 0.0, 0.0

    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    ss_xx = sum((xs[i] - mx) ** 2 for i in range(n))

    if ss_xx < 1e-15:
        return 0.0, 0.0, 0.0

    slope = ss_xy / ss_xx
    intercept = my - slope * mx

    lambda_fit = -1.0 / slope if slope < 0 else 0.0
    a_fit = math.exp(intercept) if lambda_fit > 0 else 0.0

    y_pred = [intercept + slope * x for x in xs]
    ss_res = sum((ys[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((ys[i] - my) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0

    return lambda_fit, a_fit, r2


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-037: 3D isotropy test on cubic lattice."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building 3D cubic lattice ({N}^3 = {N**3} nodes, z={Z})...")
    adj = build_cubic_adj()
    coords = node_coords()
    src_idx = idx(SRC_X, SRC_Y, SRC_Z)
    n_nodes = N * N * N

    # Predicted screening length
    lambda_pred = math.sqrt(BETA / (Z * ALPHA))
    print(f"lambda_pred = {lambda_pred:.4f}  (beta={BETA}, z={Z}, alpha={ALPHA})")

    # Initialize
    rng = random.Random(SEED)
    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(n_nodes)]
    sigma[src_idx] = SIGMA_SOURCE
    chi = [0.0] * n_nodes
    phi = [rng.uniform(-0.1, 0.1) for _ in range(n_nodes)]

    # Equilibrate
    print(f"Running {EQ_STEPS} equilibration steps...")
    for step in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, src_idx)
        if (step + 1) % 500 == 0:
            src_delta = sigma[src_idx] - SIGMA_REF
            print(f"  step {step+1}: delta_C(src)={src_delta:.4f}")

    # Compute delta_C profile
    delta_c = [sigma[i] - SIGMA_REF for i in range(n_nodes)]

    # -------------------------------------------------------------------
    # Spherically averaged profile
    # -------------------------------------------------------------------
    # Bin by distance from source
    bin_sum: dict[int, float] = {}
    bin_count: dict[int, int] = {}
    for i in range(n_nodes):
        x, y, z = coords[i]
        r = dist3d(x, y, z)
        bin_key = int(r / SPHERE_BIN_WIDTH)
        bin_sum[bin_key] = bin_sum.get(bin_key, 0.0) + delta_c[i]
        bin_count[bin_key] = bin_count.get(bin_key, 0) + 1

    sphere_rs: list[float] = []
    sphere_dc: list[float] = []
    for key in sorted(bin_sum):
        r_center = (key + 0.5) * SPHERE_BIN_WIDTH
        if SPHERE_R_MIN <= r_center <= SPHERE_R_MAX and bin_count[key] > 0:
            sphere_rs.append(r_center)
            sphere_dc.append(bin_sum[key] / bin_count[key])

    lambda_sphere, a_sphere, r2_sphere = fit_yukawa_3d(sphere_rs, sphere_dc)

    # -------------------------------------------------------------------
    # Directional profiles
    # -------------------------------------------------------------------

    # (1,0,0) direction
    rs_100: list[float] = []
    dc_100: list[float] = []
    for r in range(1, DIR_R_MAX_100 + 1):
        x = (SRC_X + r) % N
        node = idx(x, SRC_Y, SRC_Z)
        rs_100.append(float(r))
        dc_100.append(delta_c[node])

    lambda_100, a_100, r2_100 = fit_yukawa_3d(rs_100, dc_100)

    # (1,1,0) direction — actual distance r*sqrt(2)
    rs_110: list[float] = []
    dc_110: list[float] = []
    for r in range(1, DIR_R_MAX_110 + 1):
        x = (SRC_X + r) % N
        y = (SRC_Y + r) % N
        node = idx(x, y, SRC_Z)
        rs_110.append(r * math.sqrt(2.0))
        dc_110.append(delta_c[node])

    lambda_110, a_110, r2_110 = fit_yukawa_3d(rs_110, dc_110)

    # (1,1,1) direction — actual distance r*sqrt(3)
    rs_111: list[float] = []
    dc_111: list[float] = []
    for r in range(1, DIR_R_MAX_111 + 1):
        x = (SRC_X + r) % N
        y = (SRC_Y + r) % N
        z_c = (SRC_Z + r) % N
        node = idx(x, y, z_c)
        rs_111.append(r * math.sqrt(3.0))
        dc_111.append(delta_c[node])

    lambda_111, a_111, r2_111 = fit_yukawa_3d(rs_111, dc_111)

    # -------------------------------------------------------------------
    # Checks
    # -------------------------------------------------------------------

    # Check 1: Yukawa fit quality for spherical average
    check1_pass = r2_sphere > 0.97

    # Check 2: lambda_sphere within 15% of lambda_pred
    if lambda_pred > 0 and lambda_sphere > 0:
        sphere_ratio = lambda_sphere / lambda_pred
        check2_pass = abs(sphere_ratio - 1.0) < 0.15
    else:
        sphere_ratio = 0.0
        check2_pass = False

    # Check 3: isotropy -- max/min of directional lambdas < 1.20
    dir_lambdas = [l for l in [lambda_100, lambda_110, lambda_111] if l > 0]
    if len(dir_lambdas) >= 2:
        iso_ratio = max(dir_lambdas) / min(dir_lambdas)
        check3_pass = iso_ratio < 1.20
    else:
        iso_ratio = 0.0
        check3_pass = False

    # Check 4: each directional lambda within 20% of lambda_pred
    check4_details = {}
    for name, lam in [("100", lambda_100), ("110", lambda_110), ("111", lambda_111)]:
        if lambda_pred > 0 and lam > 0:
            ratio = lam / lambda_pred
            check4_details[name] = abs(ratio - 1.0) < 0.20
        else:
            check4_details[name] = False
    check4_pass = all(check4_details.values())

    # Check 5: delta_C < 0 in far field (coherence depletion)
    far_field_dc = [dc for r, dc in zip(sphere_rs, sphere_dc) if 1.0 <= r <= 8.0]
    check5_pass = all(dc < 0 for dc in far_field_dc) if far_field_dc else False

    checks = {
        "yukawa_r2_sphere_pass": check1_pass,
        "lambda_sphere_vs_pred_pass": check2_pass,
        "isotropy_ratio_pass": check3_pass,
        "each_direction_vs_pred_pass": check4_pass,
        "delta_c_negative_pass": check5_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-037",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n": N,
            "n_nodes": n_nodes,
            "eq_steps": EQ_STEPS,
            "alpha": ALPHA,
            "beta": BETA,
            "z": Z,
            "delta": DELTA,
            "sigma_ref": SIGMA_REF,
            "sigma_source": SIGMA_SOURCE,
        },
        "predictions": {
            "lambda_pred": round(lambda_pred, 4),
        },
        "spherical_fit": {
            "lambda_sphere": round(lambda_sphere, 4),
            "a_sphere": round(a_sphere, 6),
            "r2_sphere": round(r2_sphere, 6),
            "sphere_ratio": round(sphere_ratio, 4),
            "n_bins": len(sphere_rs),
        },
        "directional_fits": {
            "100": {
                "lambda": round(lambda_100, 4),
                "r2": round(r2_100, 4),
                "ratio_vs_pred": round(lambda_100 / lambda_pred, 4) if lambda_pred > 0 and lambda_100 > 0 else 0,
            },
            "110": {
                "lambda": round(lambda_110, 4),
                "r2": round(r2_110, 4),
                "ratio_vs_pred": round(lambda_110 / lambda_pred, 4) if lambda_pred > 0 and lambda_110 > 0 else 0,
            },
            "111": {
                "lambda": round(lambda_111, 4),
                "r2": round(r2_111, 4),
                "ratio_vs_pred": round(lambda_111 / lambda_pred, 4) if lambda_pred > 0 and lambda_111 > 0 else 0,
            },
        },
        "isotropy": {
            "dir_lambdas": {
                "100": round(lambda_100, 4),
                "110": round(lambda_110, 4),
                "111": round(lambda_111, 4),
            },
            "max_min_ratio": round(iso_ratio, 4),
        },
        "checks": checks,
        "check4_per_direction": check4_details,
        "interpretation": (
            "PASS: 3D cubic QNG substrate produces isotropic screened Poisson profile. "
            "Assumption D2 numerically supported for z=6 cubic lattice. "
            "Gap 1 partially closed for cubic graph geometry."
            if decision
            else "FAIL: 3D isotropy not confirmed -- see individual checks."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG 3D Isotropy Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- lattice: {N}^3 = {n_nodes} nodes, z={Z} (cubic)",
        f"- lambda_pred = {lambda_pred:.4f}",
        "",
        "## Spherically averaged Yukawa fit",
        f"- lambda_sphere = {lambda_sphere:.4f}",
        f"- ratio lambda_sphere / lambda_pred = {sphere_ratio:.4f}",
        f"- R^2 = {r2_sphere:.4f}",
        "",
        "## Directional fits",
        "",
        "| direction | lambda_fit | ratio/pred | R^2   | check4 |",
        "|-----------|------------|------------|-------|--------|",
        f"| (1,0,0)   | {lambda_100:.4f}    | {lambda_100/lambda_pred:.4f}       | {r2_100:.4f} | {'PASS' if check4_details.get('100') else 'FAIL'} |",
        f"| (1,1,0)   | {lambda_110:.4f}    | {lambda_110/lambda_pred:.4f}       | {r2_110:.4f} | {'PASS' if check4_details.get('110') else 'FAIL'} |",
        f"| (1,1,1)   | {lambda_111:.4f}    | {lambda_111/lambda_pred:.4f}       | {r2_111:.4f} | {'PASS' if check4_details.get('111') else 'FAIL'} |",
        "",
        "## Isotropy",
        f"- max/min lambda = {iso_ratio:.4f}  (gate: < 1.20)  {'PASS' if check3_pass else 'FAIL'}",
        "",
        "## Summary checks",
        f"- Check 1 (Yukawa R^2 > 0.97): {r2_sphere:.4f}  {'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (lambda within 15% of pred): ratio={sphere_ratio:.4f}  {'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (isotropy max/min < 1.20): {iso_ratio:.4f}  {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (each dir within 20% of pred): {'PASS' if check4_pass else 'FAIL'}",
        f"- Check 5 (delta_C < 0 in far field): {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_3d_isotropy_reference: {'PASS' if decision else 'FAIL'}")
    print(f"  lambda_sphere={lambda_sphere:.4f}  pred={lambda_pred:.4f}  ratio={sphere_ratio:.4f}")
    print(f"  R^2_sphere={r2_sphere:.4f}")
    print(f"  lambdas: (100)={lambda_100:.4f}  (110)={lambda_110:.4f}  (111)={lambda_111:.4f}")
    print(f"  isotropy max/min={iso_ratio:.4f}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
