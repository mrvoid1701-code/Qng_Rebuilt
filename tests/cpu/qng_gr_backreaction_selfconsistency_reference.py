from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from qng_backreaction_closure_reference import backreaction_proxy
from qng_bridge_closure_v2_reference import bridge_v2, source_amp_from_rollout
from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_geometry_estimator_reference import geometry_proxy, periodic_grad
from qng_gr_backreaction_closure_v3_reference import bridge_v3, fit_four_cols, propagator_dressing_excess
from qng_gr_tensorial_assembly_reference import tensorial_proxy
from qng_gr_linearized_assembly_reference import assemble_linearized_metric
from qng_native_update_reference import (
    Config,
    History,
    State,
    build_graph,
    clone_history,
    clone_state,
    init_state,
    one_step,
    run_rollout,
)
from qng_qm_generator_assembly_reference import psi_from_state


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-gr-backreaction-selfconsistency-reference-v1"
)

EPSILON = 0.10


def rollout_from_perturbed_phi(
    cfg: Config,
    phi_pert: list[float],
    use_history: bool,
) -> tuple[State, History, list[list[int]]]:
    """Run a full rollout from an initial state whose phi has been replaced by phi_pert."""
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)

    # replace phi with the perturbed version
    state = State(state.sigma[:], state.chi[:], phi_pert[:])

    for _ in range(cfg.steps):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)

    return state, history, adj


def compute_psi_br3(
    state: State,
    history: History,
    cfg: Config,
    use_history: bool,
) -> list[float]:
    c, l_eff = field_extract(state, history)
    phi = state.phi
    geo = geometry_proxy(c)
    psi_geo = [0.5 * x - 0.5 for x in geo["g00"]]

    src = source_amp_from_rollout(cfg, use_history=use_history)
    br2 = bridge_v2(c, phi, psi_geo, src)

    p_delta = propagator_dressing_excess(cfg, use_history=use_history)
    br3 = bridge_v3(br2["psi_br2"], p_delta)

    return br3["psi_br3"]


def compute_tensor_fit_coeff(
    state: State,
    history: History,
    cfg: Config,
    use_history: bool,
) -> dict:
    c, l_eff = field_extract(state, history)
    phi = state.phi
    geo = geometry_proxy(c)
    psi_geo = [0.5 * x - 0.5 for x in geo["g00"]]
    kappa = geo["kappa"]

    src = source_amp_from_rollout(cfg, use_history=use_history)
    br1 = backreaction_proxy(c, phi, psi_geo)
    q_src = br1["q_src"]
    p_delta = propagator_dressing_excess(cfg, use_history=use_history)

    asm = assemble_linearized_metric(c, phi)
    ten = tensorial_proxy(asm)

    fit_exx = fit_four_cols(ten["e_xx"], [kappa, q_src, src, p_delta])
    fit_ett = fit_four_cols(ten["e_tt"], [kappa, q_src, src, p_delta])

    return {
        "e_xx": fit_exx["coeffs"][3],
        "e_tt": fit_ett["coeffs"][3],
    }


def l1_norm(v: list[float]) -> float:
    return sum(abs(x) for x in v)


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG GR back-reaction self-consistency CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()

    # ── 1. Baseline rollout ──────────────────────────────────────────────────
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    # baseline Psi_BR3 (history and no-history)
    psi_br3_hist = compute_psi_br3(hist_state, hist_history, cfg, use_history=True)
    psi_br3_nohist = compute_psi_br3(nohist_state, nohist_history, cfg, use_history=False)

    # baseline tensorial coefficients
    coeffs_base = compute_tensor_fit_coeff(hist_state, hist_history, cfg, use_history=True)

    # ── 2. Perturbed initial phi ─────────────────────────────────────────────
    # reproduce the same initial phi used in run_rollout
    rng0 = random.Random(cfg.seed)
    adj0 = build_graph(cfg.n_nodes, rng0)
    init0, _ = init_state(cfg.n_nodes, rng0)
    phi_0 = init0.phi

    phi_pert_hist = [p + EPSILON * br for p, br in zip(phi_0, psi_br3_hist)]
    phi_pert_nohist = [p + EPSILON * br for p, br in zip(phi_0, psi_br3_nohist)]

    # ── 3. Perturbed rollouts ────────────────────────────────────────────────
    pert_state_hist, pert_hist_history, _ = rollout_from_perturbed_phi(cfg, phi_pert_hist, use_history=True)
    pert_state_nohist, pert_nohist_history, _ = rollout_from_perturbed_phi(cfg, phi_pert_nohist, use_history=False)

    psi_br3_prime_hist = compute_psi_br3(pert_state_hist, pert_hist_history, cfg, use_history=True)
    psi_br3_prime_nohist = compute_psi_br3(pert_state_nohist, pert_nohist_history, cfg, use_history=False)

    # perturbed tensorial coefficients
    coeffs_pert = compute_tensor_fit_coeff(pert_state_hist, pert_hist_history, cfg, use_history=True)

    # ── 4. Self-consistency metrics ──────────────────────────────────────────
    delta_br = [p - b for p, b in zip(psi_br3_prime_hist, psi_br3_hist)]
    l1_delta = l1_norm(delta_br)
    l1_base = l1_norm(psi_br3_hist)
    gamma = l1_delta / (EPSILON * l1_base) if l1_base > 0 else float("inf")

    # history imprint on perturbed closure
    l1_hist_imprint = l1_diff(psi_br3_prime_hist, psi_br3_prime_nohist)

    # ── 5. Checks ────────────────────────────────────────────────────────────
    checks = {
        "response_nontrivial_pass": l1_delta > 1e-5,
        "contraction_pass": gamma < 1.0,
        "e_xx_sign_preserved_pass": coeffs_pert["e_xx"] < 0,    # baseline was -1.48
        "e_tt_sign_preserved_pass": coeffs_pert["e_tt"] > 0,    # baseline was +0.88
        "history_imprint_survives_pass": l1_hist_imprint > 0.03,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-032",
        "decision": "pass" if decision else "fail",
        "epsilon": EPSILON,
        "l1_delta_br": l1_delta,
        "l1_psi_br3_base": l1_base,
        "gamma": gamma,
        "l1_hist_imprint_perturbed": l1_hist_imprint,
        "tensor_coefficients": {
            "baseline_e_xx": coeffs_base["e_xx"],
            "baseline_e_tt": coeffs_base["e_tt"],
            "perturbed_e_xx": coeffs_pert["e_xx"],
            "perturbed_e_tt": coeffs_pert["e_tt"],
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG GR Back-Reaction Self-Consistency",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- epsilon: `{EPSILON}`",
        f"- L1(delta_BR): `{l1_delta:.6e}`",
        f"- L1(Psi_BR3_base): `{l1_base:.6f}`",
        f"- gamma (contraction ratio): `{gamma:.6f}`",
        f"- hist_imprint_perturbed: `{l1_hist_imprint:.6f}`",
        f"- baseline e_xx: `{coeffs_base['e_xx']:.6f}`",
        f"- perturbed e_xx: `{coeffs_pert['e_xx']:.6f}`",
        f"- baseline e_tt: `{coeffs_base['e_tt']:.6f}`",
        f"- perturbed e_tt: `{coeffs_pert['e_tt']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_gr_backreaction_selfconsistency_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
