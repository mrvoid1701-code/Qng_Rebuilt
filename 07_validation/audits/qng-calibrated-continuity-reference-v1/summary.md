# QNG Calibrated Continuity

- test_id: `QNG-CPU-042`
- decision: `pass`
- verdict: `calibrated continuity SUPPORTED; α*>0 on 4/5 seeds (correct sign: outflow→density decrease); R²_calib > 0.05 on 3/5 seeds; max R²=0.572; mean|α*|=0.00110 (eff. coupling ~10⁻³), cv=0.76 (moderate stability)`

## Optimal coupling α* per seed
  seed 20260325: α*=`0.000695`, nohist=`0.000287`, neg=`False`
  seed 42: α*=`0.000689`, nohist=`-0.000195`, neg=`False`
  seed 137: α*=`0.001988`, nohist=`0.000194`, neg=`False`
  seed 1729: α*=`0.000143`, nohist=`0.000360`, neg=`False`
  seed 2718: α*=`-0.001963`, nohist=`0.000029`, neg=`True`
  mean|α*|: `0.001096`, cv: `0.7612`

## R²_calib per seed
  seed 20260325: hist=`0.0456`, nohist=`0.1100`, hist_better=`False`
  seed 42: hist=`0.1384`, nohist=`0.0309`, hist_better=`True`
  seed 137: hist=`0.5722`, nohist=`0.0920`, hist_better=`True`
  seed 1729: hist=`0.0347`, nohist=`0.0792`, hist_better=`False`
  seed 2718: hist=`0.2071`, nohist=`0.0004`, hist_better=`True`
  max R²: `0.5722`, count>0.05: `3/5`

## Scale factors per seed
  seed 20260325: rms(Δρ)=`0.005070`, rms(divJ)=`0.537985`, rms(resid_calib)=`0.005056`
  seed 42: rms(Δρ)=`0.003403`, rms(divJ)=`0.337116`, rms(resid_calib)=`0.003395`
  seed 137: rms(Δρ)=`0.005407`, rms(divJ)=`0.632478`, rms(resid_calib)=`0.005258`
  seed 1729: rms(Δρ)=`0.003553`, rms(divJ)=`0.425882`, rms(resid_calib)=`0.003552`
  seed 2718: rms(Δρ)=`0.003981`, rms(divJ)=`0.456329`, rms(resid_calib)=`0.003879`
