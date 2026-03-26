from __future__ import annotations

import argparse
import cmath
import json
import math
import random
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import bridge_v2, source_amp_from_rollout
from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_matter_sector_proxy_reference import matter_proxy
from qng_native_update_reference import Config, build_graph, init_state, one_step, run_rollout
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state
from qng_qm_operator_assembly_reference import (
    diagonal_operator,
    matvec,
    transport_operator,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-gr-backreaction-closure-v3-reference-v1"


def propagator_dressing_excess(cfg: Config, use_history: bool) -> list[float]:
    """Per-node amplitude excess of dressed propagator over diagonal propagator."""
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
    state_t = state
    history_t = history
    state_t1, history_t1 = one_step(state_t, history_t, adj, cfg, use_history=use_history)

    c_t, _ = field_extract(state_t, history_t)
    c_t1, _ = field_extract(state_t1, history_t1)
    phi_t = state_t.phi
    phi_t1 = state_t1.phi

    psi_t = psi_from_state(c_t, phi_t)
    psi_t1 = psi_from_state(c_t1, phi_t1)
    gen = generator_proxy(psi_t, psi_t1)

    p_diag = diagonal_operator(
        [cmath.exp(complex(a, w)) for a, w in zip(gen["a_loc"], gen["omega_loc"])]
    )
    t_eff = transport_operator(adj)
    lam = 0.10
    p_mix = []
    for i, row in enumerate(t_eff):
        factor = p_diag[i][i]
        p_mix.append([factor * ((1.0 if i == j else 0.0) + lam * row[j]) for j in range(len(row))])

    psi_diag = matvec(p_diag, psi_t)
    psi_mix = matvec(p_mix, psi_t)

    return [abs(pm) - abs(pd) for pm, pd in zip(psi_mix, psi_diag)]


def bridge_v3(
    psi_br2: list[float],
    p_delta: list[float],
    beta_p: float = 0.05,
) -> dict:
    p_mean = mean(p_delta)
    p_ctr = [p - p_mean for p in p_delta]
    psi_br3 = [p2 + beta_p * pc for p2, pc in zip(psi_br2, p_ctr)]
    a_br3 = [-x for x in periodic_grad(psi_br3)]
    return {"psi_br3": psi_br3, "a_br3": a_br3, "p_ctr": p_ctr}


def fit_four_cols(y: list[float], cols: list[list[float]]) -> dict:
    m = len(cols)
    n = len(y)
    mat = [[sum(cols[i][k] * cols[j][k] for k in range(n)) for j in range(m)] for i in range(m)]
    rhs = [sum(y[k] * cols[i][k] for k in range(n)) for i in range(m)]
    aug = [row[:] + [b] for row, b in zip(mat, rhs)]
    for i in range(m):
        piv = max(range(i, m), key=lambda r: abs(aug[r][i]))
        aug[i], aug[piv] = aug[piv], aug[i]
        if abs(aug[i][i]) < 1e-15:
            return {"coeffs": [0.0] * m, "ratio": 1.0}
        p = aug[i][i]
        for j in range(i, m + 1):
            aug[i][j] /= p
        for r in range(m):
            if r == i:
                continue
            f = aug[r][i]
            for j in range(i, m + 1):
                aug[r][j] -= f * aug[i][j]
    coeffs = [aug[i][m] for i in range(m)]
    pred = [sum(c * cols[j][k] for j, c in enumerate(coeffs)) for k in range(n)]
    raw = sum(v * v for v in y) ** 0.5
    residual = sum((u - v) ** 2 for u, v in zip(y, pred)) ** 0.5
    return {"coeffs": coeffs, "ratio": 0.0 if raw == 0.0 else residual / raw}


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG GR backreaction closure v3 CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    c_hist, l_hist = field_extract(hist_state, hist_history)
    c_nohist, l_nohist = field_extract(nohist_state, nohist_history)

    geo_hist = geometry_proxy(c_hist)
    geo_nohist = geometry_proxy(c_nohist)
    psi_geo_hist = [0.5 * x - 0.5 for x in geo_hist["g00"]]
    psi_geo_nohist = [0.5 * x - 0.5 for x in geo_nohist["g00"]]

    src_hist = source_amp_from_rollout(cfg, use_history=True)
    src_nohist = source_amp_from_rollout(cfg, use_history=False)

    br2_hist = bridge_v2(c_hist, hist_state.phi, psi_geo_hist, src_hist)
    br2_nohist = bridge_v2(c_nohist, nohist_state.phi, psi_geo_nohist, src_nohist)

    p_delta_hist = propagator_dressing_excess(cfg, use_history=True)
    p_delta_nohist = propagator_dressing_excess(cfg, use_history=False)

    v3_hist = bridge_v3(br2_hist["psi_br2"], p_delta_hist)
    v3_nohist = bridge_v3(br2_nohist["psi_br2"], p_delta_nohist)

    # tensor components
    asm_hist = assemble_linearized_metric(c_hist, hist_state.phi)
    ten_hist = tensorial_proxy(asm_hist)

    br1_hist = backreaction_proxy(c_hist, hist_state.phi, psi_geo_hist)
    kappa = geo_hist["kappa"]
    q_src = br1_hist["q_src"]
    m_eff = matter_proxy(c_hist, l_hist, hist_state.phi)["m_eff"]

    # 3-channel fit (without P_delta) — baseline for comparison
    fit_exx_3ch = fit_four_cols(ten_hist["e_xx"], [kappa, q_src, src_hist])
    # 4-channel fit (with P_delta)
    fit_exx_4ch = fit_four_cols(ten_hist["e_xx"], [kappa, q_src, src_hist, p_delta_hist])
    fit_ett_4ch = fit_four_cols(ten_hist["e_tt"], [kappa, q_src, src_hist, p_delta_hist])

    e_xx_4ch = fit_exx_4ch["coeffs"][3]   # P_delta coefficient for E_xx
    e_tt_4ch = fit_ett_4ch["coeffs"][3]   # P_delta coefficient for E_tt

    checks = {
        "psi_br3_bounded_pass": max_abs(v3_hist["psi_br3"]) < 0.15,
        "psi_br3_nontrivial_pass": l1_diff(v3_hist["psi_br3"], br2_hist["psi_br2"]) > 5e-4,
        "e_xx_prop_coeff_nonzero_pass": abs(e_xx_4ch) > 1e-3,
        "e_tt_e_xx_coeff_differ_pass": abs(e_xx_4ch - e_tt_4ch) > 1e-3,
        "fit_4ch_improves_3ch_pass": fit_exx_4ch["ratio"] < fit_exx_3ch["ratio"],
        "history_imprint_pass": l1_diff(v3_hist["psi_br3"], v3_nohist["psi_br3"]) > 0.05,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-031",
        "decision": "pass" if decision else "fail",
        "psi_br3": {
            "max_abs": max_abs(v3_hist["psi_br3"]),
            "l1_vs_br2": l1_diff(v3_hist["psi_br3"], br2_hist["psi_br2"]),
            "l1_history_vs_nohist": l1_diff(v3_hist["psi_br3"], v3_nohist["psi_br3"]),
        },
        "fit_ratios": {
            "e_xx_3ch": fit_exx_3ch["ratio"],
            "e_xx_4ch": fit_exx_4ch["ratio"],
            "e_tt_4ch": fit_ett_4ch["ratio"],
        },
        "propagator_coefficients": {
            "e_xx_p_delta": e_xx_4ch,
            "e_tt_p_delta": e_tt_4ch,
            "abs_diff": abs(e_xx_4ch - e_tt_4ch),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Back-Reaction Closure v3",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- psi_br3_max_abs: `{report['psi_br3']['max_abs']:.6f}`",
        f"- psi_br3_l1(vs br2): `{report['psi_br3']['l1_vs_br2']:.6e}`",
        f"- psi_br3_l1(history vs nohist): `{report['psi_br3']['l1_history_vs_nohist']:.6f}`",
        f"- ratio_e_xx_3ch: `{report['fit_ratios']['e_xx_3ch']:.6f}`",
        f"- ratio_e_xx_4ch: `{report['fit_ratios']['e_xx_4ch']:.6f}`",
        f"- ratio_e_tt_4ch: `{report['fit_ratios']['e_tt_4ch']:.6f}`",
        f"- e_xx P_delta coeff: `{report['propagator_coefficients']['e_xx_p_delta']:.6f}`",
        f"- e_tt P_delta coeff: `{report['propagator_coefficients']['e_tt_p_delta']:.6f}`",
        f"- |e_xx - e_tt|: `{report['propagator_coefficients']['abs_diff']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_backreaction_closure_v3_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
