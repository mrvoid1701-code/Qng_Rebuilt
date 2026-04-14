# v8 Channel H: Depletion-Weighted Phi Diffusion (GPU)

L=40, R=8, ALPHA=0.005, PHASE2=20000

| label | ratio | bp_min | bp_ring | M_final | late_rate | trend | status |
|-------|-------|--------|---------|---------|-----------|-------|--------|
| v5_baseline | 1.0 | 0.005 | 0.0 | 140.3 | 0.004424 | flat | PLATEAU |
| v8a_strong | 1.0 | 0.0005 | 0.005 | 243.2 | 0.003543 | dec | PLATEAU-> |
| v8b_moderate | 1.0 | 0.001 | 0.005 | 217.6 | 0.002786 | dec | PLATEAU-> |
| v8c_full | 1.0 | 0.0 | 0.01 | 286.8 | 0.003656 | dec | PLATEAU-> |
| v8d_weak | 1.0 | 0.002 | 0.005 | 191.2 | 0.002682 | dec | PLATEAU-> |
| v8b_ratio2 | 2.0 | 0.001 | 0.005 | 417.4 | 0.005134 | dec | PLATEAU-> |
