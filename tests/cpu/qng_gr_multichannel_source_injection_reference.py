"""QNG-CPU-049 — GR Multi-Channel QM Source Injection.

Tests whether the QM multi-channel current channels (div_J_mis, div_J_mem)
from CPU-046 improve GR tensor fitting (E_xx, E_tt) beyond the existing
4-channel baseline from CPU-030.

4-channel baseline (CPU-030):
    E_μν ≈ a·κ + b·q_src + c·src + d·m_eff
    ratio_e_xx = 0.2996   ratio_e_tt = 0.3328   ratio_split = 0.3162

6-channel extended (this test):
    E_μν ≈ a·κ + b·q_src + c·src + d·m_eff + e·div_J_mis + f·div_J_mem

Pass criteria (from prereg QNG-CPU-049):
    P1: ratio_e_xx(6-ch) < 0.2996  (expected by OLS; tests numerical stability)
    P2: ratio_e_tt(6-ch) < 0.3328  (expected by OLS)
    P3: ratio_split(6-ch) < 0.3162 - 0.005 = 0.3112  (substantial improvement)
    P4: max(|e_mis|, |f_mem|) > 0.1 · |a_geom| in E_tt fit  (significant coupling)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import source_amp_from_rollout
from qng_effective_field_reference import field_extract, mean
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-gr-multichannel-source-injection-reference-v1"
)

# Baseline from CPU-030
RATIO_E_XX_4CH = 0.2996
RATIO_E_TT_4CH = 0.3328
RATIO_SPLIT_4CH = 0.3162
A_GEOM_E_TT_4CH = -6.689  # geometry coeff in E_tt fit (absolute value = 6.689)


# ---------------------------------------------------------------------------
# QM multi-channel currents
# ---------------------------------------------------------------------------

def div_J_grad(
    c: list[float], f: list[float], adj: list[list[int]]
) -> list[float]:
    """Standard gradient divergence current: C_eff_i · Σ_j C_eff_j · (f_j - f_i)."""
    return [
        c[i] * sum(c[j] * (f[j] - f[i]) for j in adj[i])
        for i in range(len(c))
    ]


# ---------------------------------------------------------------------------
# OLS solvers for 4 and 6 columns
# ---------------------------------------------------------------------------

def norm2(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def ols_fit(y: list[float], cols: list[list[float]]) -> dict:
    """Solve OLS: minimize ‖y - X·β‖² with X = cols (list of column vectors).

    Returns coefficients and residual ratio ‖y - X·β‖₂ / ‖y‖₂.
    """
    m = len(cols)
    n = len(y)

    # Normal equations: (Xᵀ X) β = Xᵀ y
    A = [[sum(cols[i][k] * cols[j][k] for k in range(n)) for j in range(m)]
         for i in range(m)]
    b = [sum(y[k] * cols[i][k] for k in range(n)) for i in range(m)]

    # Gaussian elimination with partial pivoting
    aug = [A[i][:] + [b[i]] for i in range(m)]
    for col in range(m):
        max_row = max(range(col, m), key=lambda r: abs(aug[r][col]))
        aug[col], aug[max_row] = aug[max_row], aug[col]
        p = aug[col][col]
        if abs(p) < 1e-15:
            return {"coeffs": [0.0] * m, "ratio": 1.0, "singular": True}
        for k in range(col, m + 1):
            aug[col][k] /= p
        for r in range(m):
            if r == col:
                continue
            f = aug[r][col]
            for k in range(col, m + 1):
                aug[r][k] -= f * aug[col][k]

    coeffs = [aug[i][m] for i in range(m)]
    pred = [sum(coeffs[j] * cols[j][k] for j in range(m)) for k in range(n)]
    raw = norm2(y)
    residual = norm2([y[k] - pred[k] for k in range(n)])
    ratio = residual / raw if raw > 1e-15 else 0.0
    return {"coeffs": coeffs, "ratio": ratio, "singular": False}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    cfg = Config()

    # Run rollout — returns (metrics, state, history, adj)
    _, hist_state, hist_history, adj = run_rollout(cfg, use_history=True)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    phi_hist = hist_state.phi
    mismatch_hist = hist_history.mismatch
    mem_hist = hist_history.mem

    # GR tensor channels (same as CPU-030)
    asm_hist = assemble_linearized_metric(c_hist, phi_hist)
    ten_hist = tensorial_proxy(asm_hist)
    geo_hist = geometry_proxy(c_hist)
    psi_geo = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    br_hist = backreaction_proxy(c_hist, phi_hist, psi_geo)
    src_hist = source_amp_from_rollout(cfg, use_history=True)
    m_hist = matter_proxy(c_hist, l_hist, phi_hist)["m_eff"]
    kappa = geo_hist["kappa"]

    # QM multi-channel currents (new channels from CPU-046)
    dj_mis = div_J_grad(c_hist, mismatch_hist, adj)
    dj_mem = div_J_grad(c_hist, mem_hist, adj)

    # 4-channel baseline
    cols4 = [kappa, br_hist["q_src"], src_hist, m_hist]
    fit4_exx = ols_fit(ten_hist["e_xx"], cols4)
    fit4_ett = ols_fit(ten_hist["e_tt"], cols4)

    # 6-channel extended
    cols6 = [kappa, br_hist["q_src"], src_hist, m_hist, dj_mis, dj_mem]
    fit6_exx = ols_fit(ten_hist["e_xx"], cols6)
    fit6_ett = ols_fit(ten_hist["e_tt"], cols6)

    ratio4_split = (fit4_exx["ratio"] + fit4_ett["ratio"]) / 2.0
    ratio6_split = (fit6_exx["ratio"] + fit6_ett["ratio"]) / 2.0

    # Coefficient names
    names4 = ["kappa", "q_src", "src", "m_eff"]
    names6 = ["kappa", "q_src", "src", "m_eff", "div_J_mis", "div_J_mem"]

    # Pass criteria
    p1_pass = fit6_exx["ratio"] < RATIO_E_XX_4CH
    p2_pass = fit6_ett["ratio"] < RATIO_E_TT_4CH
    p3_pass = ratio6_split < (RATIO_SPLIT_4CH - 0.005)  # substantial: > 0.5% improvement
    # P4: significant QM coupling in E_tt fit
    a_geom_ett = abs(fit6_ett["coeffs"][0])  # kappa coeff in 6-ch E_tt fit
    e_mis = abs(fit6_ett["coeffs"][4])       # div_J_mis coeff
    f_mem = abs(fit6_ett["coeffs"][5])       # div_J_mem coeff
    max_qm_coeff = max(e_mis, f_mem)
    p4_pass = max_qm_coeff > 0.1 * a_geom_ett if a_geom_ett > 1e-10 else False

    n_pass = sum([p1_pass, p2_pass, p3_pass, p4_pass])
    decision = "pass" if n_pass >= 3 else ("partial" if n_pass >= 2 else "fail")

    print("=" * 72)
    print("QNG-CPU-049 — GR Multi-Channel QM Source Injection")
    print("=" * 72)
    print()
    print("4-channel baseline (CPU-030 reference):")
    print(f"  ratio_e_xx = {RATIO_E_XX_4CH:.4f}")
    print(f"  ratio_e_tt = {RATIO_E_TT_4CH:.4f}")
    print(f"  ratio_split = {RATIO_SPLIT_4CH:.4f}")
    print()
    print("4-channel fit (this run):")
    print(f"  ratio_e_xx = {fit4_exx['ratio']:.6f}  coeffs: " +
          " ".join(f"{n}={v:.4f}" for n, v in zip(names4, fit4_exx["coeffs"])))
    print(f"  ratio_e_tt = {fit4_ett['ratio']:.6f}  coeffs: " +
          " ".join(f"{n}={v:.4f}" for n, v in zip(names4, fit4_ett["coeffs"])))
    print()
    print("6-channel extended fit (with div_J_mis, div_J_mem):")
    print(f"  ratio_e_xx = {fit6_exx['ratio']:.6f}  Δ={fit6_exx['ratio']-fit4_exx['ratio']:+.6f}")
    print(f"    coeffs: " + " ".join(f"{n}={v:.4f}" for n, v in zip(names6, fit6_exx["coeffs"])))
    print(f"  ratio_e_tt = {fit6_ett['ratio']:.6f}  Δ={fit6_ett['ratio']-fit4_ett['ratio']:+.6f}")
    print(f"    coeffs: " + " ".join(f"{n}={v:.4f}" for n, v in zip(names6, fit6_ett["coeffs"])))
    print()
    print(f"ratio_split: 4-ch={ratio4_split:.6f}  6-ch={ratio6_split:.6f}  Δ={ratio6_split-ratio4_split:+.6f}")
    print()
    print(f"QM coupling in E_tt: |e_mis|={e_mis:.4f}  |f_mem|={f_mem:.4f}  |a_geom|={a_geom_ett:.4f}")
    print(f"Significance ratio: max(|e|,|f|)/|a_geom| = {max_qm_coeff/a_geom_ett:.4f}" if a_geom_ett > 1e-10 else "  a_geom=0")
    print()
    print(f"P1 (ratio_e_xx(6ch) < {RATIO_E_XX_4CH:.4f}): {'PASS' if p1_pass else 'FAIL'} ({fit6_exx['ratio']:.6f})")
    print(f"P2 (ratio_e_tt(6ch) < {RATIO_E_TT_4CH:.4f}): {'PASS' if p2_pass else 'FAIL'} ({fit6_ett['ratio']:.6f})")
    print(f"P3 (ratio_split < {RATIO_SPLIT_4CH-0.005:.4f}, substantial Δ>0.005): {'PASS' if p3_pass else 'FAIL'} ({ratio6_split:.6f})")
    print(f"P4 (|QM coeff| > 0.1·|a_geom| in E_tt): {'PASS' if p4_pass else 'FAIL'} ({max_qm_coeff:.4f} vs {0.1*a_geom_ett:.4f})")
    print(f"\nDecision: {decision.upper()} ({n_pass}/4 predictions)")

    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "test": "QNG-CPU-049",
        "theory": "DER-BRIDGE-031",
        "decision": decision,
        "n_pass": n_pass,
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_pass": p3_pass,
        "p4_pass": p4_pass,
        "ratio4_exx": fit4_exx["ratio"],
        "ratio4_ett": fit4_ett["ratio"],
        "ratio4_split": ratio4_split,
        "ratio6_exx": fit6_exx["ratio"],
        "ratio6_ett": fit6_ett["ratio"],
        "ratio6_split": ratio6_split,
        "delta_exx": fit6_exx["ratio"] - fit4_exx["ratio"],
        "delta_ett": fit6_ett["ratio"] - fit4_ett["ratio"],
        "delta_split": ratio6_split - ratio4_split,
        "fit4_exx_coeffs": dict(zip(names4, fit4_exx["coeffs"])),
        "fit4_ett_coeffs": dict(zip(names4, fit4_ett["coeffs"])),
        "fit6_exx_coeffs": dict(zip(names6, fit6_exx["coeffs"])),
        "fit6_ett_coeffs": dict(zip(names6, fit6_ett["coeffs"])),
        "qm_coupling_ett": {
            "e_mis_abs": e_mis,
            "f_mem_abs": f_mem,
            "a_geom_abs": a_geom_ett,
            "max_qm_over_geom": max_qm_coeff / a_geom_ett if a_geom_ett > 1e-10 else 0.0,
        },
    }
    with open(out_dir / "report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {out_dir / 'report.json'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    main(args.out_dir)
