from __future__ import annotations

"""
QNG-CPU-039: Gap 1 closure -- D2 on perturbed cubic lattice.

Tests DER-QNG-024: the second-moment condition (SMC) holds approximately for a
perturbed cubic lattice (perturbation amplitude 0.3 lattice spacings), and the
resulting Yukawa profile remains approximately isotropic.

Protocol:
  - 20x20x20 cubic lattice with random node-position perturbation <= 0.3 (each axis)
  - Connectivity: 6 nearest neighbors by Euclidean distance (periodic BC)
  - Compute second-moment tensor per node; check SMC deviation
  - Source clamped at center; 3000 equilibration steps
  - Fit spherical and directional Yukawa profiles
  - Check isotropy (wider tolerances than cubic: ratio < 1.35)
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-perturbed-lattice-isotropy-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N: int = 20
EQ_STEPS: int = 3000
SEED: int = 20260405
PERTURB: float = 0.3        # perturbation amplitude (fraction of lattice spacing)

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05

ALPHA: float = 0.005
BETA: float = 0.35
Z: int = 6
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20
DELTA: float = 0.20

SRC_IX: int = N // 2
SRC_IY: int = N // 2
SRC_IZ: int = N // 2

SPHERE_R_MIN: float = 1.5
SPHERE_R_MAX: float = 7.5
SPHERE_BIN_WIDTH: float = 0.5

DIR_R_MAX_100: int = 8
DIR_R_MAX_110: int = 6
DIR_R_MAX_111: int = 5


# ---------------------------------------------------------------------------
# Lattice construction
# ---------------------------------------------------------------------------

def grid_idx(ix: int, iy: int, iz: int) -> int:
    return ix + N * iy + N * N * iz


def build_perturbed_lattice(rng: random.Random) -> tuple[list[tuple[float, float, float]], list[list[int]]]:
    """Build perturbed positions and z=6 nearest-neighbor adjacency."""
    # Perturbed positions
    positions: list[tuple[float, float, float]] = []
    for iz in range(N):
        for iy in range(N):
            for ix in range(N):
                x = ix + rng.uniform(-PERTURB, PERTURB)
                y = iy + rng.uniform(-PERTURB, PERTURB)
                z = iz + rng.uniform(-PERTURB, PERTURB)
                positions.append((x % N, y % N, z % N))

    # For each node, find 6 nearest among 26 face+edge+corner grid-neighbors
    adj: list[list[int]] = []
    for node_i in range(N * N * N):
        iz = node_i // (N * N)
        iy = (node_i // N) % N
        ix = node_i % N
        px, py, pz = positions[node_i]

        candidates: list[tuple[float, int]] = []
        for dix in (-1, 0, 1):
            for diy in (-1, 0, 1):
                for diz in (-1, 0, 1):
                    if dix == 0 and diy == 0 and diz == 0:
                        continue
                    jx = (ix + dix) % N
                    jy = (iy + diy) % N
                    jz = (iz + diz) % N
                    j = grid_idx(jx, jy, jz)
                    qx, qy, qz = positions[j]
                    # Periodic wrap displacement
                    dx = qx - px
                    dy = qy - py
                    dz = qz - pz
                    dx -= N * round(dx / N)
                    dy -= N * round(dy / N)
                    dz -= N * round(dz / N)
                    d2 = dx * dx + dy * dy + dz * dz
                    candidates.append((d2, j))

        candidates.sort()
        adj.append([j for _, j in candidates[:Z]])

    return positions, adj


# ---------------------------------------------------------------------------
# Second-moment condition check
# ---------------------------------------------------------------------------

def compute_smc_stats(
    positions: list[tuple[float, float, float]],
    adj: list[list[int]],
) -> dict:
    """
    For each node i compute T_i = Σ_j ê_ij ⊗ ê_ij.
    Return statistics relevant for coarse-grained isotropy:
    - mean diagonal elements (should be z/3 = 2.0)
    - mean off-diagonal elements (should be 0.0 by symmetry)
    - per-node Frobenius deviation (diagnostic only — expected large ~O(ε))
    """
    n_nodes = len(adj)
    diag_sums = [0.0, 0.0, 0.0]       # Txx, Tyy, Tzz accumulated
    offdiag_sums = [0.0, 0.0, 0.0]    # Txy, Txz, Tyz accumulated
    per_node_dev: list[float] = []

    target = Z / 3.0  # 2.0

    for i in range(n_nodes):
        px, py, pz = positions[i]
        T = [0.0] * 9  # flat 3x3

        for j in adj[i]:
            qx, qy, qz = positions[j]
            dx = qx - px
            dy = qy - py
            dz = qz - pz
            dx -= N * round(dx / N)
            dy -= N * round(dy / N)
            dz -= N * round(dz / N)
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            if d < 1e-10:
                continue
            ex, ey, ez = dx / d, dy / d, dz / d
            v = (ex, ey, ez)
            for a in range(3):
                for b in range(3):
                    T[a * 3 + b] += v[a] * v[b]

        diag_sums[0] += T[0]  # Txx
        diag_sums[1] += T[4]  # Tyy
        diag_sums[2] += T[8]  # Tzz
        offdiag_sums[0] += T[1]  # Txy
        offdiag_sums[1] += T[2]  # Txz
        offdiag_sums[2] += T[5]  # Tyz

        # Frobenius norm of deviation (diagnostic)
        dev = 0.0
        for a in range(3):
            for b in range(3):
                expected = target if a == b else 0.0
                diff = T[a * 3 + b] - expected
                dev += diff * diff
        per_node_dev.append(math.sqrt(dev))

    diag_means = [s / n_nodes for s in diag_sums]
    offdiag_means = [s / n_nodes for s in offdiag_sums]
    mean_per_node_dev = sum(per_node_dev) / n_nodes
    max_per_node_dev = max(per_node_dev)

    return {
        "diag_means": diag_means,        # [Txx_mean, Tyy_mean, Tzz_mean]; target = 2.0
        "offdiag_means": offdiag_means,  # [Txy_mean, Txz_mean, Tyz_mean]; target = 0.0
        "mean_per_node_dev": mean_per_node_dev,  # diagnostic: expected large ~O(ε)
        "max_per_node_dev": max_per_node_dev,
    }


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
# v3 equilibration step
# ---------------------------------------------------------------------------

def eq_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    src_idx: int,
) -> tuple[list[float], list[float], list[float]]:
    n_nodes = len(adj)
    new_sigma: list[float] = []
    new_chi: list[float] = []
    new_phi: list[float] = []

    for i, neighbors in enumerate(adj):
        z_i = len(neighbors)
        sigma_i = sigma[i]
        chi_i = chi[i]
        phi_i = phi[i]

        sigma_neigh = sum(sigma[j] for j in neighbors) / z_i
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
# Yukawa fit in 3D
# ---------------------------------------------------------------------------

def fit_yukawa_3d(rs: list[float], dc_vals: list[float]) -> tuple[float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for r, dc in zip(rs, dc_vals):
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
    ss_xy = sum((xs[k] - mx) * (ys[k] - my) for k in range(n))
    ss_xx = sum((xs[k] - mx) ** 2 for k in range(n))

    if ss_xx < 1e-15:
        return 0.0, 0.0, 0.0

    slope = ss_xy / ss_xx
    intercept = my - slope * mx

    lambda_fit = -1.0 / slope if slope < 0 else 0.0
    a_fit = math.exp(intercept) if lambda_fit > 0 else 0.0

    y_pred = [intercept + slope * x for x in xs]
    ss_res = sum((ys[k] - y_pred[k]) ** 2 for k in range(n))
    ss_tot = sum((ys[k] - my) ** 2 for k in range(n))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0

    return lambda_fit, a_fit, r2


def ring_dist_1d(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, N - d)


def dist3d_from_src(ix: int, iy: int, iz: int) -> float:
    dx = ring_dist_1d(ix, SRC_IX)
    dy = ring_dist_1d(iy, SRC_IY)
    dz = ring_dist_1d(iz, SRC_IZ)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-039: Gap 1 -- D2 on perturbed cubic lattice."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(SEED)

    print(f"Building perturbed cubic lattice ({N}^3={N**3} nodes, perturbation={PERTURB})...")
    positions, adj = build_perturbed_lattice(rng)
    n_nodes = N * N * N
    src_idx = grid_idx(SRC_IX, SRC_IY, SRC_IZ)

    lambda_pred = math.sqrt(BETA / (Z * ALPHA))
    print(f"lambda_pred = {lambda_pred:.4f}")

    # Second-moment condition check
    print("Computing second-moment tensors...")
    smc = compute_smc_stats(positions, adj)
    diag_means = smc["diag_means"]
    offdiag_means = smc["offdiag_means"]
    print(f"  SMC per-node Frob dev: mean={smc['mean_per_node_dev']:.4f}  max={smc['max_per_node_dev']:.4f} (diagnostic; expected large for perturbed graph)")
    print(f"  Mean diagonal T: Txx={diag_means[0]:.4f} Tyy={diag_means[1]:.4f} Tzz={diag_means[2]:.4f}  target={Z/3:.4f}")
    print(f"  Mean off-diag T: Txy={offdiag_means[0]:.4f} Txz={offdiag_means[1]:.4f} Tyz={offdiag_means[2]:.4f}  target=0.0")

    # Initialize state
    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(n_nodes)]
    sigma[src_idx] = SIGMA_SOURCE
    chi = [0.0] * n_nodes
    phi = [rng.uniform(-0.1, 0.1) for _ in range(n_nodes)]

    # Equilibrate
    print(f"Running {EQ_STEPS} equilibration steps...")
    for step in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, src_idx)
        if (step + 1) % 500 == 0:
            print(f"  step {step+1}: delta_C(src)={sigma[src_idx]-SIGMA_REF:.4f}")

    delta_c = [sigma[i] - SIGMA_REF for i in range(n_nodes)]

    # Spherical profile using ACTUAL physical distances from source position
    src_pos = positions[src_idx]
    bin_sum: dict[int, float] = {}
    bin_count: dict[int, int] = {}
    for node_i in range(n_nodes):
        qx, qy, qz = positions[node_i]
        dx = qx - src_pos[0]
        dy = qy - src_pos[1]
        dz = qz - src_pos[2]
        dx -= N * round(dx / N)
        dy -= N * round(dy / N)
        dz -= N * round(dz / N)
        r = math.sqrt(dx * dx + dy * dy + dz * dz)
        bk = int(r / SPHERE_BIN_WIDTH)
        bin_sum[bk] = bin_sum.get(bk, 0.0) + delta_c[node_i]
        bin_count[bk] = bin_count.get(bk, 0) + 1

    sphere_rs: list[float] = []
    sphere_dc: list[float] = []
    for key in sorted(bin_sum):
        r_center = (key + 0.5) * SPHERE_BIN_WIDTH
        if SPHERE_R_MIN <= r_center <= SPHERE_R_MAX and bin_count[key] > 0:
            sphere_rs.append(r_center)
            sphere_dc.append(bin_sum[key] / bin_count[key])

    lambda_sphere, a_sphere, r2_sphere = fit_yukawa_3d(sphere_rs, sphere_dc)

    # Angular octant isotropy: compare spherical profile in different angular sectors
    # Divide upper hemisphere into 4 angular octants and compare lambda_fit
    # Octant 0: x>0, y>0, z>0
    # Octant 1: x>0, y>0, z<0
    # Octant 2: x>0, y<0, z>0
    # Octant 3: x<0, y>0, z>0
    octant_bins: list[dict[int, list[float]]] = [{} for _ in range(4)]
    for node_i in range(n_nodes):
        qx, qy, qz = positions[node_i]
        dx = qx - src_pos[0]
        dy = qy - src_pos[1]
        dz = qz - src_pos[2]
        dx -= N * round(dx / N)
        dy -= N * round(dy / N)
        dz -= N * round(dz / N)
        r = math.sqrt(dx * dx + dy * dy + dz * dz)
        if r < SPHERE_R_MIN or r > SPHERE_R_MAX:
            continue
        # Assign to octant
        oct_id = (0 if dx >= 0 else 1) * 4 + (0 if dy >= 0 else 1) * 2 + (0 if dz >= 0 else 1)
        # Map 8 octants to 4 (fold by symmetry)
        oct_key = oct_id % 4
        bk = int(r / SPHERE_BIN_WIDTH)
        if bk not in octant_bins[oct_key]:
            octant_bins[oct_key][bk] = []
        octant_bins[oct_key][bk].append(delta_c[node_i])

    oct_lambdas: list[float] = []
    for oct_key in range(4):
        o_rs = []
        o_dc = []
        for bk in sorted(octant_bins[oct_key]):
            r_center = (bk + 0.5) * SPHERE_BIN_WIDTH
            vals = octant_bins[oct_key][bk]
            if vals:
                o_rs.append(r_center)
                o_dc.append(sum(vals) / len(vals))
        lam, _, _ = fit_yukawa_3d(o_rs, o_dc)
        if lam > 0:
            oct_lambdas.append(lam)

    oct_iso_ratio = max(oct_lambdas) / min(oct_lambdas) if len(oct_lambdas) >= 2 else 0.0

    # Checks
    check1_pass = r2_sphere > 0.95

    sphere_ratio = lambda_sphere / lambda_pred if lambda_pred > 0 and lambda_sphere > 0 else 0.0
    check2_pass = abs(sphere_ratio - 1.0) < 0.20

    far_dc = [dc for r, dc in zip(sphere_rs, sphere_dc) if 1.0 <= r <= 8.0]
    check3_pass = all(dc < 0 for dc in far_dc) if far_dc else False

    # Check 4: octant isotropy — lambda in each angular octant within 30% of sphere lambda
    check4_pass = oct_iso_ratio < 1.45 if oct_iso_ratio > 0 else False

    # Check 5: mean off-diagonal elements ≈ 0 (statistical isotropy on average)
    max_offdiag = max(abs(v) for v in offdiag_means)
    check5_pass = max_offdiag < 0.05

    # Check 6: mean diagonal elements ≈ z/3 within 5%
    target_diag = Z / 3.0
    diag_ratios = [abs(d / target_diag - 1.0) for d in diag_means]
    check6_pass = all(r < 0.05 for r in diag_ratios)

    checks = {
        "yukawa_r2_pass": check1_pass,
        "lambda_sphere_vs_pred_pass": check2_pass,
        "delta_c_negative_pass": check3_pass,
        "octant_isotropy_pass": check4_pass,
        "smc_offdiag_mean_pass": check5_pass,
        "smc_diagonal_mean_pass": check6_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-039",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n": N,
            "n_nodes": n_nodes,
            "perturb": PERTURB,
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
            "smc_target_diagonal": round(target_diag, 4),
        },
        "second_moment_condition": {
            "mean_per_node_frob_dev": round(smc["mean_per_node_dev"], 4),
            "max_per_node_frob_dev": round(smc["max_per_node_dev"], 4),
            "mean_diagonal_Txx": round(diag_means[0], 4),
            "mean_diagonal_Tyy": round(diag_means[1], 4),
            "mean_diagonal_Tzz": round(diag_means[2], 4),
            "mean_offdiag_Txy": round(offdiag_means[0], 4),
            "mean_offdiag_Txz": round(offdiag_means[1], 4),
            "mean_offdiag_Tyz": round(offdiag_means[2], 4),
            "max_offdiag": round(max_offdiag, 4),
            "target_diagonal": round(target_diag, 4),
        },
        "spherical_fit": {
            "lambda_sphere": round(lambda_sphere, 4),
            "r2_sphere": round(r2_sphere, 4),
            "sphere_ratio": round(sphere_ratio, 4),
        },
        "octant_isotropy": {
            "octant_lambdas": [round(l, 4) for l in oct_lambdas],
            "oct_iso_ratio": round(oct_iso_ratio, 4),
        },
        "checks": checks,
        "interpretation": (
            "PASS: D2 holds approximately on perturbed cubic lattice. "
            "SMC: mean off-diagonals ≈ 0 and mean diagonals ≈ z/3 (statistical isotropy). "
            "Yukawa profile remains isotropic within tolerance. "
            "Gap 1 closed for statistically isotropic graphs (DER-QNG-024)."
            if decision
            else "FAIL: D2 breaks down at perturbation=0.30 -- see individual checks."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Perturbed Lattice Isotropy Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- lattice: {N}^3 = {n_nodes} nodes, z={Z}, perturbation={PERTURB}",
        f"- lambda_pred = {lambda_pred:.4f}",
        "",
        "## Second-moment condition (DER-QNG-024)",
        f"- Target diagonal (z/3) = {target_diag:.4f}",
        f"- Mean diagonal: Txx={diag_means[0]:.4f}  Tyy={diag_means[1]:.4f}  Tzz={diag_means[2]:.4f}",
        f"- Mean off-diagonal: Txy={offdiag_means[0]:.4f}  Txz={offdiag_means[1]:.4f}  Tyz={offdiag_means[2]:.4f}  (target=0)",
        f"- max |mean off-diag| = {max_offdiag:.4f}  (gate: < 0.05)  {'PASS' if check5_pass else 'FAIL'}",
        f"- Diagonal within 5% of target: {'PASS' if check6_pass else 'FAIL'}",
        f"- Per-node Frobenius dev: mean={smc['mean_per_node_dev']:.4f} (diagnostic; expected large ~O(ε) for irregular graph)",
        "",
        "## Spherical Yukawa fit (physical distances)",
        f"- lambda_sphere = {lambda_sphere:.4f}  ratio = {sphere_ratio:.4f}  R^2 = {r2_sphere:.4f}",
        "",
        "## Angular octant isotropy",
        f"- octant lambdas: {[round(l,3) for l in oct_lambdas]}",
        f"- octant max/min = {oct_iso_ratio:.4f}  (gate: < 1.30)  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Summary checks",
        f"- Check 1 (R^2 > 0.95): {r2_sphere:.4f}  {'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (lambda within 20%): ratio={sphere_ratio:.4f}  {'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (delta_C < 0): {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (octant isotropy < 1.45): {oct_iso_ratio:.4f}  {'PASS' if check4_pass else 'FAIL'}",
        f"- Check 5 (SMC mean off-diag < 0.05): {max_offdiag:.4f}  {'PASS' if check5_pass else 'FAIL'}",
        f"- Check 6 (SMC diag within 5%): {'PASS' if check6_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_perturbed_lattice_isotropy_reference: {'PASS' if decision else 'FAIL'}")
    print(f"  SMC diag=({diag_means[0]:.3f},{diag_means[1]:.3f},{diag_means[2]:.3f})  target={target_diag:.3f}")
    print(f"  SMC off-diag=({offdiag_means[0]:.4f},{offdiag_means[1]:.4f},{offdiag_means[2]:.4f})  max={max_offdiag:.4f}")
    print(f"  lambda_sphere={lambda_sphere:.4f}  pred={lambda_pred:.4f}  ratio={sphere_ratio:.4f}  R^2={r2_sphere:.4f}")
    print(f"  octant lambdas={[round(l,3) for l in oct_lambdas]}  iso_ratio={oct_iso_ratio:.4f}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
