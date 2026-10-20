"""Frobenius on the transcendental lattice of an elliptic K3 surface: Picard number and the
real-versus-complex multiplication test (the Hodge F3' attack on the Fricke route).

Target. Fibrewise cyclic N-isogenies composed with the Fricke involution give dominant self-maps f of
degree N with f^* f_* = N on T (fermat-hodge-, Thm. fricke, N = 5, 7). For an elliptic K3 over P^1 the
j-map factors through X_0(N), so X_0(N) must have genus 0; the levels with a new square class are
N = 10 and N = 13. At N = 10 the four cusps (widths 1, 2, 5, 10) and the forced odd number of starred
fibres give rho >= 20, so T has rank <= 2 (CM). At N = 13 the universal curve is itself a K3 surface R13:

    y^2 = x^3 - 27 c4 x - 54 c6,  c4 = (t^2+5t+13)(t^2+6t+13)(t^4+7t^3+20t^2+19t+1),
    c6 = (t^2+5t+13)(t^2+6t+13)^2(t^6+10t^5+46t^4+108t^3+122t^2+38t-1),
    fibres I1 (t=0), II, II (t^2+5t+13), III, III (t^2+6t+13), I13 (t=oo); Euler number 24.

Result (computed in anaxia-research/attacks/hodge with F_{p^k} counts, k <= 3): at p = 7 the
characteristic polynomial of Frobenius on T,

    P_T(x) = x^6 + 4x^5 + 84x^4 + 196x^3 + 4116x^2 + 9604x + 117649,

has no root of the form 7 * (root of unity), so rho(R13) = 16 (Tate's conjecture for K3 surfaces over
finite fields, char >= 5, with specialisation). If E = End_Hdg(T) were totally real it would contain
f^* with (f^*)^2 = 13, so E = Q(sqrt13) acting Galois-equivariantly (f is defined over Q), and P_T would
be a norm from Q(sqrt13) of a cubic. It is not, so E is a CM field and the degree-13 self-map gives no
real multiplication. Half of the traces for p < 110 vanish, as CM predicts. Label: proved, given the
point counts (rerun by ``trace_T``); it closes the Fricke route to sqrt13, and with N = 10 the Fricke
route to every new quadratic field.
"""
from fractions import Fraction
from itertools import combinations
import cmath
import math

C4 = [(1, 5, 13), (1, 6, 13), (1, 7, 20, 19, 1)]
C6 = [(1, 5, 13), (1, 6, 13), (1, 6, 13), (1, 10, 46, 108, 122, 38, -1)]

# traces of Frob_{p^k} on T(R13), k = 1, 2, 3, from the F_{p^k} counts
TRACES = {5: (0, -40, 0), 7: (-4, -152, 356)}
# traces of Frob_p on T(R13) for 5 <= p < 110, p != 13
TRACES_P = {5: 0, 7: -4, 11: 16, 17: 0, 19: 28, 23: 0, 29: -42, 31: 20, 37: 0, 41: 0, 43: 0, 47: -36,
            53: -6, 59: -40, 61: -6, 67: 68, 71: -20, 73: 0, 79: 0, 83: -60, 89: 0, 97: 0, 101: -90,
            103: 0, 107: 0, 109: 0}


def _pv(cs, t, p):
    r = 0
    for c in cs:
        r = (r * t + c) % p
    return r


