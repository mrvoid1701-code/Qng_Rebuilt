from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import source_amp_from_rollout
from qng_effective_field_reference import field_extract
from qng_geometry_estimator_reference import geometry_proxy
from qng_gr_backreaction_closure_v3_reference import fit_four_cols, propagator_dressing_excess
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-einstein-equations-proxy-reference-v1"


def mean(v: list[float]) -> float:
    return sum(v) / len(v) if v else 0.0


def correlation(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = mean(a), mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    std_a = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    std_b = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (std_a * std_b) if std_a * std_b > 1e-15 else 0.0


def equation_of_state(e_tt: list[float], e_xx: list[float]) -> float:
    """OLS estimate: E_xx ~ w_eff * E_tt."""
    stt = sum(t * t for t in e_tt)
    sxt = sum(x * t for x, t in zip(e_xx, e_tt))
    return sxt / stt if stt > 1e-20 else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG Einstein equations proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)

    asm_hist = assemble_linearized_metric(c_hist, hist_state.phi)
    asm_nohist = assemble_linearized_metric(c_nohist, nohist_state.phi)

    ten_hist = tensorial_proxy(asm_hist)
    ten_nohist = tensorial_proxy(asm_nohist)

    e_tt_hist = ten_hist["e_tt"]
    e_xx_hist = ten_hist["e_xx"]
    e_tt_nohist = ten_nohist["e_tt"]
    e_xx_nohist = ten_nohist["e_xx"]

    corr_hist = correlation(e_tt_hist, e_xx_hist)
    corr_nohist = correlation(e_tt_nohist, e_xx_nohist)
    w_hist = equation_of_state(e_tt_hist, e_xx_hist)
    w_nohist = equation_of_state(e_tt_nohist, e_xx_nohist)

    # 4-channel fit for E_tt (history)
    geo_hist = geometry_proxy(c_hist)
    psi_geo_hist = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    br_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    src_hist = source_amp_from_rollout(cfg, use_history=True)
    p_delta_hist = propagator_dressing_excess(cfg, use_history=True)
    fit_4ch_tt = fit_four_cols(
        e_tt_hist,
        [geo_hist["kappa"], br_hist["q_src"], src_hist, p_delta_hist],
    )

    checks = {
        "anticorrelation_pass": corr_hist < -0.8,
        "equation_of_state_pass": -1.5 < w_hist < -0.5,
        "history_sharpens_corr_pass": abs(corr_hist) > abs(corr_nohist),
        "history_shifts_eos_pass": abs(w_hist - w_nohist) > 0.1,
        "fit_4ch_tt_pass": fit_4ch_tt["ratio"] < 0.5,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-035",
        "decision": "pass" if decision else "fail",
        "history": {
            "corr_e_tt_e_xx": corr_hist,
            "w_eff": w_hist,
        },
        "no_history": {
            "corr_e_tt_e_xx": corr_nohist,
            "w_eff": w_nohist,
        },
        "delta_w": w_hist - w_nohist,
        "fit_4ch_tt_ratio": fit_4ch_tt["ratio"],
        "fit_4ch_tt_coeffs": fit_4ch_tt["coeffs"],
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Einstein Equations Proxy",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- corr(E_tt, E_xx) history: `{corr_hist:.6f}`",
        f"- corr(E_tt, E_xx) no-history: `{corr_nohist:.6f}`",
        f"- w_eff (history): `{w_hist:.6f}`",
        f"- w_eff (no-history): `{w_nohist:.6f}`",
        f"- delta_w (hist - nohist): `{w_hist - w_nohist:.6f}`",
        f"- 4ch fit ratio E_tt: `{fit_4ch_tt['ratio']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_einstein_equations_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
