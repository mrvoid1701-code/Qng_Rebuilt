from __future__ import annotations

"""
QNG-CPU-033: P1 confirmation — chi-to-phi coupling in v4.

Tests Prediction P1 from qng-chi-ontology-v1.md using the v4 update law
(DER-QNG-016), which adds Channel E: epsilon*chi_i in the phi channel.

v3 established (QNG-CPU-032) that P1 is a null result by construction.
v4 adds Channel E and this test verifies the linear drift prediction:

    omega_phi = epsilon * <chi>

Design:
  1. Equilibrate v3 to get chi backgrounds for Condition A (delta=0) and B (delta=0.20).
  2. Freeze sigma/chi. Reset phi to a common random perturbation.
  3. Run phi relaxation using v4 phi step (adds epsilon*chi_i).
  4. Measure mean angular drift rate omega = total_drift / PHI_STEPS.
  5. Compare omega_B to prediction epsilon * chi_mean_B.
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-p1-v4-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_NODES: int = 64
EQ_STEPS: int = 3000
PHI_STEPS: int = 500
SEED: int = 20260325
PHI_SEED: int = 20260326

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05
SOURCE_NODE: int = 0

ALPHA: float = 0.005
BETA: float = 0.35
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20

DELTA_A: float = 0.00
DELTA_B: float = 0.20
EPSILON: float = 0.02   # Channel E coupling strength


# ---------------------------------------------------------------------------
# Graph
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


def spatial_power(values: list[float]) -> float:
    n = len(values)
    power = 0.0
    for k in range(1, n // 2 + 1):
        re = sum(values[j] * math.cos(2 * math.pi * k * j / n) for j in range(n))
        im = sum(values[j] * math.sin(2 * math.pi * k * j / n) for j in range(n))
        power += re * re + im * im
    return power / n


# ---------------------------------------------------------------------------
# v3 equilibration step
# ---------------------------------------------------------------------------

def eq_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    delta: float,
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
            + BETA * (sigma_neigh - sigma_i)
        )
        chi_new = (
            chi_i
            - CHI_DECAY * chi_i
            + CHI_REL * (sigma_neigh - sigma_i)
            + delta * (SIGMA_REF - sigma_i)
        )
        phi_new = wrap_angle(phi_i + PHI_REL * angle_diff(phi_neigh, phi_i))

        new_sigma.append(sigma_new)
        new_chi.append(chi_new)
        new_phi.append(phi_new)

    new_sigma[SOURCE_NODE] = SIGMA_SOURCE
    return new_sigma, new_chi, new_phi


# ---------------------------------------------------------------------------
# v4 phi step with FROZEN sigma/chi background (Channel E active)
# phi_new = wrap(phi_i + phi_rel * angle_diff(phi_bar, phi_i) + epsilon * chi_i)
# ---------------------------------------------------------------------------

def phi_step_v4(
    phi: list[float],
    chi: list[float],
    adj: list[list[int]],
    epsilon: float,
) -> list[float]:
    new_phi: list[float] = []
    for i, neighbors in enumerate(adj):
        phi_i = phi[i]
        sin_sum = sum(math.sin(phi[j]) for j in neighbors)
        cos_sum = sum(math.cos(phi[j]) for j in neighbors)
        phi_neigh = (
            math.atan2(sin_sum, cos_sum)
            if abs(sin_sum) + abs(cos_sum) > 1e-12
            else phi_i
        )
        phi_new = wrap_angle(
            phi_i + PHI_REL * angle_diff(phi_neigh, phi_i) + epsilon * chi[i]
        )
        new_phi.append(phi_new)
    return new_phi


# ---------------------------------------------------------------------------
# Angular drift measurement
# ---------------------------------------------------------------------------

def mean_angular_drift_rate(phi_series: list[list[float]]) -> float:
    """
    Compute mean angular drift rate (rad/step) averaged over all nodes.

    Uses cumulative unwrapped phase to track total angular displacement,
    then divides by number of steps.
    """
    n_nodes = len(phi_series[0])
    T = len(phi_series) - 1  # number of steps taken

    total_drift = 0.0
    for i in range(n_nodes):
        # Accumulate total wrapped angular displacement step by step
        cumulative = 0.0
        for t in range(T):
            cumulative += angle_diff(phi_series[t + 1][i], phi_series[t][i])
        total_drift += cumulative

    return total_drift / (n_nodes * T)


# ---------------------------------------------------------------------------
# Run one condition
# ---------------------------------------------------------------------------

def run_condition(
    adj: list[list[int]],
    rng: random.Random,
    delta: float,
) -> dict:
    # Initialize
    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    sigma[SOURCE_NODE] = SIGMA_SOURCE
    chi = [0.0] * N_NODES
    phi = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]

    # v3 equilibration (establishes chi background)
    for _ in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, delta)

    # Record equilibrium stats
    chi_mean = sum(chi) / N_NODES
    sigma_mean = sum(sigma) / N_NODES
    sigma_power = spatial_power(sigma)
    chi_power = spatial_power(chi)

    # Reset phi to common random perturbation
    phi_rng = random.Random(PHI_SEED)
    phi = [phi_rng.uniform(-math.pi, math.pi) for _ in range(N_NODES)]

    # Run v4 phi relaxation with frozen sigma/chi background
    phi_series: list[list[float]] = [phi[:]]
    for _ in range(PHI_STEPS):
        phi = phi_step_v4(phi, chi, adj, EPSILON)
        phi_series.append(phi[:])

    omega = mean_angular_drift_rate(phi_series)

    return {
        "chi_mean": chi_mean,
        "chi_spatial_power": chi_power,
        "sigma_mean": sigma_mean,
        "sigma_spatial_power": sigma_power,
        "phi_omega": omega,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-033: P1 confirmation — v4 chi-to-phi frequency shift."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    adj = build_ring(N_NODES)

    rng_a = random.Random(SEED)
    rng_b = random.Random(SEED)

    print("Running Condition A (delta=0.00, Channel D off)...")
    cond_a = run_condition(adj, rng_a, DELTA_A)
    print("Running Condition B (delta=0.20, Channel D on)...")
    cond_b = run_condition(adj, rng_b, DELTA_B)

    # ------------------------------------------------------------------
    # Check 1: Drift detected in Condition B
    # omega_B > 0.5 * epsilon * chi_mean_B
    # ------------------------------------------------------------------
    omega_b = cond_b["phi_omega"]
    chi_mean_b = cond_b["chi_mean"]
    predicted_omega_b = EPSILON * chi_mean_b
    check1_pass = omega_b > 0.5 * predicted_omega_b

    # ------------------------------------------------------------------
    # Check 2: Null drift in Condition A
    # |omega_A| < 0.01
    # ------------------------------------------------------------------
    omega_a = cond_a["phi_omega"]
    check2_pass = abs(omega_a) < 0.01

    # ------------------------------------------------------------------
    # Check 3: Drift ratio confirms linear scaling
    # omega_B / (epsilon * chi_mean_B) in [0.5, 2.0]
    # ------------------------------------------------------------------
    if abs(predicted_omega_b) > 1e-9:
        drift_ratio = omega_b / predicted_omega_b
    else:
        drift_ratio = 0.0
    check3_pass = 0.5 <= drift_ratio <= 2.0

    # ------------------------------------------------------------------
    # Check 4: Sigma spatial power unchanged (null — no chi→sigma coupling)
    # |P_sigma_B / P_sigma_A - 1| < 0.01
    # ------------------------------------------------------------------
    p_sigma_a = cond_a["sigma_spatial_power"]
    p_sigma_b = cond_b["sigma_spatial_power"]
    if p_sigma_a > 1e-15:
        sigma_power_ratio = p_sigma_b / p_sigma_a
        sigma_null_diff = abs(sigma_power_ratio - 1.0)
    else:
        sigma_power_ratio = 1.0
        sigma_null_diff = 0.0
    check4_pass = sigma_null_diff < 0.01

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------
    checks = {
        "drift_detected_B_pass": check1_pass,
        "drift_null_A_pass": check2_pass,
        "drift_linear_scaling_pass": check3_pass,
        "sigma_power_null_pass": check4_pass,
    }
    decision = all(checks.values())

    interpretation = (
        "P1 confirmed in v4. Chi tension drives phase accumulation at rate "
        f"epsilon*<chi> = {EPSILON}*{chi_mean_b:.4f} = {predicted_omega_b:.4f} rad/step. "
        "Channel E is the QM-facing coupling linking the gravitational sector (sigma/chi) "
        "to the quantum-phase sector (phi)."
        if decision
        else "P1 not confirmed — see individual check results."
    )

    report = {
        "test_id": "QNG-CPU-033",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n_nodes": N_NODES,
            "eq_steps": EQ_STEPS,
            "phi_steps": PHI_STEPS,
            "alpha": ALPHA,
            "beta": BETA,
            "delta_a": DELTA_A,
            "delta_b": DELTA_B,
            "epsilon": EPSILON,
            "sigma_source": SIGMA_SOURCE,
        },
        "condition_a": {k: round(v, 6) for k, v in cond_a.items()},
        "condition_b": {k: round(v, 6) for k, v in cond_b.items()},
        "comparisons": {
            "omega_a": round(omega_a, 6),
            "omega_b": round(omega_b, 6),
            "predicted_omega_b": round(predicted_omega_b, 6),
            "drift_ratio": round(drift_ratio, 4),
            "sigma_power_null_diff": round(sigma_null_diff, 6),
        },
        "checks": checks,
        "interpretation": interpretation,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG P1 v4 Reference",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Conditions",
        f"- Condition A: delta={DELTA_A}, epsilon={EPSILON}  (Channel D off, Channel E on)",
        f"- Condition B: delta={DELTA_B}, epsilon={EPSILON}  (Channel D on, Channel E on)",
        "",
        "## Chi backgrounds (from v3 equilibration)",
        f"- ⟨χ⟩_A = {cond_a['chi_mean']:.4f}",
        f"- ⟨χ⟩_B = {cond_b['chi_mean']:.4f}",
        f"- Predicted omega_B = epsilon * ⟨χ⟩_B = {EPSILON} * {cond_b['chi_mean']:.4f} = {predicted_omega_b:.4f} rad/step",
        "",
        "## Check 1: Drift detected in Condition B",
        f"- omega_B = {omega_b:.6f} rad/step",
        f"- threshold > 0.5 * predicted = {0.5 * predicted_omega_b:.6f}",
        f"- {'PASS' if check1_pass else 'FAIL'}",
        "",
        "## Check 2: Null drift in Condition A",
        f"- omega_A = {omega_a:.6f} rad/step",
        f"- threshold |omega_A| < 0.01",
        f"- {'PASS' if check2_pass else 'FAIL'}",
        "",
        "## Check 3: Linear scaling confirmed",
        f"- drift_ratio = omega_B / predicted_omega_B = {drift_ratio:.4f}",
        f"- threshold in [0.5, 2.0]",
        f"- {'PASS' if check3_pass else 'FAIL'}",
        "",
        "## Check 4: Sigma spatial power unchanged (null)",
        f"- P_sigma_A = {p_sigma_a:.4f}  P_sigma_B = {p_sigma_b:.4f}",
        f"- |ratio-1| = {sigma_null_diff:.4f}  threshold < 0.01",
        f"- {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Interpretation",
        interpretation,
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_p1_v4_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
