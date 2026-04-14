from __future__ import annotations

"""QNG-CPU-077 diagnostic: ring stability scan.

Finds the parameter regime where M_ring(t) reaches a stable plateau.
Tests gamma_phi in {0.01, 0.02, 0.04, 0.07, 0.10} for R=4 over 4000 Phase-2 steps.
Also tests R in {4, 5, 6, 8, 10} at default params to find critical radius.

Key question from CPU-076 FAIL:
  Do rings stabilize (dM/dt -> 0) at lower gamma_phi or larger R?

Output: M_ring every 200 steps for each (R, gamma) combination.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-ring-stability-scan-v1"

# Fixed parameters
L = 20
N = L * L * L
SIGMA_REF = 0.5
ALPHA     = 0.005
BETA      = 0.35
BETA_PHI  = 0.02
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
K_BACK    = 0.10

RX = RY = RZ = float(L // 2)
PHASE1 = 300
PHASE2_LONG = 4000   # longer than CPU-074/075 to see asymptotic behavior
PRINT_EVERY = 200

# Part A: gamma scan at R=4
GAMMA_SCAN = [0.01, 0.02, 0.04, 0.07, 0.10]
RADIUS_FIXED = 4

# Part B: radius scan at default gamma
RADIUS_SCAN = [4, 5, 6, 8, 10]
GAMMA_FIXED = 0.10

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

def step_phase1(sg, sm, chi, phi):
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
        np_[i]=wrap(p+BETA_PHI*adiff(pm,p))
    return nsg,nsm,nc,np_

def step_phase2(sg, sm, chi, phi, gamma_phi):
    nsg=[0.]*N; nsm=[0.]*N; nc=[0.]*N; np_=[0.]*N
    for i in range(N):
        nbs=NBS[i]; s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        nsg[i]=clip01(s+ALPHA*(SIGMA_REF-s)+BETA*(sgb-s))
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)-gamma_phi*disorder(phi,i)*m
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

def ring_mass(sm):
    return sum(max(0., SIGMA_REF - sm[i]) for i in range(N))

def run_long(ring_r, gamma_phi, phase2_steps=PHASE2_LONG):
    """Run and return M_ring time series."""
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=init_phi(ring_r)
    for _ in range(PHASE1):
        sg,sm,chi,phi=step_phase1(sg,sm,chi,phi)
    track=[]
    prev_m=ring_mass(sm)
    for t in range(1, phase2_steps+1):
        sg,sm,chi,phi=step_phase2(sg,sm,chi,phi,gamma_phi)
        if t % PRINT_EVERY == 0:
            m=ring_mass(sm)
            rate=(prev_m-m)/PRINT_EVERY  # loss per step
            track.append({"t":t,"M":round(m,2),"rate_per_step":round(rate,4)})
            prev_m=m
    return track

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--skip-radius-scan",action="store_true")
    args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    results={}

    # -----------------------------------------------------------------------
    # Part A: gamma scan at R=4
    # -----------------------------------------------------------------------
    print("="*60)
    print(f"PART A: gamma_phi scan at R={RADIUS_FIXED}")
    print("="*60)

    gamma_results={}
    for gamma in GAMMA_SCAN:
        print(f"\n--- gamma_phi={gamma:.2f} ---", flush=True)
        track=run_long(RADIUS_FIXED, gamma)
        gamma_results[gamma]=track

        for pt in track:
            stable_tag=" <STABLE?" if pt["rate_per_step"] < 0.010 else ""
            print(f"  T={pt['t']:4d}  M={pt['M']:7.1f}  rate={pt['rate_per_step']:.4f}/step{stable_tag}",
                  flush=True)

        # Check for plateau: last 4 checkpoints rate < 0.05/step
        last_rates=[pt["rate_per_step"] for pt in track[-4:]]
        avg_late_rate=sum(last_rates)/len(last_rates)
        final_M=track[-1]["M"]
        print(f"  >> Final M={final_M:.1f}  avg late rate={avg_late_rate:.4f}/step",
              end="")
        if avg_late_rate < 0.05:
            print("  [PLATEAU CANDIDATE]")
        elif avg_late_rate < 0.15:
            print("  [SLOWING]")
        else:
            print("  [DISSOLVING]")

    results["part_a_gamma_scan"]={"R":RADIUS_FIXED,"gamma_values":GAMMA_SCAN,
                                   "tracks":{str(g):gamma_results[g] for g in GAMMA_SCAN}}

    # -----------------------------------------------------------------------
    # Part B: radius scan at default gamma
    # -----------------------------------------------------------------------
    if not args.skip_radius_scan:
        print()
        print("="*60)
        print(f"PART B: radius scan at gamma_phi={GAMMA_FIXED}")
        print("="*60)

        radius_results={}
        for R in RADIUS_SCAN:
            print(f"\n--- R={R} ---", flush=True)
            track=run_long(R, GAMMA_FIXED)
            radius_results[R]=track
            # Compute per-circumference rate at late times
            circ=2*math.pi*R
            for pt in track[-3:]:
                rate_per_len=pt["rate_per_step"]/circ
                print(f"  T={pt['t']:4d}  M={pt['M']:7.1f}  "
                      f"rate={pt['rate_per_step']:.4f}/step  "
                      f"rate/len={rate_per_len:.5f}")
            last_rates=[pt["rate_per_step"] for pt in track[-4:]]
            avg=sum(last_rates)/len(last_rates)
            print(f"  >> avg late rate={avg:.4f}/step  per circumference={avg/circ:.5f}")

        results["part_b_radius_scan"]={"gamma":GAMMA_FIXED,"radii":RADIUS_SCAN,
                                        "tracks":{str(R):radius_results[R] for R in RADIUS_SCAN}}

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    rp=out/"report.json"
    with open(rp,"w") as f:
        json.dump(results,f,indent=2)

    # Summary
    lines=["# QNG Ring Stability Scan","","## Part A: gamma_phi scan (R=4, 4000 steps)",""]
    lines.append("| gamma | M(T=200) | M(T=2000) | M(T=4000) | late rate/step | status |")
    lines.append("|-------|----------|-----------|-----------|----------------|--------|")
    for gamma in GAMMA_SCAN:
        tr=gamma_results[gamma]
        m_early=tr[0]["M"] if tr else 0
        m_mid=next((pt["M"] for pt in tr if pt["t"]==2000),tr[len(tr)//2]["M"] if tr else 0)
        m_late=tr[-1]["M"] if tr else 0
        late_r=sum(pt["rate_per_step"] for pt in tr[-4:])/4 if len(tr)>=4 else 0
        status="PLATEAU" if late_r<0.05 else ("SLOWING" if late_r<0.15 else "DISSOLVING")
        lines.append(f"| {gamma:.2f} | {m_early:.1f} | {m_mid:.1f} | {m_late:.1f} | {late_r:.4f} | {status} |")

    (out/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
