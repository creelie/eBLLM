"""Typed crossing network for planar 3-colouring gadgets (construction mode).

A gadget is a planar graph with up to three terminals on one face, typed by
  rel   - the colour patterns of the terminals that extend to a proper
          3-colouring (patterns up to renaming colours),
  dist  - pairwise terminal distances,
  size  - number of vertices.
Crossing: a random planar frame (outer terminals, hidden vertices, plain edges)
whose slots are filled with library gadgets. Every child is built as a real
graph and checked exactly (forbidden cycle lengths, planarity with terminals on
a face, relation by SAT). Children that are new or better on (rel, dist, size)
join the library. Target points: a 0-terminal non-3-colourable child, or a
gadget that a fixed planar assembly turns into one (EQ with distance >= 2, NEQ
with distance >= 3); each is verified independently before it is reported.
"""
import argparse, itertools, json, math, os, random, sys, time
import networkx as nx
from pysat.solvers import Solver

from . import graphcheck as gc


def canon(col):
    m, out = {}, []
    for c in col:
        if c not in m:
            m[c] = len(m)
        out.append(m[c])
    return tuple(out)


PATTERNS = {r: sorted(set(canon(p) for p in itertools.product(range(3), repeat=r))) for r in range(4)}


class Gadget:
    __slots__ = ("G", "terms", "rel", "dist", "size", "origin", "key")

    def __init__(self, G, terms, rel, dist, origin):
        self.G, self.terms, self.rel, self.dist, self.origin = G, tuple(terms), rel, dist, origin
        self.size = G.number_of_nodes()
        self.key = type_key(len(terms), rel, dist)


def perm_type(r, rel, dist, pi):
    rel2 = frozenset(canon(tuple(p[pi[i]] for i in range(r))) for p in rel)
    pairs = list(itertools.combinations(range(r), 2))
    d = {pq: dist[k] for k, pq in enumerate(pairs)}
    dist2 = tuple(d[tuple(sorted((pi[i], pi[j])))] for i, j in pairs)
    return rel2, dist2


def type_key(r, rel, dist):
    best = None
    for pi in itertools.permutations(range(r)):
        rel2, dist2 = perm_type(r, rel, dist, pi)
        k = (r, tuple(sorted(rel2)), dist2)
        if best is None or k < best:
            best = k
    return best


def colour_cnf(G):
    idx = {v: i for i, v in enumerate(G.nodes())}
    var = lambda v, c: 3 * idx[v] + c + 1
    cls = []
    for v in G.nodes():
        cls.append([var(v, 0), var(v, 1), var(v, 2)])
    for u, w in G.edges():
        for c in range(3):
            cls.append([-var(u, c), -var(w, c)])
    return cls, var


def relation(G, terms):
    cls, var = colour_cnf(G)
    s = Solver(name="cadical153", bootstrap_with=cls)
    rel = set()
    for p in PATTERNS[len(terms)]:
        if s.solve(assumptions=[var(t, c) for t, c in zip(terms, p)]):
            rel.add(p)
    s.delete()
    return frozenset(rel)


def distances(G, terms):
    out = []
    for a, b in itertools.combinations(terms, 2):
        try:
            out.append(nx.shortest_path_length(G, a, b))
        except nx.NetworkXNoPath:
            out.append(99)
    return tuple(out)


DISJOINT_TRIANGLES = False   # Bordeaux: no two triangles share a vertex


def has_forbidden_cycle(G, forbid):
    for c in gc.short_cycles(G, min(forbid), max(forbid)):
        if len(c) in forbid:
            return True
    if DISJOINT_TRIANGLES:
        seen = set()
        for u, w in G.edges():
            for x in set(G[u]) & set(G[w]):
                t = frozenset((u, w, x))
                if t in seen:
                    continue
                seen.add(t)
        used = set()
        for t in seen:
            if used & t:
                return True
            used |= t
    return False


def make(G, terms, origin):
    G = nx.convert_node_labels_to_integers(G, label_attribute="old")
    old = {d["old"]: v for v, d in G.nodes(data=True)}
    for v in G.nodes():
        del G.nodes[v]["old"]
    t = [old[x] for x in terms]
    return Gadget(G, t, relation(G, t), distances(G, t), origin)


