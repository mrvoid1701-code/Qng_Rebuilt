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
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-semigroup-closure-reference-v1"


def mat_l1(matrix: list[list[complex]]) -> float:
    return sum(abs(x) for row in matrix for x in row)


def build_one_step_mix(
    gen: dict,
    adj: list[list[int]],
    lam: float = 0.10,
) -> list[list[complex]]:
    p_diag = diagonal_operator(
        [cmath.exp(complex(a, w)) for a, w in zip(gen["a_loc"], gen["omega_loc"])]
    )
    t_eff = transport_operator(adj)
    n = len(adj)
    p_mix: list[list[complex]] = []
    for i, row in enumerate(t_eff):
        factor = p_diag[i][i]
        p_mix.append([factor * ((1.0 if i == j else 0.0) + lam * row[j]) for j in range(n)])
    return p_mix


def build_one_step_diag(gen: dict) -> list[list[complex]]:
    return diagonal_operator(
        [cmath.exp(complex(a, w)) for a, w in zip(gen["a_loc"], gen["omega_loc"])]
    )


def rollout_quad(cfg: Config, use_history: bool, freeze_phase: bool = False):
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 3):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)

    state_t = state
    history_t = history
    state_t1, history_t1 = one_step(state_t, history_t, adj, cfg, use_history=use_history)
    state_t2, history_t2 = one_step(state_t1, history_t1, adj, cfg, use_history=use_history)
    state_t3, history_t3 = one_step(state_t2, history_t2, adj, cfg, use_history=use_history)

    c_t, _ = field_extract(state_t, history_t)
    c_t1, _ = field_extract(state_t1, history_t1)
    c_t2, _ = field_extract(state_t2, history_t2)
    c_t3, _ = field_extract(state_t3, history_t3)

    phi_t = [0.0] * cfg.n_nodes if freeze_phase else state_t.phi
    phi_t1 = [0.0] * cfg.n_nodes if freeze_phase else state_t1.phi
    phi_t2 = [0.0] * cfg.n_nodes if freeze_phase else state_t2.phi
    phi_t3 = [0.0] * cfg.n_nodes if freeze_phase else state_t3.phi

    psi_t = psi_from_state(c_t, phi_t)
    psi_t1 = psi_from_state(c_t1, phi_t1)
    psi_t2 = psi_from_state(c_t2, phi_t2)
    psi_t3 = psi_from_state(c_t3, phi_t3)

    gen_01 = generator_proxy(psi_t, psi_t1)
    gen_12 = generator_proxy(psi_t1, psi_t2)
    gen_23 = generator_proxy(psi_t2, psi_t3)

    p_diag_01 = build_one_step_diag(gen_01)
    p_diag_12 = build_one_step_diag(gen_12)
    p_diag_23 = build_one_step_diag(gen_23)

    p_mix_01 = build_one_step_mix(gen_01, adj)
    p_mix_12 = build_one_step_mix(gen_12, adj)
    p_mix_23 = build_one_step_mix(gen_23, adj)

    p_diag_02 = matmul(p_diag_12, p_diag_01)
    p_mix_02 = matmul(p_mix_12, p_mix_01)

    p_diag_03 = matmul(p_diag_23, p_diag_02)
    p_mix_03 = matmul(p_mix_23, p_mix_02)

    return {
        "psi_t": psi_t,
        "psi_t2": psi_t2,
        "psi_t3": psi_t3,
        "p_diag_02": p_diag_02,
        "p_mix_02": p_mix_02,
        "p_diag_03": p_diag_03,
        "p_mix_03": p_mix_03,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM semigroup closure proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    hist = rollout_quad(cfg, use_history=True, freeze_phase=False)
    frozen = rollout_quad(cfg, use_history=True, freeze_phase=True)

    psi_diag_02 = matvec(hist["p_diag_02"], hist["psi_t"])
    psi_mix_02 = matvec(hist["p_mix_02"], hist["psi_t"])
    psi_diag_03 = matvec(hist["p_diag_03"], hist["psi_t"])
    psi_mix_03 = matvec(hist["p_mix_03"], hist["psi_t"])

    ov_2 = overlap_score(psi_mix_02, hist["psi_t2"])
    ov_3 = overlap_score(psi_mix_03, hist["psi_t3"])
    per_step_decay = ov_3 / ov_2 if ov_2 > 1e-12 else 0.0

    checks = {
        "diag_3step_exact_pass": complex_l1(psi_diag_03, hist["psi_t3"]) < 1e-10,
        "mix_3step_bounded_pass": max_row_sum(hist["p_mix_03"]) < 3.0,
        "mix_3step_aligned_pass": ov_3 > 0.95,
        "mix_3step_nontrivial_pass": mat_l1(matsub(hist["p_mix_03"], hist["p_diag_03"])) > 0.25,
        "per_step_decay_stable_pass": per_step_decay > 0.93,
        "phase_sensitive_3step_pass": mat_l1(matsub(hist["p_mix_03"], frozen["p_mix_03"])) > 0.25,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-028",
        "decision": "pass" if decision else "fail",
        "norms": {
            "p_diag_03_max_row_sum": max_row_sum(hist["p_diag_03"]),
            "p_mix_03_max_row_sum": max_row_sum(hist["p_mix_03"]),
        },
        "differences": {
            "psi_diag_03_l1_vs_target": complex_l1(psi_diag_03, hist["psi_t3"]),
            "p_mix_03_vs_p_diag_03_l1": mat_l1(matsub(hist["p_mix_03"], hist["p_diag_03"])),
            "p_mix_03_phase_vs_frozen_l1": mat_l1(matsub(hist["p_mix_03"], frozen["p_mix_03"])),
        },
        "overlaps": {
            "mix_02_target_overlap": ov_2,
            "mix_03_target_overlap": ov_3,
            "per_step_decay_ratio": per_step_decay,
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Semigroup Closure Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- p_diag_03_max_row_sum: `{report['norms']['p_diag_03_max_row_sum']:.6f}`",
        f"- p_mix_03_max_row_sum: `{report['norms']['p_mix_03_max_row_sum']:.6f}`",
        f"- psi_diag_03_l1(vs target): `{report['differences']['psi_diag_03_l1_vs_target']:.6e}`",
        f"- p_mix_03_vs_diag_03_l1: `{report['differences']['p_mix_03_vs_p_diag_03_l1']:.6f}`",
        f"- p_mix_03_phase_vs_frozen_l1: `{report['differences']['p_mix_03_phase_vs_frozen_l1']:.6f}`",
        f"- mix_02_target_overlap: `{report['overlaps']['mix_02_target_overlap']:.6f}`",
        f"- mix_03_target_overlap: `{report['overlaps']['mix_03_target_overlap']:.6f}`",
        f"- per_step_decay_ratio: `{report['overlaps']['per_step_decay_ratio']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_semigroup_closure_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
