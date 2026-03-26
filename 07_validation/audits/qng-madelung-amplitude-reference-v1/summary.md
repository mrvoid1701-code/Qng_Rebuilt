# QNG Madelung Amplitude

- test_id: `QNG-CPU-043`
- decision: `pass`
- verdict: `Madelung amplitude ψ_M=sqrt(C_eff)·exp(i·phi) SUPPORTED; α*_M>0 on 4/5 seeds; max R²_M=0.580; mean R²_M=0.203 vs mean R²_std=0.200; Madelung beats standard on 3/5 seeds; mean|α*_M|=0.00058, cv=0.77`

## R²_calib comparison per seed
  seed 20260325: Madelung=`0.0433`, standard=`0.0456`, Madelung_wins=`False`
  seed 42: Madelung=`0.1473`, standard=`0.1384`, Madelung_wins=`True`
  seed 137: Madelung=`0.5800`, standard=`0.5722`, Madelung_wins=`True`
  seed 1729: Madelung=`0.0339`, standard=`0.0347`, Madelung_wins=`False`
  seed 2718: Madelung=`0.2083`, standard=`0.2071`, Madelung_wins=`True`
  mean Madelung: `0.2026`, mean standard: `0.1996`

## α*_M per seed
  seed 20260325: α*_M=`0.000353`, α*_std=`0.000695`, pos=`True`
  seed 42: α*_M=`0.000370`, α*_std=`0.000689`, pos=`True`
  seed 137: α*_M=`0.001043`, α*_std=`0.001988`, pos=`True`
  seed 1729: α*_M=`0.000071`, α*_std=`0.000143`, pos=`True`
  seed 2718: α*_M=`-0.001056`, α*_std=`-0.001963`, pos=`False`
  mean|α*_M|: `0.000578`, cv: `0.7706`

## Scale ratio |divJ|/|Δρ| per seed (Madelung)
  seed 20260325: `212.0x`
  seed 42: `198.1x`
  seed 137: `233.1x`
  seed 1729: `239.9x`
  seed 2718: `223.5x`
