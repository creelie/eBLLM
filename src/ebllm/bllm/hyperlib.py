"""The library-wide layer: constructions and problems as typed nodes of a hypergraph, with a measured
test of whether the learned map proposes the right crossings.

Nodes are construction classes (the strategy labels of the Erdos harvest) and problem features (its
subject tags).  Each settled problem is a hyperedge joining its tags with the constructions its proof
used.  The encoder is a truncated SVD of the positive pointwise mutual information between tags and
constructions on the training problems.  For a held-out problem the map ranks constructions by the
inner product of the mean tag vector with each construction vector; the proposal is the top one (or
the top pair, for proofs that combined two).

The test is held-out prediction against two controls: a uniformly random construction and the most
frequent construction of the training set.  A proposal counts as a hit when the held-out proof used
it.  Nothing here proves a theorem; the layer is a router that is either better than the controls at
predicting which construction settles which problem, or not.
"""
from __future__ import annotations

import json
import os
import random
import re
from collections import Counter
from typing import Dict, List

import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "data")

# object types for typing library nodes from their descriptions
OBJECT_TYPES = {
    "graph": r"\bgraph|hypergraph|vertex|edge|colou?r",
    "set-system": r"set system|family of sets|sunflower|intersecting|sidon|sum-free|sumset",
    "integers": r"\bprime|integer|divisor|multiplicative|arithmetic progression|congruen",
    "polynomial": r"polynomial|trinomial|root",
    "analytic": r"zeta|l-function|dirichlet|exponential sum|fourier|character",
    "geometry": r"point|distance|plane|convex|packing|tiling|lattice",
    "algebraic-geometry": r"variet|hodge|cycle|sheaf|scheme|curve|surface|abelian",
    "group": r"\bgroup|representation|galois|lie algebra",
    "analysis-pde": r"navier|euler|flow|equation|operator|spectral|metric",
    "probability": r"random|probabilit|measure|entropy",
    "logic-complexity": r"circuit|complexity|decidab|model theory|categoric",
}


def type_of(text: str) -> List[str]:
    t = text.lower()
    return [k for k, rx in OBJECT_TYPES.items() if re.search(rx, t)] or ["other"]


def erdos_problems() -> List[dict]:
    d = json.load(open(os.path.join(DATA, "erdos_harvest.json")))
    out = []
    for k, v in d["strategies"]["per_problem"].items():
        if v["strategies"] and v["tags"]:
            out.append({"id": k, "tags": v["tags"], "strategies": v["strategies"], "lean": v["lean"]})
    return out


class HyperMap:
    def __init__(self, dim: int = 6):
        self.dim = dim

    def fit(self, probs: List[dict]):
        self.tags = sorted({t for p in probs for t in p["tags"]})
        self.cons = sorted({s for p in probs for s in p["strategies"]})
        ti = {t: i for i, t in enumerate(self.tags)}
        ci = {c: i for i, c in enumerate(self.cons)}
        M = np.zeros((len(self.tags), len(self.cons)))
        for p in probs:
            for t in p["tags"]:
                for s in p["strategies"]:
                    M[ti[t], ci[s]] += 1
        tot = M.sum()
        pt, pc = M.sum(1, keepdims=True) / tot, M.sum(0, keepdims=True) / tot
        with np.errstate(divide="ignore"):
            pmi = np.log((M / tot) / (pt * pc))
        ppmi = np.where(np.isfinite(pmi) & (pmi > 0), pmi, 0.0)
        U, S, Vt = np.linalg.svd(ppmi, full_matrices=False)
        k = min(self.dim, len(S))
        self.T = U[:, :k] * np.sqrt(S[:k])
        self.C = Vt[:k].T * np.sqrt(S[:k])
        self.ti, self.freq = ti, Counter(s for p in probs for s in p["strategies"])
        self.M, self.alpha = M, 1.0
        return self

    def rank(self, tags: List[str], mode: str = "bayes") -> List[str]:
        """mode 'svd': inner products in the PPMI embedding (rare associations dominate);
        mode 'bayes': log prior plus smoothed log likelihoods of the tags, the calibrated version."""
        idx = [self.ti[t] for t in tags if t in self.ti]
        if not idx:
            return [c for c, _ in self.freq.most_common()]
        if mode == "svd":
            sc = self.C @ self.T[idx].mean(0)
        else:
            prior = np.array([self.freq[c] for c in self.cons], dtype=float)
            lik = (self.M[idx] + self.alpha) / (self.M.sum(0) + self.alpha * len(self.tags))
            sc = np.log(prior / prior.sum()) + np.log(lik).sum(0)
        return [self.cons[i] for i in np.argsort(-sc)]


def evaluate(folds: int = 5, repeats: int = 10, seed: int = 0, dim: int = 6) -> Dict[str, float]:
    probs = erdos_problems()
    rng = random.Random(seed)
    hits = Counter()
    n = 0
    for _ in range(repeats):
        order = probs[:]
        rng.shuffle(order)
        for f in range(folds):
            test = order[f::folds]
            train = [p for i, p in enumerate(order) if i % folds != f]
            H = HyperMap(dim).fit(train)
            top_freq = H.freq.most_common(1)[0][0]
            for p in test:
                n += 1
                truth = set(p["strategies"])
                for mode in ("svd", "bayes"):
                    r = H.rank(p["tags"], mode)
                    hits[f"network_{mode}_top1"] += r[0] in truth
                    hits[f"network_{mode}_top2"] += bool(truth & set(r[:2]))
                hits["frequency_top1"] += top_freq in truth
                fr = [c for c, _ in H.freq.most_common()]
                hits["frequency_top2"] += bool(truth & set(fr[:2]))
                cons = H.cons
                hits["random_top1"] += rng.choice(cons) in truth
                hits["random_top2"] += bool(truth & set(rng.sample(cons, min(2, len(cons)))))
    out = {k: round(v / n, 4) for k, v in sorted(hits.items())}
    out["held_out_predictions"] = n
    out["problems"] = len(probs)
    return out


def openai_nodes(path: str) -> List[dict]:
    """Typed nodes for the OpenAI result families listed in a CONTENTS.md file."""
    t = open(path).read()
    fam = re.findall(r"^\*\*(\d{3})\. (.*?)\*\*(.*?)$", t, flags=re.M)
    return [{"id": f"OAI-{n}", "title": ti.strip(), "types": type_of(ti + " " + d),
             "lean": "(lean/docs" in d} for n, ti, d in fam]


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=1))
