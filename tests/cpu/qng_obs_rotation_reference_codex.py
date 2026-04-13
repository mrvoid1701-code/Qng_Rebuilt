from __future__ import annotations

"""
QNG-OBS-001: Galaxy rotation curves - QNG flat-ether model vs baryon-only.

Refactored standalone variant by Codex.
Original reference script remains unchanged.
"""

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-rotation-reference-codex-v1"

MIN_POINTS = 5
AUTHOR = "Codex"


@dataclass(frozen=True)
class RotationRow:
    radius: float
    v_obs: float
    v_err: float
    baryon_term: float
    history_term: float

    @property
    def v2_obs(self) -> float:
        return self.v_obs * self.v_obs

    @property
    def v2_err(self) -> float:
        return 2.0 * self.v_obs * max(self.v_err, 1e-6)

    @property
    def baryon_residual(self) -> float:
        return self.v2_obs - self.baryon_term

    @property
    def weight(self) -> float:
        if self.v2_err <= 1e-12:
            return 0.0
        return 1.0 / (self.v2_err * self.v2_err)


@dataclass(frozen=True)
class GalaxyFit:
    galaxy: str
    a_M: float
    chi2_baryon: float
    chi2_qng: float
    chi2_dof_baryon: float
    chi2_dof_qng: float
    n_points: int
    dof: int
    M_proxy: float


