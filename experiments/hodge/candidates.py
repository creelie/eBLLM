"""Explicit candidate constructions for the five target points, with their invariants and where each one
falls short, as data; written to <run dir>/candidates.md and recorded in the engine's memory (events and
blocks) whether a candidate survives or dies.  Nothing here is a proof; every 'dies' has its reason, every
'open' says what computation decides it.

    EBLLM_RUN_DIR=... PYTHONPATH=src python3 experiments/hodge/candidates.py
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
from ebllm.bllm.memory import Memory  # noqa: E402
from ebllm.bllm import hodge as H  # noqa: E402

OUT = os.environ.get("EBLLM_RUN_DIR", "/mnt/project-files/ai-paper/hodge-attack")

CANDIDATES = [
    dict(id="C1", target="F2.E06", name="Four line bundles on E_0^6 (configuration (a))",
         object="E = convolution of the 32 threefold pieces O_{Z_zeta}[s_zeta] (s = 0 for prod zeta = 1, s = 1 for "
                "prod zeta = -1, twist 0) and the four line bundles L^1[-2], L^2[-1], L^3[0], L^4[1] on A_0 = E_0^6, "
                "E_0 = C/Z[i]",
         invariants=dict(ch="32 (alpha + alphabar) + sum c_m theta^m, polarised, N = 32", hankel_rank=3, r=57,
                         C1=2523, C2=20316, C2_exact=15900, C3=35458, euler=-17665, restricted_euler=-12737,
                         safe_classes=0, closed_chains="none through a threefold piece: with four line bundles a "
                         "closed chain has shape B, which needs a threefold at shift t+4 of twist >= 4 and one at "
                         "t+2 of twist <= the least exponent (t = -2 here)"),
         achieves="the configuration family of the paper that counting does not exclude",
         short="every threefold piece lies on no closed chain, so its diagonal class ev_{F_a}(v), of rank 3 on T D, "
               "cannot be cancelled and ev_E(v) != 0; more generally every convolution with at most five line "
               "bundles fails, for any twists, because the Chern character forces equally many threefold pieces "
               "at even and at odd shifts while the chains reach only one parity (C1_chains.md, Theorem 6)",
         status="dies", decided_by="C1_chains.md Theorem 6 (by hand; checks e06_chern.py, e06_ev.py, "
                                   "e06_chainclass.py)"),
    dict(id="C8", target="F2.E06", name="Six or more line bundles on E_0^6 (rest of configuration (a))",
         object="convolutions of the threefold pieces O_{Z_zeta} L^k [s] (each Z_zeta at most once, any twists) "
                "with at least six line bundles L^l [t], Ext^1 = 0 between threefold pieces at one shift",
         invariants=dict(chern="sum eps = 0 and sum eps k = 0 over the threefold pieces (eps = (-1)^shift)",
                         searched="every configuration of at most eight line bundles whose shifts form an interval "
                                  "(4: 75, 5: 541, 6: 4683, 7: 47293, 8: 545835)",
                         live_chains="both parities: none up to seven line bundles, 31 shift patterns at eight",
                         discriminants="every weighted product polarisation of Weil type, so every discriminant "
                                       "class (e06_weights.py)"),
         achieves="the part of configuration (a) that Theorem 6 of C1_chains.md leaves",
         short="with at most seven line bundles it fails for every shift and twist and at every discriminant "
               "(C8_chains.md, Theorem 9 and the weighted polarisations): a "
               "zero up step next to a nonzero one carries no y (Lemma 7), a chain fills an interval of shifts "
               "(Lemma 8), and the live chains of a piece with six or seven line bundles reach one parity; with "
               "eight, 31 patterns such as the Koszul tower reach both parities, every Maurer-Cartan component "
               "has two paths and the combinatorics is silent; by locality (Theorem 10) a threefold piece near "
               "whose generic point E is a shifted line bundle needs an ample divisor where that stops",
         status="open", decided_by="the products along the runs in the 31 eight-line-bundle patterns (the rank of "
                                   "y -> D(y)_TT against ev_T(TD)), and several Koszul squares from twelve line "
                                   "bundles on"),
    dict(id="C2", target="F2.E06", name="One threefold at several twists (configuration (c))",
         object="the 32 pieces at twist 0 with Z_111 repeated at (twist, shift) = (1,-1), (1,0), (2,1), (2,2) and "
                "L^1, L^2, L^3 at shift 0",
         invariants=dict(polarised=True, N=32, C1=2786, C2=15417, C3=24054, safe_classes=0,
                         closed_chains={2: 2, 3: 4, 4: 2, 5: 10}),
         achieves="polarised shape with cancelling pairs; chains of length two to five exist, so products m_2..m_5 act",
         short="the degree-one component between the two copies O_Z L^1[-1] -> O_Z L^1[0] lies in Hom(O_Z L, O_Z L) "
               "= C id: if nonzero the pair is a contractible summand and the configuration reduces to one with "
               "fewer pieces; if zero the pair stays and the chains of length three to five act on the diagonal "
               "classes through products m_3, ..., m_5 whose ranks are not computed; counting gives no bound "
               "(safe classes 0)",
         status="open", decided_by="the ranks of m_3..m_5 along the listed chains; the hand computation is part F2.3 "
                                   "of the Full Hodge plan"),
    dict(id="C3", target="F2.E06", name="Two threefolds meeting along an abelian surface at the same shift (d)",
         object="the 32 pieces at twist 0, plus O_{Z_11-}[0] and O_{Z_11-}[1] (cancelling pair, one at the shift of "
                "Z_111), L^1, L^2, L^3 at shift 0; Z_111 and Z_11- share two coordinates, d = 2, D = 4",
         invariants=dict(polarised=True, N=32, C1=1586, C2=13329, C3=21944, safe_classes=5325,
                         closed_chains={2: 6, 3: 8, 4: 6}),
         achieves="the degree-(1,1) two-chain through H^0(W, O_W) of lem:cmmeet(iii) exists and can act on the "
                  "diagonal classes",
         short="5325 isolated degree-two classes survive every differential (blocks hit by nothing and mapping to "
               "nothing), so dim Ext^2 >= 5325 > 57 in all six polarised placements of the window",
         status="dies", decided_by="e06_count.py family (d), e06_chains.py"),
    dict(id="C4", target="F2.lift", name="The Weil family through A_0 = E_0^6 with the product object",
         object="the polarised abelian scheme A -> D_{3,3} (Weil type for K = Q(i), n = 3, trivial discriminant) "
                "through the CM point A_0 = E_0^6; the flat class alpha + alphabar; at A_0 the product object "
                "P = pr_1^* E_1 (x) pr_2^* E_2 of thm:product (Hankel rank 3, ch of polarised shape)",
         invariants=dict(dim_family=9, flat_class="alpha + alphabar", r=57, T_D="9-dimensional, Hom(T, T^sigma)",
                         markman="the Weil classes are algebraic on every member by Markman (trivial discriminant)"),
         achieves="every hypothesis of thm:propagation except the one it is about: CM point, flat class, polarised "
                  "shape, Hankel rank 3",
         short="dim Ext^2(P, P) at A_0 must equal 57; P is a convolution of the pieces of C1, which fails with at "
               "most seven line bundles, so this is C8 (eight or more) or C2; "
               "and the member has trivial discriminant, where the Weil classes are algebraic already (Markman), "
               "so even a success would reprove a known case, as H8 rem:convolutionsopen says; the nontrivial "
               "discriminants need the other hermitian polarisations of A_0 (BB26 ssec:f2stop1), same pieces, "
               "different theta",
         status="open", decided_by="C8 and C2, then the same computation at a non-trivial discriminant polarisation"),
    dict(id="C5", target="F2.link", name="The link class at a CM point of the sixfold",
         object="X a Mumford fourfold with cubic field F, K = F(sqrt -d) containing no imaginary quadratic field, "
                "Z_K the Weil sixfold of thm:link, c a CM point of the family C of Z_K; xi in Hom_Hdg(T_X(-1), T_Z) "
                "in H^4(X x X x Z_c); candidate cycle: the graph of the CM decomposition T_Z = (+) T_Z[chi] "
                "composed with the Mumford projector of X",
         invariants=dict(kunneth="H^1(X) (x) H^1(X) (x) H^2(Z_K), Hom(X, Z_K) = 0",
                         cm_point="Hodge group of Z_c is a torus; the Hodge classes of Z_c x Z_c are absolute Hodge "
                                  "(Deligne) and algebraic on CM abelian varieties only conditionally"),
         achieves="at c the class xi_c is absolute Hodge; the CM projectors are Hodge classes on Z_c x Z_c",
         short="algebraicity of the CM projectors on Z_c x Z_c is the Hodge conjecture for a CM abelian variety, "
               "open in dimension 6 beyond the Weil-type and split cases; and xi_c itself mixes H^1(X) with "
               "H^2(Z_c), which no cycle on X x Z_c supplies because Hom(X, Z_c) = 0 (the correspondence would be a "
               "homomorphism); so the candidate reduces to an open case of (F2) for CM varieties",
         status="dies as a construction, survives as a reduction", decided_by="BB26 thm:link, ssec:f2stop2"),
    dict(id="C6", target="F3.cubic", name="Correspondences on S_lambda from moduli of sheaves and isogenies",
         object="S = S_lambda (Picard 13, T rank 9, End_Hdg(T) = F cubic); candidates: (i) Gamma_v = the universal "
                "sheaf class on S x M_v(S) composed back, v a Mukai vector with v^2 = 0 (Fourier-Mukai partner M_v "
                "a K3 surface); (ii) the Buskin cycle of any rational Hodge isometry T(S) -> T(S'); (iii) the graph "
                "of a dominant rational self-map of degree n; (iv) sums of such",
         invariants=dict(action="(i), (ii) act on T as Hodge isometries, (iii) as a similarity of multiplier n; "
                         "any f in F acting isometrically has f^2 = 1, any similarity has f^2 = n with f in F, and "
                         "Q(f) would be quadratic inside a cubic field, so f in Q; (iv) sums stay in Q"),
         achieves="every known algebraic correspondence on T(S_lambda) in closed form; they generate Q",
         short="they generate exactly Q, by the parity of [F : Q] (prop:structure(v)); a generator of F needs a "
               "component with p_g >= 2 and transcendental rank >= 18 (prop:structure(iv)), i.e. a correspondence "
               "through a surface of general type or through an abelian variety (the Kuga-Satake class, open); "
               "no such component is constructed",
         status="dies", decided_by="prop:structure(ii),(iv),(v); recomputed here: f^2 = n in a cubic field forces f in Q"),
    dict(id="C7", target="F3.sqrt", name="Chains for sqrt 10 through symplectic quotients of order 2 and 5",
         object="S' a K3 surface with a symplectic automorphism sigma of order 5 and S a K3 surface with a "
                "symplectic involution iota with S'/sigma and S/iota the same K3 surface Y (resolved); chain "
                "S -> Y <- S' of multiplier 2/5 = 10 mod squares; the start needs e = sqrt 10 in End_Hdg(T(S)) and "
                "a Hodge isometry T(S')_Q = T(S)_Q to close the chain at S",
         invariants=dict(coinvariant_rank="Omega_{Z/5} has rank 16, Omega_{Z/2} rank 8",
                         moduli="Z/5-symplectic K3s: 4-dimensional, rho >= 17, rank T <= 6",
                         rm_locus="RM by Q(sqrt 10) with rank T = 2m has an (m - 2)-dimensional locus (van Geemen); "
                                  "rank T <= 6 gives m <= 3, a locus of dimension <= 1 inside the Z/5 family",
                         closing="T(S')(5) = T(S)(2) as Hodge structures is equivalent to T(S)(10) = T(S), which is "
                                 "the real multiplication e itself: the chain closes only where it already starts"),
         achieves="the multiplier 10 is reached by two symplectic quotients, which is the shape thm:chain needs",
         short="existence of a K3 surface with both a symplectic Z/5 action and RM by Q(sqrt 10) on a transcendental "
               "lattice of rank 6, with the quotient Y also a symplectic Z/2 quotient of an RM surface: a lattice "
               "question (embedding of U(10)-type RM lattices into the Z/5 invariant lattice) not settled here; "
               "Kummer surfaces of RM abelian surfaces give no RM on T because the Asai representation V (x) V^sigma "
               "of Res SL_2 is absolutely irreducible",
         status="dies", decided_by="prop:sqrt10 of the Full Hodge paper: a K3 surface with a symplectic "
                                   "automorphism of order five has transcendental rank at most five, and real "
                                   "multiplication by a real quadratic field needs at least six, so chains of "
                                   "symplectic quotients reach only sqrt 2, sqrt 3, sqrt 6"),
]


def main():
    mem = Memory(os.path.join(OUT, "memory", "hodge.sqlite"))
    lines = ["# Candidate constructions", "",
             "Each candidate is written down with its invariants, what it achieves, where it falls short and what "
             "decides it. Status: open = a computation decides it; dies = excluded with the reason. None is a proof.",
             ""]
    for c in CANDIDATES:
        outcome = "stopped" if c["status"].startswith("open") else "rejected"
        mem.record(["cand." + c["id"], "target." + c["target"]], H.P, outcome,
                   node="H." + c["target"].replace("F3.", "F3p."), statement=c["name"] + ": " + c["short"][:300],
                   reason=json.dumps(dict(status=c["status"], decided_by=c["decided_by"]))[:400],
                   survived=False, round_=0, arm="construction", proposer="explicit-candidate")
        if c["status"].startswith("open"):
            mem.block(c["target"], "H." + c["target"].replace("F3.", "F3p.") + ".candidate." + c["id"],
                      c["decided_by"], c["name"])
        lines += [f"## {c['id']} ({c['target']}): {c['name']}", "", f"**Object.** {c['object']}", "",
                  "**Invariants.**"] + [f"- {k}: {v}" for k, v in c["invariants"].items()] + [
                  "", f"**Achieves.** {c['achieves']}", "", f"**Falls short.** {c['short']}", "",
                  f"**Status.** {c['status']}; decided by: {c['decided_by']}", ""]
    mem.commit()
    open(os.path.join(OUT, "candidates.md"), "w").write("\n".join(lines))
    json.dump(CANDIDATES, open(os.path.join(OUT, "candidates.json"), "w"), indent=1)
    print(len(CANDIDATES), "candidates recorded")


if __name__ == "__main__":
    main()
