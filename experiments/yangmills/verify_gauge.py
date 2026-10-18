"""Independent check of the gauge-fixing pattern on a box of Z^4 (no periodicity used): every plaquette
in the box meets the fixed set F in exactly one link, F is a forest (union-find), and every active
link whose six plaquettes lie in the box has exactly 12 Dobrushin neighbours.  Also counts the
neighbours with no gauge fixing (18) and in temporal gauge (14)."""
import itertools
import sys

SIG = {"0000": 0, "0001": 1, "0010": 3, "0011": 3, "0100": 2, "0101": 1, "0110": 2, "0111": 0,
       "1000": 0, "1001": 2, "1010": 1, "1011": 2, "1100": 3, "1101": 3, "1110": 1, "1111": 0}
d = 4
n = int(sys.argv[1]) if len(sys.argv) > 1 else 6


def sigma(x):
    return SIG["".join(str(c % 2) for c in x)]


def e(x, mu):
    return (tuple(x), mu)


def shift(x, mu):
    y = list(x); y[mu] += 1; return tuple(y)


sites = list(itertools.product(range(n), repeat=d))
inbox = lambda x: all(0 <= c < n for c in x)
plaq = []
for x in sites:
    for mu, nu in itertools.combinations(range(d), 2):
        if inbox(shift(x, mu)) and inbox(shift(x, nu)):
            plaq.append([e(x, mu), e(shift(x, mu), nu), e(shift(x, nu), mu), e(x, nu)])


def fixed_sigma(link):
    x, mu = link
    return sigma(x) == mu


def fixed_temporal(link):
    return link[1] == 0


def report(name, fixed):
    links = {l for p in plaq for l in p}
    F = {l for l in links if fixed(l)}
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    forest = True
    for (x, mu) in F:
        a, b = find(x), find(shift(x, mu))
        if a == b:
            forest = False
        parent[a] = b
    counts = [sum(1 for l in p if l in F) for p in plaq]
    nb = {}
    deg = {}
    for p in plaq:
        act = [l for l in p if l not in F]
        for l in act:
            nb[l] = nb.get(l, 0) + len(act) - 1
            deg[l] = deg.get(l, 0) + 1
    full = [nb[l] for l in nb if deg[l] == 2 * (d - 1)]
    print(f"{name:9s} box {n}^4: plaquettes {len(plaq)}, F-links per plaquette {sorted(set(counts))}, "
          f"forest {forest}, neighbours of interior active links {sorted(set(full))}")
    return forest, sorted(set(full))


report("none", lambda l: False)
report("temporal", fixed_temporal)
f, full = report("one-link", fixed_sigma)
assert f and full == [12]
print("OK")
