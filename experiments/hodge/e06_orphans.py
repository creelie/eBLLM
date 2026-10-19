"""Closed chains through threefold pieces at A_0 = E_0^6, and the threefold pieces on none of them.

Setting of Proposition prop:separated of Bhattacharjee-Bhattacharya 2026, without the bound on the number
of line bundles: pieces O_{Z_a} (x) L^{k_a} [s_a] with pairwise distinct threefolds and L^{l_b} [t_b] with
pairwise distinct exponents, Ext^1 = 0 between threefold pieces at one shift.  A step a -> b of a chain
is a nonzero group Ext^{1 + s_a - s_b}(F_a, F_b); a closed chain has distinct pieces.  A threefold piece on
no closed chain keeps its diagonal component of ev_E(v), and the criterion fails (the orphan lemma).

This script checks the classification of the closed chains through threefold pieces:

  (A) a closed chain through a threefold piece visits at least four line bundles;
  (B) with exactly four it is L^{l1}[t] -> L^{l2}[t+1] -> L^{l3}[t+2] -> L^{l4}[t+3] -> O_Z L^{k}[t+4]
      -> O_{Z'} L^{k'}[t+2] -> L^{l1}[t] with k' <= l1 < l2 < l3 < l4 <= k;
  (C) if all threefold pieces have one twist, at least five;
  (D) with one twist and exactly five, the five line bundles sit at consecutive shifts t, ..., t+4 in the
      order of their exponents and the chain has one threefold piece, at shift t+2 (twist at most every
      exponent) or t+5 (twist at least every exponent);

by enumerating closed chains in a superset graph: each of the 32 threefolds Z_zeta at every shift of the
parity of zeta_1 zeta_2 zeta_3 in a window (and at the twists given), no step between two copies of one
sheaf, and a chain using two copies of one sheaf discarded.  The search runs from each threefold node and
is pruned by the excess sum (k_i - 1) so far against the line bundles still able to start an edge of
degree zero, the only steps of negative excess.

    python3 e06_orphans.py out.json
"""
import itertools, json, sys
from e06_count import ZETAS, Piece, ext_dims, zsign


def step_degrees(p, q):
    """Ext degrees k with Ext^k(p, q) != 0 (upper bounds for threefolds meeting along curves or surfaces,
    so the edge set is a superset of the true one)."""
    dims, _ = ext_dims(p, q)
    return {k for k, v in dims.items() if v}


def same_sheaf(p, q):
    """Same line bundle, or same threefold (at any twist: the threefolds are pairwise distinct)."""
    if p.kind != q.kind:
        return False
    return p.twist == q.twist if p.kind == "L" else p.zeta == q.zeta


_ZCACHE = {}


def zgraph(twists, shift_window, eps):
    key = (tuple(twists), tuple(shift_window), eps)
    if key not in _ZCACHE:
        zs = [Piece("Z", z, k, s) for z in ZETAS for k in twists for s in shift_window
              if (-1) ** (s % 2) == eps * zsign(z)]
        zadj = [[] for _ in zs]
        for a, p in enumerate(zs):
            for b, q in enumerate(zs):
                if a != b and not same_sheaf(p, q):
                    k = 1 + p.shift - q.shift
                    if k in step_degrees(p, q):
                        zadj[a].append((b, k))
        _ZCACHE[key] = (zs, zadj)
    return _ZCACHE[key]


def build(lines, twists, shift_window, eps=1):
    """Superset graph: line bundles (exponent, shift), and every Z_zeta at every twist in `twists` and every
    shift in `shift_window` with (-1)^s = eps * sign(zeta)."""
    zs, zadj = zgraph(twists, shift_window, eps)
    Ls = [Piece("L", None, l, t) for l, t in lines]
    nodes = Ls + zs
    nL = len(Ls)
    adj = [[] for _ in nodes]
    for a, p in enumerate(Ls):
        for b, q in enumerate(nodes):
            if b == a or same_sheaf(p, q):
                continue
            k = 1 + p.shift - q.shift
            if k in step_degrees(p, q):
                adj[a].append((b, k))
    for a, p in enumerate(zs):
        for b, q in enumerate(Ls):
            k = 1 + p.shift - q.shift
            if k in step_degrees(p, q):
                adj[nL + a].append((b, k))
        adj[nL + a].extend((nL + b, k) for b, k in zadj[a])
    return nodes, adj


def exit_cost(nodes, b, path, a0):
    """A lower bound for the excess (degree - 1) still needed to leave the run through the threefold piece b
    for a line bundle still available (unvisited, or a0): 2 if one has exponent >= twist(b); 4 if the run can
    first drop to a smaller twist; else 5 (an edge of degree 6)."""
    if nodes[b].kind != "Z":
        return 0
    k = nodes[b].twist
    avail = [x for x, p in enumerate(nodes) if p.kind == "L" and (x == a0 or (x not in path and x > a0))]
    if any(nodes[x].twist >= k for x in avail):
        return 2
    # or first down to a smaller twist (an internal edge of degree >= 3), then out with degree 3
    low = min(p.twist for p in nodes if p.kind == "Z")
    if low < k and any(nodes[x].twist >= low for x in avail):
        return 4
    return 5


