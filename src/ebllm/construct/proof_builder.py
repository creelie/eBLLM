"""Goal-directed construction: build a forcer together with its forcing argument.

The contacts are assumed to share one colour (call it gamma). Moves add only
structure that the argument uses:
  attach  - a new vertex next to a gamma vertex (it is not gamma);
  link    - an edge between two non-gamma vertices (their colours differ);
  derive  - a new vertex next to two non-gamma vertices whose colours are known
            to differ (it must be gamma);
  close   - an edge, or a triangle of new vertices, that leaves no colouring.
Each move must keep the graph planar with the contacts on one face, free of
the forbidden cycle lengths, and the contacts at least D apart. After each
move an exact SAT check decides whether the contacts can still share a
colour; when they cannot, the graph is a not-all-equal forcer (or, with two
contacts, a not-equal forcer).
"""
import argparse, itertools, json, os, random, sys, time
import networkx as nx
from pysat.solvers import Solver

from . import graphcheck as gc


def forbidden_ok(G, new_edges, forbid):
    """Only cycles through a new edge can be new: check paths between its ends."""
    lo, hi = min(forbid), max(forbid)
    for u, w in new_edges:
        H = G.copy(); H.remove_edge(u, w)
        # simple paths u..w of length lo-1..hi-1 in H
        stack = [(u, [u])]
        while stack:
            x, path = stack.pop()
            if len(path) - 1 >= hi - 1:
                continue
            for y in H[x]:
                if y == w:
                    if len(path) + 1 - 1 + 1 in forbid:   # cycle length = edges in path + 1
                        return False
                elif y not in path:
                    stack.append((y, path + [y]))
    return True


def planar_face(G, contacts):
    H = G.copy(); H.add_node("inf")
    for c in contacts:
        H.add_edge("inf", c)
    return nx.check_planarity(H)[0]


def dist_ok(G, contacts, D):
    """D is an int (every pair) or a dict {(i, j): minimum distance}."""
    for a, b in itertools.combinations(contacts, 2):
        need = D if isinstance(D, int) else D.get((a, b), D.get((b, a), 1))
        try:
            if nx.shortest_path_length(G, a, b) < need:
                return False
        except nx.NetworkXNoPath:
            pass
    return True


CHECKS = [0]   # exact SAT checks made by this module, read by the layer tower


def contacts_can_share(G, contacts):
    CHECKS[0] += 1
    idx = {v: i for i, v in enumerate(G.nodes())}
    var = lambda v, c: 3 * idx[v] + c + 1
    s = Solver(name="cadical153")
    for v in G.nodes():
        s.add_clause([var(v, 0), var(v, 1), var(v, 2)])
    for u, w in G.edges():
        for c in range(3):
            s.add_clause([-var(u, c), -var(w, c)])
    r = s.solve(assumptions=[var(c, 0) for c in contacts]); s.delete()
    return r


def status(G, contacts, inst=()):
    """gamma set: contacts plus derived; non-gamma: neighbours of gamma, and the
    free contact of a library gadget whose other two contacts are gamma.
    Derived gamma: a vertex adjacent to two non-gamma vertices of opposite
    parity in the non-gamma subgraph. Iterate to a fixed point."""
    gam = set(contacts)
    while True:
        non = set(v for g in gam for v in G[g]) - gam
        for t in inst:
            out = [v for v in t if v not in gam]
            if len(out) == 1:
                non.add(out[0])
        side = {}
        for comp in nx.connected_components(G.subgraph(non)):
            r = next(iter(comp)); side[r] = 0; q = [r]
            while q:
                x = q.pop()
                for y in G[x]:
                    if y in comp and y not in side:
                        side[y] = 1 - side[x]; q.append(y)
        comp_of = {}
        for i, comp in enumerate(nx.connected_components(G.subgraph(non))):
            for v in comp:
                comp_of[v] = i
        new = set()
        for z in G.nodes():
            if z in gam or z in non:
                continue
            nb = [x for x in G[z] if x in non]
            for x, y in itertools.combinations(nb, 2):
                if comp_of[x] == comp_of[y] and side[x] != side[y]:
                    new.add(z); break
        if not new:
            return gam, non, side, comp_of
        gam |= new


