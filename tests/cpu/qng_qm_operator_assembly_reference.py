from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, build_graph
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state, rollout_pair


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-operator-assembly-reference-v1"


def transport_operator(adj: list[list[int]]) -> list[list[complex]]:
    n = len(adj)
    matrix: list[list[complex]] = [[0.0 + 0.0j for _ in range(n)] for _ in range(n)]
    for i, neigh in enumerate(adj):
        deg = max(1, len(neigh))
        w = 1.0 / deg
        for j in neigh:
            matrix[i][j] = complex(w, 0.0)
    return matrix


def diagonal_operator(values: list[complex]) -> list[list[complex]]:
    n = len(values)
    matrix: list[list[complex]] = [[0.0 + 0.0j for _ in range(n)] for _ in range(n)]
    for i, v in enumerate(values):
        matrix[i][i] = v
    return matrix


def matvec(matrix: list[list[complex]], vector: list[complex]) -> list[complex]:
    out: list[complex] = []
    for row in matrix:
        acc = 0.0 + 0.0j
        for a, b in zip(row, vector):
            acc += a * b
        out.append(acc)
    return out


def matsub(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    return [[x - y for x, y in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def matmul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    n = len(a)
    out: list[list[complex]] = [[0.0 + 0.0j for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for k in range(n):
            aik = a[i][k]
            if aik == 0.0:
                continue
            for j in range(n):
                out[i][j] += aik * b[k][j]
    return out


def complex_l1(a: list[complex], b: list[complex]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


def mat_l1(matrix: list[list[complex]]) -> float:
    return sum(abs(x) for row in matrix for x in row)


def max_row_sum(matrix: list[list[complex]]) -> float:
    return max(sum(abs(x) for x in row) for row in matrix) if matrix else 0.0


def build_probe_vectors(n: int) -> tuple[list[complex], list[complex], list[complex]]:
    x = [complex(math.cos(0.23 * i), math.sin(0.17 * i)) for i in range(n)]
    y = [complex(0.5 * math.sin(0.31 * i), math.cos(0.29 * i)) for i in range(n)]
    combo = [2.0 * a - 0.5 * b for a, b in zip(x, y)]
    return x, y, combo


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM operator assembly CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=True)
    state_nt, hist_nt, state_ntp1, hist_ntp1 = rollout_pair(cfg, use_history=False)

    # Rebuild the probe adjacency deterministically from the shared config.
    import random

    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)

    c_t, _ = field_extract(state_t, hist_t)
    c_nt, _ = field_extract(state_nt, hist_nt)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)
    c_ntp1, _ = field_extract(state_ntp1, hist_ntp1)
    psi_t = psi_from_state(c_t, state_t.phi)
    psi_nt = psi_from_state(c_nt, state_nt.phi)
    psi_phase_frozen = psi_from_state(c_t, [0.0] * len(state_t.phi))
    psi_tp1 = psi_from_state(c_tp1, state_tp1.phi)
    psi_ntp1 = psi_from_state(c_ntp1, state_ntp1.phi)

    gen_hist = generator_proxy(psi_t, psi_tp1)
    gen_nohist = generator_proxy(psi_nt, psi_ntp1)
    gen_phase_frozen = generator_proxy(psi_phase_frozen, psi_from_state(c_tp1, [0.0] * len(state_tp1.phi)))

    g_hist = diagonal_operator([complex(a, w) for a, w in zip(gen_hist["a_loc"], gen_hist["omega_loc"])])
    g_nohist = diagonal_operator([complex(a, w) for a, w in zip(gen_nohist["a_loc"], gen_nohist["omega_loc"])])
    g_phase_frozen = diagonal_operator([complex(a, w) for a, w in zip(gen_phase_frozen["a_loc"], gen_phase_frozen["omega_loc"])])
    n_hist = diagonal_operator([complex(c, 0.0) for c in c_t])
    t_eff = transport_operator(adj)

    x, y, combo = build_probe_vectors(len(adj))
    lin_g = complex_l1(matvec(g_hist, combo), [2.0 * a - 0.5 * b for a, b in zip(matvec(g_hist, x), matvec(g_hist, y))])
    lin_t = complex_l1(matvec(t_eff, combo), [2.0 * a - 0.5 * b for a, b in zip(matvec(t_eff, x), matvec(t_eff, y))])
    lin_n = complex_l1(matvec(n_hist, combo), [2.0 * a - 0.5 * b for a, b in zip(matvec(n_hist, x), matvec(n_hist, y))])

    gpsi = matvec(g_hist, psi_t)
    comm_gt = matsub(matmul(g_hist, t_eff), matmul(t_eff, g_hist))

    checks = {
        "bounded_pass": max_row_sum(g_hist) < 4.0 and max_row_sum(t_eff) <= 1.0 + 1e-12 and max_row_sum(n_hist) < 2.0,
        "linearity_pass": lin_g < 1e-10 and lin_t < 1e-10 and lin_n < 1e-10,
        "generator_action_nontrivial_pass": sum(abs(v) for v in gpsi) > 0.10,
        "commutator_nontrivial_pass": mat_l1(comm_gt) > 0.05,
        "phase_sensitivity_pass": mat_l1(matsub(g_hist, g_phase_frozen)) > 0.20,
        "history_imprint_pass": mat_l1(matsub(g_hist, g_nohist)) > 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-021",
        "decision": "pass" if decision else "fail",
        "norms": {
            "g_eff_max_row_sum": max_row_sum(g_hist),
            "t_eff_max_row_sum": max_row_sum(t_eff),
            "n_eff_max_row_sum": max_row_sum(n_hist),
        },
        "linearity": {
            "g_eff_linearity_l1": lin_g,
            "t_eff_linearity_l1": lin_t,
            "n_eff_linearity_l1": lin_n,
        },
        "signals": {
            "g_eff_on_psi_l1": sum(abs(v) for v in gpsi),
            "commutator_gt_l1": mat_l1(comm_gt),
            "g_eff_phase_vs_frozen_l1": mat_l1(matsub(g_hist, g_phase_frozen)),
            "g_eff_history_vs_present_only_l1": mat_l1(matsub(g_hist, g_nohist)),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Operator Assembly v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- g_eff_max_row_sum: `{report['norms']['g_eff_max_row_sum']:.6f}`",
        f"- t_eff_max_row_sum: `{report['norms']['t_eff_max_row_sum']:.6f}`",
        f"- n_eff_max_row_sum: `{report['norms']['n_eff_max_row_sum']:.6f}`",
        f"- g_eff_linearity_l1: `{report['linearity']['g_eff_linearity_l1']:.6e}`",
        f"- t_eff_linearity_l1: `{report['linearity']['t_eff_linearity_l1']:.6e}`",
        f"- n_eff_linearity_l1: `{report['linearity']['n_eff_linearity_l1']:.6e}`",
        f"- g_eff_on_psi_l1: `{report['signals']['g_eff_on_psi_l1']:.6f}`",
        f"- commutator_gt_l1: `{report['signals']['commutator_gt_l1']:.6f}`",
        f"- g_eff_l1(phase vs frozen): `{report['signals']['g_eff_phase_vs_frozen_l1']:.6f}`",
        f"- g_eff_l1(history vs present-only): `{report['signals']['g_eff_history_vs_present_only_l1']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_operator_assembly_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
