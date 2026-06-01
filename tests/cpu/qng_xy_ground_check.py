"""Inline sanity check: does the L=28 R=4 trace verify <E_phi_A> = -beta_phi*N/2?

Loads the particle-probe-v1 trace and reports available fields; if E_phi_A
is separately recorded, compares the mean to the analytical XY ground state.
Otherwise reports what fields are available for interpretation.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "07_validation" / "audits" / "qng-v8-particle-probe-v1" / "traces.npz"

BETA_PHI = 0.06
N = 28 ** 3
PREDICTED_GROUND = -BETA_PHI * N / 2.0

print("=" * 78)
print("XY ground-state sanity check on L=28 R=4 R1 trace")
print("=" * 78)
print(f"  Predicted E_phi_A_ground = -beta_phi*N/2 = {PREDICTED_GROUND:.2f}")
print(f"  Predicted <L> = -E_phi_A_ground = {-PREDICTED_GROUND:.2f}")

data = np.load(TRACE)
print(f"\n  Available fields: {sorted(data.files)}")

times = data['times']
warm = times > 500.0
print(f"  N_samples_warm = {int(warm.sum())} / {len(times)}")

for fld in ['H', 'T_g', 'T_m', 'T_phi', 'V_couple']:
    if fld in data.files:
        v = data[fld][warm]
        print(f"  <{fld}> = {float(v.mean()):12.4f} (std {float(v.std()):.4f})")

# E_char check
if 'H' in data.files and 'T_g' in data.files:
    H = data['H'][warm]
    Tg = data['T_g'][warm]
    Tm = data['T_m'][warm]
    Tp = data['T_phi'][warm]
    Tkin = Tg + Tm + Tp
    E_char = 2 * Tkin.mean() - H.mean()
    print(f"\n  Measured E_char = 2<T>-<H> = {E_char:.4f}")
    print(f"  Predicted (XY ground state) = {-PREDICTED_GROUND:.4f}")
    print(f"  Agreement: {(E_char / -PREDICTED_GROUND - 1) * 100:+.3f}%")

print()
print("NOTE: direct sector breakdown (E_phi_A alone) not in trace.npz.")
print("Would need a post-hoc reconstruction via snapshot replay.")