def seeds(forbid):
    lib = []
    def add(edges, terms, name):
        G = nx.Graph(); G.add_edges_from(edges)
        lib.append(make(G, terms, name))
    add([(0, 1)], [0, 1], "edge")
    for L in range(2, 8):
        add([(i, i + 1) for i in range(L)], [0, L], "path%d" % L)
    add([(0, 1), (1, 2), (0, 2)], [0, 1, 2], "triangle")
    add([(9, 0), (9, 1), (9, 2)], [0, 1, 2], "claw")
    add([(3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)], [0, 1, 2], "T: triangle+pendants")
    add([(0, 3), (3, 4), (4, 1), (2, 3), (2, 4)], [0, 1, 2], "Y: a=b forces k=a")
    return [g for g in lib if not has_forbidden_cycle(g.G, forbid)]


def strength(g):
    return len(PATTERNS[len(g.terms)]) - len(g.rel)


class Library:
    def __init__(self, items):
        self.by_key = {}
        for g in items:
            self.offer(g)

    def offer(self, g):
        """Keep g if no entry with a stronger-or-equal relation, longer-or-equal
        distances and smaller-or-equal size exists (up to terminal order)."""
        r = len(g.terms)
        for h in self.by_key.values():
            if len(h.terms) != r or h.size > g.size:
                continue
            for pi in itertools.permutations(range(r)):
                rel2, dist2 = perm_type(r, h.rel, h.dist, pi)
                if rel2 <= g.rel and all(x >= y for x, y in zip(dist2, g.dist)):
                    return False
        # drop entries g dominates
        for k in list(self.by_key):
            h = self.by_key[k]
            if len(h.terms) != r or h.size < g.size:
                continue
            for pi in itertools.permutations(range(r)):
                rel2, dist2 = perm_type(r, g.rel, g.dist, pi)
                if rel2 <= h.rel and all(x >= y for x, y in zip(dist2, h.dist)):
                    del self.by_key[k]
                    break
        self.by_key[g.key] = g
        return True

    def items(self):
        return list(self.by_key.values())


def frame_planar(nv, outer, slots, edges):
    H = nx.Graph()
    H.add_nodes_from(range(nv))
    for s, (g, verts) in enumerate(slots):
        for v in verts:
            H.add_edge(("s", s), v)
    H.add_edges_from(edges)
    for v in outer:
        H.add_edge("inf", v)
    return nx.check_planarity(H)[0]


def build_child(nv, outer, slots, edges):
    G = nx.Graph()
    G.add_nodes_from(("f", v) for v in range(nv))
    for s, (g, verts) in enumerate(slots):
        m = {}
        for v in g.G.nodes():
            m[v] = ("s", s, v)
        for t, fv in zip(g.terms, verts):
            m[t] = ("f", fv)
        G.add_edges_from((m[u], m[w]) for u, w in g.G.edges())
    G.add_edges_from((("f", u), ("f", w)) for u, w in edges)
    # drop isolated hidden frame vertices
    G.remove_nodes_from([v for v in list(G.nodes()) if G.degree(v) == 0 and v[1] not in outer])
    return G


def k4_assembly(g):
    """EQ (d>=2) or NEQ (d>=3) gadget -> planar graph; each K4 edge becomes
    an edge followed by an EQ gadget, or a NEQ gadget."""
    G = nx.Graph()
    for i, j in itertools.combinations(range(4), 2):
        m = {v: ("e", i, j, v) for v in g.G.nodes()}
        u, w = g.terms
        if g.rel == frozenset({(0, 0)}):
            m[u] = ("x", i, j); m[w] = ("k", j)
            G.add_edge(("k", i), ("x", i, j))
        else:
            m[u] = ("k", i); m[w] = ("k", j)
        G.add_edges_from((m[a], m[b]) for a, b in g.G.edges())
    return G


def verify_counterexample(G, forbid):
    planar = nx.check_planarity(G)[0]
    cyc = sorted(gc.cycle_lengths_present(G, max(forbid)))
    cols = {}
    for name in ("cadical153", "glucose4", "minisat22"):
        cls, _ = colour_cnf(G)
        s = Solver(name=name, bootstrap_with=cls)
        cols[name] = s.solve(); s.delete()
    ok = planar and not has_forbidden_cycle(G, forbid) and not any(cols.values())
    return ok, {"n": G.number_of_nodes(), "m": G.number_of_edges(), "planar": planar,
                "cycle_lengths_up_to_%d" % max(forbid): cyc, "3col": cols}


