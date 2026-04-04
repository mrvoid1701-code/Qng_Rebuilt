# QNG P1 Spectrum Reference v1

- decision: `pass`

## Conditions
- Condition A: delta=0.0  (Channel D off)
- Condition B: delta=0.2  (Channel D on)

## Check 1: chi tension confirmed
- ⟨χ⟩_A=-0.0000  ⟨χ⟩_B=3.3395
- diff=3.3395  threshold > 0.10  PASS

## Check 2: chi spatial power increases with Channel D
- P_chi_A=12.6962  P_chi_B=672.7141
- ratio=52.98559005387705  threshold > 10.0  PASS

## Check 3: sigma spatial power UNCHANGED (expected null — no chi→sigma feedback)
- P_sigma_A=0.3826  P_sigma_B=0.3826
- |ratio-1|=0.0000  threshold < 0.01  PASS

## Check 4: phi relaxation rate NULL (expected)
- τ_dec_A=20.00  τ_dec_B=20.00
- relative diff=0.0000  threshold < 0.10  PASS
  Interpretation: phi dynamics independent of chi background (no chi→phi coupling in v3)


## Check 5: phi spatial power NULL (expected)
- P_phi_A=140.7876  P_phi_B=140.7876
- relative diff=0.0000  threshold < 0.15  PASS

## Interpretation
chi modulates amplitude sector only (sigma affected, phi unaffected in v3). Chi-to-phi channel is absent in v3. P1 as stated requires a direct chi→phi coupling for the phase sector.
