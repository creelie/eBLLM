"""Ultraviolet finiteness of gravity from a scale-invariant gas of branes, as construction-mode objects.

The paper "Cancellation of all ultraviolet divergences of quantum gravity by a scale-invariant
gas of branes" (D. Bhattacharjee and U. Bhattacharya, creelie/brane-cluster-gases, release 3.1.0,
doi:10.5281/zenodo.23524276) proves one theorem: a frozen Poisson gas of branes with no preferred
size multiplies the graviton kinetic operator by an entire function without zeros,

    a(z) = exp[(n/2) Ein(z^2 / M^4)] x (a random factor with a limit at high momentum),
    Ein(w) = int_0^w (1 - e^{-u}) / u du,

and for n >= 4 the theory of gravity built on that operator has no ultraviolet divergence at any
order of perturbation theory.  This module carries the constructions of that proof in the form
construction mode uses, each with a check and a refuter that run in the tests:

    response        the single-brane response of the cell model, psi(w) = 1 - exp(-w^2), with the
                    conditions (S1) no effect on long modes, (S2) passivity, (S3) saturation on the
                    real axis, (S4) saturation in a sector, (S5) no zeros (no resonances).  The
                    refuter is the obvious saturating factor 2 - exp(-w^2), which obeys (S1)-(S4)
                    and has zeros at w^2 = -log 2 + 2 pi i k: each is a complex pole of the
                    propagator, a Lee-Wick pair that a brane obeying (S5) never produces.
    formfactor      the skeleton a(z) of the gas, entire, without zeros, growing like
                    c (z/M^2)^n with c = exp(n gamma / 2) along the real axis.  Every polynomial
                    form factor, the other way of getting power growth, has zeros, hence ghosts.
    powercounting   the bound omega_bar(n, L) = 4L - (2n+2)(L-1) + 2 (L - n - 1 + m)_+ on the
                    superficial degree of an L-loop subgraph, negative for every L >= 2 exactly
                    when n >= 4.  The merging lemma behind it is re-derived here by exhaustive
                    enumeration of the vertex degrees, no inequality assumed (the refuter of the
                    lemma: it never finds a degree vector that beats the bound).
    tuning          the one-loop pole matrix of the three quartic operators,
                    (1/c) [[-12, -1, -8/3], [0, 1, 8], [0, 0, 2]], triangular with determinant
                    -24/c^3, and the tuning that cancels all three poles at once, in exact
                    rational arithmetic.
    vacuum          the zero-point energy 3 n M^4 / (64 pi^2) and the cosmological constant
                    3 n G M^4 / (8 pi), with the Mellin identity int w^{s-1} Ein(w) dw = Gamma(s)/s
                    behind the regulator independence checked in its strip.
    positivity      the refuter of the Euclidean picture: the time-slice covariance F_q(t) of the
                    free graviton of the gas turns negative at finite t (near t = 12/M for q = M),
                    which a reflection-positive Gaussian field, whose F_q is the Laplace transform
                    of a positive measure, never does.  This is why the paper claims finiteness to
                    every order of perturbation theory and no construction beyond it.
    bubble          the one-loop bubble of the skeleton with n = 4 in closed form, the table of the
                    paper, and the energy between 1.4 M and 1.9 M at which the graph overtakes the
                    tree amplitude: where the loop expansion stops being an expansion in a small
                    number.  The table entries are data from the paper (two Pauli-Villars masses
                    agree to ten digits there); only the crossing is computed here.

``check(n)`` returns the conditions the theory with exponent n violates (none for n >= 4) and
``CONSTRUCTIONS`` lists the typed nodes, in the form the crossing network reads, so that the
chain gas -> response class -> entire zero-free form factor -> power counting -> one-loop tuning
-> perturbative finiteness is a composite the engine can take apart.  Nothing here extends the
theorem: the strong-coupling region above M and a definition beyond perturbation theory stay
open, and the control ``brane-gas-uv-finite`` is a CANDIDATE (not refereed).  Everything uses the
standard library only.
"""
from __future__ import annotations

