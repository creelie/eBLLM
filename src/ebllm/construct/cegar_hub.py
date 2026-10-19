"""Exists-forall gadget search over abstract graphs with triangle-gadget hubs.

A hub is a node of degree 3 that stands for the triangle gadget T (a triangle
m n o with pendant edges to its three neighbours p, q, r). T allows exactly the
colourings of p, q, r that are not all equal, so a hub is a not-all-equal
constraint, and a hub can be drawn as a triangle in place of a degree-3 vertex,
so planarity is unchanged. A path p - h - q through a hub is a real path of
length 3 or 4, so an abstract cycle of length L through h hubs is a set of real
cycles of every length from L + h to L + 2h.

Node types are SAT variables (hub or ordinary), so hubs can sit anywhere on
the spine. Planarity with the contacts on one face: 2-page book embedding of
the abstract graph plus a vertex inf joined to the contacts, along a fixed
spine. Forall part: every colouring of the ordinary nodes that satisfies all
constraints with the contacts pinned becomes a cut. Cycles, real contact
distances and (Bordeaux) triangle conditions are cut lazily.
"""
import argparse, itertools, json, os, random, sys, time
import networkx as nx
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

from . import graphcheck as gc


def expand(G, hubs):
    """Replace every hub by a triangle gadget; returns the real graph."""
    R = nx.Graph()
    R.add_nodes_from(v for v in G.nodes() if v not in hubs)
    for u, w in G.edges():
        if u not in hubs and w not in hubs:
            R.add_edge(u, w)
    for h in hubs:
        nb = sorted(G[h])
        tri = [("h%s" % h, i) for i in range(len(nb))]
        for i, j in itertools.combinations(range(len(nb)), 2):
            R.add_edge(tri[i], tri[j])
        for t, p in zip(tri, nb):
            R.add_edge(t, p)
    return R


def colouring(G, hubs, fixed):
    ords = [v for v in G.nodes() if v not in hubs]
    pool = IDPool()
    C = lambda v, c: pool.id((v, c))
    s = Solver(name="cadical153")
    for v in ords:
        s.add_clause([C(v, 0), C(v, 1), C(v, 2)])
        for a, b in itertools.combinations(range(3), 2):
            s.add_clause([-C(v, a), -C(v, b)])
    for u, w in G.edges():
        if u not in hubs and w not in hubs:
            for c in range(3):
                s.add_clause([-C(u, c), -C(w, c)])
    for h in hubs:
        nb = list(G[h])
        for c in range(3):
            s.add_clause([-C(p, c) for p in nb])
    for v, c in fixed.items():
        s.add_clause([C(v, c)])
    ok = s.solve()
    m = set(l for l in s.get_model() if l > 0) if ok else None
    s.delete()
    if not ok:
        return None
    return {v: next(c for c in range(3) if C(v, c) in m) for v in ords}


def real_ranges(cycle, hubs):
    L = len(cycle)
    h = sum(1 for v in cycle if v in hubs)
    return L + h, L + 2 * h


