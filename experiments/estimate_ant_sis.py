#!/usr/bin/env sage -python

from __future__ import annotations

from dataclasses import dataclass
from math import log2
from estimator_path import add_lattice_estimator_to_path


add_lattice_estimator_to_path()

from sage.all import RR, log, oo  # noqa: E402
from estimator import SIS  # noqa: E402
from estimator.sis_parameters import SISParameters  # noqa: E402


N = 256
Q = 2**23 - 2**13 + 1


@dataclass(frozen=True)
class AntParams:
    name: str
    k: int
    l: int
    beta_xy: int
    beta_k: int
    claimed_lambda: int

    @property
    def beta_ver(self) -> int:
        return 2 * self.beta_xy * self.beta_k

    @property
    def sis_bound(self) -> int:
        return 2 * self.beta_ver

    @property
    def rows(self) -> int:
        return self.k * N

    @property
    def cols(self) -> int:
        return self.l * N


CONFIGS = [
    AntParams("ANT-II", k=4, l=3, beta_xy=6, beta_k=6, claimed_lambda=103),
    AntParams("ANT-III", k=5, l=4, beta_xy=5, beta_k=5, claimed_lambda=138),
    AntParams("Swapped ANT-II", k=3, l=4, beta_xy=6, beta_k=6, claimed_lambda=103),
    AntParams("Swapped ANT-III", k=4, l=5, beta_xy=5, beta_k=5, claimed_lambda=138),
]


def fmt_power(value) -> str:
    if value == oo:
        return "inf"
    try:
        return f"{float(value):.1f}"
    except Exception:
        return repr(value)


def fmt_prob_bits(value) -> str:
    if value is None:
        return "-"
    try:
        if value == 0:
            return "inf"
        return f"{float(-log(RR(value), 2)):.1f}"
    except Exception:
        return "?"


def log2_expected_short_kernel_vectors(rows: int, cols: int, bound: int) -> float:
    """Random-SIS sanity check for expected infinity-bounded kernel vectors."""
    return cols * log2(2 * bound + 1) - rows * log2(Q)


def estimate_one(params: AntParams):
    sis_params = SISParameters(
        n=params.rows,
        q=Q,
        m=params.cols,
        length_bound=params.sis_bound,
        norm=oo,
        tag=params.name,
    )
    return SIS.estimate(sis_params, quiet=True, catch_exceptions=False)["lattice"]


def main() -> None:
    print("=" * 88)
    print("ANT Ring-SIS collision-resistance estimates")
    print(f"R_q = Z_q[x]/(x^{N}+1), q = {Q}")
    print("Model: find nonzero dz with A*dz = 0 and ||dz||_inf <= 2*beta_ver")
    print("=" * 88)
    print(
        "variant             rows  cols  bound  claimed  shape                 "
        "rop       beta   d     -log2(prob)  log2 E[#short]"
    )
    print("-" * 88)

    for params in CONFIGS:
        result = estimate_one(params)
        shape = "underdetermined" if params.cols > params.rows else "overdetermined"
        expected = log2_expected_short_kernel_vectors(
            params.rows, params.cols, params.sis_bound
        )

        print(
            f"{params.name:18s} "
            f"{params.rows:4d}  {params.cols:4d}  "
            f"{params.sis_bound:5d}  {params.claimed_lambda:7d}  "
            f"{shape:20s}  "
            f"2^{fmt_power(result.get('rop')):<7s} "
            f"{fmt_power(result.get('beta')):>5s}  "
            f"{fmt_power(result.get('d')):>5s}  "
            f"{fmt_prob_bits(result.get('prob')):>12s}  "
            f"{expected:14.1f}"
        )


if __name__ == "__main__":
    main()
