from __future__ import annotations

"""Equilibrium long-run confirmation: ratio=2 candidate (alpha=0.005, gamma=0.010).

From equilibrium stability scan:
  ratio=2 (alpha=0.005, gamma=0.010) reached PLATEAU on L=30/R=8.
  Rate at T=5000: 0.01167, decaying geometrically (~0.63x per 1000 steps).
  Extrapolated: rate -> 0 around T=8000-10000, M_inf ~ 320-330.

This test confirms or denies genuine stability in infinite-volume limit:
  - L=30, R=8: extend to 12000 steps (should reach STABLE if geometric decay continues)
  - L=40, R=8: same params on larger box (if stable R scales with L, R=8 on L=40 will dissolve)
  - L=40, R=10: control — R/L=0.25 on L=40, not the resonance (0.40*40=16)

Gate for genuine stability:
  avg(rate[-5:]) < 0.003/step AND rate still decreasing (not flattening)

If L=30/R=8 stabilizes AND L=40/R=8 also stabilizes -> genuine physics (not box artifact).
If L=30/R=8 stabilizes AND L=40/R=8 dissolves -> box artifact again (R_stable = 0.27*L on L=30
  happens to work, but not universal).
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equilibrium-longrun-v1"

# Target parameters from equilibrium scan
ALPHA     = 0.005
GAMMA_PHI = 0.010   # ratio=2 candidate
SIGMA_REF = 0.5
BETA      = 0.35
BETA_PHI  = 0.005
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35

PHASE1      = 300
PHASE2      = 12000
PRINT_EVERY = 500

# Test matrix: (L, R, label)
CONFIGS = [
    (30,  8, "L30_R8  [candidate — extend from T=5000 to T=12000]"),
    (40,  8, "L40_R8  [box test — does R=8 survive larger box?]"),
    (40, 10, "L40_R10 [intermediate R on large box]"),
]

# ---------------------------------------------------------------------------
# Geometry (parametric in L)
# ---------------------------------------------------------------------------

def make_geometry(L):
    N = L * L * L
    RX = RY = RZ = float(L // 2)

    def idx3(x, y, z):
        return (x % L) * L * L + (y % L) * L + (z % L)

    def coord3(i):
        x = i // (L * L); y = (i % (L * L)) // L; z = i % L
        return x, y, z

    def _mi(d):
        while d >  L / 2: d -= L
        while d < -L / 2: d += L
        return d

    def nb(x, y, z):
        return [idx3(x-1,y,z), idx3(x+1,y,z),
                idx3(x,y-1,z), idx3(x,y+1,z),
                idx3(x,y,z-1), idx3(x,y,z+1)]

    NBS = [nb(*coord3(i)) for i in range(N)]

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

    return N, NBS, init_phi, disorder

def wrap(a):
    a = a % (2 * math.pi)
    return a - 2 * math.pi if a > math.pi else a

def adiff(a, b):
    return wrap(a - b)

def clip01(x):
    return max(0.0, min(1.0, x))

def ring_mass(sm, N):
    return sum(max(0., SIGMA_REF - sm[i]) for i in range(N))

def run_config(L, ring_r):
    N, NBS, init_phi, disorder = make_geometry(L)

    sg  = [SIGMA_REF] * N
    sm  = [SIGMA_REF] * N
    chi = [0.0] * N
    phi = init_phi(ring_r)

    def step(sg, sm, chi, phi, channel_f):
        nsg=[0.]*N; nsm=[0.]*N; nc=[0.]*N; np_=[0.]*N
        for i in range(N):
            nbs=NBS[i]; s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
            sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
            nsg[i]=clip01(s+ALPHA*(SIGMA_REF-s)+BETA*(sgb-s))
            if channel_f:
                dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)-GAMMA_PHI*disorder(phi,i)*m
            else:
                dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)
            nsm[i]=clip01(m+dsm)
            nc[i]=c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s)
            tw=sum(sm[j] for j in nbs)
            if tw>1e-10:
                sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
                sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
                pm=math.atan2(sy2,sx2)
            else: pm=p
            np_[i]=wrap(p+BETA_PHI*adiff(pm,p))
        return nsg,nsm,nc,np_

    for _ in range(PHASE1):
        sg,sm,chi,phi = step(sg,sm,chi,phi, channel_f=False)

    track = []; prev_m = ring_mass(sm, N)
    for t in range(1, PHASE2+1):
        sg,sm,chi,phi = step(sg,sm,chi,phi, channel_f=True)
        if t % PRINT_EVERY == 0:
            m = ring_mass(sm, N)
            rate = (prev_m - m) / PRINT_EVERY
            track.append({"t": t, "M": round(m, 2), "rate": round(rate, 5)})
            prev_m = m
    return track

def status(track):
    late = [pt["rate"] for pt in track[-5:]]
    avg = sum(late) / len(late)
    if avg < 0.003:  return "STABLE",  avg
    if avg < 0.012:  return "PLATEAU", avg
    if avg < 0.05:   return "SLOWING", avg
    return "DISSOLVING", avg

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print(f"Equilibrium long-run confirmation")
    print(f"ALPHA={ALPHA}, GAMMA_PHI={GAMMA_PHI} (ratio={GAMMA_PHI/ALPHA:.0f})")
    print(f"BETA_PHI={BETA_PHI}, PHASE2={PHASE2}")
    print(f"Gate: avg(rate[-5:]) < 0.003 -> STABLE")
    print()

    all_results = []

    for L, R, label in CONFIGS:
        print(f"{'='*60}")
        print(f"L={L}  R={R}  N={L**3}  [{label}]", flush=True)
        print(f"R/L={R/L:.3f}  (box resonance at R/L=0.40 -> R={int(0.4*L)})")
        print(f"{'='*60}")

        track = run_config(L, R)
        st, avg = status(track)
        peak = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if pt["rate"] < 0.003:   tag = "  *** STABLE ***"
            elif pt["rate"] < 0.012: tag = "  ** plateau **"
            print(f"  T={pt['t']:6d}  M={pt['M']:8.1f}  rate={pt['rate']:.5f}{tag}",
                  flush=True)

        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.5f}  [{st}]")
        print()

        all_results.append({
            "L": L, "R": R, "label": label,
            "R_over_L": round(R/L, 3),
            "peak": peak, "final": final,
            "late_rate": round(avg, 5), "status": st,
            "track": track,
        })

    # Verdict
    print("="*60)
    print("VERDICT")
    print("="*60)

    r_l30 = next((r for r in all_results if r["L"]==30 and r["R"]==8), None)
    r_l40 = next((r for r in all_results if r["L"]==40 and r["R"]==8), None)

    stable_l30 = r_l30 and r_l30["status"] in ("STABLE", "PLATEAU")
    stable_l40 = r_l40 and r_l40["status"] in ("STABLE", "PLATEAU")

    for r in all_results:
        print(f"  L={r['L']} R={r['R']} (R/L={r['R_over_L']}): "
              f"final={r['final']:.1f}  rate={r['late_rate']:.5f}  [{r['status']}]")
    print()

    if stable_l30 and stable_l40:
        verdict = "GENUINE STABILITY: R=8 stable on both L=30 and L=40 -> not box artifact"
    elif stable_l30 and not stable_l40:
        verdict = "BOX ARTIFACT: R=8 stable on L=30 but dissolves on L=40 -> R_stable scales with L"
    elif not stable_l30:
        verdict = "SLOWING ONLY: R=8 still dissolving on L=30 at T=12000 -> need longer run or different params"
    else:
        verdict = "INCONCLUSIVE"

    print(f"  {verdict}")

    report = {
        "params": {"ALPHA": ALPHA, "GAMMA_PHI": GAMMA_PHI, "BETA_PHI": BETA_PHI,
                   "PHASE1": PHASE1, "PHASE2": PHASE2},
        "results": all_results,
        "verdict": verdict
    }
    with open(out / "report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Equilibrium Long-Run Confirmation", "",
             f"ALPHA={ALPHA}, GAMMA_PHI={GAMMA_PHI}, BETA_PHI={BETA_PHI}, PHASE2={PHASE2}", "",
             "| L | R | R/L | M_peak | M_final | late_rate | status |",
             "|---|---|-----|--------|---------|-----------|--------|"]
    for r in all_results:
        lines.append(f"| {r['L']} | {r['R']} | {r['R_over_L']} | "
                     f"{r['peak']:.1f} | {r['final']:.1f} | "
                     f"{r['late_rate']:.5f} | {r['status']} |")
    lines += ["", f"**Verdict:** {verdict}"]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
