"""Exact f(n) for Erdos Problem 1183 by SAT: f(n) <= s - 1 iff some 2-colouring of 2^[n] has no
monochromatic sublattice with s members.  Sublattices with at least s members are listed by
`maxsub n dump s`; it suffices to forbid those with exactly the minimal sizes, but we forbid all of
them, which is the same condition.  Usage: python3 -I solve_f.py n [s]"""
import subprocess
import sys

from pysat.solvers import Cadical153


def colouring_avoids(n, s, exe="./maxsub"):
    out = subprocess.run([exe, str(n), "dump", str(s)], capture_output=True, text=True, check=True).stdout
    masks = [int(x, 16) for x in out.split()]
    P = 1 << n
    with Cadical153() as sat:
        for m in masks:
            pts = [x + 1 for x in range(P) if (m >> x) & 1]
            sat.add_clause([-v for v in pts])     # not all red
            sat.add_clause(pts)                   # not all blue
        sat.add_clause([1])                       # symmetry: the empty set is red
        if sat.solve():
            model = sat.get_model()
            red = sum(1 << (v - 1) for v in model if 0 < v <= P)
            return True, red, len(masks)
        return False, None, len(masks)


def f_exact(n):
    s = (n + 2) // 2                              # chain lower bound ceil((n+1)/2)
    while True:
        ok, red, k = colouring_avoids(n, s + 1)
        print(f"n={n}: colouring with no monochromatic sublattice of size {s + 1}: {ok} "
              f"({k} sublattices forbidden)", flush=True)
        if ok:
            return s, red
        s += 1


if __name__ == "__main__":
    n = int(sys.argv[1])
    f, red = f_exact(n)
    print(f"f({n}) = {f}; witness red mask {red:#x}")
