from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, build_graph
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state, rollout_pair
from qng_qm_operator_assembly_reference import (
    diagonal_operator,
    mat_l1,
    matmul,
    matsub,
    matvec,
    transport_operator,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-operator-algebra-reference-v1"


def commutator(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return matsub(matmul(a, b), matmul(b, a))


def matadd(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[x + y for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def build_operators(cfg: Config, use_history: bool, freeze_phase: bool = False):
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=use_history)

    import random

    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)

    c_t, _ = field_extract(state_t, hist_t)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)
    phi_t = [0.0] * len(state_t.phi) if freeze_phase else state_t.phi
    phi_tp1 = [0.0] * len(state_tp1.phi) if freeze_phase else state_tp1.phi

    psi_t = psi_from_state(c_t, phi_t)
    psi_tp1 = psi_from_state(c_tp1, phi_tp1)
    gen = generator_proxy(psi_t, psi_tp1)

    g_eff = diagonal_operator([complex(a, w) for a, w in zip(gen["a_loc"], gen["omega_loc"])])
    n_eff = diagonal_operator([complex(c, 0.0) for c in c_t])
    t_eff = transport_operator(adj)
    return g_eff, n_eff, t_eff, psi_t


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM operator algebra CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    g_hist, n_hist, t_eff, psi_hist = build_operators(cfg, use_history=True, freeze_phase=False)
    g_nohist, n_nohist, _, psi_nohist = build_operators(cfg, use_history=False, freeze_phase=False)
    g_frozen, n_frozen, _, psi_frozen = build_operators(cfg, use_history=True, freeze_phase=True)

    c_gt = commutator(g_hist, t_eff)
    c_nt = commutator(n_hist, t_eff)
    c_gn = commutator(g_hist, n_hist)

    jacobi = matadd(
        commutator(g_hist, commutator(n_hist, t_eff)),
        matadd(
            commutator(n_hist, commutator(t_eff, g_hist)),
            commutator(t_eff, commutator(g_hist, n_hist)),
        ),
    )

    c_gt_nohist = commutator(g_nohist, t_eff)
    c_gt_frozen = commutator(g_frozen, t_eff)
    c_nt_nohist = commutator(n_nohist, t_eff)
    c_nt_frozen = commutator(n_frozen, t_eff)

    gt_action = sum(abs(v) for v in matvec(c_gt, psi_hist))
    nt_action = sum(abs(v) for v in matvec(c_nt, psi_hist))

    phase_l1 = mat_l1(matsub(c_gt, c_gt_frozen)) + mat_l1(matsub(c_nt, c_nt_frozen))
    history_l1 = mat_l1(matsub(c_gt, c_gt_nohist)) + mat_l1(matsub(c_nt, c_nt_nohist))

    checks = {
        "diagonal_commuting_pass": mat_l1(c_gn) < 1e-12,
        "transport_commutators_nontrivial_pass": mat_l1(c_gt) > 0.05 and mat_l1(c_nt) > 0.05,
        "jacobi_pass": mat_l1(jacobi) < 1e-10,
        "commutator_action_nontrivial_pass": gt_action > 0.05 and nt_action > 0.05,
        "phase_sensitivity_pass": phase_l1 > 0.20,
        "history_imprint_pass": history_l1 > 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-022",
        "decision": "pass" if decision else "fail",
        "commutators": {
            "gn_l1": mat_l1(c_gn),
            "gt_l1": mat_l1(c_gt),
            "nt_l1": mat_l1(c_nt),
            "jacobi_l1": mat_l1(jacobi),
        },
        "actions": {
            "gt_on_psi_l1": gt_action,
            "nt_on_psi_l1": nt_action,
            "psi_hist_norm_l1": sum(abs(v) for v in psi_hist),
            "psi_nohist_norm_l1": sum(abs(v) for v in psi_nohist),
            "psi_frozen_norm_l1": sum(abs(v) for v in psi_frozen),
        },
        "differences": {
            "commutator_phase_l1": phase_l1,
            "commutator_history_l1": history_l1,
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Operator Algebra v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- [G,N]_l1: `{report['commutators']['gn_l1']:.6e}`",
        f"- [G,T]_l1: `{report['commutators']['gt_l1']:.6f}`",
        f"- [N,T]_l1: `{report['commutators']['nt_l1']:.6f}`",
        f"- Jacobi_l1: `{report['commutators']['jacobi_l1']:.6e}`",
        f"- [G,T]psi_l1: `{report['actions']['gt_on_psi_l1']:.6f}`",
        f"- [N,T]psi_l1: `{report['actions']['nt_on_psi_l1']:.6f}`",
        f"- commutator_l1(phase vs frozen): `{report['differences']['commutator_phase_l1']:.6f}`",
        f"- commutator_l1(history vs present-only): `{report['differences']['commutator_history_l1']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_operator_algebra_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
