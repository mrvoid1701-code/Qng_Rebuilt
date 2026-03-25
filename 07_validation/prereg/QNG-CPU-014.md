# QNG-CPU-014

Type: `test`
ID: `QNG-CPU-014`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Check that the first rebuilt Lorentzian-signature proxy has the correct sign pattern, bounded temporal modulation, phase sensitivity, and history imprint.

## Category

`qng core`

## Hardware

`CPU`

## Target

From rebuilt QNG quantities, construct:

- `Q_ctr`
- `T_sig`
- `g_sig`

and verify:

- Lorentzian sign pattern
- negative determinant
- phase sensitivity
- history imprint

## Reference implementation

- `tests/cpu/qng_lorentzian_signature_proxy_reference.py`

## Artifacts

- `07_validation/audits/qng-lorentzian-signature-proxy-reference-v1/report.json`
- `07_validation/audits/qng-lorentzian-signature-proxy-reference-v1/summary.md`
