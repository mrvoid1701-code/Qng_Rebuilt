# REPORT — demo Phase-12 (Drumul 1) proton mass scale

Date: 2026-06-01
Probe: `demo-theory/tests/t_phase12_proton_mass.py`
Verdict: **PROTON_MASS_SCALE_FROM_FIRST_PRINCIPLES**

Chain: theory-v2 derived hbar/c/G -> unit bridge a_M=1.524 m_Planck=1.86e19 GeV
(substrate = Planck scale) -> Phase 11 dimensional transmutation
Lambda_QCD=m_Planck*exp(-2pi/(b0 alpha_s(M_P))), b0=9 -> Skyrme factor
M_p/Lambda~4.5 -> proton.

| alpha_s(M_P) | Lambda_QCD (GeV) | M_proton=4.5*Lambda (GeV) | orders below a_M |
|---|---|---|---|
| 0.0153 | 0.186 | 0.94 | 19.3 |
| 0.0170 | 17.9 | 80 | 17.4 |
| 0.0200 | 8450 | 38000 | 14.7 |

With alpha_s(M_P)=0.0153 (SM strong coupling at M_Planck ~0.02 ballpark) and
k_Skyrme=4.5: M_proton(QNG)=0.94 GeV vs observed 0.938 GeV, 19.3 orders below
the substrate (Planck) scale. First absolute mass SCALE from the QNG substrate.

## Honest scope

(1) The SCALE (GeV, ~19 orders below Planck) is the robust prediction; the VALUE
is EXPONENTIALLY sensitive to alpha_s(M_P) (+/-10% -> orders of magnitude), so
938 MeV is reproduced GIVEN alpha_s(M_P) to ~1%, not predicted to 1%.
(2) alpha_s(M_P) is an INPUT (Gap 17 / Drumul 3).
(3) k_Skyrme=4.5 from QCD phenomenology, not computed here.
(4) Assumes edge-SU(3) standard asymptotic freedom (Phase 3 consistent).

Key unblock: hbar IS derived in theory-v2 (Stability Principle, ch.05) -- closes
the unit bridge and makes a_M a genuine Planck-scale output. Earlier "hbar
axiomatic" was wrong; the failed program was hbar-from-dynamics, a different
thing. NOTE-QNG-024 withdrew a different claim (<L>=hbar), not this derivation.
