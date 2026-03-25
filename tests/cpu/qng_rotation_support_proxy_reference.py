from __future__ import annotations

import argparse
import json
from pathlib import Path

from qng_effective_field_reference import centered_corr, field_extract, l1_diff, mean
from qng_gr_weakfield_proxy_reference import weakfield_proxy
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-rotation-support-proxy-reference-v1"


def toy_radius(n: int, center: int | None = None) -> list[float]:
    c = n // 2 if center is None else center
    radii: list[float] = []
    for i in range(n):
        d = abs(i - c)
        d = min(d, n - d)
        radii.append(float(1 + d))
    return radii


def rotation_proxy(l_eff: list[float], accel: list[float], eta: float = 2.0) -> dict[str, list[float] | float]:
    radii = toy_radius(len(l_eff))
    v_base_sq = [r * abs(a) for r, a in zip(radii, accel)]
    v_qng_sq = [vb * (1.0 + eta * l) for vb, l in zip(v_base_sq, l_eff)]
    delta = [vq - vb for vq, vb in zip(v_qng_sq, v_base_sq)]
    s_rot = sum(delta)
    return {
        "radii": radii,
        "v_base_sq": v_base_sq,
        "v_qng_sq": v_qng_sq,
        "delta": delta,
        "s_rot": s_rot,
    }


def max_abs(values: list[float]) -> float:
    return max(abs(x) for x in values) if values else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG rotation support proxy CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    _, hist_state, hist_history, _ = run_rollout(cfg, use_history=True)
    _, nohist_state, nohist_history, _ = run_rollout(cfg, use_history=False)

    _, l_hist = field_extract(hist_state, hist_history)
    _, l_nohist = field_extract(nohist_state, nohist_history)
    a_hist = weakfield_proxy(field_extract(hist_state, hist_history)[0])["accel"]
    a_nohist = weakfield_proxy(field_extract(nohist_state, nohist_history)[0])["accel"]

    rot_hist = rotation_proxy(l_hist, a_hist)
    rot_nohist = rotation_proxy(l_nohist, a_nohist)
    rot_mem_off = rotation_proxy([0.0] * len(l_hist), a_hist)
    modulation_source = [vb * l for vb, l in zip(rot_hist["v_base_sq"], l_hist)]

    checks = {
        "positive_excess_pass": min(rot_hist["delta"]) >= 0.0 and rot_hist["s_rot"] > 1e-3,
        "bounded_support_pass": max_abs(rot_hist["v_qng_sq"]) < 0.2,
        "memory_link_pass": centered_corr(rot_hist["delta"], modulation_source) > 0.95,
        "memory_switch_pass": l1_diff(rot_hist["delta"], rot_mem_off["delta"]) > 1e-3,
        "history_imprint_pass": abs(rot_hist["s_rot"] - rot_nohist["s_rot"]) > 1e-3,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-009",
        "decision": "pass" if decision else "fail",
        "strength": {
            "s_rot_history": rot_hist["s_rot"],
            "s_rot_present_only": rot_nohist["s_rot"],
            "s_rot_memory_off": rot_mem_off["s_rot"],
        },
        "means": {
            "delta_history_mean": mean(rot_hist["delta"]),
            "v_base_sq_history_mean": mean(rot_hist["v_base_sq"]),
            "v_qng_sq_history_mean": mean(rot_hist["v_qng_sq"]),
        },
        "max_abs": {
            "v_qng_sq": max_abs(rot_hist["v_qng_sq"]),
            "delta": max_abs(rot_hist["delta"]),
        },
        "correlations": {
            "corr_delta_modulation_source": centered_corr(rot_hist["delta"], modulation_source),
            "corr_delta_l_eff": centered_corr(rot_hist["delta"], l_hist),
        },
        "differences": {
            "delta_l1_memory_on_vs_off": l1_diff(rot_hist["delta"], rot_mem_off["delta"]),
            "s_rot_abs_difference_history_vs_present_only": abs(rot_hist["s_rot"] - rot_nohist["s_rot"]),
        },
        "checks": checks,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Rotation Support Proxy v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- s_rot_history: `{report['strength']['s_rot_history']:.12e}`",
        f"- s_rot_present_only: `{report['strength']['s_rot_present_only']:.12e}`",
        f"- s_rot_memory_off: `{report['strength']['s_rot_memory_off']:.12e}`",
        f"- delta_history_mean: `{report['means']['delta_history_mean']:.12e}`",
        f"- max_abs_v_qng_sq: `{report['max_abs']['v_qng_sq']:.12e}`",
        f"- corr_delta_modulation_source: `{report['correlations']['corr_delta_modulation_source']:.6f}`",
        f"- corr_delta_l_eff: `{report['correlations']['corr_delta_l_eff']:.6f}`",
        f"- delta_l1(memory on vs off): `{report['differences']['delta_l1_memory_on_vs_off']:.12e}`",
        f"- s_rot_abs_difference(history vs present-only): `{report['differences']['s_rot_abs_difference_history_vs_present_only']:.12e}`",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_rotation_support_proxy_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