# move priorities: lower is tried first; noise reorders them at random
PRI = {"close-T": 0, "close-edge": 0, "close-odd": 0, "lemma-close": 0, "derive": 1, "link": 2,
       "attach+link": 2, "lemma": 2, "attach": 3}


class Builder:
    def __init__(self, a, rng):
        self.a, self.rng = a, rng
        self.G = nx.Graph()
        self.contacts = list(range(a.contacts))
        self.G.add_nodes_from(self.contacts)
        self.next = a.contacts
        self.inst = []          # contact triples of library gadgets used as lemmas
        self.used = []          # names of the moves applied, in order

    def fresh(self):
        self.next += 1
        return self.next - 1

    def try_add(self, new_nodes, edges):
        G2 = self.G.copy()
        G2.add_nodes_from(new_nodes)
        G2.add_edges_from(edges)
        if not forbidden_ok(G2, edges, self.a.forbid):
            return False
        if not dist_ok(G2, self.contacts, self.a.need):
            return False
        if not planar_face(G2, self.contacts):
            return False
        if self.a.tri_disjoint or self.a.tri_free_contacts:
            tri = nx.triangles(G2)
            if self.a.tri_disjoint and max(tri.values(), default=0) > 1:
                return False
            if any(tri.get(c, 0) for c in self.a.tri_free_contacts):
                return False
        self.G = G2
        return True

    def gadget_copy(self, g, roles):
        """Copy of library gadget g with its contacts 0, 1, 2 sent to roles."""
        H = g["G"]
        m = {}
        for v in H.nodes():
            m[v] = roles[v] if v in (0, 1, 2) else self.fresh()
        return [m[v] for v in H.nodes() if v not in (0, 1, 2)], [(m[u], m[w]) for u, w in H.edges()]

    def moves(self):
        gam, non, side, comp_of = status(self.G, self.contacts, self.inst)
        gam, non = sorted(gam), sorted(non)
        rng = self.rng
        opts = []
        # attach a new non-gamma vertex to 1 gamma vertex, or to an existing non-gamma vertex too
        for _ in range(4):
            g = rng.choice(gam)
            x = self.fresh()
            if non and rng.random() < 0.6:
                y = rng.choice(non)
                opts.append(("attach+link", [x], [(g, x), (x, y)]))
            else:
                opts.append(("attach", [x], [(g, x)]))
        # link two non-gamma vertices
        for _ in range(6):
            if len(non) >= 2:
                x, y = rng.sample(non, 2)
                if not self.G.has_edge(x, y):
                    opts.append(("link", [], [(x, y)]))
        # derive gamma from opposite-parity pair
        pairs = [(x, y) for x, y in itertools.combinations(non, 2)
                 if comp_of[x] == comp_of[y] and side[x] != side[y]]
        for _ in range(6):
            if pairs:
                x, y = rng.choice(pairs)
                z = self.fresh()
                opts.append(("derive", [z], [(z, x), (z, y)]))
        # close: triangle of new vertices on three gamma vertices
        for _ in range(3):
            if len(gam) >= 3:
                g1, g2, g3 = rng.sample(gam, 3)
                m, n, o = self.fresh(), self.fresh(), self.fresh()
                opts.append(("close-T", [m, n, o], [(m, n), (n, o), (m, o), (g1, m), (g2, n), (g3, o)]))
        # close: gamma-gamma edge or same-parity link
        for _ in range(3):
            if len(gam) >= 2:
                g1, g2 = rng.sample(gam, 2)
                if not self.G.has_edge(g1, g2):
                    opts.append(("close-edge", [], [(g1, g2)]))
        sp = [(x, y) for x, y in itertools.combinations(non, 2)
              if comp_of[x] == comp_of[y] and side[x] == side[y] and not self.G.has_edge(x, y)]
        for _ in range(3):
            if sp:
                x, y = rng.choice(sp)
                opts.append(("close-odd", [], [(x, y)]))
        # lemmas: a library gadget with two contacts on gamma vertices forces its third
        lib = self.a.lib
        for _ in range(self.a.lemma_tries if lib else 0):
            if len(gam) >= 2:
                g = rng.choice(lib)
                x, y = rng.sample(gam, 2)
                z = self.fresh()
                roles = [x, y, z]; rng.shuffle(roles)
                nodes, edges = self.gadget_copy(g, dict(enumerate(roles)))
                opts.append(("lemma", nodes + [z], edges, tuple(roles)))
            if len(gam) >= 3:
                g = rng.choice(lib)
                roles = rng.sample(gam, 3)
                nodes, edges = self.gadget_copy(g, dict(enumerate(roles)))
                opts.append(("lemma-close", nodes, edges, tuple(roles)))
        rng.shuffle(opts)
        pri = getattr(self.a, "pri", None) or PRI
        opts.sort(key=lambda o: pri[o[0]] + rng.random() * self.a.noise)
        return opts

    def run(self):
        for step in range(self.a.max_steps):
            if self.G.number_of_nodes() > self.a.max_n:
                return None
            done = False
            for mv in self.moves():
                name, nodes, edges = mv[:3]
                if self.try_add(nodes, edges):
                    self.used.append(name)
                    if len(mv) > 3:
                        self.inst.append(mv[3])
                    done = True
                    break
            if not done:
                return None
            if not contacts_can_share(self.G, self.contacts):
                return self.G
        return None


