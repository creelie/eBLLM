"""The Kappa generator of Section 4: well-typed operator words up to length K.

An operator has an input type and an output type; a word o_m o ... o o_1 is well typed when each
output type matches the next input type.  Lemma 4.1 (finite coverage) is the count
|W_K| <= sum_{m <= K} |O|^m, which `count_raw_words` gives exactly.  Scoring is supplied by the
caller: the generator only enumerates, and a word is adopted only with positive gain and a
passing cross-module check, as in the paper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Operator:
    name: str
    src: str
    dst: str


def words(ops: Sequence[Operator], K: int, start: Optional[str] = None) -> Iterator[Tuple[Operator, ...]]:
    """All well-typed words of length 1..K, starting from type `start` if given."""
    frontier: List[Tuple[Operator, ...]] = [(o,) for o in ops if start is None or o.src == start]
    for m in range(1, K + 1):
        nxt = []
        for w in frontier:
            yield w
            if m < K:
                nxt.extend(w + (o,) for o in ops if o.src == w[-1].dst)
        frontier = nxt


def count_raw_words(n_ops: int, K: int) -> int:
    return sum(n_ops ** m for m in range(K + 1))


def kappa_select(ops, K, gain: Callable[[tuple], float], cmv: Callable[[tuple], bool], start=None):
    """argmax of the gain over well-typed words, adopted only if gain > 0 and cmv(word)."""
    best = None
    for w in words(ops, K, start):
        g = gain(w)
        if best is None or g > best[0]:
            best = (g, w)
    if best is None or best[0] <= 0 or not cmv(best[1]):
        return None
    return best[1]
