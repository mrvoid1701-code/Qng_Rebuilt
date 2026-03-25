from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout
from qng_qm_coherence_proxy_reference import coherence_proxy
from qng_geometry_estimator_reference import periodic_grad


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-backreaction-closure-reference-v1"


def backreaction_proxy(c_eff: list[float], phi: list[float], psi_geo: list[float], zeta: float = 0.5, beta: float = 0.02):
    qm = coherence_proxy(c_eff, phi)
    q_src = [g * (1.0 + zeta * abs(j)) for g, j in zip(qm["corr_mag"], qm["corr_im"])]
    q_mean = mean(q_src)
    q_ctr = [q - q_mean for q in q_src]
    psi_br = [p + beta * q for p, q in zip(psi_geo, q_ctr)]
    a_br = [-x for x in periodic_grad(psi_br)]
    return {
        "q_src": q_src,
        "q_ctr": q_ctr,
        "psi_br": psi_br,
        "a_br": a_br,
        "corr_im": qm["corr_im"],
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG back-reaction closure CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, _ = field_extract(hist_state, hist_history)
    c_nohist, _ = field_extract(nohist_state, nohist_history)
    weak_hist = weakfield_proxy(c_hist)
    weak_nohist = weakfield_proxy(c_nohist)

    br_hist = backreaction_proxy(c_hist, hist_state.phi, weak_hist["psi"])
    br_nohist = backreaction_proxy(c_nohist, nohist_state.phi, weak_nohist["psi"])
    br_phase_frozen = backreaction_proxy(c_hist, [0.0] * len(hist_state.phi), weak_hist["psi"])

    checks = {
        "bounded_pass": max_abs(br_hist["psi_br"]) < 0.1 and max_abs(br_hist["a_br"]) < 0.1,
        "closure_nontrivial_pass": l1_diff(br_hist["psi_br"], weak_hist["psi"]) > 0.01,
        "quantum_phase_sensitivity_pass": l1_diff(br_hist["q_src"], br_phase_frozen["q_src"]) > 0.05,
        "history_imprint_pass": l1_diff(br_hist["psi_br"], br_nohist["psi_br"]) > 0.05,
        "transport_imprint_pass": mean([abs(x) for x in br_hist["corr_im"]]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-012",
        "decision": "pass" if decision else "fail",
        "max_abs": {
            "psi_br": max_abs(br_hist["psi_br"]),
            "a_br": max_abs(br_hist["a_br"]),
        },
        "means": {
            "q_src_history_mean": mean(br_hist["q_src"]),
            "psi_br_history_mean": mean(br_hist["psi_br"]),
            "corr_im_abs_history_mean": mean([abs(x) for x in br_hist["corr_im"]]),
        },
        "differences": {
            "psi_br_l1_vs_geo_only": l1_diff(br_hist["psi_br"], weak_hist["psi"]),
            "q_src_l1_phase_vs_frozen": l1_diff(br_hist["q_src"], br_phase_frozen["q_src"]),
            "psi_br_l1_history_vs_present_only": l1_diff(br_hist["psi_br"], br_nohist["psi_br"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Back-Reaction Closure v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- max_abs_psi_br: `{report['max_abs']['psi_br']:.6f}`",
        f"- max_abs_a_br: `{report['max_abs']['a_br']:.6f}`",
        f"- q_src_history_mean: `{report['means']['q_src_history_mean']:.6f}`",
        f"- corr_im_abs_history_mean: `{report['means']['corr_im_abs_history_mean']:.6f}`",
        f"- psi_br_l1(vs geo only): `{report['differences']['psi_br_l1_vs_geo_only']:.6f}`",
        f"- q_src_l1(phase vs frozen): `{report['differences']['q_src_l1_phase_vs_frozen']:.6f}`",
        f"- psi_br_l1(history vs present-only): `{report['differences']['psi_br_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_backreaction_closure_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
