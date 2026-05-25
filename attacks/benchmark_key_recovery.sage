import time
from random import choice, sample
from statistics import mean, median

n = 256
q = 2^23 - 2^13 + 1
TRIALS = 10

PARAMS = [
    ("ANT-II", 4, 3, 6, 6),
    ("ANT-III", 5, 4, 5, 5),
]

Zq = GF(q)
R.<x> = PolynomialRing(Zq)
Rq = R.quotient(x^n + 1, 'a')

def sample_uniform_ring():
    return Rq(R([Zq.random_element() for _ in range(n)]))

def sample_small_ring(bound):
    return Rq(R([Zq(ZZ.random_element(-bound, bound + 1)) for _ in range(n)]))

def sample_sparse_ring(weight):
    coeffs = [Zq(0)] * n
    for pos in sample(range(n), weight):
        coeffs[pos] = Zq(choice([-1, 1]))
    return Rq(R(coeffs))

def ring_to_coeffs(elem):
    coeffs = list(elem.lift())
    return coeffs + [Zq(0)] * (n - len(coeffs))

def build_crt_context():
    psi = Zq.multiplicative_generator() ** ((q - 1) // (2 * n))
    assert psi ** n == -1
    assert psi ** (2 * n) == 1

    roots = [psi ** (2 * i + 1) for i in range(n)]
    vander = matrix(Zq, [[roots[i] ** j for j in range(n)] for i in range(n)])
    return vander, vander.inverse()

CRT_VANDER, CRT_INV_VANDER = build_crt_context()

def negacyclic_ntt(elem):
    """Evaluate elem at the n roots of x^n + 1 over Zq."""
    return list(CRT_VANDER * vector(Zq, ring_to_coeffs(elem)))

def negacyclic_intt(values):
    """Interpolate coefficient representation from CRT/NTT values."""
    coeffs = list(CRT_INV_VANDER * vector(Zq, values))
    return Rq(R(coeffs))

def evaluate_public_matrix(A, k, l):
    return [
        [negacyclic_ntt(A[i, j]) for j in range(l)]
        for i in range(k)
    ]

def recover_secret_crt(A_eval, target_vec, k, l):
    target_eval = [negacyclic_ntt(target_vec[i]) for i in range(k)]
    recovered_eval = [[Zq(0)] * n for _ in range(l)]

    for r in range(n):
        A_r = matrix(Zq, [[A_eval[i][j][r] for j in range(l)] for i in range(k)])
        t_r = vector(Zq, [target_eval[i][r] for i in range(k)])
        s_r = A_r.solve_right(t_r)
        for j in range(l):
            recovered_eval[j][r] = s_r[j]

    return vector([negacyclic_intt(recovered_eval[j]) for j in range(l)])

def run_trial(k, l, beta_xy, beta_k):
    A = matrix([[sample_uniform_ring() for _ in range(l)] for _ in range(k)])
    x_secret = vector([sample_small_ring(beta_xy) for _ in range(l)])
    y_secret = vector([sample_small_ring(beta_xy) for _ in range(l)])
    t_pub = A * x_secret
    t_prime_pub = A * y_secret

    t0 = time.perf_counter()
    A_eval = evaluate_public_matrix(A, k, l)
    eval_A_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    x_recovered = recover_secret_crt(A_eval, t_pub, k, l)
    solve_x_time = time.perf_counter() - t1

    t2 = time.perf_counter()
    y_recovered = recover_secret_crt(A_eval, t_prime_pub, k, l)
    solve_y_time = time.perf_counter() - t2

    assert x_recovered == x_secret
    assert y_recovered == y_secret

    h = sample_sparse_ring(beta_k)
    z_forged = vector([x_recovered[i] * h + y_recovered[i] for i in range(l)])
    lhs = A * z_forged
    rhs = vector([t_pub[i] * h + t_prime_pub[i] for i in range(k)])
    assert lhs == rhs

    return {
        "eval_A": eval_A_time,
        "solve_x": solve_x_time,
        "solve_y": solve_y_time,
        "total": eval_A_time + solve_x_time + solve_y_time,
        "forge_ok": True,
    }

def summarize(values):
    return (mean(values), median(values), min(values), max(values))

print("=" * 72)
print("PoC: complete ANT key recovery and zero-query forgery from public key")
print(f"Ring: Z_q[x]/(x^{n}+1), q = {q}, trials per parameter set = {TRIALS}")
print("=" * 72)

for name, k, l, beta_xy, beta_k in PARAMS:
    print(f"\n{name}: k = {k}, l = {l}, beta_xy = {beta_xy}, beta_k = {beta_k}")
    trials = [run_trial(k, l, beta_xy, beta_k) for _ in range(TRIALS)]

    eval_A_stats = summarize([t["eval_A"] for t in trials])
    solve_x_stats = summarize([t["solve_x"] for t in trials])
    solve_y_stats = summarize([t["solve_y"] for t in trials])
    total_stats = summarize([t["total"] for t in trials])
    forge_count = sum(1 for t in trials if t["forge_ok"])

    print(
        "  CRT eval A   : avg %.3fs  med %.3fs  min %.3fs  max %.3fs"
        % eval_A_stats
    )
    print(
        "  recover x    : avg %.3fs  med %.3fs  min %.3fs  max %.3fs"
        % solve_x_stats
    )
    print(
        "  recover y    : avg %.3fs  med %.3fs  min %.3fs  max %.3fs"
        % solve_y_stats
    )
    print(
        "  total        : avg %.3fs  med %.3fs  min %.3fs  max %.3fs"
        % total_stats
    )
    print(f"  forgery check: {forge_count}/{TRIALS}")
