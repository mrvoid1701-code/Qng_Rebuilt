from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    "01_gr_pure",
    "02_qm_pure",
    "03_gr_qm_bridge",
    "04_qng_pure",
]


def doc_type(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Type:"):
            return line.split(":", 1)[1].strip().strip("`")
    return ""


def requires_inputs(type_name: str) -> bool:
    return type_name == "derivation"


def main() -> int:
    missing_inputs: list[str] = []

    for rel in TARGETS:
        for path in sorted((ROOT / rel).glob("*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            type_name = doc_type(text)
            if requires_inputs(type_name) and "## Inputs" not in text:
                missing_inputs.append(f"{rel}: {path.name}")

    if missing_inputs:
        print("dependency_audit: FAIL")
        for item in missing_inputs:
            print(f"missing Inputs section: {item}")
        return 1

    print("dependency_audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
