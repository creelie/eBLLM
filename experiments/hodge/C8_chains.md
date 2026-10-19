# Convolutions with at most seven line bundles, and objects supported on the Weil threefolds, fail the criterion at E_0^6, at every discriminant

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

Corollary 14 below supersedes this: such an S cannot meet the criterion at all.

For a convolution, Theorem 10 applies at a threefold piece T wherever the other pieces cancel to leave a
shifted line bundle on T: it says that the locus of T where this stops must contain an ample divisor of T,
which can come from zero loci of components of delta restricted to T, or from all three neighbours of T among
the threefold pieces. Whether the pieces of the eight-line-bundle patterns cancel near T depends on delta, so
Theorem 10 does not decide those patterns; it removes every member in which, at some threefold piece T, the
other pieces cancel to a shifted line bundle on T outside a subset of T whose divisorial part is not ample.

## Theorem 12 (two threefolds meeting in a surface)

Fix weights h, a zeta and an index j, let k, l be the other two indices, and put T = Z_zeta,
T' = Z_{zeta^(j)} and S = T cap T' = P_j x C_{zeta_k} x C_{zeta_l}, where P_j = C_{zeta_j} cap C_{-zeta_j} is
four points. For y in C_{zeta_k} x C_{zeta_l} put Gamma_y = C_{zeta_j} x {y}, a curve in T, and
Gamma'_y = C_{-zeta_j} x {y}, a curve in T'. Both meet S in the same four points P_j x {y}.

Let E be an object of D^b(A_0), and U an open set containing Gamma_y and Gamma'_y for some y, with
Supp E cap U contained in T cup T'. If E deforms to first order along every v in TD_h, then E has
multiplicity zero along T and along T'.

The multiplicity along T is the alternating sum of the lengths of the cohomology sheaves of E at the generic
point of T. It is defined here because Supp E has codimension three near that point. T' may be missing from
Supp E altogether; then its multiplicity is zero and S plays no part.

*Proof.* Write mu and mu' for the two multiplicities and Z = Supp E cap U.

