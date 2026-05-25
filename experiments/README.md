# Estimator Experiments

This directory keeps the estimator-based experiments together.

- `estimate_ant_sis.py` evaluates the Ring-SIS instance that models short
  signature collisions in ANT's LM-OTS proof route.
- `estimate_signature_lwe.py` evaluates the per-block signature equation as an
  LWE instance.
- `estimator_path.py` locates the shared public `lattice-estimator` checkout.

Both scripts use the same external estimator dependency. The recommended local
layout is:

```text
aardvark-artifact/
  experiments/
  scripts/
  third_party/
    lattice-estimator/
```

Run `sh scripts/setup_lattice_estimator.sh` from the artifact root to create
that checkout, or set `LATTICE_ESTIMATOR_PATH` to an existing copy.
