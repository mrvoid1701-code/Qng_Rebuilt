from __future__ import annotations

"""
QNG-CPU-038: Emergent noise -- equilibrium sigma variance matches ring FDT prediction.

Tests DER-QNG-023: for a 1D ring (z=2), the FDT variance formula is:

    Var_ring = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))

Setting Var_ring = alpha (natural variance) gives the derived noise amplitude:

    eta_ring = sqrt(2 * alpha * sqrt(alpha * (alpha + 2*beta)))

Protocol:
  - 200-node ring, no source, homogeneous equilibrium
  - 3 runs: eta=0, eta_ring, 2*eta_ring
  - Collect sigma over last 1000 of 5000 steps (200000 samples)
  - Check Var scales as eta^2 and matches alpha at eta_ring
"""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-emergent-noise-reference-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

N: int = 200
WARMUP_STEPS: int = 4000
COLLECT_STEPS: int = 1000
SEED: int = 20260405

SIGMA_REF: float = 0.5
ALPHA: float = 0.005
BETA: float = 0.35
Z: int = 2   # ring

# ---------------------------------------------------------------------------
# Ring FDT formula
# ---------------------------------------------------------------------------
# Var_ring = eta^2 / (2 * sqrt(alpha * (alpha + 2*beta)))
# Setting Var_ring = alpha:  eta_ring = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta)))

