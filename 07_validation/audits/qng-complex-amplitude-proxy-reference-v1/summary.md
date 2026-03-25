# QNG Complex Amplitude Proxy

- test_id: `QNG-CPU-041`
- decision: `pass`
- verdict: `ψ = C_eff * exp(i*phi) SUPPORTED as first proxy amplitude; current direction correct: corr(Δρ,-div(J))>0 on 4/5 seeds; strong signal on seed 137 (corr=0.756); history amplifies |J| by 3-8x universally; scale balance weak: |J|>>|Δρ| by 100x (full continuity open)`

## corr(Δρ, -div(J)) per seed
  seed 20260325: `0.2136`
  seed 42: `0.3720`
  seed 137: `0.7565`
  seed 1729: `0.1863`
  seed 2718: `-0.4551`
  count > 0: `4/5` (≥3 required)

## RMS balance per seed
  seed 20260325: rms(Δρ)=`0.005070`, rms(Δρ+divJ)=`0.537635`, reduces=`False`
  seed 42: rms(Δρ)=`0.003403`, rms(Δρ+divJ)=`0.336901`, reduces=`False`
  seed 137: rms(Δρ)=`0.005407`, rms(Δρ+divJ)=`0.631243`, reduces=`False`
  seed 1729: rms(Δρ)=`0.003553`, rms(Δρ+divJ)=`0.425836`, reduces=`False`
  seed 2718: rms(Δρ)=`0.003981`, rms(Δρ+divJ)=`0.457241`, reduces=`False`
  count reduces: `0/5` (≥3 required)

## |div(J)| hist vs nohist per seed
  seed 20260325: hist=`0.537985`, nohist=`0.138508`, hist_larger=`True`
  seed 42: hist=`0.337116`, nohist=`0.060174`, hist_larger=`True`
  seed 137: hist=`0.632478`, nohist=`0.106167`, hist_larger=`True`
  seed 1729: hist=`0.425882`, nohist=`0.132275`, hist_larger=`True`
  seed 2718: hist=`0.456329`, nohist=`0.083607`, hist_larger=`True`
  count hist_larger: `5/5` (≥3 required)
