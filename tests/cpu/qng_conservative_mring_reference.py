from __future__ import annotations

"""QNG-CPU-074: Conservative M_ring scan for R=3,4,5.

Measures M_ring in the conservative Phase-3 protocol (no A, no F, no chi_decay)
to obtain the canonical ring mass for mass identification (DER-QNG-036 §6).

The CPU-051 dissipative value (158.4 for R=4) is deprecated for mass identification.
This test provides the correct conservative reference values.

Protocol per radius:
  Phase 1 (300 steps):  dissipative v7, no Channel F/G  — phi vortex formation
  Phase 2 (1500 steps): dissipative v7, Channel F, CHI_DECAY=0.020  — ring formation
  Phase 3 (1000 steps): conservative, no A/F/chi_decay — mass measurement
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-conservative-mring-scan-v1"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
L = 20
N = L * L * L

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020   # Gap 8 stability: K_BACK*DELTA=0.020 < ALPHA+CHI_DECAY*(1-ALPHA)=0.0249
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10    # active only in Phase 3 conservative

RX = RY = RZ = float(L // 2)

PHASE1 = 300
PHASE2 = 1500
PHASE3 = 1000

RADII = [3, 4, 5]
CHECKPOINTS_P3 = [0, 200, 500, 750, 1000]


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def idx3(x, y, z):
    return (x % L) * L * L + (y % L) * L + (z % L)

def coord3(i):
    x = i // (L * L); y = (i % (L * L)) // L; z = i % L
    return x, y, z

def _mi(d):
    while d >  L / 2: d -= L
    while d < -L / 2: d += L
    return d

def wrap(a):
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def adiff(a, b):
    return wrap(a - b)

def clip01(x):
    return max(0.0, min(1.0, x))

def nb(x, y, z):
    return [idx3(x-1,y,z), idx3(x+1,y,z),
            idx3(x,y-1,z), idx3(x,y+1,z),
            idx3(x,y,z-1), idx3(x,y,z+1)]

NBS = [nb(*coord3(i)) for i in range(N)]


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_phi(ring_r):
    p = []
    for i in range(N):
        x, y, z = coord3(i)
        dx = _mi(x - RX); dy = _mi(y - RY); dz = _mi(z - RZ)
        rho = math.sqrt(dx * dx + dy * dy)
        p.append(math.atan2(dz, rho - ring_r))
    return p

def disorder(phi, i):
    nbs = NBS[i]
    sx = sum(math.cos(phi[j]) for j in nbs) / 6.0
    sy = sum(math.sin(phi[j]) for j in nbs) / 6.0
    return max(0.0, 1.0 - math.sqrt(sx * sx + sy * sy))


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------

def step_phase1(sg, sm, chi, phi):
    """No Channel F, no Channel G, no K_GM — phi vortex forms."""
    nsg = [0.0] * N; nsm = [0.0] * N; nc = [0.0] * N; np_ = [0.0] * N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0

        nsg[i] = clip01(s + ALPHA*(SIGMA_REF-s) + BETA*(sgb-s))
        nsm[i] = clip01(m + ALPHA*(SIGMA_REF-m) + BETA*(smb-m))
        nc[i]  = c*(1-CHI_DECAY) + CHI_REL*(sgb-s) + DELTA*(SIGMA_REF-s)

        tw = sum(sm[j] for j in nbs)
        if tw > 1e-10:
            sx2 = sum(sm[j]*math.cos(phi[j]) for j in nbs) / tw
            sy2 = sum(sm[j]*math.sin(phi[j]) for j in nbs) / tw
            pm  = math.atan2(sy2, sx2)
        else:
            pm = p
        np_[i] = wrap(p + BETA_PHI * adiff(pm, p))
    return nsg, nsm, nc, np_


def step_phase2(sg, sm, chi, phi):
    """Dissipative: Channel F active, CHI_DECAY=0.020, no Channel G, no K_GM."""
    nsg = [0.0] * N; nsm = [0.0] * N; nc = [0.0] * N; np_ = [0.0] * N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0

        nsg[i] = clip01(s + ALPHA*(SIGMA_REF-s) + BETA*(sgb-s))
        dsm = ALPHA*(SIGMA_REF-m) + BETA*(smb-m) - GAMMA_PHI*disorder(phi,i)*m
        nsm[i] = clip01(m + dsm)
        nc[i]  = c*(1-CHI_DECAY) + CHI_REL*(sgb-s) + DELTA*(SIGMA_REF-s)

        tw = sum(sm[j] for j in nbs)
        if tw > 1e-10:
            sx2 = sum(sm[j]*math.cos(phi[j]) for j in nbs) / tw
            sy2 = sum(sm[j]*math.sin(phi[j]) for j in nbs) / tw
            pm  = math.atan2(sy2, sx2)
        else:
            pm = p
        np_[i] = wrap(p + BETA_PHI * adiff(pm, p))
    return nsg, nsm, nc, np_


def step_phase3(sg, sm, chi, phi):
    """Conservative: no Channel A (alpha=0), no Channel F (gamma_phi=0), no chi_decay.
    Keep: Channel B (beta), Channel G (k_back), chi_rel, phi XY weighted by sigma_m."""
    nsg = [0.0] * N; nsm = [0.0] * N; nc = [0.0] * N; np_ = [0.0] * N
    for i in range(N):
        nbs = NBS[i]
        s = sg[i]; m = sm[i]; c = chi[i]; p = phi[i]
        sgb = sum(sg[j] for j in nbs) / 6.0
        smb = sum(sm[j] for j in nbs) / 6.0

        # sigma_g: Channel B + Channel G only (no A, no K_GM)
        nsg[i] = clip01(s + BETA*(sgb-s) + K_BACK*c)

        # sigma_m: Channel B only (no A, no F)
        nsm[i] = clip01(m + BETA*(smb-m))

        # chi: chi_rel only (no chi_decay, no delta)
        nc[i] = c + CHI_REL*(sgb-s)

        # phi: XY weighted by sigma_m (unchanged)
        tw = sum(sm[j] for j in nbs)
        if tw > 1e-10:
            sx2 = sum(sm[j]*math.cos(phi[j]) for j in nbs) / tw
            sy2 = sum(sm[j]*math.sin(phi[j]) for j in nbs) / tw
            pm  = math.atan2(sy2, sx2)
        else:
            pm = p
        np_[i] = wrap(p + BETA_PHI * adiff(pm, p))
    return nsg, nsm, nc, np_


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def ring_mass(sm):
    return sum(max(0.0, SIGMA_REF - sm[i]) for i in range(N))


# ---------------------------------------------------------------------------
# Run one radius
# ---------------------------------------------------------------------------

def run_radius(ring_r):
    sg  = [SIGMA_REF] * N
    sm  = [SIGMA_REF] * N
    chi = [0.0] * N
    phi = init_phi(ring_r)

    # Phase 1
    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi)

    # Phase 2
    m_p2_track = []
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi)
        if t in (500, 1000, PHASE2):
            m_p2_track.append({"t_p2": t, "M": round(ring_mass(sm), 2)})

    M_end_p2 = ring_mass(sm)

    # Phase 3 (conservative)
    m_p3_track = []
    for t in range(PHASE3 + 1):
        if t in CHECKPOINTS_P3:
            m_p3_track.append({"t_p3": t, "M": round(ring_mass(sm), 2)})
        if t < PHASE3:
            sg, sm, chi, phi = step_phase3(sg, sm, chi, phi)

    M_p3_final = m_p3_track[-1]["M"]

    return {
        "R": ring_r,
        "M_end_phase2": round(M_end_p2, 2),
        "phase2_track": m_p2_track,
        "phase3_track": m_p3_track,
        "M_conservative": M_p3_final,   # canonical value for mass identification
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

    print("QNG-CPU-074: Conservative M_ring scan (canonical mass identification)")
    print(f"L={L}  PHASE1={PHASE1}  PHASE2={PHASE2}  PHASE3={PHASE3}")
    print(f"CHI_DECAY={CHI_DECAY}  K_BACK={K_BACK} (Phase 3 only)")
    print(f"Radii: {RADII}")
    print()
    print(f"Gap 8: K_BACK*DELTA={K_BACK*DELTA:.4f} < "
          f"ALPHA+CHI_DECAY*(1-ALPHA)={ALPHA+CHI_DECAY*(1-ALPHA):.4f}  OK")
    print()

    results = []
    for r in RADII:
        print(f"--- R={r} ---", flush=True)
        res = run_radius(r)
        results.append(res)

        print(f"  M_end_phase2 (dissipative ref): {res['M_end_phase2']:.1f}")
        print("  Phase 3 (conservative):")
        for snap in res["phase3_track"]:
            print(f"    T_P3={snap['t_p3']:4d}  M={snap['M']:.1f}", flush=True)
        print(f"  M_conservative (T_P3=1000): {res['M_conservative']:.1f}")
        print()

    # Checks
    check1 = all(r["M_conservative"] > 50 for r in results)
    check2 = all(r["M_conservative"] > r["M_end_phase2"] * 0.5 for r in results)

    M_vals = [r["M_conservative"] for r in results]
    check3 = all(M_vals[i] < M_vals[i+1] for i in range(len(M_vals)-1))

    decision = check1 and check3

    print("Summary:")
    print(f"  {'R':>3}  {'M_dissipative':>14}  {'M_conservative':>15}")
    for r in results:
        print(f"  {r['R']:>3}  {r['M_end_phase2']:>14.1f}  {r['M_conservative']:>15.1f}")
    print()
    print("Checks:")
    print(f"  Check 1 (M_conservative > 50 for all R): {'PASS' if check1 else 'FAIL'}")
    print(f"  Check 2 (M_cons > 50% of M_diss):        {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (M_cons monotone in R):           {'PASS' if check3 else 'FAIL'}")
    print()
    print(f"qng_conservative_mring_reference: {'PASS' if decision else 'FAIL'}")

    # Ratio table
    print()
    print("M_ring ratio (conservative / dissipative):")
    for r in results:
        ratio = r["M_conservative"] / r["M_end_phase2"] if r["M_end_phase2"] > 0 else 0.0
        print(f"  R={r['R']}: {ratio:.3f}x")

    report = {
        "test_id": "QNG-CPU-074",
        "decision": "pass" if decision else "fail",
        "params": {
            "L": L, "PHASE1": PHASE1, "PHASE2": PHASE2, "PHASE3": PHASE3,
            "K_BACK": K_BACK, "CHI_DECAY": CHI_DECAY,
        },
        "results": results,
        "canonical_M_ring": {r["R"]: r["M_conservative"] for r in results},
        "checks": {
            "all_rings_survive_phase3": check1,
            "conservative_above_half_dissipative": check2,
            "M_monotone_in_R": check3,
        },
        "note": (
            "M_conservative (Phase-3, T=1000) is the canonical value for mass identification "
            "per DER-QNG-036 §6. The dissipative values are deprecated for this purpose."
        ),
    }
    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    summary = [
        "# QNG-CPU-074 Conservative M_ring Scan",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Purpose",
        "Canonical M_ring values for mass identification (DER-QNG-036 §6).",
        "CPU-051 dissipative values are deprecated; Phase-3 conservative values used here.",
        "",
        "## Results",
        "| R | M_dissipative (Phase 2 end) | M_conservative (Phase 3, T=1000) | Ratio |",
        "|---|---------------------------|----------------------------------|-------|",
    ]
    for r in results:
        ratio = r["M_conservative"] / r["M_end_phase2"] if r["M_end_phase2"] > 0 else 0.0
        summary.append(
            f"| {r['R']} | {r['M_end_phase2']:.1f} | {r['M_conservative']:.1f} | {ratio:.3f}x |"
        )
    summary += [
        "",
        "## Checks",
        f"- Check 1 (all rings survive Phase 3): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (M_cons > 50% of M_diss):   {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (M_cons monotone in R):      {'PASS' if check3 else 'FAIL'}",
    ]
    (out / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
