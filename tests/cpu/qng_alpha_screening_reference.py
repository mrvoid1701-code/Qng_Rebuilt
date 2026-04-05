from __future__ import annotations

"""
QNG-CPU-036: Step N7 — Alpha-screening: lambda_screen proportional to 1/sqrt(alpha).

Tests the scaling prediction from DER-QNG-018 and DER-QNG-020:
    lambda_screen = sqrt(beta / (z * alpha))  =>  lambda ∝ alpha^(-1/2)

For each alpha in {0.001, 0.002, 0.005, 0.010, 0.020}, runs quasi-static v3
equilibration on a 128-node ring (beta=0.35 fixed), fits the exponential sigma
profile, and verifies lambda_fit * sqrt(alpha) = sqrt(beta/z) = const.

Design:
  - Fixed: beta=0.35, z=2, N=128, 5000 steps, source at node 0 (sigma=0.05)
  - For each alpha: fit |delta_C(r)| ~ A * exp(-r/lambda_fit) over r in [3, 50]
  - Check: max/min(lambda_fit * sqrt(alpha)) < 1.20
  - Check: log-log slope of lambda vs alpha within 0.08 of -0.5
  - Check: each lambda_fit within 15% of lambda_pred = sqrt(beta/(z*alpha))
  - Check: lambda_fit monotone decreasing in alpha
  - Check: R^2 > 0.99 for all fits
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-alpha-screening-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_NODES: int = 128
EQ_STEPS: int = 5000
SEED: int = 20260405

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05
SOURCE_NODE: int = 0

BETA: float = 0.35
Z: int = 2
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20
DELTA: float = 0.20

ALPHA_VALUES: list[float] = [0.001, 0.002, 0.005, 0.010, 0.020]
FIT_R_MIN: int = 3
FIT_R_MAX: int = 50


# ---------------------------------------------------------------------------
# Graph (ring)
# ---------------------------------------------------------------------------

def build_ring(n: int) -> list[list[int]]:
    return [[(i - 1) % n, (i + 1) % n] for i in range(n)]


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
# v3 quasi-static equilibration step
# ---------------------------------------------------------------------------

def eq_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    alpha: float,
) -> tuple[list[float], list[float], list[float]]:
    n = len(adj)
    new_sigma: list[float] = []
    new_chi: list[float] = []
    new_phi: list[float] = []

    for i, neighbors in enumerate(adj):
        sigma_i = sigma[i]
        chi_i = chi[i]
        phi_i = phi[i]

        sigma_neigh = sum(sigma[j] for j in neighbors) / len(neighbors)
        sin_sum = sum(math.sin(phi[j]) for j in neighbors)
        cos_sum = sum(math.cos(phi[j]) for j in neighbors)
        phi_neigh = (
            math.atan2(sin_sum, cos_sum)
            if abs(sin_sum) + abs(cos_sum) > 1e-12
            else phi_i
        )

        sigma_new = clip01(
            sigma_i
            + alpha * (SIGMA_REF - sigma_i)
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

    new_sigma[SOURCE_NODE] = SIGMA_SOURCE
    return new_sigma, new_chi, new_phi


# ---------------------------------------------------------------------------
# Exponential fit: log-linear regression for |delta_C(r)| ~ A * exp(-r/lambda)
# ---------------------------------------------------------------------------

def fit_screening_length(delta_c: list[float]) -> tuple[float, float, float]:
    """
    Returns (lambda_fit, A_fit, r_squared) from log-linear regression.
    """
    rs = list(range(FIT_R_MIN, min(FIT_R_MAX + 1, len(delta_c))))
    ys = []
    xs = []
    for r in rs:
        val = abs(delta_c[r])
        if val > 1e-10:
            ys.append(math.log(val))
            xs.append(float(r))

    if len(xs) < 3:
        return 0.0, 0.0, 0.0

    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    ss_xx = sum((xs[i] - mx) ** 2 for i in range(n))

    if ss_xx < 1e-15:
        return 0.0, 0.0, 0.0

    slope = ss_xy / ss_xx          # slope = -1/lambda
    intercept = my - slope * mx    # intercept = log(A)

    lambda_fit = -1.0 / slope if slope < 0 else 0.0
    a_fit = math.exp(intercept)

    y_pred = [intercept + slope * x for x in xs]
    ss_res = sum((ys[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((ys[i] - my) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0

    return lambda_fit, a_fit, r2


# ---------------------------------------------------------------------------
# Log-log slope: least-squares fit of log(lambda_fit) vs log(alpha)
# ---------------------------------------------------------------------------

def loglog_slope(alphas: list[float], lambdas: list[float]) -> float:
    log_a = [math.log(a) for a in alphas]
    log_l = [math.log(l) for l in lambdas]
    n = len(log_a)
    mx = sum(log_a) / n
    my = sum(log_l) / n
    ss_xy = sum((log_a[i] - mx) * (log_l[i] - my) for i in range(n))
    ss_xx = sum((log_a[i] - mx) ** 2 for i in range(n))
    return ss_xy / ss_xx if ss_xx > 1e-15 else 0.0


# ---------------------------------------------------------------------------
# Run one simulation at given alpha
# ---------------------------------------------------------------------------

def run_alpha(alpha: float) -> dict:
    adj = build_ring(N_NODES)
    rng = random.Random(SEED)

    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    sigma[SOURCE_NODE] = SIGMA_SOURCE
    chi = [0.0] * N_NODES
    phi = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]

    for _ in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, alpha)

    # Compute delta_C profile by ring distance from source
    half = N_NODES // 2
    delta_c_by_r = [0.0] * (half + 1)
    count_by_r = [0] * (half + 1)
    for i in range(N_NODES):
        r = min(i, N_NODES - i)
        if r <= half:
            delta_c_by_r[r] += sigma[i] - SIGMA_REF
            count_by_r[r] += 1
    delta_c_profile = [
        delta_c_by_r[r] / count_by_r[r] if count_by_r[r] > 0 else 0.0
        for r in range(half + 1)
    ]

    lambda_pred = math.sqrt(BETA / (Z * alpha))
    lambda_fit, a_fit, r2 = fit_screening_length(delta_c_profile)

    invariant_fit = lambda_fit * math.sqrt(alpha) if lambda_fit > 0 else 0.0
    invariant_pred = math.sqrt(BETA / Z)

    lambda_ratio = lambda_fit / lambda_pred if lambda_pred > 0 else 0.0

    return {
        "alpha": alpha,
        "lambda_pred": round(lambda_pred, 4),
        "lambda_fit": round(lambda_fit, 4),
        "lambda_ratio": round(lambda_ratio, 6),
        "a_fit": round(a_fit, 6),
        "r2": round(r2, 6),
        "invariant_fit": round(invariant_fit, 6),
        "invariant_pred": round(invariant_pred, 6),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-036: alpha-screening lambda proportional to 1/sqrt(alpha)."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[float, dict] = {}
    for alpha in ALPHA_VALUES:
        print(f"Running alpha={alpha}...")
        results[alpha] = run_alpha(alpha)

    # ------------------------------------------------------------------
    # Check 1 — invariant lambda * sqrt(alpha) is approximately constant
    # ------------------------------------------------------------------
    invariants = [r["invariant_fit"] for r in results.values() if r["lambda_fit"] > 0]
    if len(invariants) == len(ALPHA_VALUES):
        inv_ratio = max(invariants) / min(invariants)
        check1_pass = inv_ratio < 1.20
    else:
        inv_ratio = 0.0
        check1_pass = False

    # ------------------------------------------------------------------
    # Check 2 — log-log slope of lambda vs alpha ~= -0.5
    # ------------------------------------------------------------------
    valid_lambdas = [(a, r["lambda_fit"]) for a, r in results.items() if r["lambda_fit"] > 0]
    if len(valid_lambdas) >= 3:
        slope = loglog_slope([x[0] for x in valid_lambdas], [x[1] for x in valid_lambdas])
        check2_pass = abs(slope + 0.5) < 0.08
    else:
        slope = 0.0
        check2_pass = False

    # ------------------------------------------------------------------
    # Check 3 — each lambda_fit within 15% of lambda_pred
    # ------------------------------------------------------------------
    check3_details = {
        a: abs(r["lambda_ratio"] - 1.0) < 0.15
        for a, r in results.items()
    }
    check3_pass = all(check3_details.values())

    # ------------------------------------------------------------------
    # Check 4 — lambda_fit monotone decreasing as alpha increases
    # ------------------------------------------------------------------
    lambda_fits = [results[a]["lambda_fit"] for a in ALPHA_VALUES]
    check4_pass = all(lambda_fits[i] > lambda_fits[i + 1] for i in range(len(lambda_fits) - 1))

    # ------------------------------------------------------------------
    # Check 5 — R^2 > 0.99 for all fits
    # ------------------------------------------------------------------
    check5_details = {a: r["r2"] > 0.99 for a, r in results.items()}
    check5_pass = all(check5_details.values())

    checks = {
        "invariant_constant_pass": check1_pass,
        "loglog_slope_pass": check2_pass,
        "each_lambda_within_15pct_pass": check3_pass,
        "lambda_monotone_pass": check4_pass,
        "r2_above_099_pass": check5_pass,
    }
    decision = all(checks.values())

    invariant_pred = math.sqrt(BETA / Z)

    report = {
        "test_id": "QNG-CPU-036",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n_nodes": N_NODES,
            "eq_steps": EQ_STEPS,
            "beta": BETA,
            "z": Z,
            "delta": DELTA,
            "alpha_values": ALPHA_VALUES,
            "fit_r_range": [FIT_R_MIN, FIT_R_MAX],
        },
        "results": {str(a): v for a, v in results.items()},
        "comparisons": {
            "invariant_pred": round(invariant_pred, 6),
            "invariant_fits": {str(a): r["invariant_fit"] for a, r in results.items()},
            "invariant_max_min_ratio": round(inv_ratio, 4),
            "loglog_slope": round(slope, 4),
            "loglog_slope_expected": -0.5,
            "lambda_fits": {str(a): r["lambda_fit"] for a, r in results.items()},
            "lambda_preds": {str(a): r["lambda_pred"] for a, r in results.items()},
            "r2_values": {str(a): r["r2"] for a, r in results.items()},
        },
        "checks": checks,
        "check3_per_alpha": {str(a): v for a, v in check3_details.items()},
        "check5_per_alpha": {str(a): v for a, v in check5_details.items()},
        "interpretation": (
            "Confirmed: lambda_screen ∝ alpha^(-1/2). "
            "The cosmological identification alpha_phys ~ Lambda * l_Planck^2 is "
            "numerically grounded. Gap 5 of the Newtonian limit program is confirmed."
            if decision
            else "FAIL: lambda_screen scaling not confirmed — see individual checks."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Alpha Screening Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Scaling: lambda_screen ∝ alpha^(−1/2)",
        "",
        f"- Predicted invariant sqrt(beta/z) = {invariant_pred:.4f}",
        f"- Log-log slope: {slope:.4f}  (expected -0.5)",
        "",
        "| alpha | lambda_pred | lambda_fit | ratio | inv=lam*sqrt(a) | R^2    | C3   | C5   |",
        "|-------|-------------|------------|-------|-----------------|--------|------|------|",
    ]
    for a in ALPHA_VALUES:
        r = results[a]
        c3 = "PASS" if check3_details[a] else "FAIL"
        c5 = "PASS" if check5_details[a] else "FAIL"
        lines.append(
            f"| {a:.3f} | {r['lambda_pred']:>11.4f} | {r['lambda_fit']:>10.4f} | "
            f"{r['lambda_ratio']:>5.4f} | {r['invariant_fit']:>15.4f} | "
            f"{r['r2']:>6.4f} | {c3} | {c5} |"
        )

    lines += [
        "",
        "## Summary checks",
        f"- Check 1 (invariant constant): max/min = {inv_ratio:.4f} < 1.20  "
        f"{'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (log-log slope = -0.5): slope = {slope:.4f}  "
        f"{'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (each lambda within 15%): {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (lambda monotone in alpha): {'PASS' if check4_pass else 'FAIL'}",
        f"- Check 5 (R^2 > 0.99 all): {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_alpha_screening_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
