"""Crossing constructions: a typed chain reaction with a hard filter and a random control.

Constructions are typed expression trees.  Leaves are seeds taken from known constructions (each
carries its provenance); internal nodes combine them.  Two parents breed by typed subtree crossover:
a subtree of parent A whose output type matches a slot of parent B replaces that slot.  Every
offspring must pass a hard filter before it may seed the next generation, and the same budget of
filter evaluations is spent by each arm:

  network  parents drawn by fitness; several type-compatible crosses are proposed per slot and the
           one a learned survival model ranks first is evaluated; the model is refit each generation;
  random   uniformly random parents and one uniformly random type-compatible cross per slot;
  select   parents drawn by fitness as in the network arm, one cross per slot, no learned model;
  blind    uniformly random parents and a cross that ignores types (ill-typed offspring fail).

The concrete domain here is Erdos problem 1183.  A construction is a family of 2-colourings of the
Boolean lattice 2^[n], one for each n.  The filter computes, with `findmono`, the largest
monochromatic sublattice m(n) for n = 6..9 and keeps the offspring when m(n) <= f(n) + slack, where
f(n) = ceil((n+1)/2) is the exact value for these n.  The benchmark gap is f(n) = O(n): an offspring
touches it when it gives an upper bound for f(n) at an n where the exact value is unknown.

Types: Pat (a 0/1 sequence indexed by 0..n), Fam (a family of colourings).
"""
from __future__ import annotations

import math
import os
import random
import select
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------------------------------
# Seeds: leaves with provenance.  ('pat', kind, params) produce Pat; ('fam', kind, params) produce Fam.
SEEDS: List[Tuple[str, tuple, str]] = [
    ("Thue-Morse word", ("pat", "tm", (0,)), "Prouhet 1851; Thue 1912; Morse 1921"),
    ("Thue-Morse word, shift 1", ("pat", "tm", (1,)), "Prouhet 1851; Thue 1912; Morse 1921"),
    ("Rudin-Shapiro word", ("pat", "rs", (0,)), "Golay 1951; Shapiro 1952; Rudin 1959"),
    ("Fibonacci (Sturmian) word", ("pat", "sturm", (0.6180339887,)), "Sturmian words, Morse-Hedlund 1940"),
    ("Sturmian word, slope sqrt2-1", ("pat", "sturm", (0.4142135624,)), "Morse-Hedlund 1940"),
    ("Legendre symbol mod 5", ("pat", "leg", (5,)), "quadratic residue colourings"),
    ("Legendre symbol mod 7", ("pat", "leg", (7,)), "quadratic residue colourings"),
    ("Legendre symbol mod 11", ("pat", "leg", (11,)), "quadratic residue colourings"),
    ("Legendre symbol mod 13", ("pat", "leg", (13,)), "quadratic residue colourings"),
    ("period-4 levels 1100", ("pat", "lit", (1, 1, 0, 0)), "chain-bound colourings"),
    ("alternating levels", ("pat", "lit", (1, 0)), "chain bound"),
    ("optimal level pattern n=7", ("pat", "lit", (1, 0, 0, 1, 1, 0, 0, 1)), "this repository, f(7) witness"),
    ("optimal level pattern n=9", ("pat", "lit", (1, 1, 0, 0, 1, 0, 1, 1, 0, 0)), "this repository, f(9) witness"),
    ("optimal level pattern n=10", ("pat", "lit", (1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1)), "this repository, f(10) witness"),
    ("Berlekamp-style AP-free word mod 3", ("pat", "pow", (3,)), "Berlekamp 1968 (finite-field van der Waerden colourings)"),
    ("weighted sum mod 3", ("fam", "wsum", ((1, 2), 3, (0,))), "character colourings"),
    ("weighted sum mod 4", ("fam", "wsum", ((1, 1, 2), 4, (0, 1))), "character colourings"),
    ("least element parity", ("fam", "minel", (2,)), "lexicographic colourings"),
]

