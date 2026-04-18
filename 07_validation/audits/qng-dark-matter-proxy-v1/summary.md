# Dark Matter Proxy Test (QNG-GPU-004)

L=60, R_blob=6, R_ring=5, Phase2=3000

## Results

| Config | M0 | M_final | retained% | topo_grew | verdict |
|--------|----|---------|-----------|-----------|---------| 
| blob_Q0 | 180.9 | 0.0 | 0.0% | False | UNSTABLE |
| ring_Q0 | 156.3 | 0.0 | 0.0% | False | UNSTABLE |
| ring_Q1 | 156.3 | 4.2 | 2.7% | False | UNSTABLE |

## Overall: NO_DM_CANDIDATE

All Q=0 structures dissolve => dark matter needs different mechanism

## Key finding: topology is the stabilizer

At T=500:
  blob_Q0: M=0.0  (0.0% of M0)   -- dissolved immediately
  ring_Q0: M=0.0  (0.0% of M0)   -- dissolved immediately
  ring_Q1: M=596  (381% of M0)   -- grew via Channel F (phi disorder active)

At T=1500 (standard protocol endpoint):
  ring_Q1: M=224  (143.5% of M0) -- still active

The discriminator is phi winding (Q=1), not depletion geometry.
Without phi winding: disorder=0 => Channel F = 0 => ALPHA restores sigma_m.
With phi winding:   disorder>0 at torus core => Channel F sustains depletion.

Q=0 structures cannot form in v7 because the only depletion mechanism
(Channel F) requires phi disorder, which requires phi winding.

## Dark matter implications

Dark matter in QNG requires a mechanism outside the sigma_m/phi sector:
  - Candidate A: sigma_g solitons (no phi dependence)
  - Candidate B: Q=2 or higher winding structures
  - Candidate C: hopfion-type structures (different topology class)
  None of these have been tested yet.
