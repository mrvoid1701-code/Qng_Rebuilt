from __future__ import annotations

"""QNG-CPU-072: K_GM scan — gravitational signal vs coupling constant.

CPU-071: min_dsg ~ 3e-4 at K_GM=0.001, too small for Yukawa fit.
Scan K_GM = 0.001, 0.005, 0.010, 0.020, 0.050 with ring Q=0 and Hopfion Q=1.
Find maximum stable K_GM and extract Yukawa lambda.
"""

import json, math, time
from pathlib import Path

try:
    import cupy as cp
    xp = cp
    DEVICE = "GPU (CuPy)"
except ImportError:
    import numpy as cp  # type: ignore
    xp = cp
    DEVICE = "CPU (numpy fallback)"

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-hopfion-kgm-scan-v1"

L=20; PHASE1=300; PHASE2_DISS=1500
SIGMA_REF=0.5; ALPHA=0.005; BETA=0.35; BETA_PHI=0.02
DELTA=0.20; CHI_DECAY=0.020; CHI_REL=0.35; GAMMA_PHI=0.10
K_BACK=0.10; RING_R=5.0
RX=L/2.; RY=L/2.; RZ=L/2.
PI = math.pi

KGM_VALUES = [0.001, 0.005, 0.010, 0.020, 0.050]

class _NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

def _mi(d): return d - xp.round(d/L)*L
def wrap(a): a=a%(2*PI); return xp.where(a>PI,a-2*PI,a)
def adiff(a,b): return wrap(a-b)
def nb6(a): return (xp.roll(a,1,0)+xp.roll(a,-1,0)+xp.roll(a,1,1)+xp.roll(a,-1,1)+xp.roll(a,1,2)+xp.roll(a,-1,2))/6.
def nb6s(a): return (xp.roll(a,1,0)+xp.roll(a,-1,0)+xp.roll(a,1,1)+xp.roll(a,-1,1)+xp.roll(a,1,2)+xp.roll(a,-1,2))

def init_phi(q):
    xs=xp.arange(L,dtype=xp.float32)
    x3=xp.broadcast_to(xs[:,None,None],(L,L,L))
    y3=xp.broadcast_to(xs[None,:,None],(L,L,L))
    z3=xp.broadcast_to(xs[None,None,:],(L,L,L))
    dx=_mi(x3-RX); dy=_mi(y3-RY); dz=_mi(z3-RZ)
    rho=xp.sqrt(dx*dx+dy*dy)
    return wrap(xp.arctan2(dz,rho-RING_R)+q*xp.arctan2(dy,dx))

def dis(phi):
    sx=nb6(xp.cos(phi)); sy=nb6(xp.sin(phi))
    return xp.maximum(xp.zeros_like(phi),1.-xp.sqrt(sx*sx+sy*sy))

def palign(sm,phi):
    tw=nb6s(sm); safe=xp.where(tw>1e-10,tw,xp.ones_like(tw))
    pm=xp.where(tw>1e-10,xp.arctan2(nb6s(sm*xp.sin(phi))/safe,nb6s(sm*xp.cos(phi))/safe),phi)
    return wrap(phi+BETA_PHI*adiff(pm,phi))

def step_diss(sg,sm,chi,phi,k_gm):
    sgb=nb6(sg); smb=nb6(sm)
    sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg)+K_BACK*chi-k_gm*(SIGMA_REF-sm),0.,1.)
    sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm)-GAMMA_PHI*dis(phi)*sm,0.,1.)
    chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
    return sg,sm,chi,palign(sm,phi)

def M(sm):
    v=xp.sum(xp.maximum(xp.zeros_like(sm),SIGMA_REF-sm))
    return float(v.get() if xp.__name__=='cupy' else v)

def get_np(a): return a.get() if xp.__name__=='cupy' else np.array(a)

def yukawa_fit(shell_r, shell_dsg):
    """Fit dsg(r) = A*exp(-r/lam)/r. Returns (lambda, A) or (None, None)."""
    fr=np.array(shell_r); fd=np.array(shell_dsg)
    mask=(fd<0)&(fr>2.5)&(fr<L/2-1)
    if mask.sum()<4: return None,None
    fr2=fr[mask]; fd2=fd[mask]
    logy=np.log(np.abs(fd2)*fr2+1e-15)
    A_mat=np.vstack([np.ones_like(fr2),fr2]).T
    try:
        c=np.linalg.lstsq(A_mat,logy,rcond=None)[0]
        if c[1]<0:
            return round(float(-1./c[1]),3), round(float(-np.exp(c[0])),6)
    except Exception: pass
    return None,None

def shell_avg(dsg_np):
    xs=np.arange(L); xx,yy,zz=np.meshgrid(xs,xs,xs,indexing='ij')
    dx=xx-RX; dy=yy-RY; dz=zz-RZ
    dx-=np.round(dx/L)*L; dy-=np.round(dy/L)*L; dz-=np.round(dz/L)*L
    r=np.sqrt(dx**2+dy**2+dz**2)
    n_bins=L//2-1
    sr=[]; sd=[]
    for b in range(n_bins):
        mask=(r>=b)&(r<b+1)
        if mask.sum()>3:
            sr.append(float(np.mean(r[mask])))
            sd.append(float(np.mean(dsg_np[mask])))
    return sr,sd

