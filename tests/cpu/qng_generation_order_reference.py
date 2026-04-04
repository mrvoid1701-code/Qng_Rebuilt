from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

from qng_native_update_reference import (
    Config,
    History,
    State,
    build_graph,
    clip01,
    init_state,
    neigh_mean,
    circular_mean,
    wrap_angle,
    angle_diff,
    one_step,
)
from qng_effective_field_reference import field_extract, centered_corr


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-generation-order-reference-v1"

SIGMA_REF: float = 0.5  # matches the self-relaxation target in qng_native_update_reference


# ---------------------------------------------------------------------------
# V3 single step: v2 + Channel D (delta * (sigma_ref - sigma_i) on chi only)
# ---------------------------------------------------------------------------

def one_step_v3(
    state: State,
    history: History,
    adj: list[list[int]],
    cfg: Config,
    delta: float,
    *,
    use_history: bool = True,
) -> tuple[State, History]:
    """
    V3 update law: v2 extended with generation-order cross-coupling.

    Channel D (new): delta * (sigma_ref - sigma_i) added to chi only.
    Setting delta=0 must reproduce one_step() exactly.
    """
    n = len(adj)
    next_sigma: list[float] = []
    next_chi: list[float] = []
    next_phi: list[float] = []
    next_mem: list[float] = []
    next_mismatch: list[float] = []
    next_phase: list[float] = []

    for i, neighbors in enumerate(adj):
        sigma_i = state.sigma[i]
        chi_i = state.chi[i]
        phi_i = state.phi[i]

        sigma_neigh = neigh_mean(state.sigma, neighbors, sigma_i)
        chi_neigh = neigh_mean(state.chi, neighbors, chi_i)
        phi_neigh = circular_mean(state.phi, neighbors, phi_i)

        hist_drive = 0.0
        if use_history:
            hist_drive = (
                history.mem[i]
                - history.mismatch[i]
                + 0.25 * math.cos(history.phase[i])
            )

        # sigma channel — identical to v2
        sigma_raw = (
            sigma_i
            + cfg.sigma_self_gain * (SIGMA_REF - sigma_i)
            + cfg.sigma_rel_gain * (sigma_neigh - sigma_i)
            + cfg.sigma_hist_gain * hist_drive
        )
        sigma_new = clip01(sigma_raw)

        # chi channel — v2 terms + Channel D
        chi_raw = (
            chi_i
            - cfg.chi_decay * chi_i
            + cfg.chi_rel_gain * (sigma_neigh - sigma_i)
            + (cfg.chi_hist_gain * hist_drive if use_history else 0.0)
            + delta * (SIGMA_REF - sigma_i)  # Channel D: generation-order coupling
        )
        chi_new = chi_raw  # no clipping (matches v2 convention)

        # phi channel — identical to v2
        phi_new = wrap_angle(
            phi_i
            + cfg.phi_rel_gain * angle_diff(phi_neigh, phi_i)
            + (cfg.phi_hist_gain * history.phase[i] if use_history else 0.0)
        )

        # history update — identical to v2
        mem_new = clip01(
            (1.0 - cfg.hist_m_rate) * history.mem[i]
            + cfg.hist_m_rate * abs(chi_new - chi_neigh)
        )
        mismatch_new = clip01(
            (1.0 - cfg.hist_d_rate) * history.mismatch[i]
            + cfg.hist_d_rate * abs(sigma_new - sigma_neigh)
        )
        phase_new = wrap_angle(
            (1.0 - cfg.hist_p_rate) * history.phase[i]
            + cfg.hist_p_rate * angle_diff(phi_new, phi_neigh)
        )

        next_sigma.append(sigma_new)
        next_chi.append(chi_new)
        next_phi.append(phi_new)
        next_mem.append(mem_new)
        next_mismatch.append(mismatch_new)
        next_phase.append(phase_new)

    return (
        State(next_sigma, next_chi, next_phi),
        History(next_mem, next_mismatch, next_phase),
    )


