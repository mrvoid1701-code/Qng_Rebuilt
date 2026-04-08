from __future__ import annotations

"""QNG-CPU-064: Two-field v7 k_gm scan v2 — corrected sign + Gap 8 fix (CHI_DECAY=0.020)."""

import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-two-field-kgm-scan-v2"

L=20; N=L*L*L; PHASE1=300; PHASE2=1500
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10  # CHI_DECAY=0.020 (Fix B, DER-QNG-034)
K_BACK=0.10; RING_R=5.0; RX=L/2.; RY=L/2.; RZ=L/2.
K_GMS=[0.0, 0.001, 0.005, 0.01, 0.05, 0.10]
SNAP_T=1000

# Expected screening length from DER-QNG-035: lambda_g = sqrt(BETA/(z*ALPHA))
LAMBDA_G_EXPECTED = math.sqrt(BETA / (6 * ALPHA))  # = 3.416 lattice units

def idx3(x,y,z): return (x%L)*L*L+(y%L)*L+(z%L)
def coord3(i): x=i//(L*L);y=(i%(L*L))//L;z=i%L;return x,y,z
def _mi(d):
    while d>L/2: d-=L
    while d<-L/2: d+=L
    return d
def wrap(a): a=a%(2*math.pi);return a-2*math.pi if a>math.pi else a
def adiff(a,b): return wrap(a-b)
def clip01(x): return max(0.,min(1.,x))
def nb(x,y,z): return [idx3(x-1,y,z),idx3(x+1,y,z),idx3(x,y-1,z),idx3(x,y+1,z),idx3(x,y,z-1),idx3(x,y,z+1)]

def init_phi():
    p=[]
    for i in range(N):
        x,y,z=coord3(i);dx=_mi(x-RX);dy=_mi(y-RY);dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy);p.append(math.atan2(dz,rho-RING_R))
    return p

def dis(phi,i):
    x,y,z=coord3(i);nbs=nb(x,y,z)
    sx=sum(math.cos(phi[j]) for j in nbs)/6.;sy=sum(math.sin(phi[j]) for j in nbs)/6.
    return max(0.,1.-math.sqrt(sx*sx+sy*sy))

def step_v7(sg,sm,chi,phi,k_gm,channel_f,channel_g):
    nsg,nsm,nc,np_=[],[],[],[]
    for i in range(N):
        x,y,z=coord3(i);nbs=nb(x,y,z)
        sgb=sum(sg[j] for j in nbs)/6.;smb=sum(sm[j] for j in nbs)/6.
        s=sg[i];m=sm[i];c=chi[i];p=phi[i]
        # sigma_g: A + B + G(if active) + K_GM coupling (MINUS sign: depletion → attractive)
        dsg=ALPHA*(SIGMA_REF-s)+BETA*(sgb-s)
        if channel_g: dsg+=K_BACK*c
        dsg-=k_gm*(SIGMA_REF-m)   # correct sign: matter depletion depletes sigma_g
        nsg.append(clip01(s+dsg))
        # sigma_m: A + B + F(if active) — NO Channel G
        dsm=ALPHA*(SIGMA_REF-m)+BETA*(smb-m)
        if channel_f: dsm-=GAMMA_PHI*dis(phi,i)*m
        nsm.append(clip01(m+dsm))
        # chi: couples to sigma_g only
        nc.append(c*(1-CHI_DECAY)+CHI_REL*(sgb-s)+DELTA*(SIGMA_REF-s))
        # phi: weighted by sigma_m
        tw=sum(sm[j] for j in nbs)
        if tw>1e-10:
            sx2=sum(sm[j]*math.cos(phi[j]) for j in nbs)/tw
            sy2=sum(sm[j]*math.sin(phi[j]) for j in nbs)/tw
            pm=math.atan2(sy2,sx2)
        else: pm=p
        np_.append(wrap(p+BETA_PHI*adiff(pm,p)))
    return nsg,nsm,nc,np_

def ring_nodes_idx():
    idx=[]
    for i in range(N):
        x,y,z=coord3(i);dx=_mi(x-RX);dy=_mi(y-RY);dz=_mi(z-RZ)
        rho=math.sqrt(dx*dx+dy*dy);d=math.sqrt((rho-RING_R)**2+dz*dz)
        if d<=2.5: idx.append(i)
    return idx

