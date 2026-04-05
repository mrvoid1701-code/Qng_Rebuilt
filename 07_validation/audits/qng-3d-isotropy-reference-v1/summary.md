# QNG 3D Isotropy Reference v1

- decision: `pass`
- lattice: 20^3 = 8000 nodes, z=6 (cubic)
- lambda_pred = 3.4157

## Spherically averaged Yukawa fit
- lambda_sphere = 3.7463
- ratio lambda_sphere / lambda_pred = 1.0968
- R^2 = 0.9957

## Directional fits

| direction | lambda_fit | ratio/pred | R^2   | check4 |
|-----------|------------|------------|-------|--------|
| (1,0,0)   | 3.5902    | 1.0511       | 0.9947 | PASS |
| (1,1,0)   | 3.7702    | 1.1038       | 0.9985 | PASS |
| (1,1,1)   | 3.8671    | 1.1322       | 0.9993 | PASS |

## Isotropy
- max/min lambda = 1.0771  (gate: < 1.20)  PASS

## Summary checks
- Check 1 (Yukawa R^2 > 0.97): 0.9957  PASS
- Check 2 (lambda within 15% of pred): ratio=1.0968  PASS
- Check 3 (isotropy max/min < 1.20): 1.0771  PASS
- Check 4 (each dir within 20% of pred): PASS
- Check 5 (delta_C < 0 in far field): PASS

## Interpretation
PASS: 3D cubic QNG substrate produces isotropic screened Poisson profile. Assumption D2 numerically supported for z=6 cubic lattice. Gap 1 partially closed for cubic graph geometry.
