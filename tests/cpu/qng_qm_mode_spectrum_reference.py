from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

from qng_effective_field_reference import field_extract, l1_diff
from qng_qm_generator_assembly_reference import generator_proxy, psi_from_state, rollout_pair
from qng_native_update_reference import Config


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-qm-mode-spectrum-reference-v1"


def dft_power(values: list[complex]) -> tuple[list[complex], list[float]]:
    n = len(values)
    coeffs: list[complex] = []
    powers: list[float] = []
    norm = n ** -0.5
    for k in range(n):
        acc = 0.0 + 0.0j
        for i, v in enumerate(values):
            acc += v * cmath.exp(complex(0.0, -2.0 * math.pi * k * i / n))
        acc *= norm
        coeffs.append(acc)
        powers.append(abs(acc) ** 2)
    return coeffs, powers


def complex_energy(values: list[complex]) -> float:
    return sum(abs(v) ** 2 for v in values)


def top_fraction(powers: list[float], n_top: int = 3) -> float:
    total = sum(powers)
    if total == 0.0:
        return 0.0
    return sum(sorted(powers, reverse=True)[:n_top]) / total


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG QM mode spectrum CPU test.")
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
    psi_phase_frozen = psi_from_state(c_t, [0.0] * len(state_t.phi))

    gen_hist = generator_proxy(psi_t, psi_tp1)
    gen_nohist = generator_proxy(psi_nt, psi_from_state(c_ntp1, state_ntp1.phi))
    gen_phase_frozen = generator_proxy(psi_phase_frozen, psi_from_state(c_tp1, [0.0] * len(state_tp1.phi)))

    _, p_psi_hist = dft_power(psi_t)
    _, p_psi_nohist = dft_power(psi_nt)
    _, p_psi_phase_frozen = dft_power(psi_phase_frozen)
    _, p_k_hist = dft_power([complex(a, w) for a, w in zip(gen_hist["a_loc"], gen_hist["omega_loc"])])
    _, p_k_nohist = dft_power([complex(a, w) for a, w in zip(gen_nohist["a_loc"], gen_nohist["omega_loc"])])
    _, p_k_phase_frozen = dft_power([complex(a, w) for a, w in zip(gen_phase_frozen["a_loc"], gen_phase_frozen["omega_loc"])])

    checks = {
        "parseval_state_pass": abs(sum(p_psi_hist) - complex_energy(psi_t)) < 1e-9,
        "parseval_generator_pass": abs(sum(p_k_hist) - complex_energy([complex(a, w) for a, w in zip(gen_hist["a_loc"], gen_hist["omega_loc"])])) < 1e-9,
        "generator_spectrum_nontrivial_pass": sum(p_k_hist) > 1e-4 and max(p_k_hist) > 1e-5,
        "phase_sensitivity_pass": l1_diff(p_psi_hist, p_psi_phase_frozen) + l1_diff(p_k_hist, p_k_phase_frozen) > 0.10,
        "history_imprint_pass": l1_diff(p_psi_hist, p_psi_nohist) + l1_diff(p_k_hist, p_k_nohist) > 0.10,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-018",
        "decision": "pass" if decision else "fail",
        "energies": {
            "state_energy": complex_energy(psi_t),
            "state_spectral_energy": sum(p_psi_hist),
            "generator_energy": complex_energy([complex(a, w) for a, w in zip(gen_hist["a_loc"], gen_hist["omega_loc"])]),
            "generator_spectral_energy": sum(p_k_hist),
        },
        "concentration": {
            "state_top3_fraction": top_fraction(p_psi_hist),
            "generator_top3_fraction": top_fraction(p_k_hist),
        },
        "differences": {
            "state_spectrum_l1_phase_vs_frozen": l1_diff(p_psi_hist, p_psi_phase_frozen),
            "generator_spectrum_l1_phase_vs_frozen": l1_diff(p_k_hist, p_k_phase_frozen),
            "state_spectrum_l1_history_vs_present_only": l1_diff(p_psi_hist, p_psi_nohist),
            "generator_spectrum_l1_history_vs_present_only": l1_diff(p_k_hist, p_k_nohist),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG QM Mode Spectrum v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- state_energy: `{report['energies']['state_energy']:.6f}`",
        f"- state_spectral_energy: `{report['energies']['state_spectral_energy']:.6f}`",
        f"- generator_energy: `{report['energies']['generator_energy']:.6f}`",
        f"- generator_spectral_energy: `{report['energies']['generator_spectral_energy']:.6f}`",
        f"- state_top3_fraction: `{report['concentration']['state_top3_fraction']:.6f}`",
        f"- generator_top3_fraction: `{report['concentration']['generator_top3_fraction']:.6f}`",
        f"- state_spectrum_l1(phase vs frozen): `{report['differences']['state_spectrum_l1_phase_vs_frozen']:.6f}`",
        f"- generator_spectrum_l1(phase vs frozen): `{report['differences']['generator_spectrum_l1_phase_vs_frozen']:.6f}`",
        f"- state_spectrum_l1(history vs present-only): `{report['differences']['state_spectrum_l1_history_vs_present_only']:.6f}`",
        f"- generator_spectrum_l1(history vs present-only): `{report['differences']['generator_spectrum_l1_history_vs_present_only']:.6f}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_qm_mode_spectrum_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