PAT_OPS = ("xorp", "shift", "rev", "dilate", "inter")      # Pat x ... -> Pat
FAM_OPS = ("level", "xor", "split", "blowup", "dual", "sym")
#   level : Pat -> Fam                 colour of S is p(|S|)
#   xor   : Fam x Fam -> Fam
#   split : Fam x Fam -> Fam           ground set cut at round(r n), the two colours combined by op
#   blowup: Fam -> Fam                 blocks of size b, a block counts when it meets S ('any') or lies in S ('all')
#   dual  : Fam -> Fam                 S -> complement of S
#   sym   : Fam -> Fam                 colour of S is the colour of {0, ..., |S|-1}
OUT = {"pat": "Pat", "fam": "Fam", "xorp": "Pat", "shift": "Pat", "rev": "Pat", "dilate": "Pat",
       "inter": "Pat", "level": "Fam", "xor": "Fam", "split": "Fam", "blowup": "Fam", "dual": "Fam",
       "sym": "Fam"}
SLOTS = {"xorp": ("Pat", "Pat"), "shift": ("Pat",), "rev": ("Pat",), "dilate": ("Pat",),
         "inter": ("Pat", "Pat"), "level": ("Pat",), "xor": ("Fam", "Fam"), "split": ("Fam", "Fam"),
         "blowup": ("Fam",), "dual": ("Fam",), "sym": ("Fam",)}


def otype(g) -> str:
    return OUT[g[0]] if g[0] in OUT else OUT[g[0]]


# A genome is a nested tuple: leaves ('pat'|'fam', kind, params); internal (op, params, child, ...).
def children(g):
    return [] if g[0] in ("pat", "fam") else list(g[2:])


def with_children(g, ch):
    return (g[0], g[1], *ch)


def subtrees(g, path=()):
    yield path, g
    for i, c in enumerate(children(g)):
        yield from subtrees(c, path + (i,))


def get(g, path):
    for i in path:
        g = children(g)[i]
    return g


def put(g, path, new):
    if not path:
        return new
    ch = children(g)
    ch[path[0]] = put(ch[path[0]], path[1:], new)
    return with_children(g, ch)


def well_typed(g) -> bool:
    if g[0] in ("pat", "fam"):
        return True
    if g[0] not in SLOTS:
        return False
    sl = SLOTS[g[0]]
    ch = children(g)
    return len(ch) == len(sl) and all(otype(c) == t and well_typed(c) for c, t in zip(ch, sl))


def size(g) -> int:
    return 1 + sum(size(c) for c in children(g))


def depth(g) -> int:
    return 1 + max((depth(c) for c in children(g)), default=0)


def provenance(g) -> List[str]:
    names = {s[1]: s[0] for s in SEEDS}
    out = []
    for _, t in subtrees(g):
        if t[0] in ("pat", "fam") and t in names:
            out.append(names[t])
    return sorted(set(out))


# ---------------------------------------------------------------------------------------------------
# Evaluation.  pattern(g, n) -> int array of length n+1; colouring(g, n) -> int array of length 2^n.
_POP = {}


def popcounts(n):
    if n not in _POP:
        v = np.arange(1 << n, dtype=np.int64)
        c = np.zeros_like(v)
        for i in range(n):
            c += (v >> i) & 1
        _POP[n] = c
    return _POP[n]


