# QNG Sigma Stability Reference v1

- decision: `pass`

## Theoretical prediction (DER-QNG-025)
- sigma channel: purely dissipative
- decay timescale: 1/alpha = 200 steps
- predicted value at T=3000: 1.22e-07

## Results

| run | alpha_fit | ratio/pred | final |delta_C| | final integral | PASS |
|-----|-----------|------------|------------------|----------------|------|
| with chi (delta=0.2) | 0.00501 | 1.0025 | 4.34e-09 | 0.0000 | ✓ |
| no chi (delta=0) | 0.00501 | 1.0025 | 4.34e-09 | 0.0000 | ✓ |

## Summary checks
- Check 1 (deficit < 0.01 at T=3000): 4.34e-09  PASS
- Check 2 (integral decay rate within 10%): alpha_fit=0.00501  ratio=1.0025  PASS
- Check 3 (integral near-zero at T=3000 < 0.001): 3.54e-07  PASS
- Check 4 (chi does not affect sigma, within 10%): ratio=1.0000  PASS

## Interpretation
PASS: sigma channel is purely dissipative. Localized coherence deficit decays at rate ~alpha with or without chi coupling. Chi does not feed back into sigma (v3 update law confirmed). Stable matter cannot arise from sigma dynamics alone -- requires topological protection via phi winding (DER-QNG-025). This motivates QNG-CPU-041: phi vortex stability test.