_ring_corr = math.sqrt(ALPHA * (ALPHA + 2.0 * BETA))
ETA_RING: float = math.sqrt(2.0 * ALPHA * _ring_corr)
VAR_PRED: float = ALPHA   # = alpha by construction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def run_sigma(eta: float, seed_offset: int = 0) -> float:
    """Run ring, return sample variance of sigma over last COLLECT_STEPS steps."""
    rng = random.Random(SEED + seed_offset * 9973)
    sigma = [SIGMA_REF] * N
    samples: list[float] = []

    for step in range(WARMUP_STEPS + COLLECT_STEPS):
        new_sigma: list[float] = []
        for i in range(N):
            left = (i - 1) % N
            right = (i + 1) % N
            sigma_bar = (sigma[left] + sigma[right]) / Z
            noise = eta * rng.gauss(0.0, 1.0) if eta > 0 else 0.0
            s = clip01(
                sigma[i]
                - ALPHA * (sigma[i] - SIGMA_REF)
                + BETA * (sigma_bar - sigma[i])
                + noise
            )
            new_sigma.append(s)
        sigma = new_sigma
        if step >= WARMUP_STEPS:
            samples.extend(sigma)

    n_s = len(samples)
    mean_s = sum(samples) / n_s
    return sum((x - mean_s) ** 2 for x in samples) / n_s


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="QNG-CPU-038: emergent noise ring FDT variance test."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"alpha={ALPHA}, beta={BETA}, z={Z}")
    print(f"Ring FDT: eta_ring = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta)))")
    print(f"eta_ring = {ETA_RING:.6f}")
    print(f"Var_pred = alpha = {VAR_PRED}")
    print()

    runs = [("eta0", 0.0), ("eta_ring", ETA_RING), ("eta_2ring", 2.0 * ETA_RING)]
    vars_meas: dict[str, float] = {}

    for i, (label, eta) in enumerate(runs):
        print(f"Running {label} (eta={eta:.6f})...")
        var = run_sigma(eta, seed_offset=i)
        vars_meas[label] = var
        print(f"  Var(sigma) = {var:.6e}")

    var0 = vars_meas["eta0"]
    var_r = vars_meas["eta_ring"]
    var_2r = vars_meas["eta_2ring"]

    # ------------------------------------------------------------------
    # Check 1: deterministic — Var ~ 0
    # ------------------------------------------------------------------
    check1_pass = var0 < 5e-6

    # ------------------------------------------------------------------
    # Check 2: Var(eta_ring) ~ alpha  within 30%
    # ------------------------------------------------------------------
    ratio2 = var_r / VAR_PRED
    check2_pass = abs(ratio2 - 1.0) < 0.30

    # ------------------------------------------------------------------
    # Check 3: Var(2*eta_ring) ~ 4*alpha  within 30%
    # ------------------------------------------------------------------
    ratio3 = var_2r / (4.0 * VAR_PRED)
    check3_pass = abs(ratio3 - 1.0) < 0.30

    # ------------------------------------------------------------------
    # Check 4: algebraic identity (exact)
    # Var formula: eta_ring^2 / (2*sqrt(alpha*(alpha+2*beta))) = alpha
    # ------------------------------------------------------------------
    fdt_lhs = ETA_RING ** 2 / (2.0 * _ring_corr)
    check4_pass = abs(fdt_lhs / VAR_PRED - 1.0) < 1e-10

    checks = {
        "det_var_zero_pass": check1_pass,
        "fdt_ring_variance_match_pass": check2_pass,
        "eta_squared_scaling_pass": check3_pass,
        "ring_fdt_identity_pass": check4_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-038",
        "decision": "pass" if decision else "fail",
        "parameters": {
            "n": N,
            "warmup_steps": WARMUP_STEPS,
            "collect_steps": COLLECT_STEPS,
            "alpha": ALPHA,
            "beta": BETA,
            "z": Z,
            "sigma_ref": SIGMA_REF,
        },
        "predictions": {
            "eta_ring": round(ETA_RING, 8),
            "var_pred": VAR_PRED,
            "fdt_formula": "eta_ring = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta)))",
            "fdt_identity": "eta_ring^2 / (2*sqrt(alpha*(alpha+2*beta))) = alpha",
        },
        "measured_variances": {
            "eta0": round(var0, 10),
            "eta_ring": round(var_r, 8),
            "eta_2ring": round(var_2r, 8),
        },
        "ratios": {
            "var_ring_ratio": round(ratio2, 4),
            "var_2ring_ratio": round(ratio3, 4),
            "fdt_algebraic_lhs": round(fdt_lhs, 10),
        },
        "checks": checks,
        "interpretation": (
            "PASS: equilibrium sigma variance on 1D ring matches ring FDT prediction. "
            "eta = sqrt(2*alpha*sqrt(alpha*(alpha+2*beta))) is the derived noise amplitude. "
            "Noise is emergent from relaxation and relational coupling — not a free parameter."
            if decision
            else "FAIL: variance does not match ring FDT prediction — see individual checks."
        ),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Emergent Noise Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Ring FDT formula",
        f"- eta_ring = sqrt(2 * {ALPHA} * sqrt({ALPHA} * ({ALPHA} + 2*{BETA})))",
        f"- eta_ring = {ETA_RING:.6f}",
        f"- Var_pred = alpha = {VAR_PRED}",
        f"- Ring FDT identity: eta^2 / (2*sqrt(alpha*(alpha+2*beta))) = {fdt_lhs:.8f}",
        "",
        "## Measured variances",
        "",
        "| run | eta | Var_meas | ratio vs expected | check |",
        "|-----|-----|----------|-------------------|-------|",
        f"| eta=0         | 0.000000 | {var0:.2e} | < 5e-6 gate | {'PASS' if check1_pass else 'FAIL'} |",
        f"| eta=eta_ring  | {ETA_RING:.6f} | {var_r:.6f} | {ratio2:.4f} vs 1.0 (alpha={VAR_PRED}) | {'PASS' if check2_pass else 'FAIL'} |",
        f"| eta=2*eta_ring| {2*ETA_RING:.6f} | {var_2r:.6f} | {ratio3:.4f} vs 1.0 (4*alpha={4*VAR_PRED:.4f}) | {'PASS' if check3_pass else 'FAIL'} |",
        "",
        "## Summary checks",
        f"- Check 1 (det Var < 5e-6): {var0:.2e}  {'PASS' if check1_pass else 'FAIL'}",
        f"- Check 2 (ring FDT within 30%): ratio={ratio2:.4f}  {'PASS' if check2_pass else 'FAIL'}",
        f"- Check 3 (eta^2 scaling within 30%): ratio={ratio3:.4f}  {'PASS' if check3_pass else 'FAIL'}",
        f"- Check 4 (algebraic identity): lhs={fdt_lhs:.8f}  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Interpretation",
        report["interpretation"],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nqng_emergent_noise_reference: {'PASS' if decision else 'FAIL'}")
    print(f"  eta_ring={ETA_RING:.6f}  Var_pred={VAR_PRED}")
    print(f"  Var(eta=0)={var0:.2e}  Var(eta_ring)={var_r:.6f}  Var(2*eta_ring)={var_2r:.6f}")
    print(f"  ratio2={ratio2:.4f}  ratio3={ratio3:.4f}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
