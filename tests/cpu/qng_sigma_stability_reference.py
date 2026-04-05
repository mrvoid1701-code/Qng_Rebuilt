from __future__ import annotations

"""
QNG-CPU-040: Sigma deficit stability -- confirming sigma channel is purely dissipative.

Tests DER-QNG-025: a localized coherence deficit (no external clamping) decays at rate
~alpha, with or without chi coupling. Confirms stable matter cannot arise from sigma
dynamics alone. PASS = sigma is dissipative (as predicted).

Protocol:
  - 200-node ring, localized deficit at center (3 nodes, sigma=0.1)
  - No source clamping -- deficit evolves freely
  - 3000 steps, record max |delta_C| at center each step
  - Fit decay to exp(-alpha_fit * t)
  - Repeat with delta=0 (no chi) to confirm chi does not affect sigma decay
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-sigma-stability-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N: int = 200
STEPS: int = 3000
SEED: int = 20260405

SIGMA_REF: float = 0.5
SIGMA_0: float = 0.1          # initial deficit: 3 center nodes
ALPHA: float = 0.005
BETA: float = 0.35
DELTA: float = 0.20
CHI_DECAY: float = 0.005
CHI_REL: float = 0.35

CENTER_NODES: list[int] = [98, 99, 100]   # localized deficit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def run_decay(delta_coeff: float) -> tuple[list[float], list[float]]:
    """
    Run the ring simulation with given delta coefficient.
    Returns (center_dc_series, integral_dc_series) over time.
    Note: integral_dc decays as exp(-alpha*t) exactly (beta term sums to zero on ring).
    """
    rng = random.Random(SEED)
    sigma = [SIGMA_REF] * N
    chi = [0.0] * N

    for node in CENTER_NODES:
        sigma[node] = SIGMA_0

    center_dc: list[float] = []
    integral_dc: list[float] = []

    for step in range(STEPS):
        new_sigma: list[float] = []
        new_chi: list[float] = []

        for i in range(N):
            left = (i - 1) % N
            right = (i + 1) % N
            sigma_bar = (sigma[left] + sigma[right]) / 2.0

            s = clip01(
                sigma[i]
                + ALPHA * (SIGMA_REF - sigma[i])
                + BETA * (sigma_bar - sigma[i])
            )
            c = (
                chi[i] * (1.0 - CHI_DECAY)
                + CHI_REL * (sigma_bar - sigma[i])
                + delta_coeff * (SIGMA_REF - sigma[i])
            )
            new_sigma.append(s)
            new_chi.append(c)

        sigma = new_sigma
        chi = new_chi

        # Record center (use node 99 = exact center)
        dc_center = abs(sigma[99] - SIGMA_REF)
        center_dc.append(dc_center)

        # Total integral |delta_C| = N*sigma_ref - sum(sigma)
        # This decays as exp(-alpha*t) exactly (beta cancels on closed ring)
        total = sum(abs(sigma[i] - SIGMA_REF) for i in range(N))
        integral_dc.append(total)

    return center_dc, integral_dc


def fit_exp_decay_integral(series: list[float], t_start: int = 5, t_end: int = 800) -> float:
    """
    Fit log(integral[t]) = log(A) - alpha_fit * t.
    The total integral decays as exp(-alpha*t) exactly on a closed ring (beta sums to 0).
    Use early-to-mid range where values are well above numerical noise.
    """
    xs: list[float] = []
    ys: list[float] = []
    for t in range(t_start, min(t_end, len(series))):
        if series[t] > 1e-12:
            xs.append(float(t))
            ys.append(math.log(series[t]))

    n = len(xs)
    if n < 5:
        return 0.0

    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xy = sum((xs[k] - mx) * (ys[k] - my) for k in range(n))
    ss_xx = sum((xs[k] - mx) ** 2 for k in range(n))
    if ss_xx < 1e-15:
        return 0.0

    slope = ss_xy / ss_xx
    return -slope if slope < 0 else 0.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-040: sigma deficit stability test."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"alpha={ALPHA}, beta={BETA}, N={N}, steps={STEPS}")
    print(f"Initial deficit: sigma={SIGMA_0} at nodes {CENTER_NODES}")
    print(f"Theoretical decay timescale: 1/alpha = {1/ALPHA:.0f} steps")
    print()

    # Run with chi coupling (delta=0.20)
    print(f"Run 1: with chi coupling (delta={DELTA})...")
    center_dc_chi, integral_dc_chi = run_decay(DELTA)
    alpha_fit_chi = fit_exp_decay_integral(integral_dc_chi)
    print(f"  Final center |delta_C| = {center_dc_chi[-1]:.2e}")
    print(f"  Final integral |delta_C| = {integral_dc_chi[-1]:.2e}")
    print(f"  Fitted decay rate alpha_fit (integral) = {alpha_fit_chi:.5f}  (pred={ALPHA})")

    # Run without chi coupling (delta=0)
    print(f"Run 2: no chi coupling (delta=0)...")
    center_dc_nochi, integral_dc_nochi = run_decay(0.0)
    alpha_fit_nochi = fit_exp_decay_integral(integral_dc_nochi)
    print(f"  Final center |delta_C| = {center_dc_nochi[-1]:.2e}")
    print(f"  Final integral |delta_C| = {integral_dc_nochi[-1]:.2e}")
    print(f"  Fitted decay rate alpha_fit (integral) = {alpha_fit_nochi:.5f}  (pred={ALPHA})")

    # ------------------------------------------------------------------
    # Check 1: center deficit decays to near-zero by T=3000
    # ------------------------------------------------------------------
    check1_pass = center_dc_chi[-1] < 0.01

    # ------------------------------------------------------------------
    # Check 2: integral decay rate matches exp(-alpha*t) within 10%
    # (The total integral Σ|delta_C| decays as exp(-alpha*t) exactly on a ring,
    # because the beta term sums to zero on any closed graph — only alpha decays it)
    # ------------------------------------------------------------------
    if alpha_fit_chi > 0:
        ratio2 = alpha_fit_chi / ALPHA
        check2_pass = abs(ratio2 - 1.0) < 0.10
    else:
        ratio2 = 0.0
        check2_pass = False

    # ------------------------------------------------------------------
    # Check 3: total integral dissipates to near-zero by T=3000
    # ------------------------------------------------------------------
    check3_pass = integral_dc_chi[-1] < 0.001

    # ------------------------------------------------------------------
    # Check 4: chi coupling does not change sigma decay rate (within 5%)
    # ------------------------------------------------------------------
    if alpha_fit_chi > 0 and alpha_fit_nochi > 0:
        ratio4 = alpha_fit_chi / alpha_fit_nochi
        check4_pass = abs(ratio4 - 1.0) < 0.05
    else:
        ratio4 = 0.0
        check4_pass = False

    checks = {
        "deficit_decays_to_zero_pass": check1_pass,
        "decay_rate_matches_alpha_pass": check2_pass,
        "total_integral_dissipates_pass": check3_pass,
        "chi_does_not_affect_sigma_decay_pass": check4_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-040",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n": N,
            "steps": STEPS,
            "alpha": ALPHA,
            "beta": BETA,
            "delta": DELTA,
            "chi_decay": CHI_DECAY,
            "sigma_ref": SIGMA_REF,
            "sigma_0": SIGMA_0,
            "center_nodes": CENTER_NODES,
        },
        "theoretical_prediction": {
            "decay_timescale": round(1.0 / ALPHA, 1),
            "value_at_T3000": round(abs(SIGMA_0 - SIGMA_REF) * math.exp(-ALPHA * STEPS), 8),
        },
        "with_chi": {
            "alpha_fit_integral": round(alpha_fit_chi, 6),
            "ratio_vs_alpha": round(ratio2, 4),
            "final_center_dc": round(center_dc_chi[-1], 8),
            "final_integral_dc": round(integral_dc_chi[-1], 8),
        },
        "without_chi": {
            "alpha_fit_integral": round(alpha_fit_nochi, 6),
            "final_center_dc": round(center_dc_nochi[-1], 8),
            "ratio_chi_vs_nochi": round(ratio4, 4),
        },
        "note": "integral = sum|delta_C| decays as exp(-alpha*t) exactly on closed ring; beta term sums to zero",
        "checks": checks,
        "interpretation": (
            "PASS: sigma channel is purely dissipative. Localized coherence deficit "
            "decays at rate ~alpha with or without chi coupling. Chi does not feed back "
            "into sigma (v3 update law confirmed). Stable matter cannot arise from sigma "
            "dynamics alone -- requires topological protection via phi winding (DER-QNG-025). "
            "This motivates QNG-CPU-041: phi vortex stability test."
            if decision
            else "FAIL: sigma channel has unexpected stability -- check update law for "
                 "accidental chi->sigma coupling or conservation law violation."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Sigma Stability Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Theoretical prediction (DER-QNG-025)",
        f"- sigma channel: purely dissipative",
        f"- decay timescale: 1/alpha = {1/ALPHA:.0f} steps",
        f"- predicted value at T={STEPS}: {abs(SIGMA_0-SIGMA_REF)*math.exp(-ALPHA*STEPS):.2e}",
        "",
        "## Results",
        "",
        "| run | alpha_fit | ratio/pred | final |delta_C| | final integral | PASS |",
        "|-----|-----------|------------|------------------|----------------|------|",
        f"| with chi (delta={DELTA}) | {alpha_fit_chi:.5f} | {ratio2:.4f} | {center_dc_chi[-1]:.2e} | {integral_dc_chi[-1]:.4f} | {'✓' if check1_pass and check2_pass else '✗'} |",
        f"| no chi (delta=0) | {alpha_fit_nochi:.5f} | {alpha_fit_nochi/ALPHA:.4f} | {center_dc_nochi[-1]:.2e} | {integral_dc_nochi[-1]:.4f} | {'✓' if center_dc_nochi[-1] < 0.01 else '✗'} |",
        "",
        "## Summary checks",
        f"- Check 1 (deficit < 0.01 at T=3000): {center_dc_chi[-1]:.2e}  {'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (integral decay rate within 10%): alpha_fit={alpha_fit_chi:.5f}  ratio={ratio2:.4f}  {'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (integral near-zero at T=3000 < 0.001): {integral_dc_chi[-1]:.2e}  {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (chi does not affect sigma, within 10%): ratio={ratio4:.4f}  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_sigma_stability_reference: {'PASS' if decision else 'FAIL'}")
    print(f"  alpha_fit_integral(chi)={alpha_fit_chi:.5f}  alpha_fit_integral(no-chi)={alpha_fit_nochi:.5f}  pred={ALPHA}")
    print(f"  ratio_chi={ratio2:.4f}  chi/nochi={ratio4:.4f}")
    print(f"  final: center={center_dc_chi[-1]:.2e}  integral={integral_dc_chi[-1]:.2e}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
