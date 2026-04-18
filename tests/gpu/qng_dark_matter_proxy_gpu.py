from __future__ import annotations

"""Dark matter proxy test (QNG-GPU-004, GPU).

Question: does a Q=0 (no phi winding) sigma_m depletion blob survive?

In QNG, matter interacts via phi field (analog of EM/strong force).
A structure with sigma_m depletion but phi=0 everywhere would:
  - Gravitate (k_gm coupling to sigma_g active)
  - NOT interact via phi (no winding, no disorder)
  => Candidate for dark matter: gravitates but "invisible" to phi-sector

Three configurations tested:
  A) Spherical blob: sigma_m depletion in sphere of radius R_blob, phi=0
  B) Ring Q=0: ring-shaped depletion (same geometry as R=5 ring) but phi=0
  C) Control: same as A but with phi winding Q=1 (normal ring -- for comparison)

Gates:
  STABLE:   blob survives >50% of initial depletion after PHASE2 steps
  UNSTABLE: blob disperses (<10% depletion remaining)
  TOPOLOGICAL: blob spontaneously develops phi winding (Q grows from 0)

Physical interpretation:
  STABLE   => Q=0 structures exist => dark matter sector in QNG
  UNSTABLE => no stable Q=0 matter => dark matter requires different mechanism
  TOPOLOGICAL => substrate prefers topology => all stable matter has Q != 0
"""

import json
import math
from pathlib import Path

import cupy as cp
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-dark-matter-proxy-v1"

SIGMA_REF = 0.5
BETA      = 0.35
BETA_G    = 0.35
BETA_PHI  = 0.02
DELTA_CHI = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
ALPHA     = 0.005
ALPHA_G   = 0.005
GAMMA_PHI = 0.10
K_BACK    = 0.10
K_GM      = 0.010

PHASE1  = 300
PHASE2  = 3000
PRINT_EVERY = 500

L      = 60
CX, CY, CZ = 30, 30, 30
R_BLOB = 6   # sphere radius for config A
R_RING = 5   # ring radius for config B (same as Delta/baryon)


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


def radial_dist2(L, cx, cy, cz):
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    for d in [dx, dy, dz]:
        d[:] = np.where(d >  L/2, d - L, d)
        d[:] = np.where(d < -L/2, d + L, d)
    return (dx*dx + dy*dy + dz*dz).ravel()


def init_blob_q0(L, cx, cy, cz, r_blob):
    """Spherical depletion, phi=0 everywhere."""
    r2 = radial_dist2(L, cx, cy, cz)
    sm = np.full(L*L*L, SIGMA_REF)
    # Smooth depletion: sigma_m = sigma_ref * (r/r_blob)^2 inside, 1 outside
    mask = r2 < r_blob*r_blob
    r = np.sqrt(r2[mask])
    sm[mask] = SIGMA_REF * (r / r_blob)**2  # depleted at center, full at edge
    phi = np.zeros(L*L*L)
    return cp.asarray(sm), cp.asarray(phi)


def init_ring_q0(L, cx, cy, cz, r_ring):
    """Ring-shaped depletion (torus), phi=0 everywhere."""
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
    # Distance from ring core circle
    d_core2 = (rho - r_ring)**2 + dz*dz
    sm = np.full((L, L, L), SIGMA_REF)
    core_r = 2.5  # tube radius of depletion
    mask = d_core2 < core_r*core_r
    d_core = np.sqrt(d_core2[mask])
    sm[mask] = SIGMA_REF * (d_core / core_r)**2
    phi = np.zeros(L*L*L)
    return cp.asarray(sm.ravel()), cp.asarray(phi)


def init_ring_q1(L, cx, cy, cz, r_ring):
    """Ring with phi winding Q=1 (control -- normal baryon)."""
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
    d_core2 = (rho - r_ring)**2 + dz*dz
    sm = np.full((L, L, L), SIGMA_REF)
    core_r = 2.5
    mask = d_core2 < core_r*core_r
    d_core = np.sqrt(d_core2[mask])
    sm[mask] = SIGMA_REF * (d_core / core_r)**2
    phi = np.arctan2(dz, rho - r_ring)  # Q=1 winding
    return cp.asarray(sm.ravel()), cp.asarray(phi.ravel())


# ---------------------------------------------------------------------------
# GPU dynamics (v7)
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


