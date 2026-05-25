# Aardvark Artifact

This repository contains the anonymous artifact for "Aardvark: Revisiting the
Security of the ANT Signature Scheme". It provides the code needed to reproduce
the main computational claims: public-key-only period-key recovery for the
published ANT parameter sets, Ring-SIS collision-resistance estimates, and
LWE-estimator costs for the signature equation.

## Contents

- `attacks/benchmark_key_recovery.sage`

  Reproduces the public-key-only period-key recovery attack for the published
  ANT-II and ANT-III parameter sets. The script samples public matrices and
  period secrets, recovers both secret vectors from the public key using the CRT
  decomposition, and checks a zero-query forgery equation.

- `experiments/estimate_signature_lwe.py`

  Reproduces the LWE-estimator evaluation for the per-block ANT signature
  equation. The script evaluates ANT-II, ANT-III, and the corresponding swapped
  parameter choices, showing that the estimated cost depends on `(n, q,
  beta_xy)` rather than the orientation of `(k, l)`.

- `experiments/estimate_ant_sis.py`

  Reproduces the Ring-SIS estimator evaluation for ANT's collision-resistance
  route. The script models signature collisions as short nonzero vectors
  `dz` satisfying `A*dz = 0` and `||dz||_inf <= 2*beta_ver`.

- `experiments/estimator_path.py`

  Shared loader for the public `lattice-estimator` dependency used by both
  estimator scripts.

- `scripts/setup_lattice_estimator.sh`

  Fetches the public `lattice-estimator` checkout at the commit used for the
  estimates.

## Requirements

The attack benchmark is written for SageMath. The estimator scripts should be
run with `sage -python` and require the public `lattice-estimator` package.
The recommended layout is to place a checkout at
`third_party/lattice-estimator`; alternatively set `LATTICE_ESTIMATOR_PATH` to
an existing checkout. The estimates in the paper were produced with
lattice-estimator commit `6019056`.

To create the recommended local checkout:

```sh
sh scripts/setup_lattice_estimator.sh
```

The third-party checkout is intentionally not vendored into this artifact. The
artifact pins the commit and keeps only the small ANT-specific estimator
wrappers under `experiments/`.

## Running The Main Attack Benchmark

From the artifact root:

```sh
sage attacks/benchmark_key_recovery.sage
```

Expected behavior:

- The script runs trials for ANT-II and ANT-III.
- For each trial it recovers both period secret vectors from the public key.
- It checks that the recovered key produces a valid forged signature equation.
- The output reports CRT evaluation time, recovery time for each secret vector,
  total recovery time, and the number of successful forgery checks.

## Running The LWE-Estimator Experiment

From the artifact root:

```sh
sage -python experiments/estimate_signature_lwe.py
```

Expected behavior:

- The script runs the standard LWE estimator on one signature ring block.
- It reports uSVP, BDD, dual, dual-hybrid, and coded-BKW costs.
- ANT-II and swapped ANT-II have the same estimates; ANT-III and swapped
  ANT-III also have the same estimates.

## Running The Ring-SIS Estimator Experiment

From the artifact root:

```sh
sage -python experiments/estimate_ant_sis.py
```

Expected behavior:

- The script evaluates the scalarized Ring-SIS instance behind the
  collision-resistance step used by the LM-OTS route.
- It reports the matrix dimensions, infinity-norm bound, claimed security
  level, estimator cost, BKZ block size, and a random-SIS short-solution
  sanity check.

## Notes

The artifact intentionally excludes exploratory BKZ scripts, generated matrix
dumps, bytecode caches, operating-system metadata, and local environment files.
Those files are not needed to reproduce the public-key recovery, Ring-SIS, or
LWE-estimator results.
