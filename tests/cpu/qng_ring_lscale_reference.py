from __future__ import annotations

"""L-scaling test: is R=8 stability real or a box-size artifact?

On L=20, R=8 with BETA_PHI=0.005 reaches PLATEAU (rate->0, M_inf~1418).
On L=20, R=4 does NOT stabilize.

Hypothesis A (artifact): stable R scales with L -> on L=30 only R=12 stabilizes.
Hypothesis B (physics): stable R is an intrinsic property -> on L=30 R=8 ALSO stabilizes.

Test: run R=8 and R=12 on L=30 with BETA_PHI=0.005, 3000 Phase-2 steps.
Also run R=8 on L=20 as control (should reproduce PLATEAU from previous scan).

If R=8 stable on L=30 -> Hypothesis B confirmed. R=8 is the natural stable ring size.
If R=8 unstable but R=12 stable on L=30 -> Hypothesis A confirmed. Box artifact.
If neither stable on L=30 -> L=30 still too small, need L=40.

Key metric: avg(rate[-3:]) < 0.015/step -> stable/plateau
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-lscale-v1"

SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.005   # best value from BETA_PHI scan
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
K_BACK    = 0.10
GAMMA_PHI = 0.10

PHASE1     = 300
PHASE2     = 3000
PRINT_EVERY = 200

# Test matrix
CONFIGS = [
    (20,  8),   # control — known PLATEAU
    (30,  8),   # Hypothesis B: still stable?
    (30, 12),   # Hypothesis A: scales with L -> stable here
    (30, 10),   # intermediate
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

    return N, NBS, init_phi, disorder, _mi

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
    N, NBS, init_phi, disorder, _mi = make_geometry(L)

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
        sg,sm,chi,phi=step(sg,sm,chi,phi, channel_f=False)

    track=[]; prev_m=ring_mass(sm, N)
    for t in range(1, PHASE2+1):
        sg,sm,chi,phi=step(sg,sm,chi,phi, channel_f=True)
        if t % PRINT_EVERY == 0:
            m=ring_mass(sm, N)
            rate=(prev_m-m)/PRINT_EVERY
            track.append({"t":t,"M":round(m,2),"rate":round(rate,5)})
            prev_m=m
    return track

def status(track):
    late=[pt["rate"] for pt in track[-3:]]
    avg=sum(late)/len(late)
    if avg < 0.005:  return "STABLE",  avg
    if avg < 0.015:  return "PLATEAU", avg
    if avg < 0.06:   return "SLOWING", avg
    return "DISSOLVING", avg

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print(f"L-scaling test: BETA_PHI={BETA_PHI}, GAMMA_PHI={GAMMA_PHI}")
    print(f"PHASE1={PHASE1}, PHASE2={PHASE2}")
    print(f"Hypothesis A (artifact): stable R scales with L -> L=30 stable at R=12, not R=8")
    print(f"Hypothesis B (physics):  stable R fixed at R=8 -> L=30 also stable at R=8")
    print()

    all_results = {}

    for L, R in CONFIGS:
        key = f"L{L}_R{R}"
        print(f"{'='*55}")
        print(f"L={L}  R={R}  (N={L**3} nodes)", flush=True)
        print(f"{'='*55}")

        track = run_config(L, R)
        all_results[key] = {"L": L, "R": R, "track": track}

        peak = max(pt["M"] for pt in track)
        for pt in track:
            if pt["t"] % 600 == 0 or pt["t"] <= 400:
                tag = ""
                if pt["rate"] < 0.005:  tag = "  *** STABLE ***"
                elif pt["rate"] < 0.015: tag = "  ** plateau **"
                print(f"  T={pt['t']:4d}  M={pt['M']:8.1f}  rate={pt['rate']:.5f}{tag}",
                      flush=True)

        st, avg = status(track)
        print(f"  >> peak={peak:.1f}  final={track[-1]['M']:.1f}  "
              f"late_rate={avg:.5f}  [{st}]")
        print()

    # Verdict
    print("="*55)
    print("VERDICT")
    print("="*55)

    ctrl   = all_results.get("L20_R8",  {})
    l30_r8  = all_results.get("L30_R8",  {})
    l30_r12 = all_results.get("L30_R12", {})
    l30_r10 = all_results.get("L30_R10", {})

    st_ctrl,  _ = status(ctrl["track"])   if ctrl  else ("?", 0)
    st_r8,    _ = status(l30_r8["track"]) if l30_r8 else ("?", 0)
    st_r12,   _ = status(l30_r12["track"]) if l30_r12 else ("?", 0)
    st_r10,   _ = status(l30_r10["track"]) if l30_r10 else ("?", 0)

    print(f"  L=20 R=8  (control):  {st_ctrl}")
    print(f"  L=30 R=8:             {st_r8}")
    print(f"  L=30 R=10:            {st_r10}")
    print(f"  L=30 R=12:            {st_r12}")
    print()

    r8_stable  = st_r8  in ("STABLE", "PLATEAU")
    r12_stable = st_r12 in ("STABLE", "PLATEAU")

    if r8_stable and not r12_stable:
        verdict = "HYPOTHESIS B CONFIRMED: R=8 is intrinsically stable, not box artifact"
    elif r12_stable and not r8_stable:
        verdict = "HYPOTHESIS A CONFIRMED: stable R scales with L (artifact)"
    elif r8_stable and r12_stable:
        verdict = "BOTH stable: both R=8 and R=12 plateau on L=30"
    else:
        verdict = "NEITHER stable on L=30: need larger L or different parameters"

    print(f"  {verdict}")

    # Save
    report = {"params": {"BETA_PHI": BETA_PHI, "ALPHA": ALPHA, "GAMMA_PHI": GAMMA_PHI,
                          "PHASE1": PHASE1, "PHASE2": PHASE2},
              "configs": CONFIGS,
              "results": all_results,
              "verdict": verdict}
    with open(out/"report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# L-scaling test", "",
             f"BETA_PHI={BETA_PHI}, PHASE2={PHASE2}", "",
             "| L | R | M_peak | M_final | late_rate | status |",
             "|---|---|--------|---------|-----------|--------|"]
    for (L, R) in CONFIGS:
        key = f"L{L}_R{R}"
        d = all_results[key]
        peak = max(pt["M"] for pt in d["track"])
        final = d["track"][-1]["M"]
        st, avg = status(d["track"])
        lines.append(f"| {L} | {R} | {peak:.1f} | {final:.1f} | {avg:.5f} | {st} |")
    lines += ["", f"**Verdict:** {verdict}"]
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
