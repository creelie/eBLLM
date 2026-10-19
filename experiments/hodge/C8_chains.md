# Convolutions with at most seven line bundles at E_0^6 fail the criterion, at every discriminant

Candidate C8 of the Hodge attack (six or more line bundles, the rest of configuration (a)), part F2.4 of the
Full Hodge plan. This note continues `C1_chains.md`, whose setting, hypotheses (H) and Lemmas 1 to 5 it uses;
Theorem 6 there settles at most five line bundles.

## Lemma 7 (the step that carries y)

Let E meet the criterion, so that D(y) = c(v) for some cochain y of total degree 1, where c(v) is the
first-order Maurer-Cartan defect of delta along v in TD (Lemma 2). Let a -> b -> c be line bundles with
s_b = s_a + 1, s_c = s_a + 2 and lam_a < lam_b < lam_c, and suppose that a -> b -> c is the only sequence
of pieces from a to c whose steps have nonzero Ext groups of the right total degree. If delta_bc = 0 and
delta_ab != 0, then y_bc = 0. Likewise, if delta_ab = 0 and delta_bc != 0, then y_ab = 0.

*Proof.* The component (a, c) of a cochain of total degree 2 lies in Hom(L^{lam_a}, L^{lam_c}) =
H^0(L^{lam_c - lam_a}). c(v) is the sum of the first-order deformations mu_n(delta, ..., delta) of the
products along the paths of nonzero delta; the only path from a to c passes through b -> c, where
delta = 0, so c(v)_{ac} = 0. D(y)_{ac} is the sum over the same paths with y on one step and delta on the
others (a term with y on a loop at a, b or c would also need delta_ac or delta_bc, and delta_ac lies in
Ext^{-1} = 0): it is delta_ab y_bc + y_ab delta_bc = delta_ab y_bc, a product of sections. A_0 is integral and
delta_ab != 0, so y_bc = 0. The second case is the same with the component (a, c) = y_ab delta_bc. []

A closed chain through a threefold piece contributes to D(y)_{TT} only through the step carrying y, which is
its step with delta = 0. So a chain whose zero step falls under Lemma 7 contributes nothing: it is not
**live**. Lemma 2 holds with live chains in place of effective ones.

Lemma 7 already removes the windows of Theorem 6: four line bundles L_1, ..., L_4 at consecutive shifts in
exponent order, with nothing else in their range, have delta_12 delta_23 = delta_23 delta_34 = 0 (Lemma 5),
so the chain needs delta_23 = 0, and then y_23 = 0.

## Lemma 8 (intervals of shifts)

