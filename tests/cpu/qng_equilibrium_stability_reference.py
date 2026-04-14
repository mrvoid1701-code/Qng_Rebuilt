from __future__ import annotations

"""Equilibrium stability scan: find gamma/alpha ratio for stable rings.

Root cause identified: gamma/alpha=20 (current) is too high.
Channel F overwhelms Channel A at ring core -> sigma_core -> 0 -> ring dissolves.

Equilibrium condition at ring core:
  gamma * D * sigma* = alpha * (0.5 - sigma*)
  sigma* = 0.5 / (1 + gamma*D/alpha)

For healthy ring: sigma* ~ 0.15-0.25, gamma*D/alpha ~ 1-3, gamma/alpha ~ 2-6.

Test matrix: hold gamma/alpha = 4 (target), vary scale.
Also test gamma/alpha = 2 and 8 to bracket.
All on L=30, R=8 (avoids box artifact: R/L=0.27, not the 0.40 resonance).
BETA_PHI=0.005, 5000 steps.

If any config gives late_rate < 0.005 -> genuine stable ring in large-box limit.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = ROOT / "07_validation" / "audits" / "qng-equilibrium-stability-v1"

L = 30
N = L * L * L
SIGMA_REF = 0.5
BETA      = 0.35
BETA_PHI  = 0.005
DELTA     = 0.20
CHI_DECAY = 0.020
CHI_REL   = 0.35
K_BACK    = 0.10

RX = RY = RZ = float(L // 2)
PHASE1     = 300
PHASE2     = 5000
PRINT_EVERY = 500

# Test matrix: (alpha, gamma_phi) — all with gamma/alpha ratio targeted
# Also keeping alpha*gamma constant to compare "same total energy" configs
CONFIGS = [
    # (alpha,   gamma,  label)
    (0.005, 0.010,  "ratio=2   [current alpha, half gamma]"),
    (0.005, 0.020,  "ratio=4   [current alpha, gamma/5]"),
    (0.002, 0.008,  "ratio=4   [slower dynamics]"),
    (0.001, 0.004,  "ratio=4   [much slower dynamics]"),
    (0.001, 0.002,  "ratio=2   [slow + lower ratio]"),
    (0.005, 0.100,  "ratio=20  [CURRENT default — control]"),
]

R_TEST = 8   # not the box resonance on L=30 (would be R=12)

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

def step(sg, sm, chi, phi, alpha, gamma_phi, channel_f):
    nsg=[0.]*N; nsm=[0.]*N; nc=[0.]*N; np_=[0.]*N
    for i in range(N):
        nbs=NBS[i]; s=sg[i]; m=sm[i]; c=chi[i]; p=phi[i]
        sgb=sum(sg[j] for j in nbs)/6.; smb=sum(sm[j] for j in nbs)/6.
        nsg[i]=clip01(s+alpha*(SIGMA_REF-s)+BETA*(sgb-s))
        if channel_f:
            dsm=alpha*(SIGMA_REF-m)+BETA*(smb-m)-gamma_phi*disorder(phi,i)*m
        else:
            dsm=alpha*(SIGMA_REF-m)+BETA*(smb-m)
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

def run(alpha, gamma_phi):
    sg=[SIGMA_REF]*N; sm=[SIGMA_REF]*N; chi=[0.]*N; phi=init_phi(R_TEST)
    for _ in range(PHASE1):
        sg,sm,chi,phi=step(sg,sm,chi,phi,alpha,gamma_phi,channel_f=False)
    track=[]; prev_m=ring_mass(sm)
    for t in range(1, PHASE2+1):
        sg,sm,chi,phi=step(sg,sm,chi,phi,alpha,gamma_phi,channel_f=True)
        if t % PRINT_EVERY == 0:
            m=ring_mass(sm)
            rate=(prev_m-m)/PRINT_EVERY
            track.append({"t":t,"M":round(m,2),"rate":round(rate,5)})
            prev_m=m
    return track

def status(track):
    late=[pt["rate"] for pt in track[-3:]]
    avg=sum(late)/len(late)
    # Predicted sigma* from equilibrium formula (D~0.5 estimate)
    if avg < 0.003:  return "STABLE",  avg
    if avg < 0.012:  return "PLATEAU", avg
    if avg < 0.05:   return "SLOWING", avg
    return "DISSOLVING", avg

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args=ap.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    print(f"Equilibrium stability scan")
    print(f"L={L}, R={R_TEST}, BETA_PHI={BETA_PHI}, PHASE2={PHASE2}")
    print(f"Equilibrium condition: sigma* = 0.5 / (1 + gamma*D/alpha)")
    print(f"Target gamma/alpha = 2-4 for sigma* ~ 0.1-0.2")
    print()

    all_results = []

    for alpha, gamma, label in CONFIGS:
        ratio = gamma / alpha
        # Predicted sigma* (assuming D~0.5 for R=8 core)
        D_est = 0.5
        sigma_pred = 0.5 / (1 + ratio * D_est)

        print(f"{'='*55}")
        print(f"alpha={alpha}  gamma={gamma}  ratio={ratio:.1f}  [{label}]")
        print(f"Predicted sigma*~{sigma_pred:.3f}  (D~{D_est})", flush=True)
        print(f"{'='*55}")

        track = run(alpha, gamma)
        st, avg = status(track)
        peak = max(pt["M"] for pt in track)
        final = track[-1]["M"]

        for pt in track:
            tag = ""
            if pt["rate"] < 0.003:  tag = "  *** STABLE ***"
            elif pt["rate"] < 0.012: tag = "  ** plateau **"
            print(f"  T={pt['t']:5d}  M={pt['M']:8.1f}  rate={pt['rate']:.5f}{tag}",
                  flush=True)

        print(f"  >> peak={peak:.1f}  final={final:.1f}  "
              f"late_rate={avg:.5f}  [{st}]")
        print()

        all_results.append({
            "alpha": alpha, "gamma": gamma, "ratio": ratio,
            "label": label, "sigma_pred": round(sigma_pred, 3),
            "peak": peak, "final": final,
            "late_rate": round(avg, 5), "status": st,
            "track": track,
        })

    # Summary
    print("="*55)
    print("SUMMARY")
    print("="*55)
    print(f"{'alpha':>7} {'gamma':>7} {'ratio':>6} {'sigma*':>7} {'M_final':>9} {'rate':>8} {'status'}")
    print("-"*65)
    for r in all_results:
        print(f"  {r['alpha']:.3f}   {r['gamma']:.3f}   {r['ratio']:4.0f}   "
              f"{r['sigma_pred']:.3f}   {r['final']:8.1f}   {r['late_rate']:.5f}   {r['status']}")

    stable = [r for r in all_results if r["status"] in ("STABLE", "PLATEAU")]
    if stable:
        print(f"\n*** STABLE RING FOUND ***")
        for r in stable:
            print(f"  alpha={r['alpha']}  gamma={r['gamma']}  ratio={r['ratio']:.1f}"
                  f"  M_stable={r['final']:.1f}  rate={r['late_rate']:.5f}")
    else:
        best = min(all_results, key=lambda r: r["late_rate"])
        print(f"\nNo stable ring. Best: alpha={best['alpha']}, gamma={best['gamma']}"
              f", ratio={best['ratio']:.1f}, rate={best['late_rate']:.5f}")

    report = {"params": {"L": L, "R": R_TEST, "BETA_PHI": BETA_PHI,
                          "PHASE1": PHASE1, "PHASE2": PHASE2},
              "results": all_results}
    with open(out/"report.json", "w") as f:
        json.dump(report, f, indent=2)

    lines = ["# Equilibrium Stability Scan", "",
             f"L={L}, R={R_TEST}, BETA_PHI={BETA_PHI}", "",
             "| alpha | gamma | ratio | sigma* | M_peak | M_final | late_rate | status |",
             "|-------|-------|-------|--------|--------|---------|-----------|--------|"]
    for r in all_results:
        lines.append(f"| {r['alpha']} | {r['gamma']} | {r['ratio']:.0f} | "
                     f"{r['sigma_pred']:.3f} | {r['peak']:.1f} | {r['final']:.1f} | "
                     f"{r['late_rate']:.5f} | {r['status']} |")
    (out/"summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(f"\nArtifacts: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
