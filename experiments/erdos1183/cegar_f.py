"""Exact f(n) for Erdos Problem 1183 by SAT with lazily added constraints, for n <= 8.

To decide whether some 2-colouring of 2^[n] has no monochromatic sublattice with s members, solve
an incremental SAT problem whose clauses forbid the sublattices found so far; check each model with
`findmono`, which returns a monochromatic sublattice with at least s members if there is one, and
add the two clauses forbidding it.  A model with none is a witness; unsatisfiability is a proof,
since every clause is a true constraint.  Usage: python3 -I cegar_f.py n s [max_iterations]"""
import subprocess
import sys
import time

from pysat.solvers import Cadical153


def decide(n, s, exe="./findmono", max_iter=10 ** 7, seed_chains=True, log=None):
    P = 1 << n
    proc = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    sat = Cadical153()
    sat.add_clause([1])                      # symmetry: the empty set is red
    added, t0 = 0, time.time()
    try:
        for it in range(max_iter):
            if not sat.solve():
                return False, None, added, it
            model = sat.get_model()
            red = sum(1 << (v - 1) for v in model if 0 < v <= P and v > 0)
            proc.stdin.write(f"{n} {s} {red:x}\n")
            line = proc.stdout.readline().split()
            if line[0] == "none":
                return True, red, added, it
            pts = [int(x) + 1 for x in line[1:]]
            sat.add_clause([-v for v in pts])
            sat.add_clause(pts)
            added += 1
            if log and it % 2000 == 0:
                print(f"  n={n} s={s} iteration {it}, {added} sublattices, {time.time() - t0:.0f}s", file=log, flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
        sat.delete()
    return None, None, added, max_iter


if __name__ == "__main__":
    n, s = int(sys.argv[1]), int(sys.argv[2])
    mi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 7
    exe = sys.argv[4] if len(sys.argv) > 4 else "./findmono"
    ok, red, k, it = decide(n, s, exe=exe, max_iter=mi, log=sys.stdout)
    verdict = {True: "a colouring avoids", False: "no colouring avoids", None: "undecided"}[ok]
    print(f"n={n} s={s}: {verdict} monochromatic sublattices of size {s} "
          f"({k} sublattices added, {it} iterations)" + (f"; witness red {red:#x}" if red else ""))
