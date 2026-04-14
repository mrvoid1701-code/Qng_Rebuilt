from __future__ import annotations

"""BETA_PHI stability scan — does slower phi diffusion stabilize rings?

Hypothesis: rings dissolve because phi winding spreads over time (BETA_PHI=0.02).
As phi becomes uniform, disorder drops, Channel F weakens, but ring has already
been disrupted. With smaller BETA_PHI, phi stays localized -> ring stays stable.

Tests BETA_PHI in {0.001, 0.003, 0.005, 0.010, 0.020} for R=4 and R=8.
Runs 5000 Phase-2 steps, prints M every 200.

Also tests: does R=8 stability survive BETA_PHI reduction (confirm or rule out
that R=8 is purely a phi-localization effect).

Gate for stability: avg(rate[-4:]) < 0.005/step  [plateau]
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-beta-phi-stability-scan-v1"

L = 20
N = L * L * L
SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
K_BACK    = 0.10
GAMMA_PHI = 0.10

RX = RY = RZ = float(L // 2)
PHASE1     = 300
PHASE2     = 5000
PRINT_EVERY = 200

BETA_PHI_SCAN = [0.001, 0.003, 0.005, 0.010, 0.020]
RADII         = [4, 8]

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

def step_p1(sg, sm, chi, phi, bp):
    nsg=[0.]*N; nsm=[0.]*N; nc=[0.]*N; np_=[0.]*N
    for i in range(N):
        nbs=NBS[i]; s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        nsg[i]=clip01(s+ALPHA*(SIGMA_REF-s)+BETA*(sgb-s))
        nsm[i]=clip01(m+ALPHA*(SIGMA_REF-m)+BETA*(smb-m))
        nc[i]=c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s)
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_[i]=wrap(p+bp*adiff(pm,p))
    return nsg,nsm,nc,np_

def step_p2(sg, sm, chi, phi, bp):
    nsg=[0.]*N; nsm=[0.]*N; nc=[0.]*N; np_=[0.]*N
    for i in range(N):
        nbs=NBS[i]; s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        nsg[i]=clip01(s+ALPHA*(SIGMA_REF-s)+BETA*(sgb-s))
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)-GAMMA_PHI*disorder(phi,i)*m
        nsm[i]=clip01(m+dsm)
        nc[i]=c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s)
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_[i]=wrap(p+bp*adiff(pm,p))
    return nsg,nsm,nc,np_

def ring_mass(sm):
    return sum(max(0., SIGMA_REF - sm[i]) for i in range(N))

def run(ring_r, beta_phi):
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=init_phi(ring_r)
    for _ in range(PHASE1):
        sg,sm,chi,phi=step_p1(sg,sm,chi,phi,beta_phi)
    track=[]; prev_m=ring_mass(sm)
    for t in range(1, PHASE2+1):
        sg,sm,chi,phi=step_p2(sg,sm,chi,phi,beta_phi)
        if t % PRINT_EVERY == 0:
            m=ring_mass(sm)
            rate=(prev_m-m)/PRINT_EVERY
            track.append({"t":t,"M":round(m,2),"rate":round(rate,5)})
            prev_m=m
    return track

def status(track):
    late=[pt["rate"] for pt in track[-4:]]
    avg=sum(late)/len(late)
    if avg < 0.005: return "STABLE", avg
    if avg < 0.02:  return "PLATEAU", avg
    if avg < 0.08:  return "SLOWING", avg
    return "DISSOLVING", avg

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    all_results={}

    for R in RADII:
        print(f"\n{'='*60}")
        print(f"R={R}  (5000 Phase-2 steps, GAMMA_PHI={GAMMA_PHI})")
        print(f"{'='*60}")
        all_results[R]={}

        for bp in BETA_PHI_SCAN:
            print(f"\n  BETA_PHI={bp:.3f}", flush=True)
            track=run(R, bp)
            all_results[R][bp]=track

            # Print sparse output
            for pt in track:
                if pt["t"] % 1000 == 0 or pt["t"] <= 600:
                    tag=""
                    if pt["rate"] < 0.005: tag=" *** STABLE ***"
                    elif pt["rate"] < 0.02: tag=" ** plateau **"
                    print(f"    T={pt['t']:4d}  M={pt['M']:8.1f}  rate={pt['rate']:.5f}{tag}",
                          flush=True)

            st, avg=status(track)
            peak_m=max(pt["M"] for pt in track)
            final_m=track[-1]["M"]
            print(f"  >> peak={peak_m:.1f}  final={final_m:.1f}  "
                  f"late_rate={avg:.5f}  [{st}]")

    # Save
    report={"params":{"L":L,"PHASE1":PHASE1,"PHASE2":PHASE2,
                       "ALPHA":ALPHA,"BETA":BETA,"GAMMA_PHI":GAMMA_PHI},
            "results":{str(R):{str(bp):all_results[R][bp]
                               for bp in BETA_PHI_SCAN}
                       for R in RADII}}

    with open(out/"report.json","w") as f:
        json.dump(report,f,indent=2)

    # Summary table
    lines=["# BETA_PHI Stability Scan","",
           "| R | BETA_PHI | M_peak | M(T=5000) | late rate | status |",
           "|---|----------|--------|-----------|-----------|--------|"]
    for R in RADII:
        for bp in BETA_PHI_SCAN:
            tr=all_results[R][bp]
            peak=max(pt["M"] for pt in tr)
            final=tr[-1]["M"]
            st,avg=status(tr)
            lines.append(f"| {R} | {bp:.3f} | {peak:.1f} | {final:.1f} "
                         f"| {avg:.5f} | {st} |")
    (out/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
