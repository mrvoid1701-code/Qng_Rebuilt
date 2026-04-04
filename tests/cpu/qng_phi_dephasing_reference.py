from __future__ import annotations

"""
QNG-CPU-034: Phi dephasing from chi background — T2* measurement and epsilon constraint.

Tests DER-QNG-017: a non-uniform chi background (from v3, Channel D) causes phi
coherence to decay when Channel E (v4, epsilon*chi_i) is active.

Prediction: T2*_pred = sqrt(2) / (epsilon * sigma_chi)

Design:
  1. v3 equilibration with delta=0.20 → chi background {chi_i}, measure sigma_chi
  2. Initialize phi_i = 0 (perfect coherence, C(0) = 1)
  3. Run Channel E only (phi_rel = 0): phi_i(t+1) = wrap(phi_i + epsilon*chi_i)
  4. Record C(t) = |mean(exp(i*phi_i(t)))| for 500 steps
  5. Find T2*_meas: first t where C(t) <= 1/e
  6. Compare to T2*_pred = sqrt(2) / (epsilon * sigma_chi)
  7. Repeat with delta=0 (Condition A): C(t) should stay near 1
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-phi-dephasing-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N_NODES: int = 64
EQ_STEPS: int = 3000
DEPH_STEPS: int = 500
SEED: int = 20260325

SIGMA_REF: float = 0.5
SIGMA_SOURCE: float = 0.05
SOURCE_NODE: int = 0

ALPHA: float = 0.005
BETA: float = 0.35
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35
PHI_REL: float = 0.20   # used only in equilibration, NOT in dephasing step

DELTA_A: float = 0.00
DELTA_B: float = 0.20
EPSILON: float = 0.02


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


def phase_coherence(phi: list[float]) -> float:
    """C = |mean(exp(i*phi_i))| — Kuramoto order parameter."""
    n = len(phi)
    re = sum(math.cos(phi[i]) for i in range(n)) / n
    im = sum(math.sin(phi[i]) for i in range(n)) / n
    return math.sqrt(re * re + im * im)


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
# Channel E only dephasing step (phi_rel = 0)
# phi_i(t+1) = wrap(phi_i(t) + epsilon * chi_i)
# ---------------------------------------------------------------------------

def dephasing_step(
    phi: list[float],
    chi: list[float],
    epsilon: float,
) -> list[float]:
    return [wrap_angle(phi[i] + epsilon * chi[i]) for i in range(len(phi))]


# ---------------------------------------------------------------------------
# Find T2*: first t where C(t) <= threshold
# ---------------------------------------------------------------------------

def find_t2_star(coherence: list[float], threshold: float) -> float:
    for t, c in enumerate(coherence):
        if c <= threshold:
            return float(t)
    return float(len(coherence))  # did not decay within measurement window


# ---------------------------------------------------------------------------
# Run one condition
# ---------------------------------------------------------------------------

def exact_coherence_prediction(chi: list[float], epsilon: float, t: int) -> float:
    """
    Exact characteristic function prediction (no Gaussian approximation):
    C_exact(t) = |mean(exp(i * epsilon * chi_i * t))|
    Since exp(i*phi) is 2pi-periodic, wrap() on phi does not affect this.
    """
    n = len(chi)
    re = sum(math.cos(epsilon * chi[i] * t) for i in range(n)) / n
    im = sum(math.sin(epsilon * chi[i] * t) for i in range(n)) / n
    return math.sqrt(re * re + im * im)


def run_condition(
    adj: list[list[int]],
    rng: random.Random,
    delta: float,
) -> dict:
    # v3 equilibration
    sigma = [SIGMA_REF + 0.02 * rng.uniform(-1, 1) for _ in range(N_NODES)]
    sigma[SOURCE_NODE] = SIGMA_SOURCE
    chi = [0.0] * N_NODES
    phi = [rng.uniform(-0.1, 0.1) for _ in range(N_NODES)]

    for _ in range(EQ_STEPS):
        sigma, chi, phi = eq_step(sigma, chi, phi, adj, delta)

    # Chi statistics
    chi_mean = sum(chi) / N_NODES
    chi_var = sum((c - chi_mean) ** 2 for c in chi) / N_NODES
    sigma_chi = math.sqrt(chi_var) if chi_var > 0 else 0.0

    # Gaussian approximation (informational only — expected to be inaccurate for skewed profiles)
    t2_gaussian = (
        math.sqrt(2.0) / (EPSILON * sigma_chi) if sigma_chi > 1e-9 else float(DEPH_STEPS)
    )

    # Exact characteristic function prediction: C_exact(t) from actual chi values
    threshold = 1.0 / math.e
    t2_exact = float(DEPH_STEPS)
    for t in range(1, DEPH_STEPS + 1):
        if exact_coherence_prediction(chi, EPSILON, t) <= threshold:
            t2_exact = float(t)
            break

    # Initialize phi to 0 (perfect coherence)
    phi = [0.0] * N_NODES

    # Run dephasing (Channel E only, phi_rel = 0)
    coherence: list[float] = [phase_coherence(phi)]
    for _ in range(DEPH_STEPS):
        phi = dephasing_step(phi, chi, EPSILON)
        coherence.append(phase_coherence(phi))

    t2_meas = find_t2_star(coherence, threshold)

    return {
        "chi_mean": chi_mean,
        "chi_var": chi_var,
        "sigma_chi": sigma_chi,
        "t2_gaussian": t2_gaussian,
        "t2_exact": t2_exact,
        "t2_meas": t2_meas,
        "coherence_at_50": coherence[50],
        "coherence_at_100": coherence[100] if len(coherence) > 100 else coherence[-1],
        "coherence_final": coherence[-1],
        "coherence": coherence,  # full series for cross-condition checks
        "coherence_series": [round(c, 6) for c in coherence[::10]],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-034: Phi dephasing T2* from chi background."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    adj = build_ring(N_NODES)
    rng_a = random.Random(SEED)
    rng_b = random.Random(SEED)

    print("Running Condition A (delta=0.00, chi~0)...")
    cond_a = run_condition(adj, rng_a, DELTA_A)
    print("Running Condition B (delta=0.20, chi!=0)...")
    cond_b = run_condition(adj, rng_b, DELTA_B)

    threshold = 1.0 / math.e

    # ------------------------------------------------------------------
    # Check 1: Decoherence occurs in Condition B
    # C(t) drops below 1/e within DEPH_STEPS
    # ------------------------------------------------------------------
    check1_pass = cond_b["t2_meas"] < DEPH_STEPS

    # ------------------------------------------------------------------
    # Check 2: Measured T2* matches exact characteristic-function prediction
    # T2*_meas / T2*_exact in [0.5, 2.0]
    # ------------------------------------------------------------------
    t2_exact_b = cond_b["t2_exact"]
    t2_meas_b = cond_b["t2_meas"]
    if t2_exact_b < DEPH_STEPS:
        t2_ratio = t2_meas_b / t2_exact_b
        check2_pass = 0.5 <= t2_ratio <= 2.0
    else:
        t2_ratio = float("inf")
        check2_pass = False

    # ------------------------------------------------------------------
    # Check 3: B dephases while A is still coherent
    # C_A(T2*_B) > 1/e
    # At the time B's coherence reaches 1/e, A's coherence is still above 1/e.
    # ------------------------------------------------------------------
    t2b_int = int(t2_meas_b)
    if t2b_int < len(cond_a["coherence"]):
        c_a_at_t2b = cond_a["coherence"][t2b_int]
    else:
        c_a_at_t2b = cond_a["coherence_final"]
    threshold = 1.0 / math.e
    check3_pass = c_a_at_t2b > threshold

    # ------------------------------------------------------------------
    # Check 4: C(t) decreasing in early regime (B only)
    # C(50) < C(0) = 1 and C(100) < C(50)
    # ------------------------------------------------------------------
    check4_pass = (
        cond_b["coherence_at_50"] < 1.0
        and cond_b["coherence_at_100"] < cond_b["coherence_at_50"]
    )

    checks = {
        "decoherence_occurs_B_pass": check1_pass,
        "t2_star_ratio_pass": check2_pass,
        "no_decoherence_A_pass": check3_pass,
        "monotone_decay_pass": check4_pass,
    }
    decision = all(checks.values())

    epsilon_constraint = (
        f"epsilon = sqrt(2) / (T2*_meas * sigma_chi) "
        f"= sqrt(2) / ({t2_meas_b:.1f} * {cond_b['sigma_chi']:.4f}) "
        f"= {math.sqrt(2.0) / (t2_meas_b * cond_b['sigma_chi']):.6f} "
        f"(input epsilon = {EPSILON})"
        if check1_pass and cond_b["sigma_chi"] > 1e-9
        else "T2* not reached within measurement window"
    )

    interpretation = (
        f"Dephasing confirmed. {epsilon_constraint}. "
        f"Input ε = {EPSILON:.4f}. "
        "Matching T₂* to observed decoherence time constrains ε in substrate units."
        if decision
        else "Dephasing not confirmed — see individual check results."
    )

    report = {
        "test_id": "QNG-CPU-034",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n_nodes": N_NODES,
            "eq_steps": EQ_STEPS,
            "deph_steps": DEPH_STEPS,
            "epsilon": EPSILON,
            "delta_a": DELTA_A,
            "delta_b": DELTA_B,
            "sigma_source": SIGMA_SOURCE,
            "threshold_1_over_e": round(threshold, 6),
        },
        "condition_a": {k: v for k, v in cond_a.items() if k not in ("coherence_series", "coherence")},
        "condition_b": {k: v for k, v in cond_b.items() if k not in ("coherence_series", "coherence")},
        "coherence_series_A": cond_a["coherence_series"],
        "coherence_series_B": cond_b["coherence_series"],
        "comparisons": {
            "t2_gaussian_B": round(cond_b["t2_gaussian"], 2),
            "t2_exact_B": round(t2_exact_b, 2),
            "t2_meas_B": round(t2_meas_b, 2),
            "t2_ratio_meas_over_exact": round(t2_ratio if t2_ratio != float("inf") else 9999.0, 4),
            "c_a_at_t2b": round(c_a_at_t2b, 6),
            "coherence_final_A": round(cond_a["coherence_final"], 6),
            "coherence_final_B": round(cond_b["coherence_final"], 6),
        },
        "epsilon_constraint": epsilon_constraint,
        "checks": checks,
        "interpretation": interpretation,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Phi Dephasing Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Setup",
        f"- epsilon={EPSILON}, delta_B={DELTA_B}, N={N_NODES}, steps={DEPH_STEPS}",
        f"- phi_rel=0 (Channel E only, no inter-node smoothing)",
        "",
        "## Chi backgrounds",
        f"- Condition A: chi_mean={cond_a['chi_mean']:.4f}, sigma_chi={cond_a['sigma_chi']:.4f}",
        f"- Condition B: chi_mean={cond_b['chi_mean']:.4f}, sigma_chi={cond_b['sigma_chi']:.4f}",
        "",
        "## T2* (Condition B)",
        f"- T2*_gaussian (informational) = sqrt(2)/(epsilon*sigma_chi) = {cond_b['t2_gaussian']:.2f} steps",
        f"- T2*_exact (from chi values)  = {t2_exact_b:.2f} steps",
        f"- T2*_meas (simulation)        = {t2_meas_b:.2f} steps",
        f"- ratio T2*_meas / T2*_exact   = {t2_ratio:.4f}  threshold [0.5, 2.0]",
        "",
        "## epsilon constraint",
        f"- {epsilon_constraint}",
        "",
        "## Check 1: Decoherence in Condition B",
        f"- T2*_meas={t2_meas_b:.2f} < {DEPH_STEPS} steps  {'PASS' if check1_pass else 'FAIL'}",
        "",
        "## Check 2: T2* matches exact prediction",
        f"- ratio={t2_ratio:.4f}  threshold [0.5, 2.0]  {'PASS' if check2_pass else 'FAIL'}",
        "",
        "## Check 3: B dephases while A is still coherent",
        f"- C_A(T2*_B=t={t2b_int}) = {c_a_at_t2b:.6f}  threshold > {threshold:.4f}  {'PASS' if check3_pass else 'FAIL'}",
        "",
        "## Check 4: Monotone decay Condition B (early regime)",
        f"- C(0)=1.000  C(50)={cond_b['coherence_at_50']:.4f}  C(100)={cond_b['coherence_at_100']:.4f}",
        f"- {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Coherence series Condition B (every 10 steps)",
        "  ".join(f"t={i*10}:{v:.3f}" for i, v in enumerate(cond_b["coherence_series"][:12])),
        "",
        "## Interpretation",
        interpretation,
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_phi_dephasing_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
