#!/usr/bin/env sage -python
from __future__ import annotations

from estimator_path import add_lattice_estimator_to_path


add_lattice_estimator_to_path()

from estimator import LWE  # noqa: E402
from estimator.nd import Uniform  # noqa: E402
from estimator.lwe_parameters import LWEParameters  # noqa: E402


N = 256
Q = 2**23 - 2**13 + 1

CONFIGS = [
    ("ANT-II", dict(k=4, l=3, beta_xy=6, claimed_lambda=103)),
    ("ANT-III", dict(k=5, l=4, beta_xy=5, claimed_lambda=138)),
    ("Swapped ANT-II", dict(k=3, l=4, beta_xy=6, claimed_lambda=103)),
    ("Swapped ANT-III", dict(k=4, l=5, beta_xy=5, claimed_lambda=138)),
]


def run() -> None:
    for name, params_dict in CONFIGS:
        beta_xy = params_dict["beta_xy"]
        lwe_params = LWEParameters(
            n=N,
            q=Q,
            Xs=Uniform(-beta_xy, beta_xy),
            Xe=Uniform(-beta_xy, beta_xy),
            m=N,
            tag=name,
        )

        print("=" * 78)
        print(name)
        print(
            "  per-block Ring-LWE: "
            f"d=n={N}  q={Q}  k={params_dict['k']}  l={params_dict['l']}  "
            f"beta_xy={beta_xy}  claimed lambda={params_dict['claimed_lambda']}"
        )
        print("=" * 78)
        LWE.estimate(lwe_params)


if __name__ == "__main__":
    run()
