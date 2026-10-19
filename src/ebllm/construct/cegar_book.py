"""Exists-forall gadget search with planarity by construction (2-page book).

The candidate graph plus a vertex inf joined to the contacts must have a
2-page book embedding along a fixed spine order (inf first, contacts at given
spine positions). A 2-page book embedding is planar, so every candidate is
planar with the contacts on one face; the spine order costs no search and the
crossing rule is O(n^4) clauses, replacing lazy Kuratowski cuts. The search
is complete only for graphs whose planar embedding is 2-page along an order
with the contacts at those positions (all subhamiltonian ones for some order).
Forall part, cycle and distance cuts as in cegar_forcer.py.
"""
import argparse, itertools, json, os, random, sys, time
import networkx as nx
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

from . import graphcheck as gc
from .cegar_forcer import colouring_of


def run(a):
    n, kind = a.n, a.kind
    nc = 3 if kind == "NAE" else 2
    forbid = sorted(a.forbid)
    dist = {}
    for item in a.dist:
        s_, t_, D = map(int, item.split(","))
        dist[(s_, t_)] = D
    # spine: position 0 is inf; contacts at a.cpos; the rest fill in order
    cpos = [int(x) for x in a.cpos.split(",")] if a.cpos else [1 + (k * n) // nc for k in range(nc)]
    assert len(cpos) == nc and len(set(cpos)) == nc and all(1 <= p <= n for p in cpos)
    pos = {"inf": 0}
    for c, p in enumerate(cpos):
        pos[c] = p
    free = [p for p in range(1, n + 1) if p not in cpos]
    for v, p in zip(range(nc, n), free):
        pos[v] = p
    pool = IDPool()
    X, Q = {}, {}
    V = list(range(n))
    for i, j in itertools.combinations(V, 2):
        X[(i, j)] = X[(j, i)] = pool.id(("x", i, j))
        Q[(i, j)] = Q[(j, i)] = pool.id(("q", i, j))
    for c in range(nc):
        Q[("inf", c)] = Q[(c, "inf")] = pool.id(("q", "inf", c))
    cls = []
    for v in V:
        lits = [X[(v, w)] for w in V if w != v]
        need = 3 if v >= nc else a.min_contact_deg
        cls += CardEnc.atleast(lits, bound=need, vpool=pool, encoding=EncType.seqcounter).clauses
    # 2-page crossing rule over all edges of G + inf
    E = [(u, w) for u, w in itertools.combinations(V, 2)] + [("inf", c) for c in range(nc)]
    sel = lambda e: None if "inf" in e else X[e]
    span = [(min(pos[u], pos[w]), max(pos[u], pos[w]), (u, w)) for u, w in E]
    ncross = 0
    for (i, j, e), (k, l, f) in itertools.combinations(span, 2):
        if (i < k < j < l) or (k < i < l < j):
            base = [-x for x in (sel(e), sel(f)) if x is not None]
            cls.append(base + [Q[e], Q[f]])
            cls.append(base + [-Q[e], -Q[f]])
            ncross += 1
    # distances: paths with fewer edges than the bound are forbidden (eager up to 4 edges)
    for (s_, t_), D in dist.items():
        others = [w for w in V if w not in (s_, t_)]
        for L in range(1, D):
            for mid in itertools.permutations(others, L - 1):
                p = (s_,) + mid + (t_,)
                cls.append([-X[(p[k], p[k + 1])] for k in range(L)])
    # eager short cycles
    eager = [L for L in forbid if L <= a.eager_max]
    lazy = [L for L in forbid if L > a.eager_max]
    for L in eager:
        for S in itertools.combinations(V, L):
            for perm in itertools.permutations(S[1:]):
                if perm[0] < perm[-1]:
                    cyc = (S[0],) + perm
                    cls.append([-X[(cyc[k], cyc[(k + 1) % L])] for k in range(L)])
    # triangles pairwise vertex-disjoint (Bordeaux), and contacts on no triangle if asked
    if a.tri_disjoint or a.tri_free_contacts:
        T = {}
        for t in itertools.combinations(V, 3):
            x1, x2, x3 = X[(t[0], t[1])], X[(t[1], t[2])], X[(t[0], t[2])]
            if any(c in t for c in a.tri_free_contacts):
                cls.append([-x1, -x2, -x3])
                continue
            if a.tri_disjoint:
                T[t] = pool.id(("t",) + t)
                cls.append([-x1, -x2, -x3, T[t]])
        if a.tri_disjoint:
            for v in V:
                lits = [T[t] for t in T if v in t]
                if len(lits) > 1:
                    cls += CardEnc.atmost(lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses
    if a.max_edges:
        cls += CardEnc.atmost([X[(i, j)] for i, j in itertools.combinations(V, 2)], bound=a.max_edges,
                              vpool=pool, encoding=EncType.seqcounter).clauses
    s = Solver(name=a.solver, bootstrap_with=cls)
    fixed = {0: 0, 1: 1} if kind == "EQ" else {v: 0 for v in range(nc)}
    rng = random.Random(a.seed)
    stats = {"iter": 0, "cyc_cuts": 0, "colour_cuts": 0}
    t0 = time.time()
    log = open(a.log, "a") if a.log else None

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True)
        if log:
            log.write(line + "\n"); log.flush()

    say("book n=%d kind=%s forbid=%s dist=%s contact spine positions=%s eager=%s tri_disjoint=%s tri_free_contacts=%s "
        "crossing pairs=%d vars=%d clauses=%d" % (n, kind, forbid, dist, cpos, eager, a.tri_disjoint,
                                                  a.tri_free_contacts, ncross, pool.top, len(cls)))
    nonc = list(range(nc, n))
    while True:
        stats["iter"] += 1
        if not s.solve():
            say("UNSAT: none on %d vertices with this spine. %s" % (n, stats))
            return "unsat"
        m = set(l for l in s.get_model() if l > 0)
        edges = [(i, j) for i, j in itertools.combinations(V, 2) if X[(i, j)] in m]
        G = nx.Graph(); G.add_nodes_from(V); G.add_edges_from(edges)
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
        col = colouring_of(n, edges, fixed)
        if col is None:
            rep = gc.report(G, list(range(nc)), kind, cyc_hi=max(forbid) + 2)
            say("FOUND %d edges %s; independent check: %s" % (len(edges), stats, rep))
            return {"n": n, "edges": edges, "report": {k: str(v) for k, v in rep.items()}}

        def cut(c):
            return [X[(i, j)] for i, j in itertools.combinations(V, 2) if c[i] == c[j]]
        s.add_clause(cut(col)); stats["colour_cuts"] += 1
        for _ in range(a.sym_copies):
            perm = nonc[:]; rng.shuffle(perm)
            pm = dict(zip(nonc, perm))
            s.add_clause(cut({v: col[pm.get(v, v)] for v in V})); stats["colour_cuts"] += 1
        if stats["iter"] % a.every == 0:
            say("progress %s" % stats)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--kind", choices=["NAE", "NEQ", "EQ"], default="NAE")
    ap.add_argument("--forbid", type=int, nargs="+", default=[4, 5])
    ap.add_argument("--dist", nargs="*", default=["0,1,3", "0,2,3", "1,2,3"])
    ap.add_argument("--cpos", default="", help="spine positions of the contacts, e.g. 1,6,11")
    ap.add_argument("--eager-max", type=int, default=4)
    ap.add_argument("--min-contact-deg", type=int, default=2)
    ap.add_argument("--sym-copies", type=int, default=0)
    ap.add_argument("--solver", default="cadical153")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--every", type=int, default=500)
    ap.add_argument("--max-edges", type=int, default=0)
    ap.add_argument("--tri-disjoint", action="store_true", help="no two triangles share a vertex")
    ap.add_argument("--tri-free-contacts", type=int, nargs="*", default=[], help="contacts that lie on no triangle")
    ap.add_argument("--log", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    r = run(a)
    if a.out and isinstance(r, dict):
        json.dump(r, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
