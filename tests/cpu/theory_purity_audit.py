from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = {
    "01_gr_pure": ["Sigma", "chi", "tau", "Jaccard"],
    "02_qm_pure": ["Sigma", "chi", "tau", "Jaccard"],
}

IGNORE_LINE_MARKERS = (
    "Forbidden",
    "Strict exclusions",
    "Immediate exclusions",
    "This file does not yet decide",
    "The following do not belong",
    "The following do not belong in",
    "This file must remain QNG-free",
)


def load_lines(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    return text.splitlines()


def should_ignore_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith("-"):
        for marker in IGNORE_LINE_MARKERS:
            if marker in stripped:
                return True
    for marker in IGNORE_LINE_MARKERS:
        if marker in stripped:
            return True
    return False


def main() -> int:
    failures: list[str] = []

    for rel_dir, forbidden_terms in FORBIDDEN.items():
        base = ROOT / rel_dir
        for path in sorted(base.glob("*.md")):
            if path.name == "README.md":
                continue
            for lineno, line in enumerate(load_lines(path), start=1):
                if should_ignore_line(line):
                    continue
                for term in forbidden_terms:
                    if term in line:
                        failures.append(f"{rel_dir}: {path.name}:{lineno} contains '{term}'")

    if failures:
        print("theory_purity_audit: FAIL")
        for item in failures:
            print(item)
        return 1

    print("theory_purity_audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
