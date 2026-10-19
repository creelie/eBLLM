"""Construction mode for planar colouring gadgets (exists-forall search).

Search for a graph on n vertices (contacts 0..nc-1) such that
  * the graph plus a vertex joined to all contacts is planar
    (planar with the contacts on one face),
  * it has no cycle whose length is in FORBID,
  * contact distances are at least the given bounds,
  * every non-contact vertex has degree >= 3 (minimal gadgets),
  * it forces: NAE (contacts never all one colour) or NEQ (two contacts
    never equal) in every proper 3-colouring.
Exists-part: SAT over edge variables. Forall-part: counterexample-guided;
each 3-colouring that defeats a candidate becomes the clause "some chosen
edge is monochromatic under it", which every forcer satisfies.
Short cycles and planarity are added lazily (Kuratowski subgraphs).
"""
import argparse, itertools, json, os, random, sys, time
import networkx as nx
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

from . import graphcheck as gc


def build(n, nc, forbid, dist, kind, eager_cycles, min_contact_deg, seed):
    pool = IDPool()
    X = {}
    for i, j in itertools.combinations(range(n), 2):
        X[(i, j)] = X[(j, i)] = pool.id(("x", i, j))
    cls = []
    # degrees
    for v in range(n):
        lits = [X[(v, w)] for w in range(n) if w != v]
        need = 3 if v >= nc else min_contact_deg
        enc = CardEnc.atleast(lits, bound=need, vpool=pool, encoding=EncType.seqcounter)
        cls += enc.clauses
    # BFS symmetry breaking from the contact set: parent(v) = least neighbour,
    # every non-contact has a smaller neighbour, parents nondecreasing.
    P = {}
    for v in range(nc, n):
        for u in range(v):
            p = pool.id(("p", v, u))
            P[(v, u)] = p
            # p <-> x(u,v) and no smaller neighbour
            cls.append([-p, X[(u, v)]])
            for w in range(u):
                cls.append([-p, -X[(w, v)]])
            cls.append([p, -X[(u, v)]] + [X[(w, v)] for w in range(u)])
        cls.append([P[(v, u)] for u in range(v)])
    for v in range(nc + 1, n):
        for u in range(v):
            for u2 in range(u + 1, v - 1):
                cls.append([-P[(v, u)], -P[(v - 1, u2)]])
    # contact distances: forbid paths shorter than the bound
    for (s, t), D in dist.items():
        others = [w for w in range(n) if w not in (s, t)]
        if D > 1:
            cls.append([-X[(s, t)]])
        if D > 2:
            for w in others:
                cls.append([-X[(s, w)], -X[(w, t)]])
        if D > 3:
            for w1, w2 in itertools.permutations(others, 2):
                cls.append([-X[(s, w1)], -X[(w1, w2)], -X[(w2, t)]])
        if D > 4:
            raise ValueError("distance bounds above 4 not encoded")
    # eager short cycles
    ncyc = 0
    for L in eager_cycles:
        for S in itertools.combinations(range(n), L):
            first, rest = S[0], S[1:]
            for perm in itertools.permutations(rest):
                if perm[0] < perm[-1]:
                    cyc = (first,) + perm
                    cls.append([-X[(cyc[k], cyc[(k + 1) % L])] for k in range(L)])
                    ncyc += 1
    return pool, X, cls, ncyc


def schnyder(n, nc, X, pool):
    """Planarity of G + inf (inf joined to the contacts) as dimension <= 3 of
    the vertex-edge incidence order (Schnyder): three linear orders such that
    for every edge uv and vertex w not on it, some order puts w above u and v."""
    V = list(range(n)) + ["inf"]
    cls = []
    O = {}
    for i in range(3):
        for u, w in itertools.combinations(V, 2):
            o = pool.id(("o", i, u, w))
            O[(i, u, w)] = o
            O[(i, w, u)] = -o
        for u, v, w in itertools.permutations(V, 3):
            cls.append([-O[(i, u, v)], -O[(i, v, w)], O[(i, u, w)]])
    edges = [((u, v), X[(u, v)]) for u, v in itertools.combinations(range(n), 2)]
    edges += [((c, "inf"), None) for c in range(nc)]
    for (u, v), x in edges:
        for w in V:
            if w in (u, v):
                continue
            ys = []
            for i in range(3):
                y = pool.id(("y", i, u, v, w))
                cls.append([-y, O[(i, u, w)]])
                cls.append([-y, O[(i, v, w)]])
                ys.append(y)
            cls.append(([-x] if x else []) + ys)
    return cls


def colouring_of(n, edges, fixed):
    """3-colouring of the candidate (all n vertices) with contacts pinned, via SAT."""
    pool = IDPool()
    C = lambda v, c: pool.id((v, c))
    s = Solver(name="cadical153")
    for v in range(n):
        s.add_clause([C(v, 0), C(v, 1), C(v, 2)])
        for a, b in itertools.combinations(range(3), 2):
            s.add_clause([-C(v, a), -C(v, b)])
    for u, w in edges:
        for c in range(3):
            s.add_clause([-C(u, c), -C(w, c)])
    for v, c in fixed.items():
        s.add_clause([C(v, c)])
    if not s.solve():
        s.delete()
        return None
    m = set(l for l in s.get_model() if l > 0)
    s.delete()
    return {v: next(c for c in range(3) if C(v, c) in m) for v in range(n)}