def _is_qr(j, p):
    j %= p
    return j == 0 or pow(j, (p - 1) // 2, p) == 1


def pattern(g, n) -> np.ndarray:
    k, j = g[0], np.arange(n + 1)
    if k == "pat":
        kind, prm = g[1], g[2]
        if kind == "tm":
            return np.array([bin(x + prm[0]).count("1") & 1 for x in range(n + 1)])
        if kind == "rs":
            return np.array([bin((x + prm[0]) & ((x + prm[0]) >> 1)).count("1") & 1 for x in range(n + 1)])
        if kind == "sturm":
            a = prm[0]
            return np.array([int(math.floor((x + 1) * a) - math.floor(x * a)) for x in range(n + 1)])
        if kind == "leg":
            return np.array([int(_is_qr(x, prm[0])) for x in range(n + 1)])
        if kind == "lit":
            return np.array([prm[x % len(prm)] for x in range(n + 1)])
        if kind == "pow":   # digit sum of x in base q, mod 2
            q = prm[0]
            out = []
            for x in range(n + 1):
                s, y = 0, x
                while y:
                    s, y = s + y % q, y // q
                out.append(s & 1)
            return np.array(out)
        raise ValueError(kind)
    prm, ch = g[1], children(g)
    if k == "xorp":
        return pattern(ch[0], n) ^ pattern(ch[1], n)
    if k == "shift":
        return pattern(ch[0], n + prm[0])[prm[0]:]
    if k == "rev":
        return pattern(ch[0], n)[::-1].copy()
    if k == "dilate":
        p = pattern(ch[0], n)
        return p[j // prm[0]]
    if k == "inter":
        a, b = pattern(ch[0], n), pattern(ch[1], n)
        return np.where(j % 2 == 0, a[j // 2], b[j // 2])
    raise ValueError(k)


def colouring(g, n) -> np.ndarray:
    k = g[0]
    if n == 0:
        return np.zeros(1, dtype=np.int64)
    if k == "fam":
        kind, prm = g[1], g[2]
        v = np.arange(1 << n, dtype=np.int64)
        if kind == "wsum":
            w, m, res = prm
            s = np.zeros_like(v)
            for i in range(n):
                s += ((v >> i) & 1) * w[i % len(w)]
            return np.isin(s % m, res).astype(np.int64)
        if kind == "minel":
            q = prm[0]
            low = np.full_like(v, n)
            for i in range(n - 1, -1, -1):
                low = np.where((v >> i) & 1, i, low)
            return ((low % q) == 0).astype(np.int64)
        raise ValueError(kind)
    prm, ch = g[1], children(g)
    if k == "level":
        return pattern(ch[0], n)[popcounts(n)]
    if k == "xor":
        return colouring(ch[0], n) ^ colouring(ch[1], n)
    if k == "dual":
        c = colouring(ch[0], n)
        return c[(np.arange(1 << n) ^ ((1 << n) - 1))]
    if k == "sym":
        c = colouring(ch[0], n)
        return c[(1 << popcounts(n)) - 1]
    if k == "split":
        r, op = prm
        a = min(n - 1, max(1, round(r * n)))
        v = np.arange(1 << n, dtype=np.int64)
        ca, cb = colouring(ch[0], a), colouring(ch[1], n - a)
        x, y = ca[v & ((1 << a) - 1)], cb[v >> a]
        return {"xor": x ^ y, "and": x & y, "or": x | y}[op]
    if k == "blowup":
        b, mode = prm
        m = -(-n // b)
        v = np.arange(1 << n, dtype=np.int64)
        img = np.zeros_like(v)
        for blk in range(m):
            mask = sum(1 << i for i in range(blk * b, min(n, blk * b + b)))
            hit = ((v & mask) != 0) if mode == "any" else ((v & mask) == mask)
            img |= hit.astype(np.int64) << blk
        return colouring(ch[0], m)[img]
    raise ValueError(k)


def red_mask(g, n) -> int:
    c = colouring(g, n)
    return int("".join("1" if x else "0" for x in c[::-1]), 2) if len(c) else 0


# ---------------------------------------------------------------------------------------------------
class FindMono:
    """A persistent `findmono` process.  query(n, s, red) is True when a monochromatic sublattice with
    at least s members exists, False when none does, None on timeout."""

    def __init__(self, exe: str, timeout: float = 20.0):
        self.exe, self.timeout, self.p = exe, timeout, None
        self.calls = 0

    def _start(self):
        self.p = subprocess.Popen(["bash", "-c", f"ulimit -s unlimited; exec {self.exe}"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1)

    def query(self, n, s, red) -> Optional[bool]:
        if self.p is None or self.p.poll() is not None:
            self._start()
        self.calls += 1
        self.p.stdin.write(f"{n} {s} {red:x}\n")
        self.p.stdin.flush()
        r, _, _ = select.select([self.p.stdout], [], [], self.timeout)
        if not r:
            self.p.kill()
            self.p = None
            return None
        return self.p.stdout.readline().split()[0] != "none"

    def maxmono(self, n, red, cap) -> Optional[int]:
        """The largest monochromatic sublattice, when it is at most cap; cap + 1 when larger; None on timeout."""
        s = (n + 2) // 2        # the chain bound: a monochromatic chain of this size always exists
        while s < cap + 1:
            r = self.query(n, s + 1, red)
            if r is None:
                return None
            if not r:
                return s
            s += 1
        return cap + 1

    def close(self):
        if self.p:
            self.p.stdin.close()
            self.p.wait()


def f_exact(n):
    return (n + 2) // 2


@dataclass
class Result:
    genome: tuple
    passed: bool
    m: Dict[int, Optional[int]]
    score: float
    arm: str
    gen: int
    reason: str = ""


def evaluate(g, fm: FindMono, ns=(6, 7, 8, 9), slack=1, arm="", gen=0) -> Result:
    if not well_typed(g) or otype(g) != "Fam":
        return Result(g, False, {}, math.inf, arm, gen, "ill-typed")
    m = {}
    for n in ns:
        v = fm.maxmono(n, red_mask(g, n), f_exact(n) + slack)
        m[n] = v
        if v is None or v > f_exact(n) + slack:
            return Result(g, False, m, math.inf, arm, gen, "timeout" if v is None else f"m({n})={v}")
        assert v >= f_exact(n), "checker below the chain bound"
    return Result(g, True, m, float(sum(m[n] - f_exact(n) for n in ns)), arm, gen)


# ---------------------------------------------------------------------------------------------------
FEATURES = ["pat:tm", "pat:rs", "pat:sturm", "pat:leg", "pat:lit", "pat:pow", "fam:wsum", "fam:minel",
            *PAT_OPS, *FAM_OPS]


def features(g) -> np.ndarray:
    x = np.zeros(len(FEATURES) + 3)
    for _, t in subtrees(g):
        key = f"{t[0]}:{t[1]}" if t[0] in ("pat", "fam") else t[0]
        if key in FEATURES:
            x[FEATURES.index(key)] += 1
    x[-3], x[-2], x[-1] = size(g) / 10, depth(g) / 5, 1.0
    return x


class SurvivalModel:
    """Logistic regression of passing the filter on genome features, refit on every result so far."""

    def __init__(self):
        self.w = None

    def fit(self, X, y, steps=400, lr=0.5, l2=1e-2):
        X, y = np.array(X), np.array(y, dtype=float)
        w = np.zeros(X.shape[1])
        for _ in range(steps):
            p = 1 / (1 + np.exp(-X @ w))
            w -= lr * (X.T @ (p - y) / len(y) + l2 * w)
        self.w = w

    def prob(self, g) -> float:
        if self.w is None:
            return 0.5
        return float(1 / (1 + np.exp(-features(g) @ self.w)))


def mutate(g, rng: random.Random):
    paths = [p for p, _ in subtrees(g)]
    p = rng.choice(paths)
    t = get(g, p)
    if t[0] == "pat":
        kind, prm = t[1], t[2]
        if kind in ("tm", "rs"):
            return put(g, p, ("pat", kind, (rng.randrange(8),)))
        if kind == "sturm":
            return put(g, p, ("pat", kind, (round(rng.random(), 6),)))
        if kind == "leg":
            return put(g, p, ("pat", kind, (rng.choice([3, 5, 7, 11, 13, 17, 19, 23]),)))
        if kind == "pow":
            return put(g, p, ("pat", kind, (rng.choice([3, 4, 5, 6]),)))
        if kind == "lit":
            bits = list(prm)
            i = rng.randrange(len(bits))
            bits[i] ^= 1
            return put(g, p, ("pat", kind, tuple(bits)))
    if t[0] == "fam":
        return g
    if t[0] == "shift":
        return put(g, p, ("shift", (rng.randrange(1, 9),), *children(t)))
    if t[0] == "dilate":
        return put(g, p, ("dilate", (rng.choice([2, 3]),), *children(t)))
    if t[0] == "split":
        return put(g, p, ("split", (rng.choice([0.25, 1 / 3, 0.5, 2 / 3]), rng.choice(["xor", "and", "or"])),
                          *children(t)))
    if t[0] == "blowup":
        return put(g, p, ("blowup", (rng.choice([2, 3]), rng.choice(["any", "all"])), *children(t)))
    return g


def wrap(g, rng: random.Random):
    """Apply a random constructor whose slot accepts g (filling any other slot with a random seed)."""
    ty = otype(g)
    ops = [o for o, sl in SLOTS.items() if ty in sl]
    o = rng.choice(ops)
    prm = {"xorp": (), "shift": (rng.randrange(1, 9),), "rev": (), "dilate": (rng.choice([2, 3]),),
           "inter": (), "level": (), "xor": (), "split": (rng.choice([0.25, 1 / 3, 0.5, 2 / 3]),
                                                           rng.choice(["xor", "and", "or"])),
           "blowup": (rng.choice([2, 3]), rng.choice(["any", "all"])), "dual": (), "sym": ()}[o]
    sl = SLOTS[o]
    i = rng.choice([k for k, t in enumerate(sl) if t == ty])
    ch = []
    for k, t in enumerate(sl):
        if k == i:
            ch.append(g)
        else:
            cands = [s[1] for s in SEEDS if OUT[s[1][0]] == t]
            ch.append(rng.choice(cands))
    return (o, prm, *ch)


def cross(a, b, rng: random.Random, typed=True):
    """Insert a subtree of a into a slot of b.  typed: the subtree's output type equals the slot's."""
    sa = list(subtrees(a))
    sb = list(subtrees(b))
    if typed:
        pairs = [(pa, ta, pb) for pa, ta in sa for pb, tb in sb if otype(ta) == otype(tb)]
        if not pairs:
            return b
        _, ta, pb = rng.choice(pairs)
    else:
        _, ta = rng.choice(sa)
        pb, _ = rng.choice(sb)
    return put(b, pb, ta)


def offspring(a, b, rng, typed=True, max_size=14):
    r = rng.random()
    if r < 0.5:
        c = cross(a, b, rng, typed)
    elif r < 0.75:
        c = mutate(a, rng)
    else:
        c = wrap(a, rng) if typed else cross(a, b, rng, False)
    if size(c) > max_size:
        c = mutate(b, rng)
    if typed and otype(c) == "Pat":
        c = ("level", (), c)
    return c


def initial_population():
    pop = []
    for _, g, _ in SEEDS:
        pop.append(("level", (), g) if OUT[g[0]] == "Pat" else g)
    return pop


@dataclass
class Arm:
    name: str
    results: List[Result] = field(default_factory=list)
    survivors: List[Result] = field(default_factory=list)
    seen: Dict[tuple, Result] = field(default_factory=dict)


def phenotype(g, ns=(6, 7, 8, 9)) -> tuple:
    """An invariant of the colourings at ns under permutations of the ground set, complementation of
    sets and exchange of the colours.  Equal colourings up to these symmetries have equal keys; the
    converse can fail, so counts of distinct keys never overcount distinct colourings."""
    key = []
    for n in ns:
        c = colouring(g, n)
        pc = popcounts(n)
        v = np.arange(1 << n, dtype=np.int64)
        comp = v ^ ((1 << n) - 1)
        variants = []
        for d in (c, c[comp], 1 - c, (1 - c)[comp]):
            lev = tuple(int(d[pc == k].sum()) for k in range(n + 1))
            per = sorted(tuple(int(d[(pc == k) & (((v >> i) & 1) == 1)].sum()) for k in range(n + 1))
                         for i in range(n))
            variants.append((lev, tuple(per)))
        key.append(min(variants))
    return tuple(key)


def is_level(g, n=9) -> bool:
    c, pc = colouring(g, n), popcounts(n)
    return all(len(set(c[pc == k].tolist())) <= 1 for k in range(n + 1))


ARMS = ("network", "select", "random", "blind")


def run(arms=ARMS, generations=6, per_gen=40, seed=0, exe=None, log=print, novel=False):
    """Breed per_gen new genomes a generation in each arm and count, among them, those that pass the
    filter and those that give a colouring not met before (by the phenotype key).
      network  fitness-weighted parents, eight typed proposals, the one the survival model ranks first;
      select   fitness-weighted parents, one typed proposal (selection without the learned model);
      random   uniform parents, one typed proposal;
      blind    uniform parents, crossover that ignores the types.
    With novel=True every arm skips, before any check is run, an offspring whose colouring (by the
    phenotype key) it has already evaluated, so the budget is spent on colourings not tried before."""
    exe = exe or os.path.join(os.path.dirname(__file__), "..", "..", "..", "experiments", "erdos1183", "findmono4k")
    fm = FindMono(os.path.abspath(exe))
    base = [evaluate(g, fm, arm="seed", gen=0) for g in initial_population()]
    out = {"seeds": [(provenance(r.genome), r.passed, r.m) for r in base], "arms": {}}
    for name in arms:
        rng = random.Random(seed)
        A = Arm(name)
        A.survivors = [r for r in base if r.passed]
        pool = list(base)
        for r in base:
            A.seen[r.genome] = r
        phen = {phenotype(r.genome): r for r in A.survivors}
        tried = {phenotype(r.genome) for r in base if r.reason != "ill-typed"}

        def fresh_ok(x):
            if not novel:
                return True
            if not well_typed(x) or otype(x) != "Fam":
                return True
            return phenotype(x) not in tried
        model = SurvivalModel()
        per = []
        for gen in range(1, generations + 1):
            if name == "network":
                model.fit([features(r.genome) for r in pool], [r.passed for r in pool])
            batch = []
            for _ in range(per_gen):
                c = None
                for _try in range(60):
                    if name in ("network", "select"):
                        par = A.survivors or pool
                        wts = [1.0 / (1.0 + r.score) for r in par]
                        cands = []
                        for _ in range(8 if name == "network" else 1):
                            a, b = rng.choices(par, weights=wts, k=2)
                            x = offspring(a.genome, b.genome, rng, typed=True)
                            if x not in A.seen and fresh_ok(x):
                                cands.append(x)
                        if cands:
                            c = max(cands, key=model.prob) if name == "network" else cands[0]
                    else:
                        a, b = rng.choice(pool), rng.choice(pool)
                        x = offspring(a.genome, b.genome, rng, typed=(name == "random"))
                        if x not in A.seen and fresh_ok(x):
                            c = x
                    if c is not None:
                        break
                if c is None:
                    continue
                r = evaluate(c, fm, arm=name, gen=gen)
                A.seen[c] = r
                if r.reason != "ill-typed":
                    tried.add(phenotype(c))
                batch.append(r)
            A.results += batch
            pool += batch
            new = [r for r in batch if r.passed]
            A.survivors += new
            fresh = []
            for r in new:
                k = phenotype(r.genome)
                if k not in phen:
                    phen[k] = r
                    fresh.append(r)
            per.append({"gen": gen, "offspring": len(batch), "passed": len(new),
                        "new_colourings": len(fresh),
                        "new_optimal_colourings": sum(r.score == 0 for r in fresh),
                        "ill_typed": sum(r.reason == "ill-typed" for r in batch)})
            log(f"{name:8s} seed {seed} gen {gen}: {per[-1]}")
        out["arms"][name] = {"per_gen": per, "survivors": A.survivors,
                             "colourings": [r for k, r in phen.items()]}
    fm.close()
    return out


def extend(genome, fm: FindMono, ns=(10, 11, 12), slack=1) -> Dict[int, Optional[int]]:
    """Largest monochromatic sublattice of the offspring at larger n (None: undecided in the time limit)."""
    return {n: fm.maxmono(n, red_mask(genome, n), f_exact(n) + slack) for n in ns}
