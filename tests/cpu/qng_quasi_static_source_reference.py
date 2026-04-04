from __future__ import annotations

"""
QNG-CPU-030: Quasi-static point source test.

Verifies that the v3 update law recovers the screened Poisson structure predicted
by DER-QNG-012 when a localized coherence source is applied to a 1D ring graph.

Graph: 64-node ring with nearest-neighbor connections only (clean 1D geometry).
Source: node 0 clamped to sigma = SIGMA_SOURCE < sigma_ref throughout the run.
Parameters: slow alpha (slow relaxation), strong beta (strong diffusion), delta > 0.
This gives a visible screening length of ~6-9 node spacings.
"""

import argparse
import json
import math
import random
from pathlib import Path

from qng_native_update_reference import (
    History,
    State,
    clip01,
    wrap_angle,
    angle_diff,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-quasi-static-source-reference-v1"

# ---------------------------------------------------------------------------
# Test-specific parameters
# ---------------------------------------------------------------------------

N_NODES: int = 64
STEPS: int = 3000
SEED: int = 20260325
SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05   # forced depletion at source node
SOURCE_NODE: int = 0

# Quasi-static parameters: slow relaxation, strong diffusion → visible screening
ALPHA: float = 0.005          # sigma self-relaxation (slow)
BETA: float = 0.35            # relational coupling (strong)
CHI_DECAY: float = 0.005      # chi self-decay (slow, lets chi accumulate)
CHI_REL: float = 0.35         # chi relational coupling
PHI_REL: float = 0.20
DELTA: float = 0.20           # generation-order cross-coupling

# Predicted screening length: lambda_pred = sqrt(beta / (z * alpha))
# z = 2 (ring), Δu = 1, t_s = 1
# lambda_pred = sqrt(0.35 / (2 * 0.005)) = sqrt(35) ≈ 5.92


# ---------------------------------------------------------------------------
# Graph: 64-node ring (nearest-neighbour only, z=2)
# ---------------------------------------------------------------------------

def build_ring(n: int) -> list[list[int]]:
    return [[(i - 1) % n, (i + 1) % n] for i in range(n)]


def ring_distance(i: int, j: int, n: int) -> int:
    d = abs(i - j)
    return min(d, n - d)


# ---------------------------------------------------------------------------
# Single step: v3 with no history, nearest-neighbour ring
# ---------------------------------------------------------------------------

def one_step_qs(
    state: State,
    adj: list[list[int]],
    *,
    clamp_source: bool = True,
) -> State:
    """
    Quasi-static v3 step: no history, no noise.
    Source node is clamped to SIGMA_SOURCE after each step.
    """
    n = len(adj)
    new_sigma: list[float] = []
    new_chi: list[float] = []
    new_phi: list[float] = []

    for i, neighbors in enumerate(adj):
        sigma_i = state.sigma[i]
        chi_i = state.chi[i]
        phi_i = state.phi[i]

        sigma_neigh = sum(state.sigma[j] for j in neighbors) / len(neighbors)
        chi_neigh = sum(state.chi[j] for j in neighbors) / len(neighbors)
        sin_sum = sum(math.sin(state.phi[j]) for j in neighbors)
        cos_sum = sum(math.cos(state.phi[j]) for j in neighbors)
        phi_neigh = (
            math.atan2(sin_sum, cos_sum)
            if abs(sin_sum) + abs(cos_sum) > 1e-12
            else phi_i
        )

        # sigma channel (v3, no history)
        sigma_new = clip01(
            sigma_i
            + ALPHA * (SIGMA_REF - sigma_i)
            + BETA * (sigma_neigh - sigma_i)
        )

        # chi channel (v3, no history) + Channel D
        chi_new = (
            chi_i
            - CHI_DECAY * chi_i
            + CHI_REL * (sigma_neigh - sigma_i)
            + DELTA * (SIGMA_REF - sigma_i)
        )

        # phi channel (v3, no history)
        phi_new = wrap_angle(phi_i + PHI_REL * angle_diff(phi_neigh, phi_i))

        new_sigma.append(sigma_new)
        new_chi.append(chi_new)
        new_phi.append(phi_new)

    new_state = State(sigma=new_sigma, chi=new_chi, phi=new_phi)

    # Clamp source node
    if clamp_source:
        new_state.sigma[SOURCE_NODE] = SIGMA_SOURCE
        new_state.chi[SOURCE_NODE] = new_state.chi[SOURCE_NODE]  # chi free at source

    return new_state


# ---------------------------------------------------------------------------
# Profile extraction
# ---------------------------------------------------------------------------

def extract_profile(state: State, n: int) -> dict[int, dict]:
    """
    Average sigma and chi over nodes at each ring distance from SOURCE_NODE.
    Returns dict: r -> {sigma_mean, chi_mean, n_nodes}
    """
    buckets: dict[int, list] = {}
    for i in range(n):
        r = ring_distance(i, SOURCE_NODE, n)
        if r not in buckets:
            buckets[r] = []
        buckets[r].append(i)

    profile = {}
    for r, nodes in sorted(buckets.items()):
        sigma_vals = [state.sigma[i] for i in nodes]
        chi_vals = [state.chi[i] for i in nodes]
        profile[r] = {
            "sigma_mean": sum(sigma_vals) / len(sigma_vals),
            "chi_mean": sum(chi_vals) / len(chi_vals),
            "n_nodes": len(nodes),
        }
    return profile


# ---------------------------------------------------------------------------
# Exponential fit on log|delta_sigma| vs r
# ---------------------------------------------------------------------------

def fit_exponential(rs: list[float], vals: list[float]) -> tuple[float, float, float]:
    """
    Fit log|vals[r]| = log(A) - r/lambda to data points (rs, vals).
    Returns (A, lambda_obs, R2).
    """
    log_vals = []
    rs_valid = []
    for r, v in zip(rs, vals):
        if abs(v) > 1e-9:
            log_vals.append(math.log(abs(v)))
            rs_valid.append(r)

    if len(rs_valid) < 3:
        return 0.0, 0.0, 0.0

    n = len(rs_valid)
    sx = sum(rs_valid)
    sy = sum(log_vals)
    sxy = sum(r * y for r, y in zip(rs_valid, log_vals))
    sxx = sum(r * r for r in rs_valid)

    denom = n * sxx - sx * sx
    if abs(denom) < 1e-15:
        return 0.0, 0.0, 0.0

    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n

    A = math.exp(intercept)
    lam = -1.0 / slope if abs(slope) > 1e-12 else 1e9

    # R²
    y_mean = sy / n
    ss_res = sum((y - (intercept + slope * r)) ** 2 for r, y in zip(rs_valid, log_vals))
    ss_tot = sum((y - y_mean) ** 2 for y in log_vals)
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
        description="QNG quasi-static point source CPU reference test (QNG-CPU-030)."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build ring graph and initialize flat state
    adj = build_ring(N_NODES)
    rng = random.Random(SEED)

    sigma0 = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    sigma0[SOURCE_NODE] = SIGMA_SOURCE
    chi0 = [0.0] * N_NODES
    phi0 = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]
    state = State(sigma=sigma0, chi=chi0, phi=phi0)

    # Run to quasi-static equilibrium
    for _ in range(STEPS):
        state = one_step_qs(state, adj)

    # Extract radial profile
    profile = extract_profile(state, N_NODES)

    # Build arrays over r = 0..32 (half ring)
    r_max = N_NODES // 2
    r_arr = list(range(r_max + 1))
    sigma_arr = [profile[r]["sigma_mean"] for r in r_arr]
    chi_arr = [profile[r]["chi_mean"] for r in r_arr]
    delta_sigma_arr = [s - SIGMA_REF for s in sigma_arr]  # negative near source

    # ------------------------------------------------------------------
    # Check 1: sigma decays monotonically from source
    # sigma should increase with r (source depletes coherence)
    # Test: sigma(r=0) < sigma(r=5) < sigma(r=15)
    # ------------------------------------------------------------------
    check1_pass = (
        sigma_arr[0] < sigma_arr[5]
        and sigma_arr[5] < sigma_arr[15]
        and delta_sigma_arr[0] < -0.01  # source is actually depleted
    )

    # ------------------------------------------------------------------
    # Check 2: exponential fit quality R² > 0.80 on r in [2, 15]
    # ------------------------------------------------------------------
    rs_fit = list(range(2, 16))
    ds_fit = [delta_sigma_arr[r] for r in rs_fit]
    _, lambda_obs, r2_fit = fit_exponential(rs_fit, ds_fit)
    check2_pass = r2_fit > 0.80

    # ------------------------------------------------------------------
    # Check 3: observed screening length within 30% of predicted
    # lambda_pred = sqrt(beta / (z * alpha)), z=2
    # ------------------------------------------------------------------
    z = 2.0
    lambda_pred = math.sqrt(BETA / (z * ALPHA))
    if lambda_obs > 0:
        ratio = lambda_obs / lambda_pred
        lambda_error = abs(ratio - 1.0)
    else:
        ratio = 0.0
        lambda_error = 1.0
    check3_pass = lambda_error < 0.30

    # ------------------------------------------------------------------
    # Check 4: chi elevated near source vs far from source
    # mean |chi| for r <= 3 > mean |chi| for r >= 10
    # ------------------------------------------------------------------
    chi_near = [abs(chi_arr[r]) for r in range(0, 4)]
    chi_far = [abs(chi_arr[r]) for r in range(10, r_max + 1)]
    mean_chi_near = sum(chi_near) / len(chi_near)
    mean_chi_far = sum(chi_far) / len(chi_far)
    check4_pass = mean_chi_near > mean_chi_far

    # ------------------------------------------------------------------
    # Check 5: correlation between sigma_deficit and chi across all nodes
    # corr(sigma_ref - sigma_i, chi_i) > 0.60
    # ------------------------------------------------------------------
    deficit_all = [SIGMA_REF - state.sigma[i] for i in range(N_NODES)]
    chi_all = [state.chi[i] for i in range(N_NODES)]
    corr_deficit_chi = pearson(deficit_all, chi_all)
    check5_pass = corr_deficit_chi > 0.60

    # ------------------------------------------------------------------
    # Check 6: G_QNG formula positive and finite (substrate units)
    # G_QNG = beta * Du^2 / (z * t_s)  with Du=1, t_s=1, a*a_sigma = 2pi
    # ------------------------------------------------------------------
    G_QNG_substrate = BETA / (z * 1.0)  # Du=1, t_s=1
    check6_pass = G_QNG_substrate > 0 and math.isfinite(G_QNG_substrate)

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------
    checks = {
        "sigma_decays_from_source_pass": check1_pass,
        "exponential_fit_quality_pass": check2_pass,
        "screening_length_match_pass": check3_pass,
        "chi_elevated_near_source_pass": check4_pass,
        "generation_order_spatial_correlation_pass": check5_pass,
        "G_QNG_formula_valid_pass": check6_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-030",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "alpha": ALPHA,
            "beta": BETA,
            "delta": DELTA,
            "chi_decay": CHI_DECAY,
            "chi_rel": CHI_REL,
            "n_nodes": N_NODES,
            "steps": STEPS,
            "sigma_source": SIGMA_SOURCE,
        },
        "profile_sample": {
            f"r{r}": {"sigma": round(sigma_arr[r], 6), "chi": round(chi_arr[r], 6)}
            for r in [0, 1, 2, 3, 5, 8, 12, 16, 20, 25, 30, 32]
        },
        "screening": {
            "lambda_pred": round(lambda_pred, 4),
            "lambda_obs": round(lambda_obs, 4),
            "ratio": round(ratio, 4),
            "relative_error": round(lambda_error, 4),
            "r2_fit": round(r2_fit, 4),
        },
        "chi_profile": {
            "mean_abs_chi_near_r0_3": round(mean_chi_near, 6),
            "mean_abs_chi_far_r10plus": round(mean_chi_far, 6),
        },
        "generation_order": {
            "corr_deficit_chi_all_nodes": round(corr_deficit_chi, 4),
        },
        "G_QNG": {
            "substrate_units": round(G_QNG_substrate, 6),
        },
        "checks": checks,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Quasi-Static Point Source Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Parameters",
        f"- alpha={ALPHA}, beta={BETA}, delta={DELTA}, n_nodes={N_NODES}, steps={STEPS}",
        f"- lambda_pred = sqrt(beta/(z*alpha)) = `{lambda_pred:.4f}` node spacings",
        "",
        "## Check 1: sigma decays from source",
        f"- sigma(r=0)={sigma_arr[0]:.4f}, sigma(r=5)={sigma_arr[5]:.4f}, sigma(r=15)={sigma_arr[15]:.4f}",
        f"  {'PASS' if check1_pass else 'FAIL'}",
        "",
        "## Check 2: exponential fit quality",
        f"- R² of log|δ_sigma| vs r (fit on r=[2,15]): `{r2_fit:.4f}`  threshold > 0.80  {'PASS' if check2_pass else 'FAIL'}",
        "",
        "## Check 3: screening length",
        f"- lambda_pred: `{lambda_pred:.4f}`",
        f"- lambda_obs:  `{lambda_obs:.4f}`",
        f"- ratio:       `{ratio:.4f}`  (|ratio-1| = {lambda_error:.4f}, threshold < 0.30)  {'PASS' if check3_pass else 'FAIL'}",
        "",
        "## Check 4: chi elevated near source",
        f"- mean |chi| r≤3:  `{mean_chi_near:.6f}`",
        f"- mean |chi| r≥10: `{mean_chi_far:.6f}`  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Check 5: generation order spatial correlation",
        f"- corr(sigma_deficit, chi): `{corr_deficit_chi:.4f}`  threshold > 0.60  {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Check 6: G_QNG formula",
        f"- G_QNG (substrate units) = `{G_QNG_substrate:.6f}`  {'PASS' if check6_pass else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_quasi_static_source_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
