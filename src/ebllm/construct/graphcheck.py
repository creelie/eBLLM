"""Independent checks for planar colouring gadgets.

Kept separate from the search code: planarity (networkx), short cycles (DFS),
distances (BFS) and 3-colourings (plain backtracking, no SAT solver).
"""
import itertools
import networkx as nx


def short_cycles(G, lo, hi):
    """Yield cycles (as vertex lists) of length lo..hi; each cycle once."""
    order = {v: i for i, v in enumerate(G.nodes())}
    for s in G.nodes():
        stack = [(s, [s])]
        while stack:
            v, path = stack.pop()
            for w in G[v]:
                if w == s and len(path) >= 3:
                    if lo <= len(path) <= hi and order[path[1]] < order[path[-1]]:
                        yield list(path)
                elif w not in path and order[w] > order[s] and len(path) < hi:
                    stack.append((w, path + [w]))


def cycle_lengths_present(G, hi):
    out = set()
    for c in short_cycles(G, 3, hi):
        out.add(len(c))
    return out


def planar_with_face(G, contacts):
    """Planar with all contacts on one face (test: add a vertex joined to them)."""
    H = G.copy()
    H.add_node("_inf")
    for c in contacts:
        H.add_edge("_inf", c)
    return nx.check_planarity(H)[0]


def colourings(G, fixed=None, limit=None):
    """Enumerate proper 3-colourings (dict) by backtracking; fixed pins colours."""
    fixed = dict(fixed or {})
    order = sorted(G.nodes(), key=lambda v: (v not in fixed, -G.degree(v)))
    col = {}
    count = 0

    def rec(i):
        nonlocal count
        if limit is not None and count >= limit:
            return
        if i == len(order):
            count += 1
            yield dict(col)
            return
        v = order[i]
        opts = [fixed[v]] if v in fixed else range(3)
        for c in opts:
            if all(col.get(w) != c for w in G[v]):
                col[v] = c
                yield from rec(i + 1)
                del col[v]
    yield from rec(0)


def colour_fc(G, fixed=None):
    """One proper 3-colouring or None; forward checking with smallest domain first.
    Independent of the SAT solver used by the search."""
    dom = {v: {0, 1, 2} for v in G.nodes()}
    for v, c in (fixed or {}).items():
        dom[v] = {c}

    def assign(dom, v, c):
        dom = {u: set(s) for u, s in dom.items()}
        dom[v] = {c}
        stack = [v]
        while stack:
            x = stack.pop()
            (cx,) = dom[x]
            for w in G[x]:
                if cx in dom[w]:
                    dom[w].discard(cx)
                    if not dom[w]:
                        return None
                    if len(dom[w]) == 1:
                        stack.append(w)
        return dom

    start = dom
    for v, c in (fixed or {}).items():
        start = assign(start, v, c)
        if start is None:
            return None
    # propagate any singletons already present
    def rec(dom):
        free = [v for v in dom if len(dom[v]) > 1]
        if not free:
            col = {v: next(iter(s)) for v, s in dom.items()}
            assert all(col[u] != col[w] for u, w in G.edges())
            return col
        v = min(free, key=lambda u: (len(dom[u]), -G.degree(u)))
        for c in sorted(dom[v]):
            d2 = assign(dom, v, c)
            if d2 is not None:
                r = rec(d2)
                if r is not None:
                    return r
        return None
    import sys
    sys.setrecursionlimit(100000)
    return rec(start)


def three_colourable(G, fixed=None):
    return colour_fc(G, fixed) is not None


def forces(G, contacts, kind):
    """kind: 'NAE' (contacts never all equal), 'NEQ' (2 contacts never equal),
    'EQ' (2 contacts always equal; and the gadget is 3-colourable)."""
    if kind == "NAE":
        return not three_colourable(G, {c: 0 for c in contacts})
    u, v = contacts
    if kind == "NEQ":
        return not three_colourable(G, {u: 0, v: 0})
    if kind == "EQ":
        return three_colourable(G, {u: 0, v: 0}) and not three_colourable(G, {u: 0, v: 1})
    raise ValueError(kind)


def contact_distances(G, contacts):
    return {(x, y): nx.shortest_path_length(G, x, y) if nx.has_path(G, x, y) else None
            for x, y in itertools.combinations(contacts, 2)}


def report(G, contacts, kind, cyc_hi=8):
    return {
        "n": G.number_of_nodes(), "m": G.number_of_edges(),
        "planar_face": planar_with_face(G, contacts),
        "cycles_<=%d" % cyc_hi: sorted(cycle_lengths_present(G, cyc_hi)),
        "dist": contact_distances(G, contacts),
        "forces_" + kind: forces(G, contacts, kind),
    }
