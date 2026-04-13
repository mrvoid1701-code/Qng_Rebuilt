from __future__ import annotations

"""QNG-CPU-075: Extended M_ring scan for R=3,4,5,6,7.

Tests the baryon resonance ladder prediction from DER-QNG-038:
  R=4 → Nucleon N (938.27 MeV), M_ring anchor = 728.92
  R=5 → Delta Δ(1232 MeV),     M_ring anchor = 954.88
  R=6 → N*(1440) Roper,         M_ring predicted ≈ 1118
  R=7 → Δ*(1600),               M_ring predicted ≈ 1242

Protocol: same CPU-074 conservative protocol — canonical snapshot at T_P2=1000.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-extended-mring-scan-v1"

# ---------------------------------------------------------------------------
# Parameters (identical to CPU-074)
# ---------------------------------------------------------------------------
L = 20
N = L * L * L

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
GAMMA_PHI = 0.10
K_BACK    = 0.10

RX = RY = RZ = float(L // 2)

PHASE1 = 300
PHASE2 = 1500

RADII = [3, 4, 5, 6, 7]

# Canonical anchors from CPU-074 (T_P2=1000 snapshots)
ANCHOR_M = {4: 728.92, 5: 954.88}

# Predictions from DER-QNG-038 (a_M = 1.373e-3, m_u = m_proton)
A_M      = 1.3732e-3   # (a_M from R=4 and R=5 average)
M_PROTON = 938.272     # MeV

PARTICLE_CANDIDATES = {
    3: ("unknown/611 MeV", 611.0),
    4: ("Nucleon N",       938.272),
    5: ("Delta(1232)",     1232.0),
    6: ("N*(1440) Roper",  1440.0),
    7: ("Delta*(1600)",    1600.0),
}

def predicted_mring(m_mev):
    return m_mev / (A_M * M_PROTON)


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
# Step functions (identical to CPU-074)
# ---------------------------------------------------------------------------

def step_phase1(sg, sm, chi, phi):
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

    for _ in range(PHASE1):
        sg, sm, chi, phi = step_phase1(sg, sm, chi, phi)

    m_p2_track = []
    for t in range(1, PHASE2 + 1):
        sg, sm, chi, phi = step_phase2(sg, sm, chi, phi)
        if t in (500, 1000, PHASE2):
            m_p2_track.append({"t_p2": t, "M": round(ring_mass(sm), 2)})

    M_snap_1000 = m_p2_track[1]["M"]   # t_p2=1000 snapshot — canonical value

    return {
        "R": ring_r,
        "M_canonical": M_snap_1000,
        "phase2_track": m_p2_track,
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

    print("QNG-CPU-075: Extended M_ring scan — baryon resonance ladder test")
    print(f"L={L}  PHASE1={PHASE1}  PHASE2={PHASE2}  Canonical snapshot at T_P2=1000")
    print(f"a_M = {A_M:.4e}, m_proton = {M_PROTON} MeV")
    print()
    print("Predictions from DER-QNG-038:")
    for r in RADII:
        name, mass = PARTICLE_CANDIDATES[r]
        pred = predicted_mring(mass)
        if r in ANCHOR_M:
            print(f"  R={r}: {name:25s} m={mass:7.1f} MeV  M_ring anchor={ANCHOR_M[r]:.2f} (CPU-074)")
        else:
            print(f"  R={r}: {name:25s} m={mass:7.1f} MeV  M_ring predicted={pred:.0f}")
    print()

    results = []
    for r in RADII:
        print(f"--- R={r} ---", flush=True)
        res = run_radius(r)
        results.append(res)
        name, mass = PARTICLE_CANDIDATES[r]
        pred = predicted_mring(mass)
        print(f"  M_ring (T_P2=1000): {res['M_canonical']:.2f}  (predicted: {pred:.0f})")
        print()

    # -----------------------------------------------------------------------
    # Checks
    # -----------------------------------------------------------------------
    M = {r["R"]: r["M_canonical"] for r in results}

    # Check 1: CPU-074 anchors reproduced
    ch1_r4 = abs(M[4] - ANCHOR_M[4]) < 5
    ch1_r5 = abs(M[5] - ANCHOR_M[5]) < 5
    check1 = ch1_r4 and ch1_r5

    # Check 2: M_ring monotone in R
    m_vals = [M[r] for r in RADII]
    check2 = all(m_vals[i] < m_vals[i+1] for i in range(len(m_vals)-1))

    # Check 3: N*(1440) Roper prediction at R=6
    pred_r6 = predicted_mring(PARTICLE_CANDIDATES[6][1])
    check3 = abs(M[6] - pred_r6) < 60   # ±5% gate

    # Check 4: Δ*(1600) prediction at R=7
    pred_r7 = predicted_mring(PARTICLE_CANDIDATES[7][1])
    check4 = abs(M[7] - pred_r7) < 75   # ±6% gate

    decision = check1 and check2 and (check3 or check4)

    print("=" * 60)
    print("Results:")
    print(f"  {'R':>3}  {'M_canonical':>12}  {'Predicted':>10}  {'Particle':}")
    for r in RADII:
        name, mass = PARTICLE_CANDIDATES[r]
        pred = predicted_mring(mass)
        dev = (M[r] - pred) / pred * 100 if pred > 0 else 0.0
        flag = "*anchor*" if r in ANCHOR_M else f"({dev:+.1f}%)"
        print(f"  {r:>3}  {M[r]:>12.2f}  {pred:>10.0f}  {name} {flag}")
    print()
    print("Checks:")
    print(f"  Check 1 (CPU-074 anchors: R=4 d<5, R=5 d<5): {'PASS' if check1 else 'FAIL'}")
    print(f"    R=4: {M[4]:.2f} vs anchor {ANCHOR_M[4]:.2f}  d={abs(M[4]-ANCHOR_M[4]):.2f}")
    print(f"    R=5: {M[5]:.2f} vs anchor {ANCHOR_M[5]:.2f}  d={abs(M[5]-ANCHOR_M[5]):.2f}")
    print(f"  Check 2 (M_ring monotone in R):               {'PASS' if check2 else 'FAIL'}")
    print(f"  Check 3 (R=6 -> N*(1440), d<60):              {'PASS' if check3 else 'FAIL'}")
    print(f"    M(R=6)={M[6]:.2f}  predicted={pred_r6:.0f}  d={abs(M[6]-pred_r6):.1f}")
    print(f"  Check 4 (R=7 -> D*(1600), d<75):              {'PASS' if check4 else 'FAIL'}")
    print(f"    M(R=7)={M[7]:.2f}  predicted={pred_r7:.0f}  d={abs(M[7]-pred_r7):.1f}")
    print()
    print(f"qng_extended_mring_reference: {'PASS' if decision else 'FAIL'}")

    report = {
        "test_id": "QNG-CPU-075",
        "decision": "pass" if decision else "fail",
        "params": {
            "L": L, "PHASE1": PHASE1, "PHASE2": PHASE2,
            "A_M": A_M, "m_proton_MeV": M_PROTON,
        },
        "anchors": ANCHOR_M,
        "results": [
            {
                "R": r["R"],
                "M_canonical": r["M_canonical"],
                "particle": PARTICLE_CANDIDATES[r["R"]][0],
                "m_particle_MeV": PARTICLE_CANDIDATES[r["R"]][1],
                "M_ring_predicted": round(predicted_mring(PARTICLE_CANDIDATES[r["R"]][1]), 1),
                "deviation_pct": round(
                    (r["M_canonical"] - predicted_mring(PARTICLE_CANDIDATES[r["R"]][1]))
                    / predicted_mring(PARTICLE_CANDIDATES[r["R"]][1]) * 100, 2
                ),
                "phase2_track": r["phase2_track"],
            }
            for r in results
        ],
        "checks": {
            "cpu074_anchors_reproduced": check1,
            "M_ring_monotone": check2,
            "roper_1440_predicted": check3,
            "delta_star_1600_predicted": check4,
        },
    }

    rp = out / "report.json"
    with open(rp, "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# QNG-CPU-075 Extended M_ring Scan",
        f"- decision: `{'pass' if decision else 'fail'}`",
        "",
        "## Purpose",
        "Baryon resonance ladder prediction from DER-QNG-038.",
        "R=4→N(938), R=5→Δ(1232) anchored by CPU-074.",
        "R=6→N*(1440), R=7→Δ*(1600) tested here.",
        "",
        "## Results",
        f"| R | Particle | M_canonical | M_predicted | Dev% |",
        f"|---|----------|------------|------------|------|",
    ]
    for r in results:
        name, mass = PARTICLE_CANDIDATES[r["R"]]
        pred = predicted_mring(mass)
        dev = (r["M_canonical"] - pred) / pred * 100
        anchor = " *anchor*" if r["R"] in ANCHOR_M else ""
        lines.append(
            f"| {r['R']} | {name} | {r['M_canonical']:.2f} | {pred:.0f} | {dev:+.1f}%{anchor} |"
        )
    lines += [
        "",
        "## Checks",
        f"- Check 1 (CPU-074 anchors reproduced): {'PASS' if check1 else 'FAIL'}",
        f"- Check 2 (M_ring monotone in R):        {'PASS' if check2 else 'FAIL'}",
        f"- Check 3 (R=6 ↔ N*(1440)):             {'PASS' if check3 else 'FAIL'}",
        f"- Check 4 (R=7 ↔ Δ*(1600)):             {'PASS' if check4 else 'FAIL'}",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nReport: {rp}")
    return 0 if decision else 1


if __name__ == "__main__":
    raise SystemExit(main())
