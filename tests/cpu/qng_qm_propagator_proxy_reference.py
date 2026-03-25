from __future__ import annotations

import argparse
import cmath
import json
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff
from qng_native_update_reference import Config
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state, rollout_pair
from qng_qm_operator_assembly_reference import diagonal_operator, matvec, max_row_sum, matsub, transport_operator


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-propagator-proxy-reference-v1"


def complex_l1(a: list[complex], b: list[complex]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


def overlap_score(a: list[complex], b: list[complex]) -> float:
    num = sum((x.conjugate() * y) for x, y in zip(a, b))
    da = sum(abs(x) ** 2 for x in a) ** 0.5
    db = sum(abs(y) ** 2 for y in b) ** 0.5
    if da == 0.0 or db == 0.0:
        return 0.0
    return abs(num) / (da * db)


def build_propagators(cfg: Config, use_history: bool, freeze_phase: bool = False):
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=use_history)

    c_t, _ = field_extract(state_t, hist_t)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)
    phi_t = [0.0] * len(state_t.phi) if freeze_phase else state_t.phi
    phi_tp1 = [0.0] * len(state_tp1.phi) if freeze_phase else state_tp1.phi

    psi_t = psi_from_state(c_t, phi_t)
    psi_tp1 = psi_from_state(c_tp1, phi_tp1)
    gen = generator_proxy(psi_t, psi_tp1)

    p_diag = diagonal_operator([cmath.exp(complex(a, w)) for a, w in zip(gen["a_loc"], gen["omega_loc"])])

    import random
    from qng_native_update_reference import build_graph

    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    t_eff = transport_operator(adj)

    lam = 0.10
    p_mix = []
    for i, row in enumerate(t_eff):
        factor = p_diag[i][i]
        mixed_row = [factor * ((1.0 if i == j else 0.0) + lam * row[j]) for j in range(len(row))]
        p_mix.append(mixed_row)

    return psi_t, psi_tp1, p_diag, p_mix


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM propagator proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    psi_t, psi_tp1, p_diag, p_mix = build_propagators(cfg, use_history=True, freeze_phase=False)
    _, _, p_diag_nohist, p_mix_nohist = build_propagators(cfg, use_history=False, freeze_phase=False)
    _, _, p_diag_frozen, p_mix_frozen = build_propagators(cfg, use_history=True, freeze_phase=True)

    psi_diag = matvec(p_diag, psi_t)
    psi_mix = matvec(p_mix, psi_t)

    checks = {
        "diag_exact_reconstruction_pass": complex_l1(psi_diag, psi_tp1) < 1e-10,
        "mix_bounded_pass": max_row_sum(p_mix) < 2.0,
        "mix_nontrivial_pass": complex_l1(psi_mix, psi_diag) > 0.05,
        "phase_sensitivity_pass": sum(abs(x) for row in matsub(p_mix, p_mix_frozen) for x in row) > 0.20,
        "history_imprint_pass": sum(abs(x) for row in matsub(p_mix, p_mix_nohist) for x in row) > 0.10,
        "mix_alignment_pass": overlap_score(psi_mix, psi_tp1) > 0.95,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-024",
        "decision": "pass" if decision else "fail",
        "norms": {
            "p_diag_max_row_sum": max_row_sum(p_diag),
            "p_mix_max_row_sum": max_row_sum(p_mix),
        },
        "differences": {
            "psi_diag_l1_vs_target": complex_l1(psi_diag, psi_tp1),
            "psi_mix_l1_vs_diag": complex_l1(psi_mix, psi_diag),
            "p_mix_phase_vs_frozen_l1": sum(abs(x) for row in matsub(p_mix, p_mix_frozen) for x in row),
            "p_mix_history_vs_present_only_l1": sum(abs(x) for row in matsub(p_mix, p_mix_nohist) for x in row),
        },
        "overlaps": {
            "mix_target_overlap": overlap_score(psi_mix, psi_tp1),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Propagator Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- p_diag_max_row_sum: `{report['norms']['p_diag_max_row_sum']:.6f}`",
        f"- p_mix_max_row_sum: `{report['norms']['p_mix_max_row_sum']:.6f}`",
        f"- psi_diag_l1(vs target): `{report['differences']['psi_diag_l1_vs_target']:.6e}`",
        f"- psi_mix_l1(vs diag): `{report['differences']['psi_mix_l1_vs_diag']:.6f}`",
        f"- p_mix_l1(phase vs frozen): `{report['differences']['p_mix_phase_vs_frozen_l1']:.6f}`",
        f"- p_mix_l1(history vs present-only): `{report['differences']['p_mix_history_vs_present_only_l1']:.6f}`",
        f"- mix_target_overlap: `{report['overlaps']['mix_target_overlap']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_propagator_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
