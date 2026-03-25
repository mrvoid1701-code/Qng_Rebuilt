from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_qm_continuity_assembly_reference import current_divergence, rollout_pair
from qng_qm_coherence_proxy_reference import coherence_proxy
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-density-source-balance-reference-v1"


def source_balance_fit(d_rho: list[float], div_j: list[float], source: list[float]):
    aa = sum(x * x for x in div_j)
    bb = sum(x * y for x, y in zip(div_j, source))
    cc = sum(y * y for y in source)
    rhs_a = -sum(x * y for x, y in zip(d_rho, div_j))
    rhs_c = sum(x * y for x, y in zip(d_rho, source))
    det = aa * cc - bb * bb

    if abs(det) < 1e-15:
        kappa = 0.0
        sigma = 0.0
    else:
        kappa = (rhs_a * cc - bb * rhs_c) / det
        sigma = (aa * rhs_c - bb * rhs_a) / det

    residual = [dr - sigma * s + kappa * dj for dr, s, dj in zip(d_rho, source, div_j)]
    raw_l2 = sum(x * x for x in d_rho) ** 0.5
    residual_l2 = sum(x * x for x in residual) ** 0.5
    return {
        "kappa": kappa,
        "sigma": sigma,
        "residual": residual,
        "raw_l2": raw_l2,
        "residual_l2": residual_l2,
        "improvement_ratio": 0.0 if raw_l2 == 0.0 else residual_l2 / raw_l2,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM density source balance CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(__import__("qng_native_update_reference").Config(), use_history=True)
    state_nt, hist_nt, state_ntp1, hist_ntp1 = rollout_pair(__import__("qng_native_update_reference").Config(), use_history=False)

    rho_t, _ = field_extract(state_t, hist_t)
    rho_tp1, _ = field_extract(state_tp1, hist_tp1)
    rho_nt, _ = field_extract(state_nt, hist_nt)
    rho_ntp1, _ = field_extract(state_ntp1, hist_ntp1)

    psi_t = psi_from_state(rho_t, state_t.phi)
    psi_tp1 = psi_from_state(rho_tp1, state_tp1.phi)
    psi_nt = psi_from_state(rho_nt, state_nt.phi)
    psi_ntp1 = psi_from_state(rho_ntp1, state_ntp1.phi)

    gen_hist = generator_proxy(psi_t, psi_tp1)
    gen_nohist = generator_proxy(psi_nt, psi_ntp1)
    qm_hist = coherence_proxy(rho_t, state_t.phi)
    qm_nohist = coherence_proxy(rho_nt, state_nt.phi)

    d_rho_hist = [b - a for a, b in zip(rho_t, rho_tp1)]
    d_rho_nohist = [b - a for a, b in zip(rho_nt, rho_ntp1)]
    source_hist = [r * (math.exp(2.0 * a) - 1.0) for a, r in zip(gen_hist["a_loc"], rho_t)]
    source_nohist = [r * (math.exp(2.0 * a) - 1.0) for a, r in zip(gen_nohist["a_loc"], rho_nt)]
    div_j_hist = current_divergence(qm_hist["corr_im"])
    div_j_nohist = current_divergence(qm_nohist["corr_im"])

    residual_direct_hist = [dr - s for dr, s in zip(d_rho_hist, source_hist)]
    residual_direct_nohist = [dr - s for dr, s in zip(d_rho_nohist, source_nohist)]
    raw_hist = sum(x * x for x in d_rho_hist) ** 0.5
    raw_nohist = sum(x * x for x in d_rho_nohist) ** 0.5
    fit_hist = source_balance_fit(d_rho_hist, div_j_hist, source_hist)
    fit_nohist = source_balance_fit(d_rho_nohist, div_j_nohist, source_nohist)

    checks = {
        "direct_source_reconstruction_pass": (sum(x * x for x in residual_direct_hist) ** 0.5) / raw_hist < 1e-10,
        "direct_source_present_only_pass": (sum(x * x for x in residual_direct_nohist) ** 0.5) / raw_nohist < 1e-10,
        "source_nontrivial_pass": mean([abs(x) for x in source_hist]) > 1e-4,
        "transport_subleading_pass": abs(fit_hist["sigma"] - 1.0) < 0.02 and abs(fit_hist["kappa"]) < 1e-3,
        "history_imprint_pass": l1_diff(source_hist, source_nohist) > 0.01,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-023",
        "decision": "pass" if decision else "fail",
        "direct_balance": {
            "history_ratio": 0.0 if raw_hist == 0.0 else (sum(x * x for x in residual_direct_hist) ** 0.5) / raw_hist,
            "present_only_ratio": 0.0 if raw_nohist == 0.0 else (sum(x * x for x in residual_direct_nohist) ** 0.5) / raw_nohist,
        },
        "fit_history": {
            "kappa": fit_hist["kappa"],
            "sigma": fit_hist["sigma"],
            "improvement_ratio": fit_hist["improvement_ratio"],
        },
        "fit_present_only": {
            "kappa": fit_nohist["kappa"],
            "sigma": fit_nohist["sigma"],
            "improvement_ratio": fit_nohist["improvement_ratio"],
        },
        "means": {
            "source_abs_history_mean": mean([abs(x) for x in source_hist]),
            "div_j_abs_history_mean": mean([abs(x) for x in div_j_hist]),
        },
        "differences": {
            "source_l1_history_vs_present_only": l1_diff(source_hist, source_nohist),
            "div_j_l1_history_vs_present_only": l1_diff(div_j_hist, div_j_nohist),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Density Source Balance v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- direct_ratio_history: `{report['direct_balance']['history_ratio']:.6e}`",
        f"- direct_ratio_present_only: `{report['direct_balance']['present_only_ratio']:.6e}`",
        f"- kappa_history: `{report['fit_history']['kappa']:.6e}`",
        f"- sigma_history: `{report['fit_history']['sigma']:.6f}`",
        f"- fit_ratio_history: `{report['fit_history']['improvement_ratio']:.6e}`",
        f"- source_abs_history_mean: `{report['means']['source_abs_history_mean']:.6f}`",
        f"- div_j_abs_history_mean: `{report['means']['div_j_abs_history_mean']:.6f}`",
        f"- source_l1(history vs present-only): `{report['differences']['source_l1_history_vs_present_only']:.6f}`",
        f"- div_j_l1(history vs present-only): `{report['differences']['div_j_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_density_source_balance_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
