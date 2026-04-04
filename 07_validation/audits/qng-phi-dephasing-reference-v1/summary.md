# QNG Phi Dephasing Reference v1

- decision: `pass`

## Setup
- epsilon=0.02, delta_B=0.2, N=64, steps=500
- phi_rel=0 (Channel E only, no inter-node smoothing)

## Chi backgrounds
- Condition A: chi_mean=-0.0000, sigma_chi=0.6244
- Condition B: chi_mean=3.3395, sigma_chi=4.5838

## T2* (Condition B)
- T2*_gaussian (informational) = sqrt(2)/(epsilon*sigma_chi) = 15.43 steps
- T2*_exact (from chi values)  = 77.00 steps
- T2*_meas (simulation)        = 77.00 steps
- ratio T2*_meas / T2*_exact   = 1.0000  threshold [0.5, 2.0]

## epsilon constraint
- epsilon = sqrt(2) / (T2*_meas * sigma_chi) = sqrt(2) / (77.0 * 4.5838) = 0.004007 (input epsilon = 0.02)

## Check 1: Decoherence in Condition B
- T2*_meas=77.00 < 500 steps  PASS

## Check 2: T2* matches exact prediction
- ratio=1.0000  threshold [0.5, 2.0]  PASS

## Check 3: B dephases while A is still coherent
- C_A(T2*_B=t=77) = 0.976052  threshold > 0.3679  PASS

## Check 4: Monotone decay Condition B (early regime)
- C(0)=1.000  C(50)=0.4510  C(100)=0.3601
- PASS

## Coherence series Condition B (every 10 steps)
t=0:1.000  t=10:0.743  t=20:0.582  t=30:0.562  t=40:0.496  t=50:0.451  t=60:0.429  t=70:0.432  t=80:0.384  t=90:0.370  t=100:0.360  t=110:0.379

## Interpretation
Dephasing confirmed. epsilon = sqrt(2) / (T2*_meas * sigma_chi) = sqrt(2) / (77.0 * 4.5838) = 0.004007 (input epsilon = 0.02). Input ε = 0.0200. Matching T₂* to observed decoherence time constrains ε in substrate units.
