"""Turn a not-all-equal gadget H(a, b, c) into a non-3-colourable planar graph.

H is read from a builder json: contacts 0, 1, 2 play a, b, c; the pair (1, 2)
is the long one. G2 = three copies of H on (D, A, B), (F, C, A), (E, B, C)
plus the triangle DEF (Cohen-Addad, Hebdige, Kral', Li, Salgado, Lemma 2);
the final graph is their Theorem 3 frame on four copies of G2. The result is
checked from scratch: planarity, every cycle length up to the forbidden
maximum, and non-3-colourability by three SAT solvers.
"""
import argparse, json, os, sys
import networkx as nx
from .graphcheck import cycle_lengths_present, report
from .steinberg_rebuild import sat_colourable


def load(path):
    d = json.load(open(path))
    H = nx.Graph(); H.add_edges_from(tuple(e) for e in d["edges"])
    return H


def copy_h(H, p, ta, tb, tc):
    m = {v: p + str(v) for v in H.nodes()}
    m.update({0: ta, 1: tb, 2: tc})
    return nx.relabel_nodes(H, m)


def G2(H, p, A, B, C):
    D, E, F = p + "D", p + "E", p + "F"
    G = nx.compose_all([copy_h(H, p + "1.", D, A, B), copy_h(H, p + "2.", F, C, A),
                        copy_h(H, p + "3.", E, B, C)])
    G.add_edges_from([(D, E), (E, F), (D, F)])
    return G


def final(H):
    G = nx.compose_all([G2(H, "P", "a", "c", "d"), G2(H, "Q", "a", "c", "f"),
                        G2(H, "R", "a", "c'", "d'"), G2(H, "S", "a", "c'", "f'")])
    G.add_edges_from([("a", "b"), ("a", "e"), ("a", "e'"), ("b", "c"), ("c", "c'"), ("b", "c'"),
                      ("d", "e"), ("e", "f"), ("d", "f"), ("d'", "e'"), ("e'", "f'"), ("d'", "f'")])
    return G


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("gadget")
    ap.add_argument("--forbid-max", type=int, required=True, help="largest forbidden cycle length (5 or 6)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    H = load(a.gadget)
    print("H ", report(H, [0, 1, 2], "NAE", cyc_hi=a.forbid_max + 2))
    g2 = G2(H, "", "A", "B", "C")
    print("G2", report(g2, ["A", "B", "C"], "NAE", cyc_hi=a.forbid_max + 2))
    G = final(H)
    cyc = sorted(cycle_lengths_present(G, a.forbid_max + 1))
    planar = nx.check_planarity(G)[0]
    col = {s: sat_colourable(G, s) for s in ("cadical153", "glucose4", "minisat22")}
    print("G : n=%d m=%d planar=%s cycle lengths <= %d: %s" % (
        G.number_of_nodes(), G.number_of_edges(), planar, a.forbid_max + 1, cyc))
    print("    3-colourable:", col)
    bad = [l for l in cyc if 4 <= l <= a.forbid_max]
    ok = planar and not bad and not any(col.values())
    print("COUNTEREXAMPLE" if ok else "not a counterexample", "(forbidden lengths 4..%d present: %s)" % (a.forbid_max, bad))
    if a.out:
        json.dump({"edges": [[str(u), str(v)] for u, v in G.edges()], "n": G.number_of_nodes(),
                   "m": G.number_of_edges(), "planar": planar, "cycles": cyc,
                   "colourable": col, "counterexample": ok}, open(a.out, "w"))


if __name__ == "__main__":
    main()
