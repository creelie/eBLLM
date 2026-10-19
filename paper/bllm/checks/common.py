"""Shared helpers for the numerical checks of the BLLM paper."""
import heapq, itertools, math

def entropy(p):
    return -sum(x * math.log(x) for x in p if x > 0)

def huffman_lengths(w, D):
    """D-ary Huffman code lengths for weights w (padding with zero-weight leaves)."""
    n = len(w)
    if n == 1:
        return [0]
    items = [(x, i, None) for i, x in enumerate(w)]
    pad = 0
    while (n + pad - 1) % (D - 1) != 0:
        pad += 1
    for j in range(pad):
        items.append((0.0, n + j, None))
    heap = [(x, k, [i] if i < n else []) for k, (x, i, _) in enumerate(items)]
    heapq.heapify(heap)
    depth = [0] * n
    counter = len(heap)
    while len(heap) > 1:
        tot, members = 0.0, []
        for _ in range(D):
            x, _, m = heapq.heappop(heap)
            tot += x
            members += m
        for i in members:
            depth[i] += 1
        heapq.heappush(heap, (tot, counter, members))
        counter += 1
    return depth

def brute_kraft(p, D, maxlen):
    """Minimum of sum p_i l_i over integer l_i >= 0 with sum D^-l_i <= 1."""
    best = None
    for ls in itertools.product(range(maxlen + 1), repeat=len(p)):
        if sum(D ** (-l) for l in ls) <= 1 + 1e-12:
            v = sum(pi * l for pi, l in zip(p, ls))
            if best is None or v < best - 1e-15:
                best = v
    return best

def brute_schedule(a, eps, theta, rmax):
    """Minimum of sum a_i r_i over integers 1 <= r_i <= rmax with sum eps^r_i <= theta."""
    best = None
    for rs in itertools.product(range(1, rmax + 1), repeat=len(a)):
        if sum(eps ** r for r in rs) <= theta * (1 + 1e-12):
            v = sum(ai * r for ai, r in zip(a, rs))
            if best is None or v < best:
                best = v
    return best
