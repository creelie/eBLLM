"""Six or more line bundles at A_0 = E_0^6 (candidate C8): which configurations of line bundles let threefold
pieces of both parities of shift lie on effective closed chains (C1_chains.md and C8_chains.md).

A configuration is a list of line bundles L^{lam}[s] with distinct exponents; only the order of the exponents
and the shifts matter (line bundle i has the i-th smallest exponent).  Edges between line bundles:

  up    L^l[s] -> L^l'[s+1], l' > l           (Hom, degree 0, the cochain delta is a section of L^{l'-l})
  down  L^l[s] -> L^l'[s-5], l' < l           (Ext^6)
  run   L^l[s] -> ... threefolds ... -> L^l'[s-b], b >= 1, through threefold pieces (Lemma 3 degrees)

A run of excess b is realisable when some sequence of threefold pieces with the degrees of Lemma 3 has total
excess b; RUNS[b, dec] is the set of excesses x accumulated before a threefold of such a run (the threefold
then sits at shift s - x).  Every realisable run is admitted, so the paths and chains found are a superset.

Given a set Z0 of up edges with delta = 0 (run and down edges are taken nonzero):

* Maurer-Cartan.  For line bundles a, c with s_c = s_a + 2 and lam_a < lam_c the component (a, c) lies in
  H^0(L^{lam_c - lam_a}) and is the sum over the paths from a to c.  Z0 is inadmissible when the only path
  avoiding Z0 is a -> b -> c: then delta_ab delta_bc = 0 with both factors nonzero, impossible on the
  integral variety A_0.
* Lemma 7.  If the only path from a to c at all is a -> b -> c, delta_bc = 0 and delta_ab != 0, then
  D(y)_{ac} = delta_ab y_bc and c(v)_{ac} = 0, so y_bc = 0 (likewise with delta_ab = 0, delta_bc != 0).
* A closed chain is effective when at most one of its up edges is in Z0 and that edge does not carry y = 0.

classify() returns 'both' when for some admissible Z0 the effective chains carry threefold pieces of both
parities of shift, 'one' when only one parity is ever reached, 'none' when no effective chain exists.
Only configurations whose shifts form an interval are listed: a chain climbs one shift at a time, so the
line bundles of a chain or of a path occupy an interval of shifts and a configuration with a gap splits
into independent pieces.

    python3 e06_six.py N [out.json]
"""
import itertools, json, sys
from functools import lru_cache
from multiprocessing import Pool

BMAX = 12


def lz_degrees(l, k):
    if k > l:
        return (0,)
    if k < l:
        return (3,)
    return (0, 1, 2, 3)


def zl_degrees(k, l):
    if l > k:
        return (3,)
    if l < k:
        return (6,)
    return (3, 4, 5, 6)


def zz_degrees(k, k2):
    # Z != Z', meeting in dimension d in {0, 1, 2}: degrees 3-d .. 3+d (twist permitting); degree 1 excluded
    # by (H) (it needs d = 2 at one shift)
    m = k2 - k
    out = set()
    for d in (0, 1, 2):
        c = 3 - d
        if m > 0:
            out |= set(range(c, 4))
        elif m < 0:
            out |= set(range(3, 4 + d))
        else:
            out |= set(range(c, 4 + d))
    out.discard(1)
    out.discard(0)
    return tuple(sorted(out))


def run_table():
    """RUNS[(b, dec)] = frozenset of excesses x before a threefold, over all realisations."""
    table = {}
    for dec in (False, True):
        lx = -100 if dec else 100
        ks = sorted({-103, -102, -101, -100, -75, -50, -25, -1, 0, 1, 25, 50, 75, 99, 100, 101, 102, 103})

        @lru_cache(maxsize=None)
        def finish(k, x):          # totals reachable from a threefold of twist k at accumulated excess x
            tot = set()
            for d in zl_degrees(k, lx):
                tot.add(x + d - 1)
            if x < BMAX:
                for k2 in ks:
                    for d in zz_degrees(k, k2):
                        if x + d - 1 <= BMAX:
                            tot |= finish(k2, x + d - 1)
            return frozenset(t for t in tot if t <= BMAX)

        # forward: threefold states (k, x) reachable from the entry L^0
        seen = set()
        stack = []
        for k in ks:
            for d in lz_degrees(0, k):
                st = (k, d - 1)
                if st not in seen:
                    seen.add(st)
                    stack.append(st)
        while stack:
            k, x = stack.pop()
            if x >= BMAX:
                continue
            for k2 in ks:
                for d in zz_degrees(k, k2):
                    st = (k2, x + d - 1)
                    if st[1] <= BMAX and st not in seen:
                        seen.add(st)
                        stack.append(st)
        for b in range(1, BMAX + 1):
            xs = frozenset(x for (k, x) in seen if b in finish(k, x))
            table[(b, dec)] = xs
    return table