def trace_T(p: int) -> int:
    """Trace of Frob_p on T(R13) by counting points of the smooth model over F_p (p >= 5, p != 13)."""
    sq = [0] * p
    for x in range(1, p):
        sq[x * x % p] = 1
    chi = [0] + [1 if sq[a] else -1 for a in range(1, p)]

    def weier(A, B):
        return p + 1 + sum(chi[(x * x * x + A * x + B) % p] for x in range(p))

    total = 0
    for t in range(p):
        c4 = c6 = 1
        for f in C4:
            c4 = c4 * _pv(f, t, p) % p
        for f in C6:
            c6 = c6 * _pv(f, t, p) % p
        total += weier(-27 * c4 % p, -54 * c6 % p)
    n3 = sum(1 for t in range(p) if _pv((1, 6, 13), t, p) == 0)     # III fibres: 2p+1 points, Weierstrass gives p+1
    w = weier(-27 % p, -54 % p)                                     # fibre at infinity (leading coefficients 1, 1)
    split = w == p
    total += p * n3 + w + (12 * p if split else 0)                  # I13 split: 13p points, Weierstrass gives p
    tr_ns = 2 * p + (12 * p if split else 0) + p * n3
    return total - 1 - p * p - tr_ns


def charpoly(p: int, traces):
    """Coefficients (x^6 first) of P_T with the functional equation x^6 P(p^2/x) = p^6 P(x)."""
    t1, t2, t3 = traces
    e1 = Fraction(t1)
    e2 = (e1 * t1 - t2) / 2
    e3 = (e2 * t1 - e1 * t2 + t3) / 3
    return [1, -e1, e2, -e3, p ** 2 * e2, -p ** 4 * e1, p ** 6]


def _roots(coeffs):
    """Durand-Kerner roots of a monic real polynomial."""
    n = len(coeffs) - 1
    a = [complex(float(c)) for c in coeffs]
    z = [cmath.exp(2j * math.pi * (k + 0.3) / n) * 1.1 for k in range(n)]
    for _ in range(2000):
        nz = []
        for i in range(n):
            num = sum(a[k] * z[i] ** (n - k) for k in range(n + 1))
            den = 1
            for j in range(n):
                if j != i:
                    den *= z[i] - z[j]
            nz.append(z[i] - num / den)
        z = nz
    return z


def unit_roots(p: int, coeffs):
    """Normalised roots alpha/p of P_T; Weil says they lie on the unit circle."""
    return [r / p for r in _roots(coeffs)]


def cyclotomic_roots(p: int, coeffs, max_order: int = 60, tol: float = 1e-7):
    """Normalised roots that are roots of unity of order <= max_order: each adds one to rho over F_p-bar."""
    return [r for r in unit_roots(p, coeffs) if any(abs(r ** m - 1) < tol for m in range(1, max_order + 1))]


def splits_over_real_quadratic(p: int, coeffs, D: int = 13, tol: float = 1e-6) -> bool:
    """Is P_T = g * g' with g a monic cubic over Q(sqrt D) and g' its conjugate? (needed for RM by Q(sqrt D))"""
    rs = _roots(coeffs)
    for S in combinations(range(6), 3):
        g = [1]
        for i in S:
            g = [x - rs[i] * y for x, y in zip(g + [0], [0] + g)]
        h = [1]
        for i in range(6):
            if i not in S:
                h = [x - rs[i] * y for x, y in zip(h + [0], [0] + h)]
        ok = True
        for a, b in zip(g, h):
            s, d = a + b, (a - b) / math.sqrt(D)
            if any(abs(v.imag) > tol for v in (s, d)):
                ok = False
                break
            # coefficients of g, g' in the ring of integers of Q(sqrt D), D = 1 mod 4: s and d are integers
            if abs(s.real - round(s.real)) > tol or abs(d.real - round(d.real)) > tol:
                ok = False
                break
        if ok:
            return True
    return False


def verdict(p: int = 7) -> dict:
    cf = charpoly(p, TRACES[p])
    return {"p": p, "charpoly": [str(c) for c in cf],
            "on_unit_circle": all(abs(abs(r) - 1) < 1e-6 for r in unit_roots(p, cf)),
            "rho_bound": 16 + len(cyclotomic_roots(p, cf)),
            "rm_by_sqrt13_possible": splits_over_real_quadratic(p, cf),
            "zero_trace_fraction": sum(1 for a in TRACES_P.values() if a == 0) / len(TRACES_P)}
