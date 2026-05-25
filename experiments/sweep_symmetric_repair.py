#!/usr/bin/env sage -python
from __future__ import annotations

import csv
import math
from pathlib import Path

from sage.all import binomial, log

from estimator_path import add_lattice_estimator_to_path


add_lattice_estimator_to_path()

from estimator import LWE  # noqa: E402
from estimator.nd import Uniform  # noqa: E402
from estimator.lwe_parameters import LWEParameters  # noqa: E402


Q = 2**23 - 2**13 + 1
ATTACKS = ("usvp", "bdd", "dual", "dual_hybrid")
DENY_LIST = ("arora-gb", "bkw", "bdd_hybrid", "bdd_mitm_hybrid")


def rop_bits(cost) -> float:
    return float(math.log(float(cost["rop"]), 2))


def estimate_lwe(n: int, beta_xy: int) -> dict[str, float | str | int]:
    params = LWEParameters(
        n=n,
        q=Q,
        Xs=Uniform(-beta_xy, beta_xy),
        Xe=Uniform(-beta_xy, beta_xy),
        m=n,
        tag=f"n{n}-beta{beta_xy}",
    )
    res = LWE.estimate(
        params,
        deny_list=DENY_LIST,
        jobs=1,
        quiet=True,
        catch_exceptions=True,
    )
    row: dict[str, float | str | int] = {"n": n, "beta_xy": beta_xy}
    vals = {}
    for attack in ATTACKS:
        if attack in res:
            try:
                vals[attack] = rop_bits(res[attack])
            except Exception:
                pass
        row[attack] = vals.get(attack, "")
    best_attack = min(vals, key=vals.get)
    row["min_attack"] = best_attack
    row["min_bits"] = vals[best_attack]
    return row


def message_bits(n: int, beta_k: int) -> float:
    return float(log(binomial(n, beta_k), 2) + beta_k)


def min_beta_k_for_birthday(n: int, target_bits: int) -> tuple[int, float]:
    for beta_k in range(1, n + 1):
        bits = message_bits(n, beta_k)
        if bits >= 2 * target_bits:
            return beta_k, bits
    raise ValueError(f"no beta_k found for n={n}, target={target_bits}")


def packed_sizes(n: int, k: int, ell: int, beta_xy: int, beta_k: int) -> dict[str, float | int]:
    q_bits = math.ceil(math.log2(Q))
    beta_ver = 2 * beta_xy * beta_k
    sig_coeff_bits = math.ceil(math.log2(2 * beta_ver + 1))
    secret_coeff_bits = math.ceil(math.log2(2 * beta_xy + 1))
    return {
        "beta_ver": beta_ver,
        "q_bits": q_bits,
        "sig_coeff_bits": sig_coeff_bits,
        "secret_coeff_bits": secret_coeff_bits,
        "pk_kb": (2 * k * n * q_bits / 8) / 1024,
        "sig_kb": (ell * n * sig_coeff_bits / 8) / 1024,
        "x_or_y_kb": (ell * n * secret_coeff_bits / 8) / 1024,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def print_table(title: str, rows: list[dict], fields: list[str]) -> None:
    print("\n" + title)
    print(",".join(fields))
    for row in rows:
        out = []
        for field in fields:
            value = row[field]
            out.append(f"{value:.2f}" if isinstance(value, float) else str(value))
        print(",".join(out))


def run() -> None:
    out_dir = Path(__file__).resolve().parent / "results"

    dimension_rows = []
    for variant, beta_xy, target in [
        ("ANT-II-like", 6, 103),
        ("ANT-III-like", 5, 138),
    ]:
        for n in [256, 512, 1024, 2048, 4096]:
            row = {"variant": variant, "target": target, **estimate_lwe(n, beta_xy)}
            dimension_rows.append(row)
    write_csv(out_dir / "symmetric_dimension_sweep.csv", dimension_rows)
    print_table(
        "LWE dimension sweep",
        dimension_rows,
        ["variant", "target", "n", "beta_xy", "usvp", "bdd", "dual", "dual_hybrid", "min_attack", "min_bits"],
    )

    beta_rows = []
    for n in [512, 1024]:
        for beta_xy in [5, 6, 8, 12, 16, 24, 32, 48, 64, 80, 96, 100, 128]:
            beta_rows.append(estimate_lwe(n, beta_xy))
    write_csv(out_dir / "symmetric_beta_tradeoff.csv", beta_rows)
    print_table(
        "LWE beta_xy tradeoff",
        beta_rows,
        ["n", "beta_xy", "usvp", "bdd", "dual", "dual_hybrid", "min_attack", "min_bits"],
    )

    candidate_rows = []
    for variant, target, k, ell, beta_xy in [
        ("ANT-II-like", 103, 3, 4, 6),
        ("ANT-III-like", 138, 4, 5, 5),
    ]:
        n = 1024
        beta_k, bits = min_beta_k_for_birthday(n, target)
        candidate_rows.append(
            {
                "variant": variant,
                "target": target,
                "n": n,
                "k": k,
                "ell": ell,
                "beta_xy": beta_xy,
                "beta_k": beta_k,
                "log2_message_space": bits,
                "birthday_bits": bits / 2,
                **packed_sizes(n, k, ell, beta_xy, beta_k),
            }
        )
    write_csv(out_dir / "symmetric_candidate_sizes.csv", candidate_rows)
    print_table(
        "Candidate symmetric repaired sizes",
        candidate_rows,
        [
            "variant",
            "target",
            "n",
            "k",
            "ell",
            "beta_xy",
            "beta_k",
            "beta_ver",
            "birthday_bits",
            "pk_kb",
            "sig_kb",
            "x_or_y_kb",
        ],
    )


if __name__ == "__main__":
    run()