def radial_profile_dsg(sg):
    """Compute mean dsg = SIGMA_REF - sigma_g in shells at distance r from center."""
    profile={}
    counts={}
    cx,cy,cz=L/2.,L/2.,L/2.
    for i in range(N):
        x,y,z=coord3(i)
        dx=_mi(x-cx);dy=_mi(y-cy);dz=_mi(z-cz)
        r=int(round(math.sqrt(dx*dx+dy*dy+dz*dz)))
        dsg_i=SIGMA_REF-sg[i]
        profile[r]=profile.get(r,0.)+dsg_i
        counts[r]=counts.get(r,0)+1
    return {r: profile[r]/counts[r] for r in sorted(profile.keys()) if counts[r]>0}

def fit_lambda(profile, r_min=4, r_max=9):
    """Fit lambda from dsg(r) ~ A*exp(-r/lambda) using log-linear regression."""
    pts=[(r, v) for r,v in profile.items() if r_min<=r<=r_max and v>1e-8]
    if len(pts)<3: return None
    rs=[p[0] for p in pts]; vs=[math.log(p[1]) for p in pts]
    n=len(rs); sr=sum(rs); sv=sum(vs); sr2=sum(r*r for r in rs); srv=sum(rs[i]*vs[i] for i in range(n))
    denom=n*sr2-sr*sr
    if abs(denom)<1e-10: return None
    slope=(n*srv-sr*sv)/denom  # slope = -1/lambda
    if slope>=0: return None
    return -1./slope

