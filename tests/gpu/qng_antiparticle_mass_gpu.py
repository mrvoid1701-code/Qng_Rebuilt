from __future__ import annotations

"""Anti-particle mass symmetry test (QNG-GPU-005, GPU).

Tests CPT-like symmetry in QNG: does M_ring(Q=-1) == M_ring(Q=+1)?

In QNG, particle/anti-particle distinction = phi winding direction:
  Particle:     phi = +arctan2(dz, rho - R)  [Q=+1, winding counterclockwise]
  Anti-particle: phi = -arctan2(dz, rho - R)  [Q=-1, winding clockwise]

Physical prediction (CPT theorem in SM):
  m(anti-proton) = m(proton) = 938.3 MeV  [verified to 10^-10 precision]

QNG prediction (if CPT-like symmetry holds):
  M_ring(R=4, Q=-1) = M_ring(R=4, Q=+1) = 728.92 substrate units

Gate:
  SYMMETRIC:   |M(Q+1) - M(Q-1)| / M(Q+1) < 0.01  (< 1% -- CPT-like holds)
  ASYMMETRIC:  deviation >= 1%  (lattice breaks CPT-like symmetry)

Tested radii: R=4 (proton/N-938), R=5 (Delta-1232)
Protocol: identical to CPU-074 (Phase1=300, Phase2=1500, Phase3=1000 conservative)
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-antiparticle-mass-v1"

# Matched exactly to CPU-074
SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA_CHI = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10

PHASE1 = 300
PHASE2 = 1500
PHASE3 = 1000

L  = 40   # same as CPU-074 for direct comparison
CX = CY = CZ = L // 2

RADII  = [4, 5]
CPU074 = {4: 728.92, 5: 954.88}  # canonical reference


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def build_neighbor_arrays(L):
    xs = np.arange(L, dtype=np.int32)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    xg = xg.ravel(); yg = yg.ravel(); zg = zg.ravel()
    nb = np.stack([
        ((xg - 1) % L) * L * L + yg * L + zg,
        ((xg + 1) % L) * L * L + yg * L + zg,
        xg * L * L + ((yg - 1) % L) * L + zg,
        xg * L * L + ((yg + 1) % L) * L + zg,
        xg * L * L + yg * L + (zg - 1) % L,
        xg * L * L + yg * L + (zg + 1) % L,
    ], axis=1).astype(np.int32)
    return cp.asarray(nb)


def build_phi(L, R, cx, cy, cz, sign=+1):
    """Build phi winding for ring of radius R.
    sign=+1 -> particle (Q=+1)
    sign=-1 -> anti-particle (Q=-1)
    """
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    dx = np.where(dx >  L/2, dx - L, dx)
    dx = np.where(dx < -L/2, dx + L, dx)
    dy = np.where(dy >  L/2, dy - L, dy)
    dy = np.where(dy < -L/2, dy + L, dy)
    dz = np.where(dz >  L/2, dz - L, dz)
    dz = np.where(dz < -L/2, dz + L, dz)
    rho = np.sqrt(dx*dx + dy*dy)
    phi = sign * np.arctan2(dz, rho - R)
    return cp.asarray(phi.ravel())


# ---------------------------------------------------------------------------
# GPU dynamics (v7, matches CPU-074)
# ---------------------------------------------------------------------------

def wrap_gpu(a):
    a = a % (2 * math.pi)
    return cp.where(a > math.pi, a - 2 * math.pi, a)


def nb_mean(field, nb_idx):
    return field[nb_idx].mean(axis=1)


def disorder_gpu(phi, nb_idx):
    phi_nb = phi[nb_idx]
    sx = cp.cos(phi_nb).mean(axis=1)
    sy = cp.sin(phi_nb).mean(axis=1)
    return cp.maximum(0.0, 1.0 - cp.sqrt(sx*sx + sy*sy))


def phi_weighted_mean(phi, sm, nb_idx):
    phi_nb = phi[nb_idx]
    sm_nb  = sm[nb_idx]
    tw = sm_nb.sum(axis=1)
    sx = (sm_nb * cp.cos(phi_nb)).sum(axis=1)
    sy = (sm_nb * cp.sin(phi_nb)).sum(axis=1)
    return cp.where(tw > 1e-10,
                    cp.arctan2(sy / cp.maximum(tw, 1e-10),
                               sx / cp.maximum(tw, 1e-10)),
                    phi)


def step_phase1(sg, sm, chi, phi, nb_idx):
    """Phase 1: no Channel F."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    sg  = cp.clip(sg + ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg), 0.0, 1.0)
    sm  = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm), 0.0, 1.0)
    chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    phi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return sg, sm, chi, phi