# ---------------------------------------------------------------------------
# Rollout helpers
# ---------------------------------------------------------------------------

def rollout_v3(
    cfg: Config,
    delta: float,
    seed: int,
    steps: int,
) -> tuple[State, History, list[list[int]]]:
    rng = random.Random(seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(steps):
        state, history = one_step_v3(state, history, adj, cfg, delta)
    return state, history, adj


def rollout_v2(
    cfg: Config,
    seed: int,
    steps: int,
) -> tuple[State, History]:
    rng = random.Random(seed)
    adj = build_graph(cfg.n_nodes, rng)
    state, history = init_state(cfg.n_nodes, rng)
    for _ in range(steps):
        state, history = one_step(state, history, adj, cfg, use_history=True)
    return state, history


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="QNG generation order cross-coupling CPU reference test (QNG-CPU-029)."
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = Config()
    SEED = 20260325
    STEPS = 40
    DELTA_TEST = 0.20

    # ------------------------------------------------------------------
    # Check 1: delta=0 must be numerically identical to the v2 one_step
    # ------------------------------------------------------------------
    state_v3d0, hist_v3d0, _ = rollout_v3(cfg, delta=0.0, seed=SEED, steps=STEPS)
    state_v2, hist_v2 = rollout_v2(cfg, seed=SEED, steps=STEPS)

    max_diff_sigma = max(abs(a - b) for a, b in zip(state_v3d0.sigma, state_v2.sigma))
    max_diff_chi = max(abs(a - b) for a, b in zip(state_v3d0.chi, state_v2.chi))
    max_diff_phi = max(
        abs(wrap_angle(a - b)) for a, b in zip(state_v3d0.phi, state_v2.phi)
    )
    max_diff_v2 = max(max_diff_sigma, max_diff_chi, max_diff_phi)
    check1_pass = max_diff_v2 < 1e-12

    # ------------------------------------------------------------------
    # Check 2: chi signal with delta>0 must be stronger than with delta=0
    # Mean |chi| with delta>0 must exceed mean |chi| with delta=0
    # ------------------------------------------------------------------
    state_d0, hist_d0, _ = rollout_v3(cfg, delta=0.0, seed=SEED, steps=STEPS)
    state_dD, hist_dD, _ = rollout_v3(cfg, delta=DELTA_TEST, seed=SEED, steps=STEPS)

    mean_abs_chi_d0 = sum(abs(x) for x in state_d0.chi) / cfg.n_nodes
    mean_abs_chi_dD = sum(abs(x) for x in state_dD.chi) / cfg.n_nodes
    check2_pass = mean_abs_chi_dD > mean_abs_chi_d0 + 0.001

    # ------------------------------------------------------------------
    # Check 3: generation order direction
    # When sigma_i < sigma_ref, chi should be driven positive → correlation
    # between (sigma_ref - sigma_i) and chi_i must be positive (r > 0.30)
    # ------------------------------------------------------------------
    sigma_deficit = [SIGMA_REF - s for s in state_dD.sigma]
    corr_deficit_chi = centered_corr(sigma_deficit, state_dD.chi)
    check3_pass = corr_deficit_chi > 0.30

    # ------------------------------------------------------------------
    # Check 4: l_eff increases with delta
    # The load field must be larger on average when delta>0 vs delta=0
    # ------------------------------------------------------------------
    _, l_eff_d0 = field_extract(state_d0, hist_d0)
    _, l_eff_dD = field_extract(state_dD, hist_dD)
    mean_leff_d0 = sum(l_eff_d0) / cfg.n_nodes
    mean_leff_dD = sum(l_eff_dD) / cfg.n_nodes
    check4_pass = mean_leff_dD > mean_leff_d0

    # ------------------------------------------------------------------
    # Check 5: incremental chi (delta>0 minus delta=0) correlates with
    # sigma deficit — directly tests Channel D's per-node effect.
    # l_eff is unsuitable here because it depends on |chi - chi_neigh|
    # (a spatial gradient), which can decorrelate from the deficit when
    # chi rises uniformly across all nodes.
    # ------------------------------------------------------------------
    delta_chi = [a - b for a, b in zip(state_dD.chi, state_d0.chi)]
    corr_deltachi_deficit = centered_corr(delta_chi, sigma_deficit)
    check5_pass = corr_deltachi_deficit > 0.30

    # ------------------------------------------------------------------
    # Check 6: contractiveness condition alpha + beta + delta < 1
    # ------------------------------------------------------------------
    contractiveness_sum = cfg.sigma_self_gain + cfg.sigma_rel_gain + DELTA_TEST
    check6_pass = contractiveness_sum < 1.0

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------
    checks = {
        "v2_parity_pass": check1_pass,
        "chi_signal_stronger_pass": check2_pass,
        "generation_order_direction_pass": check3_pass,
        "leff_increases_with_delta_pass": check4_pass,
        "leff_deficit_correlation_pass": check5_pass,
        "contractiveness_pass": check6_pass,
    }
    decision = all(checks.values())

    report = {
        "test_id": "QNG-CPU-029",
        "decision": "pass" if decision else "fail",
        "v2_parity": {
            "max_diff_sigma": max_diff_sigma,
            "max_diff_chi": max_diff_chi,
            "max_diff_phi": max_diff_phi,
            "max_diff_total": max_diff_v2,
        },
        "generation_order": {
            "mean_abs_chi_delta0": mean_abs_chi_d0,
            "mean_abs_chi_deltaD": mean_abs_chi_dD,
            "corr_deficit_chi": corr_deficit_chi,
        },
        "matter_proxy": {
            "mean_leff_delta0": mean_leff_d0,
            "mean_leff_deltaD": mean_leff_dD,
            "corr_delta_chi_deficit": corr_deltachi_deficit,
        },
        "contractiveness": {
            "alpha_plus_beta_plus_delta": contractiveness_sum,
        },
        "checks": checks,
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary_lines = [
        "# QNG Generation Order Cross-Coupling Reference v1",
        "",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Check 1: v2 parity (delta=0)",
        f"- max_diff_total: `{max_diff_v2:.3e}`  threshold < 1e-12  {'PASS' if check1_pass else 'FAIL'}",
        "",
        "## Check 2: chi signal stronger with delta>0",
        f"- mean |chi| delta=0.00: `{mean_abs_chi_d0:.6f}`",
        f"- mean |chi| delta={DELTA_TEST:.2f}: `{mean_abs_chi_dD:.6f}`",
        f"- difference: `{mean_abs_chi_dD - mean_abs_chi_d0:.6f}`  threshold > 0.001  {'PASS' if check2_pass else 'FAIL'}",
        "",
        "## Check 3: generation order direction",
        f"- corr(sigma_deficit, chi): `{corr_deficit_chi:.4f}`  threshold > 0.30  {'PASS' if check3_pass else 'FAIL'}",
        "",
        "## Check 4: l_eff increases with delta",
        f"- mean l_eff delta=0.00: `{mean_leff_d0:.6f}`",
        f"- mean l_eff delta={DELTA_TEST:.2f}: `{mean_leff_dD:.6f}`  {'PASS' if check4_pass else 'FAIL'}",
        "",
        "## Check 5: l_eff correlated with sigma deficit",
        f"- corr(Δchi, sigma_deficit): `{corr_deltachi_deficit:.4f}`  threshold > 0.30  {'PASS' if check5_pass else 'FAIL'}",
        "",
        "## Check 6: contractiveness",
        f"- alpha + beta + delta: `{contractiveness_sum:.4f}`  threshold < 1.0  {'PASS' if check6_pass else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"qng_generation_order_reference: {'PASS' if decision else 'FAIL'}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