import cmath
import math
from fractions import Fraction
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

EULER = 0.5772156649015329
DOI = "10.5281/zenodo.23524276"
REPO = "https://github.com/creelie/brane-cluster-gases"


# --------------------------------------------------------------------------- the entire exponential integral
def _e1(x: float) -> float:
    """E_1(x) for x > 0 by the continued fraction (modified Lentz); used for x > 5."""
    tiny = 1e-300
    b = x + 1.0
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 400):
        an = -float(i * i)
        b += 2.0
        d = 1.0 / (an * d + b)
        c = b + an / c
        delta = c * d
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return h * math.exp(-x)


def ein(w: float) -> float:
    """Ein(w) = int_0^w (1 - e^{-u})/u du = sum_k (-1)^{k+1} w^k / (k k!) = log w + gamma + E_1(w)."""
    if w < 0:
        raise ValueError("ein is used on the real half line w >= 0")
    if w <= 5.0:
        s = 0.0
        term = 1.0
        for k in range(1, 300):
            term = term * (-w) / k if k > 1 else w
            s += term / k
            if abs(term / k) < 1e-17 * abs(s) + 1e-300:
                break
        return s
    return math.log(w) + EULER + _e1(w)


# --------------------------------------------------------------------------- the single-brane response (S1)-(S5)
def psi_star(w: complex) -> complex:
    """The response of the cell model, psi_*(w) = 1 - exp(-w^2); w = s z, s the brane size."""
    return 1.0 - cmath.exp(-w * w)


def response_conditions(psi=psi_star, grid: Sequence[float] = tuple(x / 4.0 for x in range(-40, 41)),
                        sector: float = math.pi / 4) -> List[str]:
    """The conditions (S1)-(S4) on a response psi, tested on a grid of the real axis and on the closed
    subsector |arg(+-w)| <= 3 sector / 4 at |w| = 4, 5, 6; (S5), no zeros of exp(theta psi), holds for every entire psi.  Returns the
    violated ones (empty for psi_*)."""
    bad = []
    if abs(psi(0.0)) > 1e-14:
        bad.append("(S1) psi(0) != 0: the brane acts on arbitrarily long modes")
    vals = [psi(x) for x in grid]
    if any(abs(v.imag) > 1e-12 for v in vals):
        bad.append("(S2) psi is not real on the real axis")
    if any(v.real < -1e-12 or v.real > 1.0 + 1e-12 for v in vals):
        bad.append("(S2) passivity fails: psi leaves [0, 1] on the real axis")
    tail = [abs(1.0 - psi(x)) for x in (3.0, 4.0, 5.0, -3.0, -4.0, -5.0)]
    if not all(t < 1e-3 for t in tail) or not tail[2] < tail[1] < tail[0]:
        bad.append("(S3) no saturation: 1 - psi does not fall along the real axis")
    for r in (4.0, 5.0, 6.0):
        for sign in (1.0, -1.0):
            for ang in (0.0, 0.5 * sector, 0.75 * sector):
                w = sign * r * cmath.exp(1j * ang)
                if abs(1.0 - psi(w)) > 1e-2:
                    bad.append("(S4) no saturation in the sector |arg(+-w)| < %.3f" % sector)
                    break
            else:
                continue
            break
        else:
            continue
        break
    return bad


def resonances(k_max: int = 3) -> List[complex]:
    """The zeros of the saturating factor 2 - exp(-w^2), the refuter of (S5): w^2 = -log 2 + 2 pi i k."""
    out = []
    for k in range(-k_max, k_max + 1):
        w2 = complex(-math.log(2.0), 2.0 * math.pi * k)
        out.append(cmath.sqrt(w2))
    return out


def no_resonance_factor(w: complex) -> complex:
    return 2.0 - cmath.exp(-w * w)


# --------------------------------------------------------------------------- the form factor of the gas
def form_factor(z: float, n: int = 4, M: float = 1.0) -> float:
    """The skeleton a(z) = exp[(n/2) Ein(z^2/M^4)] on the real axis of z = p^2 (Euclidean or Lorentzian)."""
    return math.exp(0.5 * n * ein((z / (M * M)) ** 2))