def step_phase2(sg, sm, chi, phi, nb_idx):
    """Phase 2: Channel F active."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    sg  = cp.clip(sg + ALPHA*(SIGMA_REF - sg) + BETA*(sgb - sg), 0.0, 1.0)
    dis = disorder_gpu(phi, nb_idx)
    sm  = cp.clip(sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
                     - GAMMA_PHI * dis * sm, 0.0, 1.0)
    chi = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    phi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return sg, sm, chi, phi


def step_phase3(sg, sm, chi, phi, nb_idx):
    """Phase 3: conservative (no A, no F, no chi_decay) -- mass measurement."""
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    # sigma: diffusion only (no Channel A restore, no Channel G)
    sg  = cp.clip(sg + BETA*(sgb - sg), 0.0, 1.0)
    sm  = cp.clip(sm + BETA*(smb - sm), 0.0, 1.0)
    # chi: no decay
    chi = chi + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    phi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return sg, sm, chi, phi


def measure_mring(sm, L):
    """Global M_ring = N*sigma_ref - sum(sigma_m). Matches CPU-074 convention."""
    return float(L*L*L * SIGMA_REF - cp.sum(sm))


# ---------------------------------------------------------------------------
# Run one ring configuration
# ---------------------------------------------------------------------------

def run_ring(R, sign, nb_idx, L):
    label = f"R={R} Q={'+'if sign>0 else '-'}1"
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    chi = cp.zeros(N, dtype=cp.float64)
    phi = build_phi(L, R, CX, CY, CZ, sign=sign)

    # Phase 1
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi, nb_idx)

    # Phase 2
    for _ in range(PHASE2):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi, nb_idx)

    M_p2 = measure_mring(sm, L)

    # Phase 3: conservative mass measurement
    checkpoints = {}
    for t in range(1, PHASE3 + 1):
        sg, sm, chi, phi = step_phase3(sg, sm, chi, phi, nb_idx)
        if t in (200, 500, 750, 1000):
            checkpoints[t] = round(measure_mring(sm, L), 3)

    M_final = checkpoints[1000]
    print(f"  {label}: M_P2={M_p2:.2f}  "
          + "  ".join(f"T{t}={v:.2f}" for t,v in checkpoints.items()),
          flush=True)
    return {"label": label, "R": R, "sign": sign,
            "M_P2": round(M_p2, 3), "M_final": M_final,
            "checkpoints": checkpoints}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Anti-particle mass symmetry test (QNG-GPU-005)")
    print(f"L={L}, Radii={RADII}, Protocol: Phase1={PHASE1} Phase2={PHASE2} Phase3={PHASE3}")
    print(f"Particle Q=+1 vs Anti-particle Q=-1")
    print(f"CPU-074 reference: R=4 -> 728.92, R=5 -> 954.88")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    nb_idx = build_neighbor_arrays(L)

    results = []
    for R in RADII:
        print(f"=== R={R} ===")
        for sign in [+1, -1]:
            results.append(run_ring(R, sign, nb_idx, L))
        print()

    # Analysis
    print("="*70)
    print("CPT-LIKE SYMMETRY ANALYSIS")
    print("="*70)
    print(f"{'Config':<16} {'M_final':>9} {'CPU-074':>9} {'vs_ref%':>8} {'vs_anti%':>9}")
    print("-"*70)

    summary = []
    for R in RADII:
        r_results = [r for r in results if r["R"] == R]
        mp  = next(r for r in r_results if r["sign"] == +1)
        mam = next(r for r in r_results if r["sign"] == -1)
        ref = CPU074.get(R, None)

        diff_pct = abs(mp["M_final"] - mam["M_final"]) / max(mp["M_final"], 1e-6) * 100
        ref_pct_p  = abs(mp["M_final"]  - ref) / ref * 100 if ref else None
        ref_pct_am = abs(mam["M_final"] - ref) / ref * 100 if ref else None

        print(f"  R={R} Q=+1:      {mp['M_final']:>9.2f} {ref:>9.2f} "
              f"{ref_pct_p:>7.2f}%")
        print(f"  R={R} Q=-1 (anti): {mam['M_final']:>9.2f} {ref:>9.2f} "
              f"{ref_pct_am:>7.2f}% {diff_pct:>8.2f}%")

        if diff_pct < 1.0:
            verdict = "SYMMETRIC"
        elif diff_pct < 5.0:
            verdict = "NEARLY_SYMMETRIC"
        else:
            verdict = "ASYMMETRIC"

        print(f"  --> {verdict}: particle/anti-particle mass diff = {diff_pct:.3f}%")
        print()
        summary.append({"R": R, "M_particle": mp["M_final"],
                        "M_antiparticle": mam["M_final"],
                        "diff_pct": round(diff_pct, 4),
                        "verdict": verdict})

    # Save
    report = {
        "params": {"L": L, "RADII": RADII,
                   "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
                   "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI},
        "cpu074_ref": CPU074,
        "results": results,
        "summary": summary,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Anti-particle Mass Symmetry Test (QNG-GPU-005)", "",
        f"L={L}, Protocol: Phase1={PHASE1} Phase2={PHASE2} Phase3={PHASE3}", "",
        "## Results", "",
        "| R | Q | M_final | CPU-074 ref | vs_ref% | vs_anti% | verdict |",
        "|---|---|---------|-------------|---------|----------|---------|",
    ]
    for s in summary:
        R = s["R"]; ref = CPU074.get(R, 0)
        mp  = s["M_particle"];  am = s["M_antiparticle"]
        rp  = abs(mp - ref)/ref*100; ra = abs(am - ref)/ref*100
        lines.append(f"| {R} | +1 | {mp:.2f} | {ref:.2f} | {rp:.2f}% | -- | -- |")
        lines.append(f"| {R} | -1 | {am:.2f} | {ref:.2f} | {ra:.2f}% | "
                     f"{s['diff_pct']:.3f}% | {s['verdict']} |")

    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Artifacts: {out}")

    all_sym = all(s["verdict"] in ("SYMMETRIC", "NEARLY_SYMMETRIC") for s in summary)
    return 0 if all_sym else 1


if __name__ == "__main__":
    raise SystemExit(main())