def run(a):
    n, kind = a.n, a.kind
    nc = 3 if kind == "NAE" else 2
    forbid = sorted(a.forbid)
    dist = {}
    for item in a.dist:
        s, t, D = map(int, item.split(","))
        dist[(s, t)] = D
    eager = [L for L in forbid if L <= a.eager_max]
    lazy = [L for L in forbid if L > a.eager_max]
    pool, X, cls, ncyc = build(n, nc, forbid, dist, kind, eager, a.min_contact_deg, a.seed)
    if a.max_edges:
        lits = [X[(i, j)] for i, j in itertools.combinations(range(n), 2)]
        cls += CardEnc.atmost(lits, bound=a.max_edges, vpool=pool, encoding=EncType.seqcounter).clauses
    if a.planar == "schnyder":
        cls += schnyder(n, nc, X, pool)
    s = Solver(name=a.solver, bootstrap_with=cls)
    fixed = {v: 0 for v in range(nc)}
    rng = random.Random(a.seed)
    stats = {"iter": 0, "cyc_cuts": 0, "planar_cuts": 0, "colour_cuts": 0}
    t0 = time.time()
    log = open(a.log, "a") if a.log else None

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True)
        if log:
            log.write(line + "\n"); log.flush()

    say("n=%d kind=%s forbid=%s dist=%s eager=%s (%d cycle clauses) vars=%d clauses=%d"
        % (n, kind, forbid, dist, eager, ncyc, pool.top, len(cls)))
    nonc = list(range(nc, n))
    while True:
        stats["iter"] += 1
        if a.max_iter and stats["iter"] > a.max_iter:
            say("STOP max_iter %s" % stats); return None
        if not s.solve():
            say("UNSAT: no gadget on %d vertices under these constraints. %s" % (n, stats))
            return "unsat"
        m = set(l for l in s.get_model() if l > 0)
        edges = [(i, j) for i, j in itertools.combinations(range(n), 2) if X[(i, j)] in m]
        G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(edges)
        # lazy cycles
        if lazy:
            k = 0
            for cyc in gc.short_cycles(G, min(lazy), max(lazy)):
                if len(cyc) in lazy:
                    s.add_clause([-X[(cyc[i], cyc[(i + 1) % len(cyc)])] for i in range(len(cyc))])
                    k += 1
                    if k >= 5000:
                        break
            if k:
                stats["cyc_cuts"] += k
                continue
        # planarity with contacts on a face
        H = G.copy(); H.add_node("inf")
        for c in range(nc):
            H.add_edge("inf", c)
        ok, cert = nx.check_planarity(H, counterexample=True)
        if not ok:
            added = 0
            Hc = H.copy()
            for _ in range(a.kura_per_iter):
                kedges = [(u, w) for u, w in cert.edges() if "inf" not in (u, w)]
                if not kedges:
                    break
                s.add_clause([-X[(u, w)] for u, w in kedges])
                added += 1
                # remove one edge of this obstruction and look for another
                Hc.remove_edge(*rng.choice(kedges))
                ok2, cert = nx.check_planarity(Hc, counterexample=True)
                if ok2:
                    break
            stats["planar_cuts"] += added
            continue
        col = colouring_of(n, edges, fixed)
        if col is None:
            say("FOUND candidate forcer: %d edges %s" % (len(edges), stats))
            rep = gc.report(G, list(range(nc)), kind, cyc_hi=max(forbid) + 2)
            say("independent check: %s" % rep)
            return {"n": n, "edges": edges, "report": {k: str(v) for k, v in rep.items()}}
        # forall cut, plus copies under random relabelling of non-contacts
        def cut(c):
            return [X[(i, j)] for i, j in itertools.combinations(range(n), 2) if c[i] == c[j]]
        s.add_clause(cut(col)); stats["colour_cuts"] += 1
        for _ in range(a.sym_copies):
            perm = nonc[:]; rng.shuffle(perm)
            pm = dict(zip(nonc, perm))
            c2 = {v: col[pm.get(v, v)] for v in range(n)}
            s.add_clause(cut(c2)); stats["colour_cuts"] += 1
        if stats["iter"] % a.every == 0:
            say("progress %s" % stats)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--kind", choices=["NAE", "NEQ"], default="NAE")
    ap.add_argument("--forbid", type=int, nargs="+", default=[4, 5])
    ap.add_argument("--dist", nargs="*", default=["0,1,3", "0,2,3", "1,2,3"])
    ap.add_argument("--eager-max", type=int, default=5)
    ap.add_argument("--min-contact-deg", type=int, default=2)
    ap.add_argument("--kura-per-iter", type=int, default=8)
    ap.add_argument("--sym-copies", type=int, default=4)
    ap.add_argument("--solver", default="cadical153")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-iter", type=int, default=0)
    ap.add_argument("--every", type=int, default=2000)
    ap.add_argument("--log", default="")
    ap.add_argument("--max-edges", type=int, default=0)
    ap.add_argument("--planar", choices=["lazy", "schnyder"], default="lazy")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    r = run(a)
    if a.out and isinstance(r, dict):
        json.dump(r, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
