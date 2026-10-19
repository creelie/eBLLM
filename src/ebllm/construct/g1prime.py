"""Variant of Steinberg's G1 without the contact triangles."""
import networkx as nx
from .graphcheck import report


def Y(G, a, b, k, p):
    """a=b forces k=a: path a-f-e-b and k joined to e and f."""
    f, e = p + "f", p + "e"
    G.add_edges_from([(a, f), (f, e), (e, b), (k, e), (k, f)])


def T(G, j, k, l, p):
    """triangle with one pendant edge to each of j, k, l: j=k=l impossible."""
    m, n, o = p + "m", p + "n", p + "o"
    G.add_edges_from([(m, n), (n, o), (m, o), (j, m), (k, n), (l, o)])


def G1prime():
    G = nx.Graph()
    Y(G, "a", "b", "k", "1"); Y(G, "a", "c", "l", "2"); Y(G, "b", "c", "j", "3")
    T(G, "j", "k", "l", "4")
    return G


def main(argv=None):
    print(report(G1prime(), ["a", "b", "c"], "NAE", cyc_hi=9))


if __name__ == "__main__":
    main()
