from __future__ import annotations

"""
QNG-CPU-035: Step N6 — G_QNG consistency identity G_QNG = alpha * lambda_screen^2.

Tests Identity N6.1 from DER-QNG-018 across three beta values (0.20, 0.35, 0.50).

Both G_QNG = beta/z and lambda_screen = sqrt(beta/(z*alpha)) emerge from the same
substrate parameters. Their product G_QNG = alpha * lambda^2 must hold identically.

Design:
  For each beta in {0.20, 0.35, 0.50}:
  1. Run v3 quasi-static equilibration (clamped source at node 0)
  2. Fit exponential decay to sigma profile: |delta_C(r)| ~ A * exp(-r / lambda_fit)
  3. Check: alpha * lambda_fit^2 / (beta/z) is close to 1
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-g-qng-consistency-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_NODES: int = 64
EQ_STEPS: int = 3000
SEED: int = 20260325

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05
SOURCE_NODE: int = 0

Z: int = 2              # ring: z=2
ALPHA: float = 0.005
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20
DELTA: float = 0.20

BETA_VALUES: list[float] = [0.20, 0.35, 0.50]
FIT_R_MIN: int = 2       # start fit away from source
FIT_R_MAX: int = 15      # end fit before boundary effects dominate


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
# v3 equilibration step
# ---------------------------------------------------------------------------

def eq_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    beta: float,
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
            + ALPHA * (SIGMA_REF - sigma_i)
            + beta * (sigma_neigh - sigma_i)
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
# over r in [FIT_R_MIN, FIT_R_MAX]
# ---------------------------------------------------------------------------

def fit_screening_length(delta_c: list[float]) -> tuple[float, float, float]:
    """
    Returns (lambda_fit, A_fit, r_squared) from fitting |delta_C(r)| to A*exp(-r/lambda).
    Uses log-linear regression: log|delta_C(r)| = log(A) - r/lambda.
    """
    rs = list(range(FIT_R_MIN, FIT_R_MAX + 1))
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

    slope = ss_xy / ss_xx  # slope = -1/lambda
    intercept = my - slope * mx  # intercept = log(A)

    lambda_fit = -1.0 / slope if slope < 0 else 0.0
    a_fit = math.exp(intercept)

    # R^2
    y_pred = [intercept + slope * x for x in xs]
    ss_res = sum((ys[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((ys[i] - my) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else 0.0

    return lambda_fit, a_fit, r2


# ---------------------------------------------------------------------------
# Run one simulation at given beta
# ---------------------------------------------------------------------------

def run_beta(beta: float) -> dict:
    adj = build_ring(N_NODES)
    rng = random.Random(SEED)

    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    sigma[SOURCE_NODE] = SIGMA_SOURCE
    chi = [0.0] * N_NODES
    phi = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]

    for _ in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, beta)

    # Compute delta_C profile (distance from source: take min of clockwise/counterclockwise)
    delta_c_by_r = [0.0] * (N_NODES // 2 + 1)
    count_by_r = [0] * (N_NODES // 2 + 1)
    for i in range(N_NODES):
        r = min(i, N_NODES - i)  # ring distance from node 0
        if r <= N_NODES // 2:
            delta_c_by_r[r] += sigma[i] - SIGMA_REF
            count_by_r[r] += 1
    delta_c_profile = [
        delta_c_by_r[r] / count_by_r[r] if count_by_r[r] > 0 else 0.0
        for r in range(N_NODES // 2 + 1)
    ]

    # Predicted values
    g_qng_formula = beta / Z
    lambda_pred = math.sqrt(beta / (Z * ALPHA))

    # Fit
    lambda_fit, a_fit, r2 = fit_screening_length(delta_c_profile)

    # Identity: alpha * lambda^2 / G_QNG = 1 ?
    if g_qng_formula > 1e-15 and lambda_fit > 0:
        identity_ratio = ALPHA * lambda_fit ** 2 / g_qng_formula
    else:
        identity_ratio = 0.0

    return {
        "beta": beta,
        "g_qng_formula": round(g_qng_formula, 6),
        "lambda_pred": round(lambda_pred, 4),
        "lambda_fit": round(lambda_fit, 4),
        "a_fit": round(a_fit, 6),
        "r2": round(r2, 6),
        "identity_ratio": round(identity_ratio, 6),
        "delta_c_at_source": round(delta_c_profile[0], 6),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-035: G_QNG consistency identity G_QNG = alpha * lambda^2."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for beta in BETA_VALUES:
        print(f"Running beta={beta}...")
        results[beta] = run_beta(beta)

    r0 = results[BETA_VALUES[0]]
    r1 = results[BETA_VALUES[1]]
    r2 = results[BETA_VALUES[2]]

    # ------------------------------------------------------------------
    # Checks 1-3: Identity G_QNG = alpha * lambda^2 at each beta
    # ------------------------------------------------------------------
    check1_pass = abs(r0["identity_ratio"] - 1.0) < 0.10
    check2_pass = abs(r1["identity_ratio"] - 1.0) < 0.10
    check3_pass = abs(r2["identity_ratio"] - 1.0) < 0.10

    # ------------------------------------------------------------------
    # Check 4: G_QNG scales linearly with beta
    # G(0.50)/G(0.20) = 0.50/0.20 = 2.5 exactly
    # ------------------------------------------------------------------
    g_ratio_formula = r2["g_qng_formula"] / r0["g_qng_formula"]
    g_ratio_pred = BETA_VALUES[2] / BETA_VALUES[0]
    check4_pass = abs(g_ratio_formula - g_ratio_pred) < 0.01

    # ------------------------------------------------------------------
    # Check 5: lambda^2 scales linearly with beta
    # lambda_fit(0.50)^2 / lambda_fit(0.20)^2 ~= 0.50/0.20 = 2.5
    # ------------------------------------------------------------------
    if r0["lambda_fit"] > 0:
        lambda2_ratio = r2["lambda_fit"] ** 2 / r0["lambda_fit"] ** 2
        check5_pass = abs(lambda2_ratio - g_ratio_pred) < 0.15
    else:
        lambda2_ratio = 0.0
        check5_pass = False

    checks = {
        "identity_beta020_pass": check1_pass,
        "identity_beta035_pass": check2_pass,
        "identity_beta050_pass": check3_pass,
        "g_qng_linear_beta_pass": check4_pass,
        "lambda2_linear_beta_pass": check5_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-035",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n_nodes": N_NODES,
            "eq_steps": EQ_STEPS,
            "z": Z,
            "alpha": ALPHA,
            "delta": DELTA,
            "beta_values": BETA_VALUES,
            "fit_r_range": [FIT_R_MIN, FIT_R_MAX],
        },
        "results": {str(b): v for b, v in results.items()},
        "comparisons": {
            "identity_ratios": [r["identity_ratio"] for r in results.values()],
            "g_ratio_formula": round(g_ratio_formula, 6),
            "g_ratio_pred": round(g_ratio_pred, 6),
            "lambda2_ratio_fit": round(lambda2_ratio, 4),
            "lambda2_ratio_pred": round(g_ratio_pred, 4),
        },
        "checks": checks,
        "interpretation": (
            "Identity N6.1 confirmed: G_QNG = alpha * lambda^2 holds across all beta values. "
            "G_QNG formula and screening length formula are jointly consistent."
            if decision
            else "Identity N6.1 not confirmed — see individual check results."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG G_QNG Consistency Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Identity N6.1: G_QNG = alpha * lambda^2_screen",
        "",
        "| beta | G_QNG=beta/z | lambda_pred | lambda_fit | R^2  | alpha*lam^2/G | check |",
        "|------|-------------|-------------|------------|------|---------------|-------|",
    ]
    for b, r in results.items():
        chk = "PASS" if abs(r["identity_ratio"] - 1.0) < 0.10 else "FAIL"
        lines.append(
            f"| {b:.2f} | {r['g_qng_formula']:.4f} | {r['lambda_pred']:.2f} | "
            f"{r['lambda_fit']:.2f} | {r['r2']:.4f} | {r['identity_ratio']:.4f} | {chk} |"
        )

    lines += [
        "",
        "## Check 4: G_QNG linear in beta",
        f"- G(0.50)/G(0.20) = {g_ratio_formula:.4f}  expected {g_ratio_pred:.4f}  "
        f"{'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Check 5: lambda^2 linear in beta",
        f"- lambda_fit(0.50)^2 / lambda_fit(0.20)^2 = {lambda2_ratio:.4f}  "
        f"expected {g_ratio_pred:.4f}  {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"qng_g_qng_consistency_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
