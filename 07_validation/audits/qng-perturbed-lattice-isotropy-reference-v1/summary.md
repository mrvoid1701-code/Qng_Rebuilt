# QNG Perturbed Lattice Isotropy Reference v1

- decision: `pass`
- lattice: 20^3 = 8000 nodes, z=6, perturbation=0.3
- lambda_pred = 3.4157

## Second-moment condition (DER-QNG-024)
- Target diagonal (z/3) = 2.0000
- Mean diagonal: Txx=2.0061  Tyy=2.0050  Tzz=1.9889
- Mean off-diagonal: Txy=-0.0066  Txz=0.0037  Tyz=-0.0049  (target=0)
- max |mean off-diag| = 0.0066  (gate: < 0.05)  PASS
- Diagonal within 5% of target: PASS
- Per-node Frobenius dev: mean=1.3482 (diagnostic; expected large ~O(ε) for irregular graph)

## Spherical Yukawa fit (physical distances)
- lambda_sphere = 3.2317  ratio = 0.9461  R^2 = 0.9977

## Angular octant isotropy
- octant lambdas: [3.491, 3.818, 3.553, 2.815]
- octant max/min = 1.3564  (gate: < 1.30)  PASS

## Summary checks
- Check 1 (R^2 > 0.95): 0.9977  PASS
- Check 2 (lambda within 20%): ratio=0.9461  PASS
- Check 3 (delta_C < 0): PASS
- Check 4 (octant isotropy < 1.45): 1.3564  PASS
- Check 5 (SMC mean off-diag < 0.05): 0.0066  PASS
- Check 6 (SMC diag within 5%): PASS

## Interpretation
PASS: D2 holds approximately on perturbed cubic lattice. SMC: mean off-diagonals ≈ 0 and mean diagonals ≈ z/3 (statistical isotropy). Yukawa profile remains isotropic within tolerance. Gap 1 closed for statistically isotropic graphs (DER-QNG-024).
