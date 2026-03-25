from __future__ import annotations

import argparse
import cmath
import json
import random
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, build_graph, init_state, one_step
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state
from qng_qm_operator_assembly_reference import (
    diagonal_operator,
    matsub,
    matmul,
    matvec,
    max_row_sum,
    transport_operator,
)
from qng_qm_propagator_proxy_reference import complex_l1, overlap_score


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-propagator-composition-reference-v1"


def mat_l1(matrix: list[list[complex]]) -> float:
    return sum(abs(x) for row in matrix for x in row)


def rollout_triplet(cfg: Config, use_history: bool, freeze_phase: bool = False):
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 2):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)

    state_t = state
    history_t = history
    state_tp1, history_tp1 = one_step(state_t, history_t, adj, cfg, use_history=use_history)
    state_tp2, history_tp2 = one_step(state_tp1, history_tp1, adj, cfg, use_history=use_history)

    c_t, _ = field_extract(state_t, history_t)
    c_tp1, _ = field_extract(state_tp1, history_tp1)
    c_tp2, _ = field_extract(state_tp2, history_tp2)

    phi_t = [0.0] * len(state_t.phi) if freeze_phase else state_t.phi
    phi_tp1 = [0.0] * len(state_tp1.phi) if freeze_phase else state_tp1.phi
    phi_tp2 = [0.0] * len(state_tp2.phi) if freeze_phase else state_tp2.phi

    psi_t = psi_from_state(c_t, phi_t)
    psi_tp1 = psi_from_state(c_tp1, phi_tp1)
    psi_tp2 = psi_from_state(c_tp2, phi_tp2)

    gen_01 = generator_proxy(psi_t, psi_tp1)
    gen_12 = generator_proxy(psi_tp1, psi_tp2)

    p_diag_01 = diagonal_operator([cmath.exp(complex(a, w)) for a, w in zip(gen_01["a_loc"], gen_01["omega_loc"])])
    p_diag_12 = diagonal_operator([cmath.exp(complex(a, w)) for a, w in zip(gen_12["a_loc"], gen_12["omega_loc"])])

    t_eff = transport_operator(adj)
    lam = 0.10
    p_mix_01: list[list[complex]] = []
    p_mix_12: list[list[complex]] = []
    for i, row in enumerate(t_eff):
        factor_01 = p_diag_01[i][i]
        factor_12 = p_diag_12[i][i]
        p_mix_01.append([factor_01 * ((1.0 if i == j else 0.0) + lam * row[j]) for j in range(len(row))])
        p_mix_12.append([factor_12 * ((1.0 if i == j else 0.0) + lam * row[j]) for j in range(len(row))])

    return {
        "psi_t": psi_t,
        "psi_tp2": psi_tp2,
        "p_diag_02": matmul(p_diag_12, p_diag_01),
        "p_mix_02": matmul(p_mix_12, p_mix_01),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM propagator composition proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    hist = rollout_triplet(cfg, use_history=True, freeze_phase=False)
    nohist = rollout_triplet(cfg, use_history=False, freeze_phase=False)
    frozen = rollout_triplet(cfg, use_history=True, freeze_phase=True)

    psi_diag_02 = matvec(hist["p_diag_02"], hist["psi_t"])
    psi_mix_02 = matvec(hist["p_mix_02"], hist["psi_t"])

    checks = {
        "diag_composition_exact_pass": complex_l1(psi_diag_02, hist["psi_tp2"]) < 1e-10,
        "mix_composition_bounded_pass": max_row_sum(hist["p_mix_02"]) < 1.5,
        "mix_composition_nontrivial_pass": complex_l1(psi_mix_02, psi_diag_02) > 0.25,
        "mix_composition_alignment_pass": overlap_score(psi_mix_02, hist["psi_tp2"]) > 0.98,
        "phase_sensitivity_pass": mat_l1(matsub(hist["p_mix_02"], frozen["p_mix_02"])) > 0.25,
        "history_imprint_pass": mat_l1(matsub(hist["p_mix_02"], nohist["p_mix_02"])) > 0.20,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-027",
        "decision": "pass" if decision else "fail",
        "norms": {
            "p_diag_02_max_row_sum": max_row_sum(hist["p_diag_02"]),
            "p_mix_02_max_row_sum": max_row_sum(hist["p_mix_02"]),
        },
        "differences": {
            "psi_diag_02_l1_vs_target": complex_l1(psi_diag_02, hist["psi_tp2"]),
            "psi_mix_02_l1_vs_diag_02": complex_l1(psi_mix_02, psi_diag_02),
            "p_mix_02_phase_vs_frozen_l1": mat_l1(matsub(hist["p_mix_02"], frozen["p_mix_02"])),
            "p_mix_02_history_vs_present_only_l1": mat_l1(matsub(hist["p_mix_02"], nohist["p_mix_02"])),
        },
        "overlaps": {
            "mix_02_target_overlap": overlap_score(psi_mix_02, hist["psi_tp2"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Propagator Composition Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- p_diag_02_max_row_sum: `{report['norms']['p_diag_02_max_row_sum']:.6f}`",
        f"- p_mix_02_max_row_sum: `{report['norms']['p_mix_02_max_row_sum']:.6f}`",
        f"- psi_diag_02_l1(vs target): `{report['differences']['psi_diag_02_l1_vs_target']:.6e}`",
        f"- psi_mix_02_l1(vs diag): `{report['differences']['psi_mix_02_l1_vs_diag_02']:.6f}`",
        f"- p_mix_02_l1(phase vs frozen): `{report['differences']['p_mix_02_phase_vs_frozen_l1']:.6f}`",
        f"- p_mix_02_l1(history vs present-only): `{report['differences']['p_mix_02_history_vs_present_only_l1']:.6f}`",
        f"- mix_02_target_overlap: `{report['overlaps']['mix_02_target_overlap']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_propagator_composition_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
