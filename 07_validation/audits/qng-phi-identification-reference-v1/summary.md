# QNG Phi Identification

- test_id: `QNG-CPU-040`
- decision: `pass`
- verdict: `phi is a near-perfectly synchronized phase field (sync>0.94 universally); history introduces phase diversity (anti-ordering, var_hist>var_nohist); phi-L_eff coupling weak and sign-unstable (tier-2); phi->C_eff indirect and topology-dependent (tier-2)`

## corr(phi, L_eff) per seed
  seed 20260325: `-0.3086`
  seed 42: `-0.4615`
  seed 137: `-0.4601`
  seed 1729: `0.1715`
  seed 2718: `0.3108`
  max_abs: `0.4615` (< 0.5 required; sign-unstable = tier-2)

## corr(phi, C_eff) per seed
  seed 20260325: `-0.2621`
  seed 42: `-0.3451`
  seed 137: `-0.7877`
  seed 1729: `0.3687`
  seed 2718: `0.7375`
  count |corr|<0.5: `3/5` (≥3 required)

## corr(phi, sigma) per seed
  seed 20260325: `-0.3039`
  seed 42: `-0.5103`
  seed 137: `-0.7743`
  seed 1729: `0.3539`
  seed 2718: `0.7914`

## corr(phi, history.phase) per seed
  seed 20260325: `0.8682`
  seed 42: `0.8765`
  seed 137: `0.9764`
  seed 1729: `0.8512`
  seed 2718: `0.9639`

## corr(history.phase, C_eff) per seed
  seed 20260325: `-0.0257`
  seed 42: `-0.3126`
  seed 137: `-0.8249`
  seed 1729: `0.0345`
  seed 2718: `0.7309`

## Synchronization order parameter
  seed 20260325: hist=`0.9547`, nohist=`0.9919`, ratio=`0.9624`
  seed 42: hist=`0.9861`, nohist=`0.9986`, ratio=`0.9876`
  seed 137: hist=`0.9411`, nohist=`0.9973`, ratio=`0.9436`
  seed 1729: hist=`0.9554`, nohist=`0.9879`, ratio=`0.9671`
  seed 2718: hist=`0.9819`, nohist=`0.9988`, ratio=`0.9832`
  min(sync_hist): `0.9411` (> 0 required)

## History reduces phase variance?
  seed 20260325: `False` (var_hist=0.1018, var_nohist=0.0228)
  seed 42: `False` (var_hist=0.0434, var_nohist=0.0054)
  seed 137: `False` (var_hist=0.1529, var_nohist=0.0064)
  seed 1729: `False` (var_hist=0.1773, var_nohist=0.0540)
  seed 2718: `False` (var_hist=0.0450, var_nohist=0.0033)
  count var_hist > var_nohist: `5/5` (5/5 required = anti-ordering)