def growth_constant(n: int) -> float:
    """a(z) ~ c (|z|/M^2)^n along the real axis, with c = exp(n gamma / 2)."""
    return math.exp(0.5 * n * EULER)


def asymptotic_ratio(z: float, n: int = 4, M: float = 1.0) -> float:
    """a(z) / (c |z/M^2|^n), which tends to 1 like 1 + O(M^4/z^2)."""
    x = abs(z) / (M * M)
    return form_factor(z, n, M) / (growth_constant(n) * x ** n)


def polynomial_zeros_count(coefficients: Sequence[float]) -> int:
    """A polynomial form factor 1 + ... of degree d >= 1 has d zeros (fundamental theorem of algebra),
    each an extra pole of the propagator: the reason power growth cannot come from a polynomial."""
    coeffs = list(coefficients)
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    return max(len(coeffs) - 1, 0)


# --------------------------------------------------------------------------- power counting
def pos(x: int) -> int:
    return x if x > 0 else 0


def omega_bar(n: int, L: int, m_sigma: int = 0) -> int:
    """The bound on the superficial degree of an L-loop subgraph, Eq. (omega) of the paper:
    4L - (2n+2)(L-1) + 2 (L - n - 1 + m_sigma)_+ ; m_sigma = 0 for the saturating response."""
    return 4 * L - (2 * n + 2) * (L - 1) + 2 * pos(L - n - 1 + m_sigma)


@lru_cache(maxsize=None)
def max_excess(V: int, total: int, k: int) -> Optional[int]:
    """max of sum_{v=1}^V (h_v - k)_+ over vertex degrees h_v >= 2 with sum h_v = total, by enumeration."""
    if V == 1:
        return pos(total - k) if total >= 2 else None
    best = None
    for h in range(2, total - 2 * (V - 1) + 1):
        rest = max_excess(V - 1, total - h, k)
        if rest is None:
            continue
        cand = pos(h - k) + rest
        if best is None or cand > best:
            best = cand
    return best


def merging_lemma_counterexample(L_max: int = 6, k_max: int = 20) -> Optional[Tuple[int, int, int, int]]:
    """Search every (V, L, k) with L <= L_max loops, up to 2L+2 vertices and I = V + L - 1 lines for a
    degree vector whose excess sum_v (h_v - k)_+ exceeds (2L - k)_+ ; returns the first one found or
    None.  The merging lemma of the paper says there is none."""
    for L in range(1, L_max + 1):
        for V in range(1, 2 * L + 3):
            total = 2 * (V + L - 1)
            if total < 2 * V:
                continue
            for k in range(3, k_max):
                m = max_excess(V, total, k)
                if m is not None and m > pos(2 * L - k):
                    return (V, L, k, m)
    return None


def finite_beyond_one_loop(n: int, L_max: int = 40, m_sigma: int = 0) -> bool:
    """Every graph with 2 <= L <= L_max loops converges: omega_bar < 0.  (True for n >= 4, false for n <= 3.)"""
    return all(omega_bar(n, L, m_sigma) < 0 for L in range(2, L_max + 1))


def power_table(ns=range(3, 9), Ls=range(1, 6), m_sigma: int = 0) -> Dict[int, List[int]]:
    """The power-counting table of the paper: rows n, columns L."""
    return {n: [omega_bar(n, L, m_sigma) for L in Ls] for n in ns}


# --------------------------------------------------------------------------- the one-loop tuning
POLE_MATRIX = (
    (Fraction(-12), Fraction(-1), Fraction(-8, 3)),
    (Fraction(0), Fraction(1), Fraction(8)),
    (Fraction(0), Fraction(0), Fraction(2)),
)   # times 1/c: the shift of the poles (R^2, Ric^2, E) by the three quartic operators with coefficients t


