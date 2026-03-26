from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import source_amp_from_rollout
from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_lap
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-tensorial-assembly-reference-v1"


def tensorial_proxy(asm: dict[str, list[float]]) -> dict[str, list[float]]:
    lap_xx = periodic_lap(asm["h_xx"])
    lap_tt = periodic_lap(asm["h_tt"])
    e_tt = lap_xx                                                    # time-time component
    e_xx = lap_tt                                                    # space-space component
    e_trace = [a + b for a, b in zip(e_tt, e_xx)]
    e_traceless_tt = [a - 0.5 * t for a, t in zip(e_tt, e_trace)]
    r_lin_check = [a - b for a, b in zip(e_xx, e_tt)]              # should match existing R_lin
    return {
        "e_tt": e_tt,
        "e_xx": e_xx,
        "e_trace": e_trace,
        "e_traceless_tt": e_traceless_tt,
        "r_lin_check": r_lin_check,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def mean_abs(values: list[float]) -> float:
    return sum(abs(x) for x in values) / len(values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG GR tensorial assembly proxy CPU test.")
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

    # source channels
    geo_hist = geometry_proxy(c_hist)
    psi_geo_hist = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    br_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    src_hist = source_amp_from_rollout(cfg, use_history=True)
    m_hist = matter_proxy(c_hist, l_hist, hist_state.phi)["m_eff"]

    # differential alignment: E_xx vs E_tt correlation with each source
    corr_exx_qsrc = centered_corr(ten_hist["e_xx"], br_hist["q_src"])
    corr_ett_qsrc = centered_corr(ten_hist["e_tt"], br_hist["q_src"])
    corr_exx_meff = centered_corr(ten_hist["e_xx"], m_hist)
    corr_ett_meff = centered_corr(ten_hist["e_tt"], m_hist)

    checks = {
        "e_tt_bounded_pass": max_abs(ten_hist["e_tt"]) < 0.25,
        "e_xx_bounded_pass": max_abs(ten_hist["e_xx"]) < 0.25,
        "components_differ_pass": l1_diff(ten_hist["e_tt"], ten_hist["e_xx"]) > 0.10,
        "e_xx_more_transport_pass": corr_exx_qsrc > corr_ett_qsrc,
        "e_components_opposite_sign_pass": corr_exx_qsrc - corr_ett_qsrc > 0.10,
        "traceless_nontrivial_pass": mean_abs(ten_hist["e_traceless_tt"]) > 0.001,
        "e_tt_history_imprint_pass": l1_diff(ten_hist["e_tt"], ten_nohist["e_tt"]) > 0.05,
        "e_xx_history_imprint_pass": l1_diff(ten_hist["e_xx"], ten_nohist["e_xx"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-029",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "e_tt": max_abs(ten_hist["e_tt"]),
            "e_xx": max_abs(ten_hist["e_xx"]),
            "e_trace": max_abs(ten_hist["e_trace"]),
            "e_traceless_tt": max_abs(ten_hist["e_traceless_tt"]),
        },
        "mean_abs": {
            "e_traceless_tt": mean_abs(ten_hist["e_traceless_tt"]),
        },
        "correlations": {
            "corr_e_xx_q_src": corr_exx_qsrc,
            "corr_e_tt_q_src": corr_ett_qsrc,
            "corr_e_xx_m_eff": corr_exx_meff,
            "corr_e_tt_m_eff": corr_ett_meff,
        },
        "differences": {
            "e_tt_vs_e_xx_l1": l1_diff(ten_hist["e_tt"], ten_hist["e_xx"]),
            "e_tt_history_vs_nohist_l1": l1_diff(ten_hist["e_tt"], ten_nohist["e_tt"]),
            "e_xx_history_vs_nohist_l1": l1_diff(ten_hist["e_xx"], ten_nohist["e_xx"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Tensorial Assembly Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- max_abs_e_tt: `{report['max_abs']['e_tt']:.6f}`",
        f"- max_abs_e_xx: `{report['max_abs']['e_xx']:.6f}`",
        f"- e_tt_vs_e_xx_l1: `{report['differences']['e_tt_vs_e_xx_l1']:.6f}`",
        f"- corr_e_xx_q_src: `{report['correlations']['corr_e_xx_q_src']:.6f}`",
        f"- corr_e_tt_q_src: `{report['correlations']['corr_e_tt_q_src']:.6f}`",
        f"- corr_e_xx_m_eff: `{report['correlations']['corr_e_xx_m_eff']:.6f}`",
        f"- corr_e_tt_m_eff: `{report['correlations']['corr_e_tt_m_eff']:.6f}`",
        f"- mean_abs_e_traceless_tt: `{report['mean_abs']['e_traceless_tt']:.6f}`",
        f"- e_tt_history_l1: `{report['differences']['e_tt_history_vs_nohist_l1']:.6f}`",
        f"- e_xx_history_l1: `{report['differences']['e_xx_history_vs_nohist_l1']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_tensorial_assembly_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