def load_data(path: Path) -> dict[str, list[RotationRow]]:
    galaxies: dict[str, list[RotationRow]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gid = row["system_id"].strip()
            galaxies.setdefault(gid, []).append(
                RotationRow(
                    radius=float(row["radius"]),
                    v_obs=float(row["v_obs"]),
                    v_err=float(row["v_err"]),
                    baryon_term=float(row["baryon_term"]),
                    history_term=float(row["history_term"]),
                )
            )
    return galaxies


def weighted_mean(values: list[float], weights: list[float]) -> float:
    total_weight = sum(weights)
    if total_weight <= 1e-30:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def chi2_for_offset(rows: list[RotationRow], offset: float) -> float:
    chi2 = 0.0
    for row in rows:
        if row.v2_err <= 1e-12:
            continue
        normalized = (row.baryon_residual - offset) / row.v2_err
        chi2 += normalized * normalized
    return chi2


def fit_galaxy(galaxy: str, rows: list[RotationRow]) -> GalaxyFit:
    n_points = len(rows)
    dof = max(1, n_points - 1)

    residuals = [row.baryon_residual for row in rows]
    weights = [row.weight for row in rows]
    a_m = weighted_mean(residuals, weights)

    chi2_baryon = chi2_for_offset(rows, offset=0.0)
    chi2_qng = chi2_for_offset(rows, offset=a_m)
    chi2_dof_baryon = chi2_baryon / n_points
    chi2_dof_qng = chi2_qng / dof
    m_proxy = max(row.baryon_term for row in rows)

    return GalaxyFit(
        galaxy=galaxy,
        a_M=a_m,
        chi2_baryon=chi2_baryon,
        chi2_qng=chi2_qng,
        chi2_dof_baryon=chi2_dof_baryon,
        chi2_dof_qng=chi2_dof_qng,
        n_points=n_points,
        dof=dof,
        M_proxy=m_proxy,
    )


def median(values: list[float]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        return 0.0
    mid = count // 2
    if count % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def pearson_r(xs: list[float], ys: list[float]) -> float:
    count = len(xs)
    if count < 2:
        return 0.0
    mean_x = sum(xs) / count
    mean_y = sum(ys) / count
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x < 1e-30 or std_y < 1e-30:
        return 0.0
    return cov / (std_x * std_y)


def evaluate_sample(results: list[GalaxyFit]) -> dict[str, float]:
    chi2_baryon = [fit.chi2_dof_baryon for fit in results]
    chi2_qng = [fit.chi2_dof_qng for fit in results]
    a_m_values = [fit.a_M for fit in results]
    mass_proxies = [fit.M_proxy for fit in results]

    n_fit = len(results)
    frac_improved = sum(1 for fit in results if fit.chi2_qng < fit.chi2_baryon) / n_fit
    frac_positive = sum(1 for fit in results if fit.a_M > 0.0) / n_fit

    neg_mass = [fit.M_proxy for fit in results if fit.a_M < 0.0]
    pos_mass = [fit.M_proxy for fit in results if fit.a_M >= 0.0]

    return {
        "median_chi2_dof_baryon": median(chi2_baryon),
        "median_chi2_dof_qng": median(chi2_qng),
        "fraction_improved": frac_improved,
        "pearson_r_aM_Mproxy": pearson_r(a_m_values, mass_proxies),
        "fraction_positive_aM": frac_positive,
        "mean_Mproxy_neg_aM": sum(neg_mass) / len(neg_mass) if neg_mass else 0.0,
        "mean_Mproxy_pos_aM": sum(pos_mass) / len(pos_mass) if pos_mass else 0.0,
    }


def build_checks(summary: dict[str, float]) -> dict[str, bool]:
    return {
        "chi2_dof_qng_lt_baryon_pass": summary["median_chi2_dof_qng"] < summary["median_chi2_dof_baryon"],
        "fraction_improved_gt_0p60_pass": summary["fraction_improved"] > 0.60,
        "pearson_r_gt_0p40_pass": summary["pearson_r_aM_Mproxy"] > 0.40,
        "fraction_positive_aM_pass": summary["fraction_positive_aM"] > 0.60,
        "check5_neg_more_baryon_rich_info": summary["mean_Mproxy_neg_aM"] > summary["mean_Mproxy_pos_aM"],
    }


def write_artifacts(
    out_dir: Path,
    results: list[GalaxyFit],
    skipped: int,
    summary: dict[str, float],
    checks: dict[str, bool],
    decision: bool,
) -> None:
    med_b = summary["median_chi2_dof_baryon"]
    med_q = summary["median_chi2_dof_qng"]

    report = {
        "test_id": "QNG-OBS-001",
        "variant": "codex-refactor",
        "author": AUTHOR,
        "decision": "pass" if decision else "fail",
        "n_galaxies_fit": len(results),
        "n_skipped": skipped,
        "median_chi2_dof_baryon": round(med_b, 4),
        "median_chi2_dof_qng": round(med_q, 4),
        "improvement_ratio": round(med_b / med_q, 4) if med_q > 0 else 0.0,
        "fraction_improved": round(summary["fraction_improved"], 4),
        "pearson_r_aM_Mproxy": round(summary["pearson_r_aM_Mproxy"], 4),
        "fraction_positive_aM": round(summary["fraction_positive_aM"], 4),
        "mean_Mproxy_neg_aM": round(summary["mean_Mproxy_neg_aM"], 2),
        "mean_Mproxy_pos_aM": round(summary["mean_Mproxy_pos_aM"], 2),
        "checks": checks,
        "per_galaxy": [
            {
                "galaxy": fit.galaxy,
                "a_M": round(fit.a_M, 2),
                "chi2_dof_baryon": round(fit.chi2_dof_baryon, 4),
                "chi2_dof_qng": round(fit.chi2_dof_qng, 4),
                "M_proxy": round(fit.M_proxy, 2),
                "n_points": fit.n_points,
            }
            for fit in results
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG-OBS-001: Rotation Curve Reference (Codex Refactor)",
        f"- author: `{AUTHOR}`",
        f"- decision: `{'pass' if decision else 'fail'}`",
        f"- galaxies fit: {len(results)}",
        "",
        "## Summary Statistics",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Median chi2/dof baryon-only | {med_b:.3f} |",
        f"| Median chi2/dof QNG | {med_q:.3f} |",
        f"| Improvement ratio | {med_b / med_q:.2f}x |",
        f"| Fraction improved | {summary['fraction_improved']:.3f} |",
        f"| Pearson r(a_M, M_proxy) | {summary['pearson_r_aM_Mproxy']:.4f} |",
        f"| Fraction a_M > 0 | {summary['fraction_positive_aM']:.3f} |",
        "",
        "## Checks",
        f"- Check 1 (chi2/dof QNG < baryon): {'PASS' if checks['chi2_dof_qng_lt_baryon_pass'] else 'FAIL'}",
        f"- Check 2 (frac improved > 0.60): {'PASS' if checks['fraction_improved_gt_0p60_pass'] else 'FAIL'}",
        f"- Check 3 (Pearson r > 0.40): {'PASS' if checks['pearson_r_gt_0p40_pass'] else 'FAIL'}",
        f"- Check 4 (frac a_M > 0 > 0.60): {'PASS' if checks['fraction_positive_aM_pass'] else 'FAIL'}",
        f"- Check 5 [info] (neg a_M galaxies more baryon-rich): {'PASS' if checks['check5_neg_more_baryon_rich_info'] else 'FAIL'}",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="QNG-OBS-001 refactored rotation-curve fit by Codex.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from: {DATA_FILE}")
    galaxies = load_data(DATA_FILE)
    print(f"Galaxies loaded: {len(galaxies)}")

    results: list[GalaxyFit] = []
    skipped = 0
    for galaxy, rows in sorted(galaxies.items()):
        if len(rows) < MIN_POINTS:
            skipped += 1
            continue
        results.append(fit_galaxy(galaxy, rows))

    print(f"Galaxies fit: {len(results)}  (skipped {skipped} with <{MIN_POINTS} points)")
    print()

    summary = evaluate_sample(results)
    checks = build_checks(summary)
    decision = (
        checks["chi2_dof_qng_lt_baryon_pass"]
        and checks["fraction_improved_gt_0p60_pass"]
        and checks["pearson_r_gt_0p40_pass"]
        and checks["fraction_positive_aM_pass"]
    )

    print("=" * 60)
    print("Results:")
    print(f"  Author:                 {AUTHOR}")
    print(f"  Galaxies fit:           {len(results)}")
    print(f"  Median chi2/dof (baryon-only): {summary['median_chi2_dof_baryon']:.3f}")
    print(f"  Median chi2/dof (QNG):         {summary['median_chi2_dof_qng']:.3f}")
    print(f"  Improvement ratio:      {summary['median_chi2_dof_baryon'] / summary['median_chi2_dof_qng']:.2f}x")
    print(f"  Fraction improved:      {summary['fraction_improved']:.3f}")
    print(f"  Pearson r(a_M, M_proxy):{summary['pearson_r_aM_Mproxy']:.4f}")
    print(f"  Fraction a_M > 0:       {summary['fraction_positive_aM']:.3f}")
    print(f"  Mean M_proxy (a_M < 0): {summary['mean_Mproxy_neg_aM']:.1f}")
    print(f"  Mean M_proxy (a_M >= 0):{summary['mean_Mproxy_pos_aM']:.1f}")
    print()
    print(f"qng_obs_rotation_reference_codex: {'PASS' if decision else 'FAIL'}")

    write_artifacts(out_dir, results, skipped, summary, checks, decision)
    print((out_dir / "report.json").as_posix())
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