def step_v7(sg, sm, chi, phi, nb_idx):
    sgb = nb_mean(sg, nb_idx)
    smb = nb_mean(sm, nb_idx)
    nsg = cp.clip(
        sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg)
           + K_BACK*(chi - sg)
           - K_GM * cp.maximum(0.0, SIGMA_REF - sm),
        0.0, 1.0
    )
    dis = disorder_gpu(phi, nb_idx)
    nsm = cp.clip(
        sm + ALPHA*(SIGMA_REF - sm) + BETA*(smb - sm)
           - GAMMA_PHI * dis * sm
           + K_GM * cp.maximum(0.0, SIGMA_REF - sg),
        0.0, 1.0
    )
    nc  = chi*(1 - CHI_DECAY) + CHI_REL*(sgb - sg) + DELTA_CHI*(SIGMA_REF - sg)
    pm  = phi_weighted_mean(phi, sm, nb_idx)
    np_ = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))
    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def total_depletion(sm):
    return float(cp.sum(cp.maximum(0.0, SIGMA_REF - sm)))


def grav_well(sg, nb_idx, cx, cy, cz, win_r=10):
    xs = np.arange(L, dtype=np.float64)
    xg, yg, zg = np.meshgrid(xs, xs, xs, indexing='ij')
    dx = xg - cx; dy = yg - cy; dz = zg - cz
    mask = cp.asarray(((dx*dx+dy*dy+dz*dz) < win_r*win_r).ravel())
    n = float(cp.sum(mask)) + 1e-12
    return float(SIGMA_REF - cp.sum(sg * mask) / n)


def winding_proxy(phi, sm, nb_idx):
    """Global winding proxy: depletion-weighted disorder."""
    dis = disorder_gpu(phi, nb_idx)
    dep = cp.maximum(0.0, SIGMA_REF - sm)
    norm = float(cp.sum(dep)) + 1e-12
    return float(cp.sum(dis * dep)) / norm


# ---------------------------------------------------------------------------
# Run one configuration
# ---------------------------------------------------------------------------

