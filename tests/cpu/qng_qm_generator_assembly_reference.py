from __future__ import annotations

import argparse
import cmath
import json
import math
import random
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff, mean
from qng_native_update_reference import Config, build_graph, init_state, one_step, wrap_angle


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-generator-assembly-reference-v1"


def rollout_pair(cfg: Config, use_history: bool):
    rng = random.Random(cfg.seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(cfg.steps - 1):
        state, history = one_step(state, history, adj, cfg, use_history=use_history)
    state_t = state
    history_t = history
    state_tp1, history_tp1 = one_step(state_t, history_t, adj, cfg, use_history=use_history)
    return state_t, history_t, state_tp1, history_tp1


def psi_from_state(c_eff: list[float], phi: list[float]) -> list[complex]:
    return [math.sqrt(max(0.0, c)) * complex(math.cos(p), math.sin(p)) for c, p in zip(c_eff, phi)]


def generator_proxy(psi_t: list[complex], psi_tp1: list[complex]) -> dict[str, list[float] | list[complex]]:
    u_loc: list[complex] = []
    a_loc: list[float] = []
    omega_loc: list[float] = []
    psi_recon: list[complex] = []
    eps = 1e-12

    for a, b in zip(psi_t, psi_tp1):
        if abs(a) < eps:
            u = 0.0 + 0.0j
            amp = 0.0
            omega = 0.0
            recon = 0.0 + 0.0j
        else:
            u = b / a
            amp = math.log(max(abs(u), eps))
            omega = wrap_angle(cmath.phase(u))
            recon = a * cmath.exp(complex(amp, omega))
        u_loc.append(u)
        a_loc.append(amp)
        omega_loc.append(omega)
        psi_recon.append(recon)

    return {
        "u_loc": u_loc,
        "a_loc": a_loc,
        "omega_loc": omega_loc,
        "psi_recon": psi_recon,
    }


def complex_l1(a: list[complex], b: list[complex]) -> float:
    return sum(abs(x - y) for x, y in zip(a, b))


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM generator assembly CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    state_t, hist_t, state_tp1, hist_tp1 = rollout_pair(cfg, use_history=True)
    state_nt, hist_nt, state_ntp1, hist_ntp1 = rollout_pair(cfg, use_history=False)

    c_t, _ = field_extract(state_t, hist_t)
    c_tp1, _ = field_extract(state_tp1, hist_tp1)
    c_nt, _ = field_extract(state_nt, hist_nt)
    c_ntp1, _ = field_extract(state_ntp1, hist_ntp1)

    psi_t = psi_from_state(c_t, state_t.phi)
    psi_tp1 = psi_from_state(c_tp1, state_tp1.phi)
    psi_nt = psi_from_state(c_nt, state_nt.phi)
    psi_ntp1 = psi_from_state(c_ntp1, state_ntp1.phi)
    psi_phase_frozen_t = psi_from_state(c_t, [0.0] * len(state_t.phi))
    psi_phase_frozen_tp1 = psi_from_state(c_tp1, [0.0] * len(state_tp1.phi))

    gen_hist = generator_proxy(psi_t, psi_tp1)
    gen_nohist = generator_proxy(psi_nt, psi_ntp1)
    gen_phase_frozen = generator_proxy(psi_phase_frozen_t, psi_phase_frozen_tp1)

    checks = {
        "bounded_pass": max_abs(gen_hist["a_loc"]) < 0.2 and max_abs(gen_hist["omega_loc"]) <= math.pi,
        "nontrivial_pass": mean([abs(x) for x in gen_hist["omega_loc"]]) > 0.05 or mean([abs(x) for x in gen_hist["a_loc"]]) > 1e-3,
        "reconstruction_pass": complex_l1(gen_hist["psi_recon"], psi_tp1) < 1e-9,
        "phase_sensitivity_pass": l1_diff(gen_hist["omega_loc"], gen_phase_frozen["omega_loc"]) > 0.20,
        "history_imprint_pass": l1_diff(gen_hist["omega_loc"], gen_nohist["omega_loc"]) + l1_diff(gen_hist["a_loc"], gen_nohist["a_loc"]) > 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-017",
        "decision": "pass" if decision else "fail",
        "means": {
            "a_loc_history_mean": mean(gen_hist["a_loc"]),
            "omega_abs_history_mean": mean([abs(x) for x in gen_hist["omega_loc"]]),
        },
        "max_abs": {
            "a_loc": max_abs(gen_hist["a_loc"]),
            "omega_loc": max_abs(gen_hist["omega_loc"]),
        },
        "differences": {
            "psi_recon_l1_vs_target": complex_l1(gen_hist["psi_recon"], psi_tp1),
            "omega_l1_phase_vs_frozen": l1_diff(gen_hist["omega_loc"], gen_phase_frozen["omega_loc"]),
            "omega_l1_history_vs_present_only": l1_diff(gen_hist["omega_loc"], gen_nohist["omega_loc"]),
            "a_loc_l1_history_vs_present_only": l1_diff(gen_hist["a_loc"], gen_nohist["a_loc"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Generator Assembly v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- a_loc_history_mean: `{report['means']['a_loc_history_mean']:.6f}`",
        f"- omega_abs_history_mean: `{report['means']['omega_abs_history_mean']:.6f}`",
        f"- max_abs_a_loc: `{report['max_abs']['a_loc']:.6f}`",
        f"- max_abs_omega_loc: `{report['max_abs']['omega_loc']:.6f}`",
        f"- psi_recon_l1(vs target): `{report['differences']['psi_recon_l1_vs_target']:.6e}`",
        f"- omega_l1(phase vs frozen): `{report['differences']['omega_l1_phase_vs_frozen']:.6f}`",
        f"- omega_l1(history vs present-only): `{report['differences']['omega_l1_history_vs_present_only']:.6f}`",
        f"- a_loc_l1(history vs present-only): `{report['differences']['a_loc_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_generator_assembly_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