RUNS = run_table()


def analyse(conf):
    """conf: tuple of shifts s_0..s_{n-1}, line bundle i has exponent rank i. Returns (survives, info)."""
    n = len(conf)
    s = conf
    up = [(a, b) for a in range(n) for b in range(a + 1, n) if s[b] == s[a] + 1]
    upi = {e: i for i, e in enumerate(up)}
    # adjacency for chains: list of (target, kind, data)
    adj = [[] for _ in range(n)]
    for (a, b) in up:
        adj[a].append((b, "up", upi[(a, b)]))
    for a in range(n):
        for b in range(n):
            if b == a:
                continue
            beta = s[a] - s[b]
            if beta >= 1:
                xs = RUNS.get((beta, b < a), frozenset())
                if xs:
                    par = frozenset((s[a] - x) % 2 for x in xs)
                    adj[a].append((b, "run", par))
            if b < a and s[b] == s[a] - 5:
                adj[a].append((b, "down", None))
    # Maurer-Cartan conflicts
    conflicts = []
    for a in range(n):
        for c in range(a + 1, n):
            if s[c] != s[a] + 2:
                continue
            mids = [b for b in range(a + 1, c) if s[b] == s[a] + 1]
            if len(mids) != 1:
                continue
            b = mids[0]
            # another path from a to c (distinct nodes) using at least one run or down edge?
            other = False
            stack = [(a, frozenset([a]), False)]
            while stack and not other:
                v, vis, special = stack.pop()
                for (w, kind, _) in adj[v]:
                    if w in vis:
                        continue
                    sp = special or kind != "up"
                    if w == c:
                        if sp:
                            other = True
                            break
                        continue
                    stack.append((w, vis | {w}, sp))
            if not other:
                conflicts.append((upi[(a, b)], upi[(b, c)]))
    # closed chains through at least one run: record (set of up edges, parities)
    cycles = []
    for start in range(n):
        stack = [(start, (start,), frozenset(), frozenset(), False)]
        while stack:
            v, path, ups, par, hasrun = stack.pop()
            for (w, kind, data) in adj[v]:
                nups, npar, nrun = ups, par, hasrun
                if kind == "up":
                    nups = ups | {data}
                elif kind == "run":
                    npar = par | data
                    nrun = True
                if w == start:
                    if nrun:
                        cycles.append((nups, npar))
                    continue
                if w < start or w in path:
                    continue
                stack.append((w, path + (w,), nups, npar, nrun))
    if not cycles:
        return False, {"cycles": 0}
    # sets meeting every conflict, by branching on the first conflict not yet met (all minimal ones occur)
    covers = []

    def branch(z0):
        for (x, y) in conflicts:
            if x not in z0 and y not in z0:
                branch(z0 | {x})
                branch(z0 | {y})
                return
        covers.append(z0)

    branch(frozenset())
    best = None
    for z0 in covers:
        reach = set()
        for (ups, par) in cycles:
            if len(ups & z0) <= 1:
                reach |= par
        if len(reach) == 2:
            return True, {"cycles": len(cycles), "conflicts": len(conflicts), "Z0": sorted(z0),
                          "up": up}
        best = reach
    return False, {"cycles": len(cycles), "conflicts": len(conflicts)}


def paths(adj, a, c):
    """All paths a -> c through distinct line bundles, as tuples of (kind, data) steps."""
    out = []
    stack = [(a, frozenset([a]), ())]
    while stack:
        v, vis, steps = stack.pop()
        for (w, kind, data) in adj[v]:
            if w in vis:
                continue
            st = steps + ((kind, data if kind == "up" else None),)
            if w == c:
                out.append(st)
                continue
            stack.append((w, vis | {w}, st))
    return out