A closed chain climbs only by up steps L^l[s] -> L^{l'}[s+1], and every other step lowers the shift; so the
line bundles of a chain occupy every shift between their least and their greatest. The same holds for the
paths of a Maurer-Cartan component and of a component of D(y). Hence if some shift between two line bundles
of E carries no line bundle, the line bundles on each side form independent pieces: no chain, no
Maurer-Cartan path and no path of D(y) uses both.

## Theorem 9

Under (H), if ch(E) has the polarised shape with N != 0 and E has at most seven line-bundle pieces, then E
does not meet the criterion. This holds for every choice of shifts and of twists of the threefold pieces.

*Proof.* By Lemma 2, with Lemma 7, every threefold piece lies on a live closed chain, and by Lemma 1 there
are threefold pieces of both parities of shift. By Lemma 8 the line bundles split into pieces whose shifts
form intervals, and each live chain lies in one piece. Within one piece, a closed chain is a cycle in the
graph of up steps, down steps (L^l[s] -> L^{l'}[s-5], l' < l) and runs (Lemma 4) on the line bundles; the
threefold pieces of a run of excess b from a line bundle at shift s sit at the shifts s - x for the x
allowed by Lemma 3. A set Z0 of up steps with delta = 0 is admissible when no Maurer-Cartan component
between line bundles two shifts apart is left with the single path a -> b -> c (that product of two
nonzero sections would vanish), and a chain is live when at most one of its up steps lies in Z0 and that
step is not killed by Lemma 7. Run and down steps are taken nonzero and every realisable run is admitted,
which can only add live chains.

`e06_six.py` runs through every configuration of n line bundles whose shifts form an interval (the order of
the exponents and the shifts are all that matter) and every Z0:

| line bundles | configurations | live chains of both parities | of one parity | none |
|---|---|---|---|---|
| 4 | 75 | 0 | 0 | 75 |
| 5 | 541 | 0 | 0 | 541 |
| 6 | 4683 | 0 | 4 | 4679 |
| 7 | 47293 | 0 | 140 | 47153 |

So a piece with at most five line bundles carries no live chain, and a piece with six or seven carries live
chains of one parity only. With at most seven line bundles in all, at most one piece has six or more, and
the live chains reach one parity of shift, against Lemma 1. []

The four configurations with six line bundles and live chains are the "Koszul squares": two line bundles at
each of the two middle shifts, such as L^{l_0}[0], L^{l_1}[1], L^{l_2}[1], L^{l_3}[2], L^{l_4}[2], L^{l_5}[3],
where the Maurer-Cartan components (0, 3) and (1, 5) have two paths each and can cancel, so all four up
steps of a window may be nonzero and y sits on the run.

## Every discriminant

Theorems 6 and 9 hold at every product polarisation of Weil type on A_0. For positive integers h_1, ..., h_6
let theta_h = sum_j (h_j a_j + h_{3+j} b_j) be the class of the product polarisation with weight h_k on the
k-th factor, L_h a line bundle of class theta_h, and replace L by L_h and TD by TD_h, the tangent space of
the Weil family through (A_0, K, theta_h). The class theta_h is K-invariant, so (A_0, K, theta_h) is of Weil
type of signature (3, 3). Its discriminant is that of the unweighted product polarisation times the class
of h_1 ... h_6 modulo norms from K (sums of two squares), so as h varies it runs through every discriminant
class allowed by the signature; h = (1, 1, 1, 1, 1, 3) changes the class. The Weil plane does not depend on
the polarisation.

The proofs use the polarisation in two places only.

* *Lemma 2.* TD_h consists of the K-linear v with h_k v_kl = h_l v_lk, again of dimension 9 with coordinates
  Y_mj = v_{3+m, j}, and ev_Z(v) is the matrix (h_{3+j}/h_m) Y_jm - zeta_m zetabar_j Y_mj. Each pair
  {(m, j), (j, m)} with m != j contributes a nonzero 2 x 2 block, so the rank is at least 3 for every zeta
  (it is 3, 6 or 9 according to the weights).
* *Lemma 1, the part used:* sum_x eps_x = 0. Give dz_j and dzbar_j the weights +e_j and -e_j in Z^3 and dz_{3+j},
  dzbar_{3+j} the weights -e_j and +e_j. Then a_j, b_j and theta_h have weight 0, X_e has weight -2e, and
  the Weil classes have weights +-2(1, 1, 1). The weight-zero part of ch(E) in degree 6 is M_0(0) X_0 plus a
  multiple of theta_h^3 from the line bundles, and it must be a multiple of theta_h^3. The class X_0 =
  prod (a_j + b_j) takes one class from each factor E_0^2, while theta_h^3 contains the term
  6 h_1 h_4 h_2 a_1 b_1 a_2, so X_0 is not a multiple of theta_h^3 and M_0(0) = sum_x eps_x = 0.

Lemmas 3 to 8 use only that L_h restricts to an ample line bundle on every abelian subvariety, and the search
of Theorem 9 uses only the degrees of Lemma 3. Hence: **under (H), a convolution of the Z_zeta (any twists)
with at most seven powers of L_h, whose Chern character is N (alpha + alphabar) plus a polynomial in theta_h
with N != 0, does not meet the criterion, for every h and so for every discriminant.** The thirty-two
threefolds at twist 0 with shifts of the parity of zeta_1 zeta_2 zeta_3 have the polarised shape for every h,
so the shape itself is attainable at every discriminant.

## Eight line bundles: the frontier

With eight line bundles the search leaves 31 configurations (20 up to the duality that reverses shifts and
exponents) whose live chains reach both parities; they are listed in
`e06_six_n8.json`. The typical one is the Koszul tower

    L^{l_0}[0], L^{l_1}[1], L^{l_2}[1], L^{l_3}[2], L^{l_4}[2], L^{l_5}[3], L^{l_6}[3], L^{l_7}[4]

with windows starting at shift 0 (threefold pieces at even shifts) and at shift 1 (odd shifts), every up step
nonzero, the 2 x 2 blocks of delta of rank one, and y on the runs. Lemma 7 does not apply there: each
Maurer-Cartan component between line bundles two shifts apart has two paths. Deciding these configurations
needs the products along the runs (the components of D(y) between a line bundle and a threefold piece, and
the rank of y -> D(y)_{TT} on H^1(Z, N_Z)), which the combinatorics does not see.

With twelve or more line bundles two separate pieces, each a Koszul square, can carry live chains of
opposite parity, so beyond eight the parity argument alone cannot decide anything.

## Theorem 10 (locality)

Let h be any weights, T = Z_zeta one of the thirty-two threefolds and E any object of D^b(A_0), not
necessarily a convolution. Suppose there are an open set U of A_0 meeting T, a line bundle M on T cap U and an
integer s with E|_U = i_* M [s], and that the union of the components of codimension one of T \ U is not an
ample divisor of T (it may be empty). Then E does not deform to first order along some v in TD_h. In
particular, if ch(E) has the polarised shape, E does not meet the criterion.

*Proof.* Suppose E deforms along every v (by Lemma 2 this is what the criterion forces). Restricting a
deformation of E to U gives a deformation of i_* M [s], and a first-order deformation of a shifted sheaf is a
shifted sheaf F_v flat over C[eps]. By Nakayama F_v is locally cyclic, so its Fitting ideal cuts out a closed
subscheme of U_v flat over C[eps] with fibre T cap U (Fitting ideals commute with base change, and that of
i_* M is the ideal of T). So T cap U deforms inside U_v, and the obstruction to this, the restriction of
ev_T(v) to T cap U in H^1(T cap U, N_T), vanishes for every v.

Let S be the divisorial part of T \ U, H the connected component of {x in T : S + x = S} and q: T -> T/H.
Then S = q^{-1}(Sbar) with Sbar ample on T/H (Mumford, Abelian Varieties, Section 6, Application 1), and
H != 0 since S is not ample (H = T if S is empty). Removing from T \ S the rest of T \ U, of codimension
two, keeps H^1(O) injective (local cohomology of O in codimension two vanishes in degree one). Pull back
along an isogeny H x H' -> T (Poincare reducibility), which is injective on cohomology: T \ S becomes
H x U', with U' the complement of an ample divisor of H', so U' is affine and by Kunneth
H^1(H x U', O) = H^1(H, O) (x) O(U'). A class of H^1(T, O) goes to its restriction to H, as a constant.
Hence the kernel of H^1(T, O) -> H^1(T cap U, O) is q^* H^1(T/H, O), the classes that vanish on the
tangent directions of H. With N_T trivial, ev_T(v) restricts to zero exactly when, as an element of
Hom(Wbar, V/W), it kills ubar for every u in Lie H.

That fails. Take u = sum_j u_j w_j != 0 in Lie H, so ubar = sum_j ubar_j wbar_j, an index a with u_a != 0
and b != a, and v with Y = E_ab (the single entry Y_ab = 1). Then
ev_T(v) ubar = (h_{3+a}/h_b) ubar_a f_b - zeta_a zetabar_b ubar_b f_a, which is nonzero because its f_b
coefficient is. []

A divisor of T is ample exactly when its stabiliser is finite. Zero loci of sections of L_h^m restricted to T
are ample; the surfaces in which T meets other threefolds are not, by the next observation.

**Neighbours.** Z_zeta meets Z_zeta' in a surface exactly when zeta' agrees with zeta in two coordinates;
since (zeta'_1 zeta'_2 zeta'_3)^2 = 1, zeta' is then one of the three zeta^(j) obtained by negating the j-th
coordinate, of the opposite sign, and Z_zeta cap Z_zeta^(j) = pr_j^{-1}(C_{zeta_j} cap C_{-zeta_j}), four
translates of the product of the other two curves. A union of such surfaces over a set J of indices is
ample on Z_zeta exactly when J = {1, 2, 3}.

## Corollary 11 (objects carried by the threefolds)

Let E be an object of D^b(A_0) whose cohomology sheaves are H^i(E) = sum_{zeta in S_i} i_* M_zeta, with M_zeta a
line bundle on Z_zeta and the sets S_i pairwise disjoint, and put S = union of the S_i. If ch(E) has the
polarised shape for some theta_h and E meets the criterion, then S is closed under negating any one
coordinate: with zeta it contains zeta^(1), zeta^(2) and zeta^(3). So S is a union of the orbits
{+-zeta_1} x {+-zeta_2} x {+-zeta_3}, of eight threefolds each, four of each sign.

*Proof.* For zeta in S, i in its degree, let U be the complement of the other Z_zeta', zeta' in S. On U only
H^i(E) is nonzero and it is i_* M_zeta, so E|_U = i_* M_zeta [-i]. The divisorial part of Z_zeta \ U is the
union of the surfaces Z_zeta cap Z_zeta^(j) with zeta^(j) in S, which is ample only when all three neighbours
lie in S. Theorem 10 gives the rest. []

For a convolution, Theorem 10 applies at a threefold piece T wherever the other pieces cancel to leave a
shifted line bundle on T: it says that the locus of T where this stops must contain an ample divisor of T,
which can come from zero loci of components of delta restricted to T, or from all three neighbours of T among
the threefold pieces. Whether the pieces of the eight-line-bundle patterns cancel near T depends on delta, so
Theorem 10 does not decide those patterns; it removes every member in which, at some threefold piece T, the
other pieces cancel to a shifted line bundle on T outside a subset of T whose divisorial part is not ample.

## What C8 now asks

* Eight to eleven line bundles: one piece with at least eight line bundles must carry both parities; with
  eight the 31 configurations above.
* Twelve or more: also two or more pieces.
* In every case the decision is the rank of y -> (D(y)_{TT})_T against ev_T(TD), with the Fourier and twist
  conditions of Lemma 1 on the threefolds present, and at each threefold piece where E is a shifted line
  bundle near the generic point, an ample divisor of T where it stops being one (Theorem 10).
* Everything above holds at every discriminant (weights h).

## Checks

* `e06_six.py N` for N = 4 to 8; log in `e06_six.log`. The run table
  it prints (threefold shifts allowed in a run of each excess) agrees with Lemma 4: excess 1 puts the
  threefold at s + 1, the decreasing run of excess 3 puts its two threefolds at s + 1 and s - 1.
* It reproduces Theorem 6: no configuration with four or five line bundles keeps a live chain.
* `e06_weights.py`: for nine weight vectors, with h_1 ... h_6 in {1, 2, 3, 4, 6, 7, 27, 30030} (the values
  3, 6, 7, 27 and 30030 are not sums of two squares, so these change the discriminant class), it checks that
  TD_h kills theta_h, that ev_Z has rank at least 3 on TD_h and is nonzero on every tested direction of Wbar
  for all thirty-two threefolds, exactly over Q(i), and that every random configuration with the polarised
  shape for theta_h has sum eps = 0 (exact Chern characters); it also checks the neighbours of each
  threefold. Log in `e06_weights.log`.
