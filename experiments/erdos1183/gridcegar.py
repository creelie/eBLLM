"""Exact search over grid colourings of 2^[n] with lazily added clauses (the method of cegar_f.py).

Variables: one per grid point v of prod [0, d_i], true for colour 1.  Each model is checked by
`gridwit`, which returns a monochromatic sublattice with at least s members as its set of grid
points; the clause that these points are not all of one colour is added, for both colours, since
the sublattice exists as soon as its points agree.  A model with none is a grid colouring with
no monochromatic sublattice of s members; unsatisfiability proves that no grid colouring with
these block sizes has one.  "undecided" from the checker stops the run.
Usage: python3 -I gridcegar.py s d_1 .. d_k [budget]"""
import subprocess
import sys
import time

from pysat.solvers import Cadical153


def main():
    s = int(sys.argv[1]); dims = [int(x) for x in sys.argv[2:]]
    budget = None
    if len(dims) > 1 and dims[-1] > 1000:
        budget = dims.pop()
    npts = 1
    for d in dims:
        npts *= d + 1
    cmd = ["./gridwit", str(len(dims))] + [str(d) for d in dims] + [str(s)] + ([str(budget)] if budget else [])
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    sat = Cadical153()
    sat.add_clause([-1])                    # symmetry under exchange of colours: the empty set has colour 0
    t0, it = time.time(), 0
    while True:
        if not sat.solve():
            print(f"UNSAT dims={dims} s={s}: no grid colouring avoids {s} after {it} clauses pairs, {time.time()-t0:.0f}s", flush=True)
            return
        m = sat.get_model()
        pos = {v for v in m if v > 0}
        bits = "".join("1" if v + 1 in pos else "0" for v in range(npts))
        proc.stdin.write(bits + "\n")
        out = proc.stdout.readline().split()
        if out[0] == "none":
            print(f"FOUND dims={dims} s={s} after {it}: {bits}", flush=True)
            return
        if out[0] == "undecided":
            print(f"UNDECIDED at iteration {it}: {bits}", flush=True)
            return
        c = int(out[0]); pts = [int(x) for x in out[1:]]
        assert all(bits[p] == str(c) for p in pts), "witness disagrees with the model"
        sat.add_clause([p + 1 for p in pts])
        sat.add_clause([-(p + 1) for p in pts])
        it += 1
        if it % 100 == 0:
            print(f"  iteration {it}, {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
