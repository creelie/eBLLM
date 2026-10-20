"""The chart weight of the Cech homotopy moves the one-homotopy factors between oo and P0 (candidate C8, Lemma 23).

The homotopy of e0_ainf sends a monomial of U01 that is regular on both charts to U1. The family h_t sends it with
weight t to U0 and 1 - t to U1 (with the matching projection); each h_t is a homotopy retract of the same Cech
complex, so each gives a minimal model. Only the weight on the constants (Hom complexes of degree c = 0) matters.
The script checks t = 0, 1/2, 1: the C-type half-trees of e06_halftree_points.py vanish at oo for t = 0 and at P0
for t = 1, and at both points for none of the three; at P1 and P-1 they vanish for all three. (Fitting more values
of t, each value at oo is t(t + r) times a fixed vector and each value at P0 is (t - 1)(t - r') times one, with
r, r' depending on the random inputs, so no t kills both points for those inputs.)

    python3 e06_charts.py 5 0,2,3,4          # runs t = 0, 1/2, 1, and t = 1 on c = 0 only
"""
import json, os, subprocess, sys
from fractions import Fraction
import e0_ainf as E

HERE = os.path.dirname(os.path.abspath(__file__))


def weights():
    tw = {int(k): Fraction(v) for k, v in json.loads(os.environ.get("E06_TW", "{}")).items()}
    td = Fraction(os.environ.get("E06_T", "0"))
    return lambda c, n: tw.get(c, td)


def install():
    tw = weights()

    def h(x, sign=1):
        c = x.b - x.a
        if x.deg != 1:
            return E.Elt(x.a, x.b, x.deg - 1)
        f0, f1 = {}, {}
        for n, v in x.g.items():
            in0, in1 = n >= 0, E.ord_oo(n) >= -c
            if not (in0 or in1):
                continue                      # the cohomology classes
            t = tw(c, n) if (in0 and in1) else (Fraction(0) if in1 else Fraction(1))
            if t:
                f0[n] = f0.get(n, 0) - sign * t * v
            if 1 - t:
                f1[n] = f1.get(n, 0) + sign * (1 - t) * v
        return E.Elt(x.a, x.b, 0, {k: a for k, a in f0.items() if a}, {k: a for k, a in f1.items() if a})

    def proj(x):
        c = x.b - x.a
        if x.deg == 0:
            out = {}
            for n in set(x.f0) | set(x.f1):
                if n >= 0 and E.ord_oo(n) >= -c:
                    t = tw(c, n)
                    v = (1 - t) * x.f0.get(n, 0) + t * x.f1.get(n, 0)
                    if v:
                        out[n] = v
            return out
        if x.deg == 1:
            return {n: v for n, v in x.g.items() if n < 0 and E.ord_oo(n) < -c}
        return {}

    E.h, E.proj = h, proj


if __name__ == "__main__":
    if os.environ.get("E06_CHILD"):
        install()
        import runpy
        sys.argv = [sys.argv[0]] + sys.argv[1:]
        runpy.run_path(os.path.join(HERE, "e06_halftree_points.py"), run_name="__main__")
        sys.exit(0)
    args = sys.argv[1:] or ["5", "0,2,3,4"]
    for label, env in (("t = 0", {"E06_T": "0"}), ("t = 1/2", {"E06_T": "1/2"}), ("t = 1", {"E06_T": "1"}),
                       ("t = 1 on c = 0 only", {"E06_TW": '{"0": 1}'})):
        r = subprocess.run([sys.executable, __file__] + args, env={**os.environ, **env, "E06_CHILD": "1"},
                           cwd=HERE, capture_output=True, text=True, check=True)
        print(label, "|", " ; ".join(l.replace("half-trees: 308 ", "") for l in r.stdout.splitlines()), flush=True)
