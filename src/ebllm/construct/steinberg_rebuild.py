"""Level-0 calibration: rebuild the 2017 Steinberg counterexample and check it
(arXiv 1604.05108, Lemmas 1-2 and Theorem 3)."""
import itertools
import networkx as nx
from pysat.solvers import Solver
from .graphcheck import report, cycle_lengths_present


def G1(p=""):
    E = "bd be de af ag fg ch ci hi ef gh jd ji ke kf lg lh mj nk ol mn no mo".split()
    G = nx.Graph()
    G.add_edges_from((p + e[0], p + e[1]) for e in E)
    return G


def copy_g1(p, ta, tb, tc):
    """Copy of G1 with its contacts a, b, c renamed ta, tb, tc."""
    return nx.relabel_nodes(G1(p), {p + "a": ta, p + "b": tb, p + "c": tc})


def G2(p, A, B, C):
    # G1 has distances ab = ac = 3, bc = 4: put the distance-4 pair on each
    # pair of G2 contacts so that G2 has all contact distances 4.
    D, E, F = p + "D", p + "E", p + "F"
    G = nx.compose_all([copy_g1(p + "1", D, A, B),   # A-B at distance 4
                        copy_g1(p + "2", F, C, A),   # A-C
                        copy_g1(p + "3", E, B, C)])  # B-C
    G.add_edges_from([(D, E), (E, F), (D, F)])
    return G


def G_final():
    G = nx.compose_all([G2("P", "a", "c", "d"), G2("Q", "a", "c", "f"),
                        G2("R", "a", "c'", "d'"), G2("S", "a", "c'", "f'")])
    G.add_edges_from([("a", "b"), ("a", "e"), ("a", "e'"),
                      ("b", "c"), ("c", "c'"), ("b", "c'"),
                      ("d", "e"), ("e", "f"), ("d", "f"),
                      ("d'", "e'"), ("e'", "f'"), ("d'", "f'")])
    return G


def sat_colourable(G, name):
    idx = {v: i for i, v in enumerate(G.nodes())}
    var = lambda v, c: 3 * idx[v] + c + 1
    s = Solver(name=name)
    for v in G.nodes():
        s.add_clause([var(v, c) for c in range(3)])
    for u, w in G.edges():
        for c in range(3):
            s.add_clause([-var(u, c), -var(w, c)])
    s.add_clause([var(next(iter(G.nodes())), 0)])  # symmetry
    r = s.solve(); s.delete(); return r


SOLVERS = ("cadical153", "glucose4", "minisat22")


def check():
    """The three graphs and the facts the paper quotes, recomputed."""
    G = G_final()
    return {
        "G1": report(G1(), ["a", "b", "c"], "NAE"),
        "G2": report(G2("", "A", "B", "C"), ["A", "B", "C"], "NAE"),
        "G": {"n": G.number_of_nodes(), "m": G.number_of_edges(), "planar": nx.check_planarity(G)[0],
              "cycles_<=6": sorted(cycle_lengths_present(G, 6)),
              "colourable": {name: sat_colourable(G, name) for name in SOLVERS}},
    }


def main(argv=None):
    r = check()
    print("G1", r["G1"])
    print("G2", r["G2"])
    g = r["G"]
    print("G: n=%d m=%d planar=%s cycle lengths<=6: %s" % (g["n"], g["m"], g["planar"], g["cycles_<=6"]))
    for name, ok in g["colourable"].items():
        print("3-colourable by %s: %s" % (name, ok))


if __name__ == "__main__":
    main()