def run(a):
    n, kind = a.n, a.kind
    nc = 3 if kind == "NAE" else 2
    forbid = set(a.forbid)
    dist = {}
    for item in a.dist:
        s_, t_, D = map(int, item.split(","))
        dist[(s_, t_)] = D
    cpos = [int(x) for x in a.cpos.split(",")] if a.cpos else [1 + (k * n) // nc for k in range(nc)]
    pos = {"inf": 0}
    for c, p in enumerate(cpos):
        pos[c] = p
    free = [p for p in range(1, n + 1) if p not in cpos]
    for v, p in zip(range(nc, n), free):
        pos[v] = p
    V = list(range(n))
    pool = IDPool()
    X, Q, H, O = {}, {}, {}, {}
    for i, j in itertools.combinations(V, 2):
        X[(i, j)] = X[(j, i)] = pool.id(("x", i, j))
        Q[(i, j)] = Q[(j, i)] = pool.id(("q", i, j))
    for c in range(nc):
        Q[("inf", c)] = Q[(c, "inf")] = pool.id(("q", "inf", c))
    for v in V:
        H[v] = pool.id(("h", v))
    cls = []
    for c in range(nc):
        cls.append([-H[c]])
    for i, j in itertools.combinations(V, 2):
        cls.append([-H[i], -H[j], -X[(i, j)]])                      # hubs not adjacent
        O[(i, j)] = O[(j, i)] = pool.id(("o", i, j))                 # ordinary edge
        cls += [[-O[(i, j)], X[(i, j)]], [-O[(i, j)], -H[i]], [-O[(i, j)], -H[j]],
                [O[(i, j)], -X[(i, j)], H[i], H[j]]]
    for v in V:
        lits = [X[(v, w)] for w in V if w != v]
        need = 3 if v >= nc else a.min_contact_deg
        cls += CardEnc.atleast(lits, bound=need, vpool=pool, encoding=EncType.seqcounter).clauses
        if v >= nc:
            for cl in CardEnc.atmost(lits, bound=3, vpool=pool, encoding=EncType.seqcounter).clauses:
                cls.append(cl + [-H[v]])
    if a.max_hubs >= 0:
        cls += CardEnc.atmost([H[v] for v in V], bound=a.max_hubs, vpool=pool, encoding=EncType.seqcounter).clauses
    if a.min_hubs > 0:
        cls += CardEnc.atleast([H[v] for v in V], bound=a.min_hubs, vpool=pool, encoding=EncType.seqcounter).clauses
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
    # eager: forbidden lengths among ordinary triangles and 4-cycles of ordinary nodes
    for S in itertools.combinations(V, 3):
        if 3 in forbid:
            cls.append([-O[(S[0], S[1])], -O[(S[1], S[2])], -O[(S[0], S[2])]])
    if 4 in forbid:
        for S in itertools.combinations(V, 4):
            for perm in itertools.permutations(S[1:]):
                if perm[0] < perm[-1]:
                    cyc = (S[0],) + perm
                    cls.append([-X[(cyc[k], cyc[(k + 1) % 4])] for k in range(4)])
    # Bordeaux: ordinary triangles pairwise vertex-disjoint; listed contacts on no ordinary triangle
    if a.tri_disjoint or a.tri_free_contacts:
        T = {}
        for t in itertools.combinations(V, 3):
            o1, o2, o3 = O[(t[0], t[1])], O[(t[1], t[2])], O[(t[0], t[2])]
            if any(c in t for c in a.tri_free_contacts):
                cls.append([-o1, -o2, -o3])
                continue
            if a.tri_disjoint:
                T[t] = pool.id(("t",) + t)
                cls.append([-o1, -o2, -o3, T[t]])
        if a.tri_disjoint:
            for v in V:
                lits = [T[t] for t in T if v in t]
                if len(lits) > 1:
                    cls += CardEnc.atmost(lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses
    s = Solver(name=a.solver, bootstrap_with=cls)
    fixed = {0: 0, 1: 1} if kind == "EQ" else {v: 0 for v in range(nc)}
    stats = {"iter": 0, "cyc_cuts": 0, "dist_cuts": 0, "colour_cuts": 0}
    rng = random.Random(a.seed)
    t0 = time.time()
    log = open(a.log, "a") if a.log else None

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True)
        if log:
            log.write(line + "\n"); log.flush()

    say("hub n=%d kind=%s forbid=%s dist=%s cpos=%s tri_disjoint=%s tri_free=%s hubs<=%s crossing pairs=%d vars=%d clauses=%d"
        % (n, kind, sorted(forbid), dist, cpos, a.tri_disjoint, a.tri_free_contacts, a.max_hubs, ncross,
           pool.top, len(cls)))
    lo_f, hi_f = min(forbid), max(forbid)
    while True:
        stats["iter"] += 1
        if not s.solve():
            say("UNSAT: none on %d abstract nodes with this spine. %s" % (n, stats))
            return "unsat"
        m = set(l for l in s.get_model() if l > 0)
        edges = [(i, j) for i, j in itertools.combinations(V, 2) if X[(i, j)] in m]
        hubs = set(v for v in V if H[v] in m)
        G = nx.Graph(); G.add_nodes_from(V); G.add_edges_from(edges)
        tlits = lambda vs: [(-H[v] if v in hubs else H[v]) for v in vs]
        # lazy cycles: abstract cycles whose real lengths meet the forbidden set
        k = 0
        for cyc in gc.short_cycles(G, 3, hi_f):
            lo, hi = real_ranges(cyc, hubs)
            if any(lo <= L <= hi for L in forbid) and not (len(cyc) == 3 and not (set(cyc) & hubs) and 3 not in forbid):
                s.add_clause([-X[(cyc[i], cyc[(i + 1) % len(cyc)])] for i in range(len(cyc))] + tlits(cyc))
                k += 1
                if k >= 3000:
                    break
        if k:
            stats["cyc_cuts"] += k
            continue
        # lazy real distances between contacts (a path through a hub costs 3)
        W = nx.Graph()
        for u, w in edges:
            W.add_edge(u, w, weight=1.5 if (u in hubs or w in hubs) else 1.0)
        bad = False
        for (s_, t_), D in dist.items():
            try:
                L, path = nx.single_source_dijkstra(W, s_, t_)
            except nx.NetworkXNoPath:
                continue
            if L < D - 1e-9:
                s.add_clause([-X[(path[i], path[i + 1])] for i in range(len(path) - 1)] + tlits(path))
                stats["dist_cuts"] += 1; bad = True
        if bad:
            continue
        col = colouring(G, hubs, fixed)
        if col is None:
            R = expand(G, hubs)
            rep = gc.report(R, list(range(nc)), kind, cyc_hi=hi_f + 2)
            tri = nx.triangles(R)
            rep["max_triangles_per_vertex"] = max(tri.values(), default=0)
            rep["contact_triangles"] = [tri.get(c, 0) for c in range(nc)]
            say("FOUND %d abstract edges, %d hubs, real n=%d %s; independent check: %s"
                % (len(edges), len(hubs), R.number_of_nodes(), stats, rep))
            return {"n": n, "edges": edges, "hubs": sorted(hubs),
                    "real_edges": [[str(u), str(w)] for u, w in R.edges()],
                    "report": {kk: str(v) for kk, v in rep.items()}}
        # full colouring of all nodes: the ordinary ones as found, current hubs at random; the cut says
        # "under this colouring some ordinary edge is monochromatic or some hub sees one colour only",
        # which every forcer satisfies whatever its node types, so the cut is sound for all candidates
        full = dict(col)
        for v in V:
            if v not in full:
                full[v] = rng.randrange(3)
        cut = [O[(i, j)] for i, j in itertools.combinations(V, 2) if full[i] == full[j]]
        for h in range(nc, n):
            for c in range(3):
                mh = pool.id(("m", stats["iter"], h, c))
                s.add_clause([-mh, H[h]])
                for w in V:
                    if w != h and full[w] != c:
                        s.add_clause([-mh, -X[(h, w)]])
                cut.append(mh)
        s.add_clause(cut); stats["colour_cuts"] += 1
        if stats["iter"] % a.every == 0:
            say("progress %s" % stats)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--kind", choices=["NAE", "NEQ", "EQ"], default="NAE")
    ap.add_argument("--forbid", type=int, nargs="+", default=[4, 5, 6])
    ap.add_argument("--dist", nargs="*", default=["0,1,3", "0,2,3", "1,2,5"])
    ap.add_argument("--cpos", default="")
    ap.add_argument("--min-contact-deg", type=int, default=1)
    ap.add_argument("--max-hubs", type=int, default=-1)
    ap.add_argument("--min-hubs", type=int, default=0)
    ap.add_argument("--tri-disjoint", action="store_true")
    ap.add_argument("--tri-free-contacts", type=int, nargs="*", default=[])
    ap.add_argument("--solver", default="cadical153")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--every", type=int, default=500)
    ap.add_argument("--log", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    r = run(a)
    if a.out and isinstance(r, dict):
        json.dump(r, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