def run_config(label, sm_init, phi_init, nb_idx, out_dir):
    N = L * L * L
    sg  = cp.full(N, SIGMA_REF, dtype=cp.float64)
    sm  = sm_init.copy()
    chi = cp.zeros(N, dtype=cp.float64)
    phi = phi_init.copy()

    M0 = total_depletion(sm)
    Q0 = winding_proxy(phi, sm, nb_idx)
    G0 = grav_well(sg, nb_idx, CX, CY, CZ)

    print(f"  [{label}] M0={M0:.2f}  Q0={Q0:.5f}  G0={G0:.6f}", flush=True)

    # Phase 1: relax without Channel F
    for _ in range(PHASE1):
        sgb = nb_mean(sg, nb_idx)
        smb = nb_mean(sm, nb_idx)
        sg  = cp.clip(sg + ALPHA_G*(SIGMA_REF - sg) + BETA_G*(sgb - sg), 0.0, 1.0)
        sm  = cp.clip(sm + ALPHA  *(SIGMA_REF - sm) + BETA  *(smb - sm), 0.0, 1.0)
        chi = chi*(1-CHI_DECAY) + CHI_REL*(sgb-sg) + DELTA_CHI*(SIGMA_REF-sg)
        pm  = phi_weighted_mean(phi, sm, nb_idx)
        phi = wrap_gpu(phi + BETA_PHI * wrap_gpu(pm - phi))

    # Phase 2: full v7
    track = []
    prev_M = total_depletion(sm)

    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_v7(sg, sm, chi, phi, nb_idx)

        if t % PRINT_EVERY == 0:
            M  = total_depletion(sm)
            Q  = winding_proxy(phi, sm, nb_idx)
            G  = grav_well(sg, nb_idx, CX, CY, CZ)
            dM = (prev_M - M) / PRINT_EVERY
            prev_M = M
            retained = M / max(M0, 1e-6)
            print(f"  [{label}] T={t:6d}  M={M:8.2f} ({retained*100:.1f}%)  "
                  f"Q={Q:.5f}  G={G:.6f}  dM={dM:.6f}", flush=True)
            track.append({"t": t, "M": round(M, 3), "Q": round(Q, 6),
                          "G": round(G, 7), "dM": round(dM, 7),
                          "retained": round(retained, 4)})

    M_final   = track[-1]["M"]
    Q_final   = track[-1]["Q"]
    retained  = M_final / max(M0, 1e-6)
    topo_grew = Q_final > Q0 * 2 and Q_final > 0.01

    if retained > 0.50:
        verdict = "STABLE"
    elif retained < 0.10:
        verdict = "UNSTABLE"
    else:
        verdict = "DECAYING"

    if topo_grew:
        verdict += "+TOPOLOGICAL"

    print(f"  [{label}] VERDICT: {verdict}  "
          f"retained={retained*100:.1f}%  Q_final={Q_final:.5f}", flush=True)
    print()

    return {
        "label": label,
        "M0": round(M0, 3),
        "Q0": round(Q0, 6),
        "M_final": round(M_final, 3),
        "Q_final": round(Q_final, 6),
        "retained": round(retained, 4),
        "topo_grew": topo_grew,
        "verdict": verdict,
        "track": track,
    }


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

    print("Dark matter proxy test (QNG-GPU-004)")
    print(f"L={L}, center=({CX},{CY},{CZ})")
    print(f"R_blob={R_BLOB}, R_ring={R_RING}, Phase2={PHASE2}")
    print(f"Configs: A=blob_Q0, B=ring_Q0, C=ring_Q1(control)")
    print()

    dev = cp.cuda.Device(0)
    print(f"GPU: device 0, free mem = {dev.mem_info[0]/1e9:.2f} GB\n")

    nb_idx = build_neighbor_arrays(L)

    sm_blob_q0, phi_blob_q0 = init_blob_q0(L, CX, CY, CZ, R_BLOB)
    sm_ring_q0, phi_ring_q0 = init_ring_q0(L, CX, CY, CZ, R_RING)
    sm_ring_q1, phi_ring_q1 = init_ring_q1(L, CX, CY, CZ, R_RING)

    results = []

    print("=== Config A: spherical blob, Q=0 ===")
    results.append(run_config("blob_Q0", sm_blob_q0, phi_blob_q0, nb_idx, out))

    print("=== Config B: ring-shaped depletion, Q=0 ===")
    results.append(run_config("ring_Q0", sm_ring_q0, phi_ring_q0, nb_idx, out))

    print("=== Config C: ring Q=1 (control, normal baryon) ===")
    results.append(run_config("ring_Q1", sm_ring_q1, phi_ring_q1, nb_idx, out))

    # Summary
    print()
    print("="*70)
    print("DARK MATTER PROXY SUMMARY")
    print("="*70)
    print(f"{'Config':<12} {'M0':>8} {'M_final':>9} {'retained':>9} "
          f"{'topo':>6} {'verdict'}")
    print("-"*70)
    for r in results:
        print(f"{r['label']:<12} {r['M0']:>8.1f} {r['M_final']:>9.1f} "
              f"{r['retained']*100:>8.1f}%  {str(r['topo_grew']):>6}  {r['verdict']}")

    # Overall verdict
    blob_stable = results[0]["retained"] > 0.50
    ring_q0_stable = results[1]["retained"] > 0.50
    ring_q1_stable = results[2]["retained"] > 0.50
    any_topo = any(r["topo_grew"] for r in results[:2])

    print()
    if blob_stable or ring_q0_stable:
        dm_verdict = "DM_CANDIDATE_EXISTS"
        dm_detail  = "Q=0 structures are stable => dark matter sector present in QNG"
    elif any_topo:
        dm_verdict = "TOPOLOGICAL_PREFERENCE"
        dm_detail  = "Q=0 spontaneously acquires winding => substrate prefers topology"
    else:
        dm_verdict = "NO_DM_CANDIDATE"
        dm_detail  = "All Q=0 structures dissolve => dark matter needs different mechanism"

    print(f"OVERALL: {dm_verdict}")
    print(f"  {dm_detail}")
    print(f"  Q=1 control (normal baryon) retained: {results[2]['retained']*100:.1f}%")

    # Save
    report = {
        "params": {"L": L, "R_BLOB": R_BLOB, "R_RING": R_RING,
                   "PHASE1": PHASE1, "PHASE2": PHASE2,
                   "K_GM": K_GM, "K_BACK": K_BACK,
                   "GAMMA_PHI": GAMMA_PHI, "CHI_DECAY": CHI_DECAY},
        "results": results,
        "dm_verdict": dm_verdict,
        "dm_detail": dm_detail,
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Dark Matter Proxy Test (QNG-GPU-004)", "",
        f"L={L}, R_blob={R_BLOB}, R_ring={R_RING}, Phase2={PHASE2}", "",
        "## Results", "",
        "| Config | M0 | M_final | retained% | topo_grew | verdict |",
        "|--------|----|---------|-----------|-----------|---------| ",
    ]
    for r in results:
        lines.append(f"| {r['label']} | {r['M0']:.1f} | {r['M_final']:.1f} | "
                     f"{r['retained']*100:.1f}% | {r['topo_grew']} | {r['verdict']} |")
    lines += ["", f"## Overall: {dm_verdict}", "", dm_detail]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nArtifacts: {out}")
    return 0 if dm_verdict != "NO_DM_CANDIDATE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
