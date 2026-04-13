from __future__ import annotations

"""
Observational comparison board for QNG rotation-curve variants.

Codex variant:
  - reads existing audit reports instead of mutating any prior scripts
  - compares the main baselines and all Codex v7 proxies on one sheet
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-obs-comparison-codex-v1"
AUTHOR = "Codex"

DEFAULT_REPORTS = {
    "QNG-OBS-001 Codex": ROOT / "07_validation" / "audits" / "qng-obs-rotation-reference-codex-v1" / "report.json",
    "MOND OBS-003": ROOT / "07_validation" / "audits" / "qng-obs-mond-reference-v1" / "report.json",
    "Ring OBS-005": ROOT / "07_validation" / "audits" / "qng-obs-ring-reference-v1" / "report.json",
    "v7 Double-Yukawa Codex": ROOT / "07_validation" / "audits" / "qng-obs-v7-double-yukawa-codex-v1" / "report.json",
    "v7 Ring Cascade Codex": ROOT / "07_validation" / "audits" / "qng-obs-v7-ring-cascade-codex-v1" / "report.json",
    "v7 Hopfion Codex": ROOT / "07_validation" / "audits" / "qng-obs-v7-hopfion-codex-v1" / "report.json",
}


def detect_model_metric(report: dict) -> tuple[str, float]:
    for key, value in report.items():
        if not key.startswith("median_chi2_dof_"):
            continue
        if key == "median_chi2_dof_baryon":
            continue
        if isinstance(value, (int, float)):
            return key, float(value)
    return "median_chi2_dof_unknown", float("nan")


def best_param_summary(report: dict) -> str:
    keys = [
        key for key in sorted(report)
        if key.startswith("best_")
    ]
    if not keys:
        return "-"
    parts: list[str] = []
    for key in keys:
        value = report[key]
        if isinstance(value, float):
            parts.append(f"{key}={value:.4f}")
        else:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def load_entry(label: str, path: Path) -> dict | None:
    if not path.exists():
        return None
    report = json.loads(path.read_text(encoding="utf-8"))
    model_key, model_value = detect_model_metric(report)
    return {
        "label": label,
        "path": str(path),
        "test_id": report.get("test_id", "-"),
        "decision": report.get("decision", "-"),
        "model_metric_key": model_key,
        "median_baryon": float(report.get("median_chi2_dof_baryon", 0.0)),
        "median_model": model_value,
        "improvement_ratio": float(report.get("improvement_ratio", 0.0)),
        "fraction_improved": float(report.get("fraction_improved", 0.0)),
        "author": report.get("author", "-"),
        "best_params": best_param_summary(report),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare QNG observational reports by Codex.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    missing: list[str] = []
    for label, path in DEFAULT_REPORTS.items():
        entry = load_entry(label, path)
        if entry is None:
            missing.append(label)
            continue
        entries.append(entry)

    entries.sort(key=lambda item: item["improvement_ratio"], reverse=True)

    print(f"Author: {AUTHOR}")
    print("Observational ranking by improvement ratio:")
    for idx, item in enumerate(entries, start=1):
        print(
            f"  {idx}. {item['label']}: ratio={item['improvement_ratio']:.3f}x  "
            f"model={item['median_model']:.3f}  decision={item['decision']}"
        )

    report = {
        "author": AUTHOR,
        "entries": entries,
        "missing": missing,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Observational Comparison Board (Codex)",
        f"- author: `{AUTHOR}`",
        "",
        "## Ranking",
        "| Rank | Variant | Test ID | Decision | Median chi2/dof model | Improvement ratio | Fraction improved |",
        "|------|---------|---------|----------|-----------------------|-------------------|-------------------|",
    ]
    for idx, item in enumerate(entries, start=1):
        lines.append(
            f"| {idx} | {item['label']} | {item['test_id']} | {item['decision']} | "
            f"{item['median_model']:.3f} | {item['improvement_ratio']:.3f}x | {item['fraction_improved']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Best Parameters",
        ]
    )
    for item in entries:
        lines.append(f"- {item['label']}: {item['best_params']}")

    if missing:
        lines.extend(
            [
                "",
                "## Missing Reports",
            ]
        )
        for label in missing:
            lines.append(f"- {label}")

    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport: {(out_dir / 'report.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