def det3(a) -> Fraction:
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def tuning(b1, b2, bE) -> Tuple[Fraction, Fraction, Fraction]:
    """The coefficients t = s/c of the three quartic operators that cancel the one-loop poles b1, b2, bE
    of R^2, R_{mu nu}R^{mu nu} and the Gauss-Bonnet density: Eq. (tuning) of the paper."""
    b1, b2, bE = Fraction(b1), Fraction(b2), Fraction(bE)
    u1 = 3 * b1 + 3 * b2 - 8 * bE
    u2 = -36 * b2 + 144 * bE
    u3 = -18 * bE
    return (u1 / 36, u2 / 36, u3 / 36)


def poles_after_tuning(b, t) -> Tuple[Fraction, Fraction, Fraction]:
    """b + A t, which the tuning makes (0, 0, 0)."""
    return tuple(Fraction(b[i]) + sum(POLE_MATRIX[i][j] * Fraction(t[j]) for j in range(3)) for i in range(3))


# --------------------------------------------------------------------------- the vacuum energy
def zero_point_energy(n: int, M: float = 1.0) -> float:
    """rho_1 = 3 n M^4 / (64 pi^2), the mean over realizations, the same for every regulator."""
    return 3.0 * n * M ** 4 / (64.0 * math.pi ** 2)


def cosmological_constant(n: int, M: float = 1.0, G: float = 1.0) -> float:
    """Lambda_1 = kappa^2 rho_1 / 4 with kappa^2 = 32 pi G, i.e. 3 n G M^4 / (8 pi)."""
    return 3.0 * n * G * M ** 4 / (8.0 * math.pi)


def mellin_ein(s: float, lo: float = -40.0, hi: float = 45.0, N: int = 40000) -> float:
    """int_0^inf w^{s-1} Ein(w) dw for -1 < s < 0, by Simpson's rule in u = log w.  Equals Gamma(s)/s."""
    if not -1.0 < s < 0.0:
        raise ValueError("the Mellin transform of Ein converges for -1 < s < 0")
    h = (hi - lo) / N
    acc = 0.0
    for i in range(N + 1):
        u = lo + i * h
        w = math.exp(u)
        f = math.exp(s * u) * ein(w)
        acc += f * (1 if i in (0, N) else (4 if i % 2 else 2))
    return acc * h / 3.0


def gamma_over_s(s: float) -> float:
    return math.gamma(s) / s


# --------------------------------------------------------------------------- reflection positivity (refuter)
def time_slice_covariance(t: float, q: float = 1.0, n: int = 4, M: float = 1.0,
                          P: float = 25.0, N: int = 20000) -> float:
    """F_q(t) = int dp0/(2 pi) cos(p0 t) / ((p0^2 + q^2) a(p0^2 + q^2)) for the free Euclidean graviton of
    the gas; a reflection-positive Gaussian field has F_q >= 0 for every t.  Simpson's rule on [0, P];
    the integrand falls like p0^{-2-2n}, so the tail beyond P = 25 M is below 1e-13."""
    h = P / N
    acc = 0.0
    for i in range(N + 1):
        p = i * h
        z = p * p + q * q
        acc += (1 if i in (0, N) else (4 if i % 2 else 2)) * math.cos(p * t) / (z * form_factor(z, n, M))
    return acc * h / (3.0 * math.pi)


def reflection_positivity_witness(n: int = 4, q: float = 1.0, M: float = 1.0,
                                  ts: Sequence[float] = (8, 9, 10, 11, 12, 13, 14, 15, 16)) -> Optional[Tuple[float, float]]:
    """A time t with F_q(t) < 0, with the value, computed on two grids so that the sign is above the
    quadrature error; None if no sign change is seen on ``ts``."""
    best = None
    for t in ts:
        v1 = time_slice_covariance(t, q, n, M)
        v2 = time_slice_covariance(t, q, n, M, N=10000)
        if v1 < 0 and v2 < 0 and abs(v1 - v2) < 0.1 * abs(v1):
            if best is None or v1 < best[1]:
                best = (float(t), v1)
    return best