def run_kgm(k_gm, ring_idx, base_phi):
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=list(base_phi)
    # Phase 1: no Channel F, no Channel G (let phi settle)
    for _ in range(PHASE1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,0.0,False,False)
    snap1000=None; snap1500=None
    for t in range(1,PHASE2+1):
        sg,sm,chi,phi=step_v7(sg,sm,chi,phi,k_gm,True,True)
        if t==SNAP_T:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            dsg_ring=sum(SIGMA_REF-sg[i] for i in ring_idx)/len(ring_idx) if ring_idx else 0.
            cr=math.sqrt(sum(c*c for c in chi)/N)
            prof=radial_profile_dsg(sg)
            lam=fit_lambda(prof)
            snap1000={"t":t,"M":round(M,2),"dsg_ring":round(dsg_ring,6),
                      "chi_rms":round(cr,4),"lambda_fit":round(lam,3) if lam else None,
                      "profile":{r:round(v,6) for r,v in prof.items() if r<=12}}
        if t==PHASE2:
            M=sum(max(0.,SIGMA_REF-sm[i]) for i in range(N))
            dsg_ring=sum(SIGMA_REF-sg[i] for i in ring_idx)/len(ring_idx) if ring_idx else 0.
            cr=math.sqrt(sum(c*c for c in chi)/N)
            prof=radial_profile_dsg(sg)
            lam=fit_lambda(prof)
            snap1500={"t":t,"M":round(M,2),"dsg_ring":round(dsg_ring,6),
                      "chi_rms":round(cr,4),"lambda_fit":round(lam,3) if lam else None,
                      "profile":{r:round(v,6) for r,v in prof.items() if r<=12}}
    return {"k_gm":k_gm,"snap_1000":snap1000,"snap_1500":snap1500,
            "ring_alive":(snap1500["M"]>50 if snap1500 else False)}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-064: Two-field v7 k_gm scan v2 (corrected sign + CHI_DECAY=0.020)")
    print(f"L={L}  R={RING_R}  K_BACK={K_BACK}  CHI_DECAY={CHI_DECAY}  k_gm scan={K_GMS}")
    print(f"Stability check: K_BACK*DELTA={K_BACK*DELTA:.3f} vs threshold={ALPHA+CHI_DECAY*(1-ALPHA):.4f}",
          "STABLE" if K_BACK*DELTA < ALPHA+CHI_DECAY*(1-ALPHA) else "UNSTABLE")
    print(f"Expected lambda_g = sqrt(BETA/(z*ALPHA)) = {LAMBDA_G_EXPECTED:.3f} lattice units")
    print()

    base_phi=init_phi()
    ring_idx=ring_nodes_idx()
    print(f"Ring tube nodes: {len(ring_idx)}")
    print()

    results=[]
    for kgm in K_GMS:
        print(f"  k_gm={kgm:.3f}...", flush=True)
        r=run_kgm(kgm,ring_idx,base_phi)
        results.append(r)
        s1=r["snap_1000"]; s2=r["snap_1500"]
        print(f"    T=1000: M={s1['M']:7.1f}  dsg_ring={s1['dsg_ring']:+.6f}  "
              f"chi={s1['chi_rms']:.4f}  lambda={s1['lambda_fit']}")
        print(f"    T=1500: M={s2['M']:7.1f}  dsg_ring={s2['dsg_ring']:+.6f}  "
              f"chi={s2['chi_rms']:.4f}  lambda={s2['lambda_fit']}")
        # Print radial profile for k_gm=0.01
        if abs(kgm-0.01)<1e-6:
            print("    Radial profile (k_gm=0.01, T=1000):")
            prof=s1["profile"]
            for rr in sorted(prof.keys()):
                if rr<=12:
                    print(f"      r={rr:2d}: dsg={prof[rr]:+.6f}")

    print()
    print("="*70)

    # Checks
    c1=all(r["snap_1000"]["M"]>50 for r in results)
    c2=all(r["snap_1000"]["dsg_ring"]>0 for r in results if r["k_gm"]>0)
    # Check 3: Yukawa decay at k_gm=0.01
    r01=[r for r in results if abs(r["k_gm"]-0.01)<1e-6]
    if r01:
        prof=r01[0]["snap_1000"]["profile"]
        c3=(prof.get(6,0)>prof.get(8,0)>0 and
            prof.get(10,0)>0 and
            (prof.get(6,0)-prof.get(10,0))/(prof.get(6,1e-10) if prof.get(6,0)>1e-10 else 1e-10)>0.10)
        c3=(prof.get(6,0)>0 and prof.get(10,0)>0 and
            (prof.get(6,0)-prof.get(10,0))/prof.get(6,0)>0.10)
    else:
        c3=False
    c4=all(r["snap_1500"]["chi_rms"]<0.05 for r in results if r["k_gm"]<=0.01)

    # Check 5 (informational): screening length
    lam_vals=[r["snap_1000"]["lambda_fit"] for r in results if r["k_gm"]==0.01 and r["snap_1000"]["lambda_fit"]]
    c5_info=f"lambda_fit={lam_vals[0]:.3f} (expected {LAMBDA_G_EXPECTED:.3f})" if lam_vals else "no fit"

    print(f"Check 1 (ring M>50 all k_gm):           {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (dsg_ring > 0, attractive):     {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (Yukawa decay dsg(r=6)>dsg(r=10) by >10%): {'PASS' if c3 else 'FAIL'}")
    print(f"Check 4 (chi_rms < 0.05 at T=1500):     {'PASS' if c4 else 'FAIL'}")
    print(f"Check 5 (screening length, informational): {c5_info}")

    overall="pass" if (c1 and c2 and c3 and c4) else "fail"
    print(f"\nqng_two_field_kgm_scan_v2_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-064","decision":overall,
            "chi_decay":CHI_DECAY,"k_back":K_BACK,
            "stability_lhs":K_BACK*DELTA,"stability_rhs":ALPHA+CHI_DECAY*(1-ALPHA),
            "lambda_g_expected":round(LAMBDA_G_EXPECTED,3),
            "checks":{"ring_alive":c1,"attractive_potential":c2,"yukawa_decay":c3,"chi_stable":c4},
            "results":[{
                "k_gm":r["k_gm"],
                "M_1000":r["snap_1000"]["M"],"dsg_ring_1000":r["snap_1000"]["dsg_ring"],
                "chi_rms_1000":r["snap_1000"]["chi_rms"],"lambda_fit_1000":r["snap_1000"]["lambda_fit"],
                "M_1500":r["snap_1500"]["M"],"dsg_ring_1500":r["snap_1500"]["dsg_ring"],
                "chi_rms_1500":r["snap_1500"]["chi_rms"],"lambda_fit_1500":r["snap_1500"]["lambda_fit"],
                "ring_alive":r["ring_alive"]
            } for r in results],
            "radial_profile_kgm001":r01[0]["snap_1000"]["profile"] if r01 else {}}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