def random_child(lib, rng, a):
    items = lib.items()
    w2 = [g for g in items if len(g.terms) == 2]
    w3 = [g for g in items if len(g.terms) == 3]
    r = rng.choices([0, 2, 3], weights=[2, 3, 3])[0]
    h = rng.randint(max(1, 3 - r), max(a.max_hidden, 3 - r))
    nv = r + h
    outer = list(range(r))
    slots = []
    for _ in range(rng.randint(1, a.max_slots)):
        pool = w3 if (w3 and rng.random() < 0.6) else w2
        wts = [(1 + strength(g)) ** 2 / math.sqrt(g.size) for g in pool]
        g = rng.choices(pool, weights=wts)[0]
        verts = rng.sample(range(nv), len(g.terms))
        slots.append((g, verts))
    edges = set()
    for _ in range(rng.randint(0, a.max_edges)):
        u, w = rng.sample(range(nv), 2)
        edges.add((min(u, w), max(u, w)))
    return nv, outer, slots, sorted(edges)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--forbid", type=int, nargs="+", default=[4, 5, 6])
    ap.add_argument("--rounds", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-hidden", type=int, default=6)
    ap.add_argument("--max-slots", type=int, default=5)
    ap.add_argument("--max-edges", type=int, default=5)
    ap.add_argument("--max-size", type=int, default=300)
    ap.add_argument("--out", default="ga_out")
    ap.add_argument("--every", type=int, default=2000)
    ap.add_argument("--disjoint-triangles", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    global DISJOINT_TRIANGLES
    DISJOINT_TRIANGLES = a.disjoint_triangles
    rng = random.Random(a.seed)
    forbid = set(a.forbid)
    lib = Library(seeds(forbid))
    log = open(os.path.join(a.out, "log.txt"), "a")
    t0 = time.time()

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True); log.write(line + "\n"); log.flush()

    def dump():
        rows = []
        for g in sorted(lib.items(), key=lambda g: (len(g.terms), -strength(g), g.size)):
            rows.append({"arity": len(g.terms), "rel": sorted(g.rel), "dist": g.dist, "size": g.size,
                         "origin": g.origin, "terms": list(g.terms), "edges": sorted(g.G.edges())})
        json.dump(rows, open(os.path.join(a.out, "library.json"), "w"))

    say("forbid=%s seeds=%s" % (sorted(forbid), [(g.origin, sorted(g.rel), g.dist) for g in lib.items()]))
    st = dict(tried=0, nonplanar=0, cycles=0, big=0, trivial=0, added=0)
    for it in range(1, a.rounds + 1):
        if it % a.every == 0:
            say("round %d %s library=%d" % (it, st, len(lib.by_key)))
            dump()
        nv, outer, slots, edges = random_child(lib, rng, a)
        st["tried"] += 1
        if not frame_planar(nv, outer, slots, edges):
            st["nonplanar"] += 1; continue
        G = build_child(nv, outer, slots, edges)
        if G.number_of_nodes() > a.max_size:
            st["big"] += 1; continue
        if has_forbidden_cycle(G, forbid):
            st["cycles"] += 1; continue
        terms = [("f", v) for v in outer]
        if not terms:
            cls, _ = colour_cnf(G)
            s = Solver(name="cadical153", bootstrap_with=cls); col = s.solve(); s.delete()
            if not col:
                ok, rep = verify_counterexample(G, forbid)
                say("TARGET 0-terminal non-colourable child: verified=%s %s" % (ok, rep))
                nx.write_edgelist(G, os.path.join(a.out, "counterexample_%d.edgelist" % it), data=False)
                if ok:
                    dump(); return
            continue
        if not nx.is_connected(G):
            st["trivial"] += 1; continue
        origin = "frame(nv=%d,outer=%d,slots=[%s],edges=%s)" % (
            nv, len(outer), ";".join("%s@%s" % (g.key, v) for g, v in slots), edges)
        g = make(G, terms, origin)
        if len(g.rel) == len(PATTERNS[len(terms)]) or min(g.dist) < 2:
            st["trivial"] += 1; continue
        if lib.offer(g):
            st["added"] += 1
            say("new gadget arity=%d rel=%s dist=%s size=%d" % (len(g.terms), sorted(g.rel), g.dist, g.size))
            if len(g.terms) == 2 and ((g.rel == frozenset({(0, 0)}) and g.dist[0] >= 2) or
                                      (g.rel == frozenset({(0, 1)}) and g.dist[0] >= 3)):
                ok, rep = verify_counterexample(k4_assembly(g), forbid)
                say("TARGET via K4 assembly: verified=%s %s" % (ok, rep))
                if ok:
                    dump(); return
    dump()
    say("done %s" % st)


if __name__ == "__main__":
    main()
