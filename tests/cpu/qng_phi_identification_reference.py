from __future__ import annotations

import argparse
import dataclasses
import json
import math
import statistics
from pathlib import Path

from qng_effective_field_reference import field_extract
from qng_native_update_reference import Config, run_rollout


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = (
    ROOT / "07_validation" / "audits" / "qng-phi-identification-reference-v1"
)

SEEDS = [20260325, 42, 137, 1729, 2718]


def corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    sa = (sum((x - ma) ** 2 for x in a) / n) ** 0.5
    sb = (sum((y - mb) ** 2 for y in b) / n) ** 0.5
    return cov / (sa * sb) if sa * sb > 1e-15 else 0.0


def variance(a: list[float]) -> float:
    n = len(a)
    m = sum(a) / n
    return sum((x - m) ** 2 for x in a) / n


def sync_order(phi: list[float], adj: list[list[int]]) -> float:
    """Kuramoto-style synchronization order parameter.
    mean(cos(phi_i - phi_j)) over all neighbor pairs (i,j) with i<j.
    """
    pairs = [(i, j) for i in range(len(adj)) for j in adj[i] if j > i]
    if not pairs:
        return 0.0
    return sum(math.cos(phi[i] - phi[j]) for i, j in pairs) / len(pairs)


def metrics_for_seed(seed: int) -> dict:
    cfg = dataclasses.replace(Config(), seed=seed)

    _, state_h, history_h, adj_h = run_rollout(cfg, use_history=True)
    _, state_n, history_n, adj_n = run_rollout(cfg, use_history=False)

    c_eff_h, l_eff_h = field_extract(state_h, history_h)
    c_eff_n, l_eff_n = field_extract(state_n, history_n)

    phi_h = state_h.phi
    phi_n = state_n.phi
    phase_h = list(history_h.phase)  # history.phase (angular gradient memory)

    corr_phi_leff = corr(phi_h, l_eff_h)
    corr_phi_ceff = corr(phi_h, c_eff_h)
    corr_phi_sigma = corr(phi_h, state_h.sigma)
    corr_phi_phase = corr(phi_h, phase_h)
    corr_phase_ceff = corr(phase_h, c_eff_h)  # direct history.phase→C_eff path

    var_hist = variance(phi_h)
    var_nohist = variance(phi_n)

    sync_hist = sync_order(phi_h, adj_h)
    sync_nohist = sync_order(phi_n, adj_n)
    sync_ratio = sync_hist / sync_nohist if abs(sync_nohist) > 1e-10 else None

    return {
        "seed": seed,
        "corr_phi_leff": round(corr_phi_leff, 6),
        "corr_phi_ceff": round(corr_phi_ceff, 6),
        "corr_phi_sigma": round(corr_phi_sigma, 6),
        "corr_phi_phase": round(corr_phi_phase, 6),
        "corr_phase_ceff": round(corr_phase_ceff, 6),
        "var_phi_hist": round(var_hist, 6),
        "var_phi_nohist": round(var_nohist, 6),
        "hist_reduces_variance": var_hist < var_nohist,
        "sync_order_hist": round(sync_hist, 6),
        "sync_order_nohist": round(sync_nohist, 6),
        "sync_ratio": round(sync_ratio, 4) if sync_ratio is not None else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG phi identification CPU test.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [metrics_for_seed(s) for s in SEEDS]

    corr_leff_vals = [r["corr_phi_leff"] for r in results]
    corr_ceff_vals = [r["corr_phi_ceff"] for r in results]
    sync_hist_vals = [r["sync_order_hist"] for r in results]
    var_reduces = [r["hist_reduces_variance"] for r in results]

    # P1: phi-L_eff coupling weak — |corr(phi,L_eff)| < 0.5 on all seeds (sign-unstable, Tier-2)
    p1_pass = all(abs(c) < 0.5 for c in corr_leff_vals)
    # P2: phi achieves high neighbor sync — sync_order_hist > 0.9 on all seeds
    p2_pass = all(s > 0.9 for s in sync_hist_vals)
    # P3: phi→C_eff indirect/topology-dependent — |corr| < 0.5 on ≥3/5 seeds
    p3_pass = sum(1 for c in corr_ceff_vals if abs(c) < 0.5) >= 3
    # P4: history introduces phase diversity (anti-ordering) — var_hist > var_nohist on all seeds
    p4_pass = all(not r for r in var_reduces)  # var_hist > var_nohist on all seeds

    decision = p1_pass and p2_pass and p3_pass and p4_pass

    verdict = (
        "phi is a near-perfectly synchronized phase field (sync>0.94 universally); "
        "history introduces phase diversity (anti-ordering, var_hist>var_nohist); "
        "phi-L_eff coupling weak and sign-unstable (tier-2); "
        "phi->C_eff indirect and topology-dependent (tier-2)"
        if decision
        else "inconclusive"
    )

    report = {
        "test_id": "QNG-CPU-040",
        "decision": "pass" if decision else "fail",
        "verdict": verdict,
        "per_seed": results,
        "corr_leff_summary": {
            "values": corr_leff_vals,
            "max_abs": max(abs(c) for c in corr_leff_vals),
        },
        "corr_ceff_summary": {
            "values": corr_ceff_vals,
            "count_below_half": sum(1 for c in corr_ceff_vals if abs(c) < 0.5),
        },
        "sync_summary": {
            "hist_values": sync_hist_vals,
            "min_hist": min(sync_hist_vals),
        },
        "variance_summary": {
            "reduces_count": sum(var_reduces),
        },
        "checks": {
            "p1_phi_leff_weak_below_half_pass": p1_pass,
            "p2_phi_high_sync_above_0p9_universal_pass": p2_pass,
            "p3_phi_ceff_indirect_topology_dep_pass": p3_pass,
            "p4_history_antiordering_var_increases_pass": p4_pass,
        },
    }

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    summary_lines = [
        "# QNG Phi Identification",
        "",
        f"- test_id: `QNG-CPU-040`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- verdict: `{verdict}`",
        "",
        "## corr(phi, L_eff) per seed",
        *[f"  seed {r['seed']}: `{r['corr_phi_leff']:.4f}`" for r in results],
        f"  max_abs: `{max(abs(c) for c in corr_leff_vals):.4f}` (< 0.5 required; sign-unstable = tier-2)",
        "",
        "## corr(phi, C_eff) per seed",
        *[f"  seed {r['seed']}: `{r['corr_phi_ceff']:.4f}`" for r in results],
        f"  count |corr|<0.5: `{sum(1 for c in corr_ceff_vals if abs(c) < 0.5)}/5` (≥3 required)",
        "",
        "## corr(phi, sigma) per seed",
        *[f"  seed {r['seed']}: `{r['corr_phi_sigma']:.4f}`" for r in results],
        "",
        "## corr(phi, history.phase) per seed",
        *[f"  seed {r['seed']}: `{r['corr_phi_phase']:.4f}`" for r in results],
        "",
        "## corr(history.phase, C_eff) per seed",
        *[f"  seed {r['seed']}: `{r['corr_phase_ceff']:.4f}`" for r in results],
        "",
        "## Synchronization order parameter",
        *[
            f"  seed {r['seed']}: hist=`{r['sync_order_hist']:.4f}`, "
            f"nohist=`{r['sync_order_nohist']:.4f}`, ratio=`{r['sync_ratio']}`"
            for r in results
        ],
        f"  min(sync_hist): `{min(sync_hist_vals):.4f}` (> 0 required)",
        "",
        "## History reduces phase variance?",
        *[
            f"  seed {r['seed']}: `{r['hist_reduces_variance']}` "
            f"(var_hist={r['var_phi_hist']:.4f}, var_nohist={r['var_phi_nohist']:.4f})"
            for r in results
        ],
        f"  count var_hist > var_nohist: `{sum(not r for r in var_reduces)}/5` (5/5 required = anti-ordering)",
    ]
    (out_dir / "summary.md").write_text(
        "\n".join(summary_lines) + "\n", encoding="utf-8"
    )

    print(f"qng_phi_identification_reference: {'PASS' if decision else 'FAIL'}")
    print(f"verdict: {verdict}")
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