# --------------------------------------------------------------------------- the one-loop bubble (data)
# E/M, Re A, Im A, lower bound, s a(-s) Re A  for the skeleton with n = 4, units M = 1 (table of the paper)
BUBBLE_TABLE = (
    (1.00, 11.7, -31.006, 0.37, 57.3),
    (1.25, 24.7, -31.006, 0.54, 770.0),
    (1.40, 82.1, -31.006, 0.80, 7.60e3),
    (1.50, 475.0, -31.006, 1.14, 8.70e4),
    (1.60, 1.27e4, -31.006, 3.78, 4.45e6),
    (1.70, 4.54e6, -31.006, 156.0, 2.90e9),
    (1.80, 2.42e26, -31.006, 1.94e5, 2.74e29),
    (1.90, 3.81e88, -31.006, 2.00e11, 7.42e91),
)


def breakdown_energy(M_over_MP: float) -> float:
    """The energy E/M at which the one-loop bubble equals the tree amplitude, G s a(-s) Re A = 1, i.e.
    s a(-s) Re A = (M_P/M)^2, by log-linear interpolation of the last column of the table."""
    target = math.log((1.0 / M_over_MP) ** 2)
    rows = [(e, math.log(r)) for e, _, _, _, r in BUBBLE_TABLE]
    if target <= rows[0][1]:
        return rows[0][0]
    for (e0, l0), (e1, l1) in zip(rows, rows[1:]):
        if l0 <= target <= l1:
            return e0 + (e1 - e0) * (target - l0) / (l1 - l0)
    return rows[-1][0]


# --------------------------------------------------------------------------- the composite
CONSTRUCTIONS = (
    {"id": "bg.gas", "gives": "poisson-gas", "needs": (), "note": "scale-invariant Poisson gas of branes, n per e-fold of size"},
    {"id": "bg.response", "gives": "brane-response", "needs": ("cell-model",),
     "note": "psi_* = 1 - exp(-w^2) from (M1)-(M3); obeys (S1)-(S5)"},
    {"id": "bg.formfactor", "gives": "entire-zero-free-form-factor", "needs": ("poisson-gas", "brane-response"),
     "note": "exp[(n/2) Ein(z^2/M^4)] times a random factor with a limit, for almost every realization under (G)"},
    {"id": "bg.powercounting", "gives": "two-loop-convergence", "needs": ("entire-zero-free-form-factor",),
     "note": "omega_bar(n, L) < 0 for L >= 2 iff n >= 4"},
    {"id": "bg.tuning", "gives": "one-loop-finite", "needs": ("two-loop-convergence",),
     "note": "three quartic operators cancel the three poles; det -24/c^3"},
    {"id": "bg.unitarity", "gives": "unitary-S-matrix", "needs": ("entire-zero-free-form-factor",),
     "note": "cutting rules of Pius-Sen and Briscese-Modesto with the quartet mechanism"},
    {"id": "bg.finite", "gives": "perturbative-uv-finiteness", "needs": ("one-loop-finite", "unitary-S-matrix"),
     "note": "no divergence at any loop order for n >= 4; G and Lambda do not run"},
)


def check(n: int) -> List[str]:
    """The conditions of the theorem that the exponent n violates: empty for n >= 4."""
    bad = []
    if n < 4:
        bad.append("power counting: omega_bar(%d, 2) = %d >= 0, a two-loop graph diverges" % (n, omega_bar(n, 2)))
    if response_conditions():
        bad.append("response: psi_* fails " + ", ".join(response_conditions()))
    if merging_lemma_counterexample(L_max=4) is not None:
        bad.append("merging lemma refuted")
    return bad


def summary(n: int = 4, M: float = 1.0) -> Dict[str, object]:
    return {
        "n": n, "M": M, "finite": not check(n),
        "growth_constant": growth_constant(n),
        "zero_point_energy": zero_point_energy(n, M),
        "pole_matrix_det": det3(POLE_MATRIX),
        "breakdown_E_over_M": (breakdown_energy(1e-2), breakdown_energy(1e-40)),
        "reflection_positive": reflection_positivity_witness(n, 1.0, M) is None,
        "doi": DOI, "repo": REPO,
    }
