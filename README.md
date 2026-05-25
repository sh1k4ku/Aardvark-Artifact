# Aardvark Artifact

Anonymous artifact for "Aardvark: Revisiting the Security of the ANT Signature
Scheme".

## Contents

- `attacks/benchmark_key_recovery.sage`: reproduces public-key-only period-key
  recovery and forgery checks for ANT-II and ANT-III.
- `experiments/estimate_ant_sis.py`: estimates the Ring-SIS instance for short
  signature collisions.
- `experiments/estimate_signature_lwe.py`: estimates the per-block signature
  equation as an LWE instance.

## Requirements

- SageMath
- `lattice-estimator` for the two estimator scripts

To fetch the estimator version used for the reported numbers:

```sh
sh scripts/setup_lattice_estimator.sh
```

An existing checkout can also be used by setting `LATTICE_ESTIMATOR_PATH`.

## Run

```sh
sage attacks/benchmark_key_recovery.sage
sage -python experiments/estimate_ant_sis.py
sage -python experiments/estimate_signature_lwe.py
```

The helper script pins `lattice-estimator` to commit `6019056`.