def run_scan(q_twist, label):
    print(f"\n{'='*60}")
    print(f"Structure: {label} (q_twist={q_twist})")
    scan_results=[]

    for k_gm in KGM_VALUES:
        # Build fresh for each K_GM
        phi=init_phi(q_twist)
        sg=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
        sm=xp.full((L,L,L),SIGMA_REF,dtype=xp.float32)
        chi=xp.zeros((L,L,L),dtype=xp.float32)

        # Phase 1
        for _ in range(PHASE1):
            sgb=nb6(sg); smb=nb6(sm)
            sg=xp.clip(sg+ALPHA*(SIGMA_REF-sg)+BETA*(sgb-sg),0.,1.)
            sm=xp.clip(sm+ALPHA*(SIGMA_REF-sm)+BETA*(smb-sm),0.,1.)
            chi=chi*(1-CHI_DECAY)+CHI_REL*(sgb-sg)+DELTA*(SIGMA_REF-sg)
            phi=palign(sm,phi)

        # Phase 2 dissipative
        stable=True
        for t in range(1,PHASE2_DISS+1):
            sg,sm,chi,phi=step_diss(sg,sm,chi,phi,k_gm)
            # Check stability: sigma_g must not collapse
            sg_min=float(xp.min(sg).get() if xp.__name__=='cupy' else xp.min(sg))
            if sg_min < 0.1:  # collapse threshold
                stable=False; print(f"  K_GM={k_gm}: UNSTABLE at t={t}"); break

        if not stable:
            scan_results.append({"k_gm":k_gm,"stable":False})
            continue

        M_val=M(sm)
        sg_np=get_np(sg); sm_np=get_np(sm)
        dsg=sg_np-SIGMA_REF

        min_dsg=float(np.min(dsg))
        sr,sd=shell_avg(dsg)
        lam,A=yukawa_fit(sr,sd)

        # Bipolar
        xs=np.arange(L); xx,yy,zz=np.meshgrid(xs,xs,xs,indexing='ij')
        dz_a=zz-RZ; dz_a-=np.round(dz_a/L)*L
        n_mean=float(np.mean(dsg[dz_a>3]))
        s_mean=float(np.mean(dsg[dz_a<-3]))
        b_rms=float(np.mean(np.abs(dsg[np.abs(dz_a)<=3])))
        bipolar=abs(n_mean-s_mean)/(b_rms+1e-12)

        print(f"  K_GM={k_gm:5.3f}: M={M_val:.0f}  min_dsg={min_dsg:.6f}  "
              f"lambda={lam}  bipolar={bipolar:.3f}  stable={stable}")

        scan_results.append({
            "k_gm":k_gm,"stable":True,"M":round(M_val,1),
            "min_dsg":round(min_dsg,7),"lambda_fit":lam,"A_fit":A,
            "bipolar_ratio":round(bipolar,4),
            "shell_r":[round(x,3) for x in sr],
            "shell_dsg":[round(x,7) for x in sd]
        })

    return scan_results

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",default=str(DEFAULT_OUT_DIR))
    args=p.parse_args(); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    print("QNG-CPU-072: K_GM scan — gravitational signal vs coupling")
    print(f"Device: {DEVICE}  K_GM values: {KGM_VALUES}")
    print(f"Phase1={PHASE1}  Phase2_diss={PHASE2_DISS}")

    all_results={}
    for label,q in [("ring_Q0",0),("hopfion_Q1",1)]:
        all_results[label]=run_scan(q,label)

    print("\n" + "="*60)
    print("SUMMARY")
    print(f"{'K_GM':>8} {'Ring min_dsg':>14} {'Ring lambda':>12} {'Hopf min_dsg':>14} {'Hopf lambda':>12}")
    for i,k_gm in enumerate(KGM_VALUES):
        r0=all_results["ring_Q0"][i]
        r1=all_results["hopfion_Q1"][i]
        d0=f"{r0.get('min_dsg',0):.6f}" if r0.get('stable') else "UNSTABLE"
        d1=f"{r1.get('min_dsg',0):.6f}" if r1.get('stable') else "UNSTABLE"
        l0=str(r0.get('lambda_fit','?')) if r0.get('stable') else "-"
        l1=str(r1.get('lambda_fit','?')) if r1.get('stable') else "-"
        print(f"{k_gm:>8.3f} {d0:>14} {l0:>12} {d1:>14} {l1:>12}")

    # Checks
    r0_001=[r for r in all_results["ring_Q0"] if r.get("k_gm")==0.001][0]
    r0_020=[r for r in all_results["ring_Q0"] if r.get("k_gm")==0.020][0]
    c1=(r0_020.get("stable",False) and
        abs(r0_020.get("min_dsg",0)) > 10*abs(r0_001.get("min_dsg",0)))
    c2=any(r.get("lambda_fit") is not None for r in all_results["ring_Q0"]+all_results["hopfion_Q1"])
    c3=r0_020.get("stable",False) and r0_020.get("M",0)>0

    print(f"\nCheck 1 (signal 10x at K_GM=0.020): {'PASS' if c1 else 'FAIL'}")
    print(f"Check 2 (Yukawa lambda found): {'PASS' if c2 else 'FAIL'}")
    print(f"Check 3 (stable at K_GM=0.020): {'PASS' if c3 else 'FAIL'}")

    overall="pass" if (c1 and c3) else "fail"
    print(f"\nqng_hopfion_kgm_scan_reference: {overall.upper()}")

    report={"test_id":"QNG-CPU-072","decision":overall,"device":DEVICE,
            "kgm_values":KGM_VALUES,
            "checks":{"signal_scales":c1,"yukawa_fit_found":c2,"stable_020":c3},
            "ring_Q0":all_results["ring_Q0"],"hopfion_Q1":all_results["hopfion_Q1"]}
    rp=out/"report.json"
    with open(rp,"w") as f: json.dump(report,f,indent=2,cls=_NpEncoder)
    print(f"\nReport: {rp}")
    return 0 if overall=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