def chains_through(nodes, adj, a0, max_len=12):
    """Closed chains of distinct sheaves through the line bundle a0 that visit no line bundle of smaller
    index (so each chain through a line bundle is found exactly once over all a0)."""
    nL = sum(1 for p in nodes if p.kind == "L")
    out = []
    # stack: (current, path, excess, line bundles used as sources)
    stack = [(a0, [a0], 0, 0)]
    while stack:
        cur, path, exc, used = stack.pop()
        src_is_L = nodes[cur].kind == "L"
        used2 = used + (1 if src_is_L else 0)
        for b, k in adj[cur]:
            e2 = exc + k - 1
            if b == a0:
                if e2 == 0 and len(path) >= 2:
                    out.append(list(path))
                continue
            if len(path) >= max_len:
                continue
            if any(same_sheaf(nodes[b], nodes[x]) for x in path):
                continue
            if nodes[b].kind == "L" and b < a0:
                continue
            # line bundles that can still start an edge of degree 0: unused ones (b if it is one, others);
            # from a threefold the chain still has to leave for a line bundle, an edge of degree >= 3
            remaining = nL - used2
            if e2 + exit_cost(nodes, b, path, a0) > remaining:
                continue
            stack.append((b, path + [b], e2, used2))
    return out


def classify(nodes, chain):
    pcs = [nodes[x] for x in chain]
    Ls = [p for p in pcs if p.kind == "L"]
    Zs = [p for p in pcs if p.kind == "Z"]
    return len(Ls), Ls, Zs


def is_special4(nodes, chain):
    """Shape (B): rotate so that it starts at the line bundle of least exponent."""
    pcs = [nodes[x] for x in chain]
    i = min(range(len(pcs)), key=lambda j: (pcs[j].kind != "L", pcs[j].twist if pcs[j].kind == "L" else 0))
    pcs = pcs[i:] + pcs[:i]
    if [p.kind for p in pcs] != ["L"] * 4 + ["Z", "Z"]:
        return False
    t = pcs[0].shift
    ls = [p.twist for p in pcs[:4]]
    ok = [p.shift for p in pcs] == [t, t + 1, t + 2, t + 3, t + 4, t + 2]
    return ok and ls == sorted(ls) and len(set(ls)) == 4 and pcs[5].twist <= ls[0] and ls[3] <= pcs[4].twist


def is_shape5(nodes, chain):
    pcs = [nodes[x] for x in chain]
    Ls = sorted((p for p in pcs if p.kind == "L"), key=lambda p: p.twist)
    Zs = [p for p in pcs if p.kind == "Z"]
    if len(Ls) != 5 or len(Zs) != 1:
        return False
    t = Ls[0].shift
    if [p.shift for p in Ls] != [t + j for j in range(5)]:
        return False
    z = Zs[0]
    return (z.shift == t + 2 and z.twist <= Ls[0].twist) or (z.shift == t + 5 and z.twist >= Ls[4].twist)


def survey(lines, twists, window, eps):
    nodes, adj = build(lines, twists, window, eps)
    res = dict(chains=0, min_lines=None, shapes=set(), onchain_shifts=set(), onchain_signs=set(), bad=[])
    for a0, p in enumerate(nodes):
        if p.kind != "L":
            continue
        for ch in chains_through(nodes, adj, a0):
            nl, Ls, Zs = classify(nodes, ch)
            if not Zs:
                continue
            res["chains"] += 1
            res["min_lines"] = nl if res["min_lines"] is None else min(res["min_lines"], nl)
            for z in Zs:
                res["onchain_shifts"].add(z.shift)
                res["onchain_signs"].add((-1) ** (z.shift % 2))
            if nl <= 3:
                res["bad"].append(("A", [repr(nodes[x]) for x in ch]))
            elif nl == 4:
                if len(twists) == 1 or not is_special4(nodes, ch):
                    res["bad"].append(("B/C", [repr(nodes[x]) for x in ch]))
            elif nl == 5 and len(twists) == 1 and not is_shape5(nodes, ch):
                res["bad"].append(("D", [repr(nodes[x]) for x in ch]))
    return res


def _job(args):
    lines, twists, eps = args
    r = survey(lines, twists, range(-4, 10), eps)
    return lines, twists, eps, r["chains"], sorted(r["onchain_shifts"]), sorted(r["onchain_signs"]), r["bad"][:3]


def configs(nl, exps, twists):
    """Line bundles with distinct exponents from `exps`, least shift 0, shifts in 0..5."""
    for ls in itertools.combinations(exps, nl):
        for ts in itertools.product(range(0, 6), repeat=nl):
            if min(ts) == 0:
                for eps in (1, -1):
                    yield list(zip(ls, ts)), twists, eps


def main():
    from multiprocessing import Pool
    out = {}
    plan = [(3, range(-2, 4), (0,)), (4, range(-2, 4), (0,)), (5, range(-2, 4), (0,)),
            (4, range(0, 5), (0, 4))]
    with Pool(4) as pool:
        for nl, exps, twists in plan:
            tot = dict(configs=0, with_chain=0, chains=0, bad=0, mixed_sign=0, bad_examples=[], examples=[])
            for lines, tw, eps, nch, shifts, signs, bad in pool.imap_unordered(_job, configs(nl, exps, twists), 8):
                tot["configs"] += 1
                if nch:
                    tot["with_chain"] += 1
                    tot["chains"] += nch
                    if len(signs) > 1:
                        tot["mixed_sign"] += 1
                    if len(tot["examples"]) < 5:
                        tot["examples"].append(dict(lines=lines, eps=eps, shifts=shifts))
                if bad:
                    tot["bad"] += 1
                    if len(tot["bad_examples"]) < 5:
                        tot["bad_examples"].append(dict(lines=lines, eps=eps, bad=bad))
            name = f"{nl} line bundles, exponents {exps.start}..{exps.stop - 1}, twists {twists}"
            print(name, {k: v for k, v in tot.items() if k not in ("examples", "bad_examples")}, flush=True)
            out[name] = tot
            if len(sys.argv) > 1:
                json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
