# m-sequence level colourings for Erdős problem 1183

Colour S ⊆ [n] by s(|S|), s(i) = Tr(β α^i), α primitive in GF(2^p), n ≤ 2^p − 2. Both colour classes
have no long arithmetic progressions, which is why these colourings were tried for f(n) = O(n).

**Antichains are bounded (proved).** Let p be prime. A weighted antichain {w_1, …, w_k} with base t is
monochromatic when every α^{t + Σ_{i∈I} w_i} has the same trace. These elements span
α^t · Π_i span{1, α^{w_i}}, and by the theorem of Hou, Leung and Xiang (a field GF(2^p), p prime, has no
intermediate subfield) a product of subspaces of dimensions d_i has dimension at least
min(p, Σ d_i − (k − 1)) = min(p, k + 1). Colour 0 needs the span inside a hyperplane, so k ≤ p − 2.
Colour 1: the differences α^{t + Σ_I w}(1 + α^{w_j}) over I ∌ j have trace 0 and span a product of k − 1
such subspaces, so k ≤ p − 1. Hence Boolean sublattices have at most 2^{p−1} ≈ n/2 members.

**Chains with three ranks are not (proved, and computed).** If α^e = 1 + α^d (d, e any Zech pair), the ranks t + a d + b e
give α^{t}(α^d)^a(1 + α^d)^b ∈ span{α^{t + j d} : 0 ≤ j ≤ a + b}. So when t, t + d, …, t + kd all lie in
colour 0 and t + k·max(d, e) ≤ n, the weighted poset made of k disjoint chains with ranks {0, d, e} is
monochromatic, with 3^k members. For the primitive trinomial x^p + x + 1 (d = 1, e = p) the condition
is a run of k + 1 zeros of the m-sequence, and every period has a run of p − 1 zeros, so k = p − 2 is
reached whenever that run starts below n − p(p − 2): 3^{p−2} = Θ(n^{log₂ 3}) members.

Computed (`triangle.py`, one period, three offsets): p = 5: 27 = 0.84 (n+2); p = 6: 81 = 1.27 (n+2);
p = 7: 243 = 1.90 (n+2), with (d, e) = (2, 5), (1, 6), (1, 7) for the taps x^5+x^2+1, x^6+x+1, x^7+x+1. For p = 8 (GF(256) has subfields) the antichain bound fails
too: a cube of dimension 14, 16384 members, at n = 254 (`mseq.py`).

**Verdict.** Linear-recurrence level colourings fail Question 9.3: the linearity that keeps progressions
short turns every short progression into a triangle of rank sets. An O(n) level colouring would need
colour classes free of long progressions and of these triangles at the same time.