def refine(conf, want=2):
    """Exact use of the Maurer-Cartan components between line bundles two shifts apart: a set Z0 of zero
    up edges is admissible unless, for some such pair (a, c), the only path that avoids Z0 is a -> b -> c
    (then delta_ab delta_bc = 0 with both factors nonzero, impossible on the integral A_0).  Returns the
    admissible Z0 (as sets of up edges) whose effective chains carry both parities."""
    n = len(conf)
    s = conf
    up = [(a, b) for a in range(n) for b in range(a + 1, n) if s[b] == s[a] + 1]
    upi = {e: i for i, e in enumerate(up)}
    adj = [[] for _ in range(n)]
    for (a, b) in up:
        adj[a].append((b, "up", upi[(a, b)]))
    for a in range(n):
        for b in range(n):
            if b == a:
                continue
            beta = s[a] - s[b]
            if beta >= 1:
                xs = RUNS.get((beta, b < a), frozenset())
                if xs:
                    adj[a].append((b, "run", frozenset((s[a] - x) % 2 for x in xs)))
            if b < a and s[b] == s[a] - 5:
                adj[a].append((b, "down", None))
    pairs = [(a, c, paths(adj, a, c)) for a in range(n) for c in range(a + 1, n) if s[c] == s[a] + 2]
    cycles = []
    for start in range(n):
        stack = [(start, (start,), frozenset(), frozenset(), False)]
        while stack:
            v, path, ups, par, hasrun = stack.pop()
            for (w, kind, data) in adj[v]:
                nups, npar, nrun = ups, par, hasrun
                if kind == "up":
                    nups = ups | {data}
                elif kind == "run":
                    npar = par | data
                    nrun = True
                if w == start:
                    if nrun:
                        cycles.append((nups, npar, path))
                    continue
                if w < start or w in path:
                    continue
                stack.append((w, path + (w,), nups, npar, nrun))
    good = []
    for r in range(len(up) + 1):
        for z in itertools.combinations(range(len(up)), r):
            z0 = frozenset(z)
            ok = True
            for (a, c, ps) in pairs:
                alive = [p for p in ps if not any(k == "up" and d in z0 for (k, d) in p)]
                if len(alive) == 1 and len(alive[0]) == 2 and all(k == "up" for (k, d) in alive[0]):
                    ok = False
                    break
            if not ok:
                continue
            # Lemma 7: y on a zero up edge b -> c is forced to vanish when a nonzero up edge a -> b (or
            # c -> d) is the only path of its pair: then D(y)_{ac} = delta_ab y_bc while c(v)_{ac} = 0
            dead = set()
            for i in z0:
                (b, c) = up[i]
                for (a2, c2, ps) in pairs:
                    if len(ps) != 1 or len(ps[0]) != 2 or not all(k == "up" for (k, d) in ps[0]):
                        continue
                    e1, e2 = ps[0][0][1], ps[0][1][1]
                    if (e2 == i and e1 not in z0) or (e1 == i and e2 not in z0):
                        dead.add(i)
            reach = set()
            used = []
            for (ups, par, path) in cycles:
                zs = ups & z0
                if len(zs) <= 1 and not (zs & dead):
                    reach |= par
                    used.append((path, sorted(par)))
            if len(reach) >= want:
                good.append((sorted(up[i] for i in z0), used))
                if want == 1:
                    return up, good
    return up, good


def contiguous(n):
    """Configurations whose occupied shifts form an interval [0, k-1] (line bundle i has exponent rank i).
    A chain climbs by up steps of one shift, so the line bundles of a chain, and of a Maurer-Cartan path,
    occupy an interval of shifts; configurations with a gap split into independent pieces."""
    for k in range(1, n + 1):
        for conf in itertools.product(range(k), repeat=n):
            if len(set(conf)) == k:
                yield conf


def classify(conf):
    """'both', 'one' or 'none': the largest set of parities carried by effective chains, over admissible Z0,
    after the exact Maurer-Cartan components and Lemma 7."""
    ok, info = analyse(conf)
    if ok and refine(conf)[1]:
        return "both"
    if info.get("cycles", 0) == 0:
        return "none"
    return "one" if any_reach(conf) else "none"


def any_reach(conf):
    up, good = refine(conf, want=1)
    return bool(good)


def worker2(confs):
    out = {"both": [], "one": [], "none": 0}
    for conf in confs:
        c = classify(conf)
        if c == "none":
            out["none"] += 1
        else:
            out[c].append(conf)
    return out


def main():
    n = int(sys.argv[1])
    confs = list(contiguous(n))
    chunks = [confs[i::64] for i in range(64)]
    res = {"both": [], "one": [], "none": 0}
    with Pool(4) as pool:
        for out in pool.imap_unordered(worker2, chunks):
            res["both"] += out["both"]
            res["one"] += out["one"]
            res["none"] += out["none"]
    print(f"{n} line bundles, {len(confs)} configurations with an interval of shifts: "
          f"{len(res['both'])} carry both parities, {len(res['one'])} carry one, {res['none']} none")
    for conf in res["both"][:10]:
        print("  both:", conf)
    for conf in sorted(res["one"], key=lambda c: (max(c), c))[:10]:
        print("  one:", conf)
    if len(sys.argv) > 2:
        json.dump({"n": n, "both": res["both"], "one": res["one"], "none": res["none"]},
                  open(sys.argv[2], "w"))


if __name__ == "__main__":
    for b in range(1, 8):
        print("run excess", b, "non-decreasing x:", sorted(RUNS[(b, False)]), "decreasing x:", sorted(RUNS[(b, True)]))
    main()