def minimise(G, contacts, forbid):
    """Drop vertices while the forcing property holds."""
    changed = True
    while changed:
        changed = False
        for v in sorted(G.nodes(), key=lambda v: G.degree(v)):
            if v in contacts:
                continue
            H = G.copy(); H.remove_node(v)
            if not contacts_can_share(H, contacts):
                G = H; changed = True; break
    return G


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--contacts", type=int, default=3)
    ap.add_argument("--forbid", type=int, nargs="+", default=[4, 5, 6])
    ap.add_argument("--D", type=int, default=4)
    ap.add_argument("--dist", nargs="+", default=None, help="per-pair minimum distances, e.g. 0,1,3 0,2,3 1,2,5")
    ap.add_argument("--max-n", type=int, default=60)
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--noise", type=float, default=2.5)
    ap.add_argument("--tries", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="pb_out")
    ap.add_argument("--lemmas", nargs="*", default=[], help="gadget json files (contacts 0, 1, 2) used as lemmas")
    ap.add_argument("--lemma-tries", type=int, default=4)
    ap.add_argument("--tri-disjoint", action="store_true", help="no two triangles share a vertex (Bordeaux)")
    ap.add_argument("--tri-free-contacts", type=int, nargs="*", default=[], help="contacts that lie on no triangle")
    a = ap.parse_args(argv)
    a.forbid = set(a.forbid)
    if a.dist:
        a.need = {}
        for t in a.dist:
            i, j, d = map(int, t.split(","))
            a.need[(i, j)] = d
    else:
        a.need = a.D
    os.makedirs(a.out, exist_ok=True)
    a.lib = []
    for f in a.lemmas:
        d = json.load(open(f))
        H = nx.Graph(); H.add_nodes_from([0, 1, 2]); H.add_edges_from(tuple(e) for e in d["edges"])
        a.lib.append({"G": H, "name": os.path.basename(f)})
    rng = random.Random(a.seed)
    log = open(os.path.join(a.out, "log.txt"), "a")
    t0 = time.time()
    def say(m):
        line = "[%7.1fs] %s" % (time.time() - t0, m); print(line, flush=True); log.write(line + "\n"); log.flush()
    say("contacts=%d forbid=%s dist=%s max_n=%d lemmas=%s tri_disjoint=%s tri_free_contacts=%s"
        % (a.contacts, sorted(a.forbid), a.need, a.max_n, [g["name"] for g in a.lib], a.tri_disjoint, a.tri_free_contacts))
    best = None
    for t in range(1, a.tries + 1):
        G = Builder(a, rng).run()
        if G is None:
            if t % 2000 == 0:
                say("try %d: no forcer yet" % t)
            continue
        G = minimise(G, list(range(a.contacts)), a.forbid)
        rep = gc.report(G, list(range(a.contacts)), "NAE" if a.contacts == 3 else "NEQ", cyc_hi=max(a.forbid) + 2)
        say("try %d FORCER n=%d %s" % (t, G.number_of_nodes(), rep))
        if best is None or G.number_of_nodes() < best:
            best = G.number_of_nodes()
            json.dump({"contacts": list(range(a.contacts)), "edges": sorted(G.edges()), "report": {k: str(v) for k, v in rep.items()}},
                      open(os.path.join(a.out, "forcer_n%d.json" % best), "w"))
    say("done")


if __name__ == "__main__":
    main()
