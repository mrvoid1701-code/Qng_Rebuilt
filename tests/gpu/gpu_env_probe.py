from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "07_validation" / "audits" / "gpu-env-probe-v1"


def probe_command(name: str) -> dict:
    path = shutil.which(name)
    result = {"found": bool(path), "path": path}
    if not path:
        return result
    try:
        completed = subprocess.run([name, "-L"], capture_output=True, text=True, timeout=10)
        result["exit_code"] = completed.returncode
        result["stdout"] = completed.stdout.strip()
        result["stderr"] = completed.stderr.strip()
    except Exception as exc:
        result["error"] = str(exc)
    return result


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "nvidia_smi": probe_command("nvidia-smi"),
        "cupy_installed": importlib.util.find_spec("cupy") is not None,
        "torch_installed": importlib.util.find_spec("torch") is not None,
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print((OUT_DIR / "report.json").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