*Step 1: semiregularity with supports.* Buchweitz and Flenner (Compositio Math. 137 (2003)) define a
semiregularity map sigma from Ext^2(E, E) to H^4(Omega^2), by the trace of the composite with At(E)^2/2. They
show that it sends the obstruction ob(v) to c kappa(v) _| ch_3(E), with c a nonzero constant. On U, E is
supported on Z. There the trace of an endomorphism of E lies in cohomology with supports in Z, and the same
proof gives sigma(ob(v)) = c kappa(v) _| ch_3^Z(E) in H^4_Z(U, Omega^2). Here ch_3^Z(E) in H^3_Z(U, Omega^3)
is the localised Chern character. Z has codimension three, so by Angeniol and Lejeune-Jalabert (Calcul
differentiel et classes caracteristiques en geometrie algebrique, 1989) ch_3^Z(E) is c_0 times the
fundamental class of the cycle of E. In H^3_{T cup T'}(U, Omega^3) that class is c_0 (mu [T] + mu' [T']).
The criterion gives ob(v) = 0 (Lemma 2 of `C1_chains.md`), and therefore

    mu kappa(v) _| [T] + mu' kappa(v) _| [T'] = 0   in H^4_{T cup T'}(U, Omega^2).

*Step 2: Mayer-Vietoris.* The sequence H^4_S(U, F) -> H^4_T(U, F) + H^4_{T'}(U, F) -> H^4_{T cup T'}(U, F)
for cohomology with supports is exact. So there is a class s in H^4_S(U, Omega^2) whose image in H^4_T is
mu kappa(v) _| [T] and whose image in H^4_{T'} is -mu' kappa(v) _| [T'].

T and T' are smooth of codimension three and S is smooth of codimension four. So the sheaves H^q_T(O) vanish
for q != 3 and H^q_S(O) vanish for q != 4. This gives H^4_T(U, F) = H^1(U, H^3_T F). Since S lies in T,
Gamma_S = Gamma_S Gamma_T, so H^4_S(U, F) = H^1_S(U, H^3_T F), and the map to H^4_T is the forgetful map
H^1_S -> H^1. The same holds for T'.

*Step 3: coordinates.* By check (B) the six covectors

    a = f_j(zeta),  b = f_j(zeta^(j)),  n_k = f_k(zeta),  n_l = f_l(zeta),  r_k = f_k(-zeta),  r_l = f_l(-zeta)

form a basis of Vdual, so they are linear coordinates near every point. In them, locally, T = {a = n_k = n_l = 0},
T' = {b = n_k = n_l = 0} and S = {a = b = n_k = n_l = 0}, and r_k, r_l are coordinates along S. Omega^2 is
O (x) wedge^2 Vdual, with the constant basis of wedges of two of these covectors. Near a point of S the
section s has a unique Cech expansion

    s = sum c_{alpha beta gamma delta, w}(r) [a^-alpha b^-beta n_k^-gamma n_l^-delta] (x) w,

with all exponents at least 1, w running over the basis 2-forms, and the c functions of r_k, r_l. As a
section of H^1_S(H^3_T) it is sum c [a^-alpha n_k^-gamma n_l^-delta] (x) b^-beta (x) w, with poles along
S = {b = 0} inside T. As a section of H^1_S(H^3_{T'}) it is sum c [b^-beta n_k^-gamma n_l^-delta] (x)
a^-alpha (x) w, with poles along S = {a = 0} inside T'.

*Step 4: the socle.* Put B = Z_{-zeta}. By (B), W(T) + W(B) = V, so T x B -> A_0 is an isogeny. The
coordinates along T are b, r_k, r_l, which vanish on W(B), and those along B are a, n_k, n_l. Through the
isogeny, H^3_T(O) = O_T (x) H^3_0(O_B). The Grothendieck residue on H^3_0(O_B) against da ^ dn_k ^ dn_l
takes the coefficient of [a^-1 n_k^-1 n_l^-1]. It gives an O_T-linear map
rho_T: H^3_T(Omega^2) -> O_T (x) wedge^2 Vdual.

The same construction with B' = Z_{-zeta^(j)} gives rho_{T'}. The coordinates along T' are a, r_k, r_l and
those along B' are b, n_k, n_l, and rho_{T'} takes the coefficient of [b^-1 n_k^-1 n_l^-1].

*Step 5: the two sides.* kappa(v) is the class of the constant vector field with (0,1)-form coefficients v,
and [T] = [1/(a n_k n_l)] da ^ dn_k ^ dn_l. Hence

    kappa(v) _| [T] = [1/(a n_k n_l)] (x) ( <da, v> dn_k ^ dn_l - <dn_k, v> da ^ dn_l + <dn_l, v> da ^ dn_k ),

where <f, v> is the (0,1)-form wbar -> f(v(wbar)). The da ^ dn_l component is -[1/(a n_k n_l)] <dn_k, v>.
On Gamma_y, whose direction is w_j, the class of <dn_k, v> is the one whose value on wbar_j is
f_k(zeta)(v(wbar_j)) = M_kj(v). That is the (k, j) entry of ev_T(v) (section "Every discriminant").

On T',

    kappa(v) _| [T'] = [1/(b n_k n_l)] (x) ( <db, v> dn_k ^ dn_l - <dn_k, v> db ^ dn_l + <dn_l, v> db ^ dn_k )

has no da ^ dn_l component. In terms of the decomposition
wedge^2 Vdual = wedge^2 N_{T'}dual + N_{T'}dual (x) W_{B'}perp + wedge^2 W_{B'}perp, the form a ^ n_l lies in
the middle summand, because a is in W_{B'}perp and n_l in N_{T'}dual. kappa(v) _| [T'] never reaches that
summand.

*Step 6: residues.* In the two identities of Step 2, take the da ^ dn_l components. Apply rho_T and
rho_{T'}, and restrict to Gamma_y and Gamma'_y. On a curve Gamma, the forgetful map
H^1_{points}(Gamma, O) -> H^1(Gamma, O), followed by Serre duality against an invariant differential omega, is
2 pi i times the sum of the residues of g omega. On Gamma_y take omega = db. Near each p in P_j x {y} the
section from Step 3 is sum_beta c_{1 beta 1 1, a^n_l}(p) b^-beta, with residue c_{1111, a^n_l}(p). On Gamma'_y
take omega = da. The residue there is c_{1111, a^n_l}(p) at the same four points. Put
R = sum_p c_{1111, a^n_l}(p).

On the T' side the component is -mu' times the da ^ dn_l component of kappa(v) _| [T'], which is zero, so
R = 0. On the T side the component is -mu times the class phi with value M_kj(v) on wbar_j, so
2 pi i R = -mu M_kj(v) b(w_j) int_Gamma dtbar ^ dt, with b(w_j) = -2 zeta_j != 0 (check (B)).

Hence mu M_kj(v) = 0 for every v. At the v whose only nonzero coordinate is Y_jk = 1, M_kj = h_{3+j}/h_k != 0
(check (A)), so mu = 0. The hypotheses are symmetric in T and T', so the same argument with zeta^(j) in place
of zeta gives mu' = 0. []

The proof uses a single off-diagonal entry of one column of ev_T. So it holds for every weight vector h,
whatever the rank of ev_T on TD_h, and hence at every discriminant.

## Theorem 13 (where the rest of the support must go)

Let h be any weights and E an object of D^b(A_0) that deforms to first order along every v in TD_h. Suppose
that Supp E has codimension three near the generic point of T = Z_zeta and that E has nonzero multiplicity
along T. Then for each j in {1, 2, 3}, Supp E has an irreducible component R_j with these properties:

* dim R_j >= 3;
* R_j is none of the thirty-two threefolds, and is not contained in T cup Z_{zeta^(j)};
* R_j meets Gamma_y cup Gamma'_y for every y in C_{zeta_k} x C_{zeta_l}.

In particular R_j cap (T cup Z_{zeta^(j)}) contains a surface that maps onto C_{zeta_k} x C_{zeta_l}.

*Proof.* Let W be the union of the components of Supp E that are not contained in T cup T',
T' = Z_{zeta^(j)}. Suppose W missed Gamma_y cup Gamma'_y for some y. Then U = A_0 \ W satisfies the
hypotheses of Theorem 12, and the multiplicity along T would be zero. So W meets Gamma_y cup Gamma'_y for
every y.

The projection of T cup T' onto C_{zeta_k} x C_{zeta_l} is proper. The image of the closed set
W cap (T cup T') is therefore closed, and it contains every y. So some component of W cap (T cup T') maps
onto the surface and has dimension at least two. Let R_j be a component of W that contains it.

R_j is not contained in T cup T', so R_j cap (T cup T') is a proper closed subset of R_j, and dim R_j >= 3.
By check (C), no threefold other than T and T' meets a general Gamma_y or Gamma'_y. So R_j is none of the
thirty-two threefolds. []

## Corollary 14 (objects supported on the threefolds)

Let E be an object of D^b(A_0) whose support lies in the union of the thirty-two threefolds Z_zeta. Nothing
is assumed about its cohomology sheaves, and components of lower dimension inside the threefolds are
allowed. If E meets the criterion for some weights h, then ch_3(E) = 0. In particular ch(E) is not of the
form N (alpha + alphabar) + (a polynomial in theta_h) with N != 0. So no object supported on the threefolds
meets the criterion with the polarised shape, at any discriminant.

This contains Corollary 11, where the cohomology sheaves were line bundles on distinct threefolds. It also
contains every convolution of threefold pieces alone, with any twists, shifts and differentials, whether or
not (H) holds.

*Proof.* Supp E has codimension three, so ch_i(E) = 0 for i < 3 and ch_3(E) = sum_zeta mu_zeta [Z_zeta], the
class of the three-dimensional part of the cycle of E. Take any zeta with Z_zeta in the support, and any j.
Every component of Supp E lies in some Z_zeta'. So a component not contained in Z_zeta cup Z_{zeta^(j)} lies
in another threefold, and by check (C) it misses the general Gamma_y and Gamma'_y. Theorem 13 then gives
mu_zeta = 0. So ch_3(E) = 0. The polarised shape has degree-six part N (alpha + alphabar) + c_3 theta_h^3;
alpha + alphabar and theta_h^3 have different weights, so this part can vanish only when N = 0. []

## Lemma 15 (the four orbits)

Label each of the thirty-two threefolds x by c(x) = (x_1^2, x_2^2, x_3^2). This is one of (1, 1, 1),
(1, -1, -1), (-1, 1, -1) and (-1, -1, 1). The four labels are the orbits of the three coordinate
negations, with eight threefolds each, four of each sign.

For rational numbers nu_x put w_c(nu) = sum_{c(x) = c} nu_x zsign(x). Suppose the components of
sum_x nu_x [Z_x] of the eight weights -2e, e in {+-1}^3, are those of N (alpha + alphabar). This holds, for
example, when sum_x nu_x [Z_x] is N (alpha + alphabar) modulo theta_h H^4(A_0) and classes of weight zero.
Then w_c(nu) = N/4 for each of the four labels c.

For the eps_x of a convolution with the polarised shape this gives 4 | N. If N != 0, every orbit contains a
threefold piece with eps_x != 0.

*Proof.* [Z_x] = prod_j (a_j + b_j + xbar_j c_j + x_j cbar_j). Its component of weight -2e, e in {+-1}^3, is
X_e = prod_j (c_j if e_j = 1, cbar_j if e_j = -1), times prod_{e_j = 1} xbar_j prod_{e_j = -1} x_j. Since
xbar_j = x_j^3 = x_j x_j^2, that product is zsign(x) prod_{e_j = 1} c(x)_j (check (D)).

By check (E), X_e alone spans the part of H^6(A_0) of weight -2e, and theta_h X_e = 0. So X_e is primitive.
Primitive classes meet theta_h H^4(A_0) only in zero (Lefschetz decomposition), so theta_h H^4(A_0) has no
component of these weights, and the hypothesis is the same in either form.

alpha + alphabar = X_{(1,1,1)} + X_{(-1,-1,-1)}. Use prod_j c_j = 1. The equations for e = +-(1, 1, 1) both
read sum_c w_c = N, and those for the other six weights read sum_c w_c c_j = 0, for j = 1, 2, 3. The 4 x 4
matrix with rows (1, 1, 1, 1) and (c_j)_c is a Hadamard matrix H, with H H^T = 4 I. So
w = H^T (N, 0, 0, 0)/4, that is, w_c = N/4 for every c.

For a convolution, ch_3(E) = sum_x eps_x [Z_x] + l theta_h^3, where the second term comes from the line
bundles and eps_x is the sum of (-1)^shift over the threefold pieces at Z_x. The eps_x are integers, so
N = sum_c w_c = 4 w_c is divisible by 4. []

## Corollary 16 (a smooth complete intersection cannot carry the rest)

Let E be an object of D^b(A_0) with ch(E) = N (alpha + alphabar) + (a polynomial in theta_h), N != 0.
Suppose Supp E lies in Y cup (union of Z_x over x in S), where S is a set of the threefolds and Y is a smooth
complete intersection of dimension d <= 5 of divisors from linear systems |L_h^{m_i}|, m_i >= 1.

1. The multiplicities mu_x of E along the Z_x not contained in Y satisfy w_c(mu) = N/4 for each orbit c. So
   S contains, in each of the four orbits, a threefold not contained in Y along which E has nonzero
   multiplicity.
2. Suppose also that d <= 4 and that Y meets every Z_x in dimension at most one. This is automatic for
   general divisors in base-point-free systems. Then E does not meet the criterion.

*Proof.* By the Riemann-Roch theorem of Baum, Fulton and MacPherson, ch(E) td(A_0) = i_* tau(E) with
tau(E) in H_*(Supp E; Q), and td(A_0) = 1. On a three-dimensional component, the top part of tau is the
multiplicity times the fundamental class. Let X = Y cup (union of Z_x) and let D be the union of the
pairwise intersections of the threefolds. By excision, H_6(X, Y cup D) is the sum of the
H_6(Z_x, Z_x cap (Y cup D)) = Q over the Z_x not contained in Y; this uses that Z_x cap (Y cup D) has real
dimension at most four. The image of tau_3(E) there is (mu_x). So tau_3(E) - sum mu_x [Z_x] comes from
H_6(Y cup D) = H_6(Y).

Y is smooth of dimension d. By Poincare duality H_6(Y) = H^{2d-6}(Y), and 2d - 6 < d. So by the Lefschetz
hyperplane theorem H^{2d-6}(A_0) -> H^{2d-6}(Y) is onto. Restriction followed by the Gysin map is
multiplication by [Y] = (prod m_i) theta_h^{6-d}. So the image of H_6(Y) in H^6(A_0) is
theta_h^{6-d} H^{2d-6}(A_0), which lies in theta_h H^4(A_0). Hence
ch_3(E) - sum mu_x [Z_x] is in theta_h H^4(A_0). Lemma 15 with nu = mu then gives part 1.

For part 2, take x and j. The components of Supp E not contained in Z_x cup Z_{x^(j)} lie either in Y or in
other threefolds. The other threefolds miss the general Gamma_y and Gamma'_y by (C). Y cap Z_x and
Y cap Z_{x^(j)} have dimension at most one, so they do not map onto C_{x_k} x C_{x_l}, and Y also misses the
general Gamma_y and Gamma'_y. By Theorem 13 every mu_x is zero, against part 1. []

When d = 5, Y is an ample divisor. It meets every curve, so Theorem 13 leaves room there. Part 1 still holds:
at least one threefold of each orbit must carry nonzero multiplicity.

## What this does to the eight-line-bundle frontier

For a convolution E, let Lambda be the union of the components of Supp E that are not among the threefolds.
Off the threefolds, E restricts to a twisted complex of the line-bundle pieces, so Lambda is the closure of
the support of that twisted complex.

Lambda is not just the degeneracy locus of the components of delta between line bundles. The homotopy transfer
through the threefold pieces gives the twisted complex components in H^p(U, L^m), p >= 2, of the open
complement U, where H^p(U, L^m) = H^{p+1}_Z(L^m) != 0 for 2 <= p <= 5.

* The 8 configurations of rank +-2 have Supp E = A_0. Theorems 12 to 16 do not touch them.
* The 23 configurations of rank 0 meet the criterion with N != 0 only if either Supp E = A_0, or the
  following all hold:
  * Lambda has components of dimension at least three;
  * at every threefold with nonzero multiplicity, and in each of the three directions, Lambda meets every
    curve C_{x_j} x {y} or C_{-x_j} x {y} (Theorem 13);
  * Lambda lies in no smooth complete intersection of codimension at least two that meets the threefolds
    properly (Corollary 16).

  When Supp E has no component of dimension above three, ch_3(E) = sum_x mu_x [Z_x] + sum_R mu_R [R], over
  the three-dimensional components R of Lambda. The criterion kills mu_x at every threefold whose general
  curves Lambda misses, so the class N (alpha + alphabar) + c_3 theta_h^3 must then be carried by Lambda
  together with the threefolds that Lambda meets in all three directions.
* Whatever the line bundles, no object supported on the threefolds alone meets the criterion with N != 0
  (Corollary 14).

## What C8 now asks

* Eight to eleven line bundles: one piece with at least eight line bundles must carry both parities. With
  eight, these are the 31 configurations above. Of them, 23 have rank 0 and are narrowed as just described;
  8 have rank +-2 and are open.
* Twelve or more: also two or more pieces.
* In every case the decision is the rank of y -> (D(y)_{TT})_T against ev_T(TD), with the Fourier and twist
  conditions of Lemma 1 on the threefolds present. In addition, wherever E is supported on two threefolds
  near the generic curves of a coordinate direction, the multiplicity there is zero (Theorems 12 and 13).
* Everything above holds at every discriminant (weights h).

## Checks

* `e06_six.py N` for N = 4 to 8; log in `e06_six.log`. The run table it prints (the threefold shifts allowed
  in a run of each excess) agrees with Lemma 4: excess 1 puts the threefold at s + 1, and the decreasing run
  of excess 3 puts its two threefolds at s + 1 and s - 1.
* It reproduces Theorem 6: no configuration with four or five line bundles keeps a live chain.
* `e06_weights.py` uses nine weight vectors, with h_1 ... h_6 in {1, 2, 3, 4, 6, 7, 27, 30030}; the values 3, 6,
  7, 27 and 30030 are not sums of two squares, so these change the discriminant class. For all thirty-two
  threefolds, exactly over Q(i), it checks:
  * TD_h kills theta_h;
  * ev_Z has rank at least 3 on TD_h and is nonzero on every tested direction of Wbar;
  * every random configuration with the polarised shape for theta_h has sum eps = 0 (exact Chern
    characters);
  * the neighbours of each threefold.

  Log in `e06_weights.log`.
* `e06_pairs.py`, exactly over Q(i), for the nine weight vectors and all thirty-two threefolds; log in
  `e06_pairs.log`. It checks:
  * (A) the entries M_mj at Y = E_jm, 6912 cases;
  * (B) the basis a, b, n_k, n_l, r_k, r_l, the four kernels, the two isogenies T x B and T' x B', the place
    of a ^ n_l in the decomposition for T', and b(w_j) = -2 zeta_j;
  * (C) the threefolds meeting the general curves, and |C_u cap C_{-u}| = 4;
  * (D) the X_e coefficients zsign(x) prod x_j^2, the span of w_c - N/4, and w_c = N/4 with 4 | N in 121
    random polarised configurations;
  * (E) theta_h X_e = 0 for every weight, and each weight -2e occurring on X_e alone.
