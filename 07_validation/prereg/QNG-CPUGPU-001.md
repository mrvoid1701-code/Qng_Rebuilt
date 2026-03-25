# QNG-CPUGPU-001

Type: `test`
ID: `QNG-CPUGPU-001`
Status: `draft`
Author: `C.D Gabriel`

## Objective

Define the first cross-hardware agreement test for a future QNG-core numerical object.

## Category

`QNG pure`

## Hardware

`CPU+GPU`

## Target

When the first native QNG numerical kernel exists, compare CPU and GPU implementations on the same object.

## Candidate object classes

- graph Laplacian spectrum
- propagator estimate
- emergent metric estimator
- return-probability / spectral-dimension estimator

## Pass condition

- same input manifest on CPU and GPU
- metric agreement within declared tolerance
- mismatch recorded explicitly if present

## Artifacts

- CPU result bundle
- GPU result bundle
- comparison report
