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

Theorem 17 below drops the hypothesis on E|_U: it needs only that Supp E cap U lies in T and that the
multiplicity along T is nonzero.

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

For a convolution, Theorem 17 applies at every threefold T along which E has nonzero multiplicity, whatever
the other pieces do near T: the other components of Supp E must cut out on T a set whose divisorial part is
ample. That divisor can come from the support of the line-bundle part, or from all three neighbours of T among
the threefold pieces.

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

## Theorem 17 (locality with no condition on the sheaves)

Let h be any weights, T = Z_zeta one of the thirty-two threefolds and E an object of D^b(A_0) that deforms
to first order along every v in TD_h. Suppose there is an open set U of A_0 meeting T with
Supp E cap U contained in T, and that E has nonzero multiplicity mu along T. Then the divisorial part of
T \ U is an ample divisor of T.

In particular, if T is an irreducible component of Supp E along which E has nonzero multiplicity, and R is
the union of the other irreducible components of Supp E, then the divisorial part of T cap R is an ample
divisor of T (take U = A_0 \ R).

This contains Theorem 10, where E|_U = i_* M [s], so that Supp E cap U = T cap U and mu = (-1)^s. Here
nothing is assumed about the cohomology sheaves of E on U: they may have any ranks, embedded parts and
lower-dimensional pieces inside T.

*Proof.* Put Z = T cap U, a smooth closed subset of U of codimension three. As in Step 1 of Theorem 12,
semiregularity with supports in Z and ob(v) = 0 give

    mu kappa(v) _| [T] = 0   in H^4_Z(U, Omega^2).

Here the localised class ch_3^Z(E|_U) lies in H^3_Z(U, Omega^3) = H^0(U, H^3_T Omega^3), and through the
isogeny T x B -> A_0 of Step 4 of Theorem 12, with B = Z_{-zeta}, the sheaf H^3_T(Omega^3) is
O_T (x) H^3_0(O_B) (x) wedge^3 Vdual, a direct limit of free O_T-modules. A section of it is therefore
determined at the generic point of T, where the class is c_0 mu [T]; the lower-dimensional parts of
Supp E cap U, which lie in Z, add nothing.

The sheaves H^q_T vanish for q != 3, so H^4_Z(U, F) = H^1(U, H^3_T F) = H^1(Z, H^3_T F). The residue rho_T
of Step 4 of Theorem 12 is built from the isogeny and from the three normal coordinates f_1(zeta), f_2(zeta),
f_3(zeta), which are linear. So it is an O_T-linear map of sheaves on all of T, and it commutes with
restriction to Z. By Step 5 of Theorem 12, written with all three normal coordinates,

    rho_T(kappa(v) _| [T]) = <df_1, v> (x) df_2 ^ df_3 - <df_2, v> (x) df_1 ^ df_3 + <df_3, v> (x) df_1 ^ df_2,

with f_i = f_i(zeta). Its three components are the classes <df_i, v> in H^1(T, O), and <df_i, v> takes the
value M_im(v) on wbar_m. Together they are ev_T(v) in Hom(Wbar, V/W) = H^1(T, N_T). Hence
mu ev_T(v)|_Z = 0 in H^1(Z, N_T), and since mu != 0, ev_T(v) restricts to zero on T cap U for every v in
TD_h.

The proof of Theorem 10 derived exactly this from the deformation of a shifted line bundle, and its second
and third paragraphs apply word for word. If the divisorial part S of T \ U were not ample, the connected
stabiliser H of S would be a nonzero subtorus. The kernel of H^1(T, O) -> H^1(T cap U, O) would be
q^* H^1(T/H, O), so ev_T(v) would kill ubar for every u in Lie H, and this fails at the v with Y = E_ab
(check (A)). []

What it adds. An ample divisor of T meets every curve of T. So at every threefold T with nonzero
multiplicity, and in every direction j, the other components of the support meet every curve
Gamma_y = C_{zeta_j} x {y}, for every y in C_{zeta_k} x C_{zeta_l}. Among the threefolds only the three
neighbours of T meet it in surfaces, and their surfaces together are ample only when all three are present.
Theorem 13 asks, in each direction, for a component off the threefolds meeting every Gamma_y cup Gamma'_y.
Theorem 17 asks for more on T itself: the trace on T of the other components must contain an ample divisor
of T.

## Proposition 18 (where semiregularity with supports stops)

Let E be an object of D^b(A_0) with kappa(v) _| ch(E) = 0 in H^*(A_0, Omega^*) for every v in TD_h. This
holds when ch(E) has the polarised shape for theta_h: the Weil classes and the powers of theta_h stay of
Hodge type on the whole Weil family through (A_0, K, theta_h). Suppose that Supp E contains an ample divisor
Y of A_0, as it does when Supp E = A_0. Then for every k >= 0, every open set U of A_0, every closed subset
Z of U containing Supp E cap U and every v in TD_h,

    kappa(v) _| ch_{k+1}^Z(E|_U) = 0   in H^{k+2}_Z(U, Omega^k),

whether or not E deforms along v.

*Proof.* Put Sigma = Supp E and c = kappa(v) _| ch_{k+1}^Sigma(E) in H^{k+2}_Sigma(A_0, Omega^k). The open
set X = A_0 \ Y is affine, because Y is ample. So H^1(X, T_X) = 0 and kappa(v) restricts to zero on X;
hence so does c, which is the cup product of kappa(v) with the localised Chern character.

For Y contained in Sigma the sequence of cohomology with supports

    H^{k+2}_Y(A_0, Omega^k) -> H^{k+2}_Sigma(A_0, Omega^k) -> H^{k+2}_{Sigma \ Y}(X, Omega^k)

is exact, so c is the image of some c' in H^{k+2}_Y(A_0, Omega^k). In the sequence

    H^{k+1}(X, Omega^k) -> H^{k+2}_Y(A_0, Omega^k) -> H^{k+2}(A_0, Omega^k)

the first group is zero, because X is affine and k + 1 >= 1. So c' is determined by its image in
H^{k+2}(A_0, Omega^k). That image is also the image of c, namely kappa(v) _| ch_{k+1}(E), which is zero by
hypothesis. Hence c' = 0 and c = 0.

Localised Chern characters are compatible with restriction to open sets and with enlarging the support. So
kappa(v) _| ch_{k+1}^Z(E|_U) is the image of c under H^{k+2}_Sigma(A_0) -> H^{k+2}_{Sigma cap U}(U) ->
H^{k+2}_Z(U), and it is zero. []

What it means. The semiregularity map of Buchweitz and Flenner, with any supports and on any open set, sends
ob(v) to the classes kappa(v) _| ch_{k+1}^Z(E|_U). For an object whose support contains an ample divisor these
classes vanish identically, so that map gives no condition at all. Theorems 12, 13 and 17 and Corollaries 14
and 16 all come from it, so none of them can say anything about such an object. Whether it meets the
criterion is decided by ob(v) in Ext^2(E, E) itself, that is, for a convolution, by the products of its pieces,
and by nothing that sees only the support and the Chern character.

This is also why part 2 of Corollary 16 stops at d <= 4: when Supp E contains a smooth ample divisor Y of
dimension five, no argument of this kind can exclude E.

## Lemma 19 (the product model of one orbit)

Take the principal weights h = (1, ..., 1), or any h with h_j = h_{3+j} for j = 1, 2, 3. Fix zeta, and let
O = {+-zeta_1} x {+-zeta_2} x {+-zeta_3} be its orbit of Lemma 15. Put T = Z_zeta, B = Z_{-zeta}, and let
mu: T x B -> A_0 be the sum map. Write C_j = C_{zeta_j}, C'_j = C_{-zeta_j}, each a copy of E_0, and
P_j = C_j cap C'_j.

1. mu is an isogeny of degree 64, with kernel {(p, -p) : p in P_1 x P_2 x P_3}, and P_j = E_0[2] on each
   curve.
2. mu^* L_h^l is an external product M_1(l) x ... x M_6(l) of line bundles on the six curves
   C_1, C_2, C_3, C'_1, C'_2, C'_3, each of degree 2 h_j l.
3. For x in O let J(x) be the set of j with x_j = zeta_j. Then mu^* O_{Z_x} is the direct sum, over the 64
   points of the kernel orbit, of the external products whose j-th pair of factors is O_{C_j} x O_q
   (q_j in P_j) for j in J(x) and O_{q_j} x O_{C'_j} for j not in J(x), over the 64 choices of
   (q_1, q_2, q_3).
4. For any objects F, G built from these pieces, Ext_{A_0}(F, G) is the K-invariant part of
   Ext_{T x B}(mu^* F, mu^* G), K = ker mu, and the minimal A-infinity structure of the full subcategory of
   D^b(A_0) on the pieces L_h^l and O_{Z_x} L_h^k, x in O, is the K-invariant part of the one on their
   pullbacks, computed with K-invariant homotopies.

So every product among line bundles and threefold pieces of one orbit is a product of external tensor
products on E_0^6, and by the Kunneth formula and the tensor trick for homotopy transfer it is computed from
the A-infinity structure of D^b(E_0) on line bundles of even degree and the skyscrapers of the four points of
order two.

*Proof.* (1) C_j = {(-zeta_j t, t)} and C'_j = {(zeta_j t, t)} have independent tangent lines, so the sum map
C_j x C'_j -> E_0^2 is onto with finite kernel; (-zeta_j t, t) + (zeta_j t', t') = 0 forces t' = -t and
2 zeta_j t = 0, so the kernel is {(p, -p)} with p in E_0[2], four points, which is C_j cap C'_j.
(2) The polarisation of the j-th factor is H((z, w), (z', w')) = h_j z zbar' + h_{3+j} w wbar'. On a vector
(-zeta t, t) of C_j and a vector (zeta s, s) of C'_j it gives (h_{3+j} - h_j |zeta|^2) t sbar = 0, since
|zeta| = 1 and h_j = h_{3+j}. So C_j and C'_j are orthogonal, mu^* theta_h has no mixed term, and
mu^* L_h = M_1 x ... x M_6 tensored with an element of Pic^0 of the product, which is itself an external
product and is absorbed into the M_i. The degree of theta_h on C_j is the intersection number with
h_j (a_j + b_j), which is 2 h_j. (3) mu^{-1}(C_j) = {(s, t) : s + t in C_j} = C_j x P_j, and
mu^{-1}(C'_j) = P_j x C'_j; take the product over j. (4) mu is an etale Galois cover with group K acting by
translations, so mu^* identifies D^b(A_0) with the K-equivariant objects of D^b(T x B) and the Ext groups
with the invariants. Averaging any homotopy over the finite group K gives a K-equivariant one, and homotopy
transfer with it commutes with the K-action. []

The model fails when h_j != h_{3+j} for some j, because mu^* theta_h then has a mixed term on that factor, and
for threefolds of two different orbits, because for x outside O some C_{x_j} is a graph in C_j x C'_j. Every
closed chain through a threefold piece of one orbit whose other pieces are line bundles or threefolds of the
same orbit, at the principal weights, can therefore be computed on E_0^6. That includes the special runs of
Lemma 4 of `C1_chains.md` whose second threefold is B = Z_{-zeta}.

## Lemma 20 (how a simple chain splits over the six curves)

Keep the principal weights and the notation of Lemma 19, with T = O_Z L^k, Z = Z_zeta. Call a closed chain
through T **simple** if T is its only threefold piece and k differs from the exponents l_1 and l_m of the line
bundles next to T, and no step between line bundles goes down. Such a chain is
T -> L^{l_1} -> ... -> L^{l_m} -> T with l_1 < ... < l_m, and y sits on one of its m + 1 steps. (By Lemma 4 a
chain with T as its only threefold piece and one down step has 8 line bundles and an increasing run through
T; those chains are not treated here.) Put sigma = [l_1 < k] + [k < l_m] and write the
target ev_T(v) in H^1(Z, N_Z) in components (i, j): H^1 of O on the curve C_i, tensored with the normal
direction of the j-th pair, that is Ext^1(O_q, O_q) on C'_j.

1. m = 3 sigma + 2 and sigma >= 1, so a simple chain has 5 line bundles (k below l_1 or above l_m) or 8
   (l_1 < k < l_m).
2. The diagonal components (i, i) of ev_T(v) vanish, and ev_T(TD) is the space of matrices M with zero
   diagonal and M_ji = -zeta_i zetabar_j M_ij.
3. In the model of Lemma 19 with K-invariant special homotopies on each curve, every term of the (i, j)
   component of D(y)_{TT} along a simple chain is a planar binary tree with m + 1 leaves whose m - 1 internal
   edges each carry the homotopy of one curve. For i != j each such term puts no homotopy on C'_j, exactly one
   on each of the other two curves C'_{j'}, sigma - 1 on C_i and sigma on each of the other two curves C_{i'}.
4. On C'_j the factor of each term is the composite in cohomology of the entry class in Ext^1(O_q, M), the
   values at q of the sections along the chain and the evaluation at q. So the (i, j) component depends on
   the steps between line bundles only through their restrictions to the slice where the coordinate on
   C'_j equals q, and it vanishes if one of them vanishes on that slice.
5. When sigma = 1, the factor on C_i is likewise a composite in cohomology: the Serre pairing of the product
   of the sections along the chain with the one class of degree 1 among the entry and the exit. The four
   remaining factors, on the C'_{j'} and the C_{i'}, carry one homotopy each.

*Proof.* (1) By Lemma 3 the step L^{l_m} -> T has degree 0 if k > l_m and 3 if k < l_m, and T -> L^{l_1} has
degree 3 if l_1 > k and 6 if l_1 < k; their sum is 3 + 3 sigma, the up steps have degree 0, and the
output lies in Ext^2(T, T). The product of its m + 1 entries has degree (3 + 3 sigma) - (m + 1) + 2, which is 2
exactly when m = 3 sigma + 2. The chain must go down somewhere, and only the run L^{l_m} -> T -> L^{l_1} can,
so l_1 < l_m, which excludes l_m < k < l_1, that is sigma = 0. (2) The matrix of ev_T(v) is
Y_jm - zeta_m zetabar_j Y_mj (Lemma 2 of `C1_chains.md`); its diagonal is zero because |zeta_j| = 1, and
M_mj = -zeta_j zetabar_m M_jm. (3) On each pair of curves T pulls back to
O_{C_j} (x) M_j(k) on C_j times a skyscraper O_q on C'_j, and L^l to line bundles of degree 2l on all six
curves (Lemma 19). By the Kunneth formula the entry T -> L^{l_1} has degree 1 on each C'_j and
[l_1 < k] on each C_j, the exit has degree 0 on each C'_j and [k < l_m] on each C_j, and the up steps have
degree 0 everywhere. A Dolbeault model of each curve is a dg category, so the transferred products are sums
over planar binary trees; with the homotopy of the tensor product, sum over f of
(i p)^{(x) (f-1)} (x) h_f (x) 1 (x) ... (x) 1, each internal edge carries h on one curve. The degree on a curve
drops by one for each homotopy on it, so a curve with input degree a and output degree b carries a - b of
them. The (i, j) component has output degree 1 on C_i and C'_j and 0 elsewhere, which gives the count. (4) With
no homotopy on C'_j, every edge there carries i p or the identity. The inputs on C'_j are cocycles, and
1 - i p = dh + hd, so replacing i p by the identity on an edge changes the value by p applied to an exact form,
which is zero. Hence the factor is the composite in cohomology, and Ext^1(O_q, M) (x) Hom(M, M') ->
Ext^1(O_q, M') is multiplication by the value of the section at q. (5) The same argument on C_i, which has
input degree 1 and output degree 1 when sigma = 1. []

So for five line bundles each term of D(y)_{TT} is the product of two composites in cohomology and four
products on E_0 with a single homotopy, which are triple products of the kind computed by Polishchuk for line
bundles and points on an elliptic curve. For eight line bundles the curves C_{i'} carry two homotopies each.
Chains through T and B = Z_{-zeta} (the special runs) are also inside the model of Lemma 19 and are not
treated here.

## Lemma 21 (the triple products through a point are derivatives)

Work in a minimal model of the full subcategory of D^b(E_0) on a skyscraper O_q and line bundles M_a. The
spaces Ext^1(O_q, M_a) = M_a|_q (x) T_q and Hom(M_b, O_q) = M_b|_q^* are lines; fix generators X_a and ev_b,
compatible with the products, so that m_2(X_a, s) = s(q) X_b and m_2(s, ev_c) = s(q) ev_b for s in
H^0(M_b M_a^{-1}), resp. H^0(M_c M_b^{-1}). For a < b (deg M_b > deg M_a) define the linear form
lambda_ab(s) by m_3(X_a, s, ev_b) = lambda_ab(s) id_{O_q}. These are the triple products that occur on the
curves C'_{j'} in Lemma 20.

1. If s(q) = 0, then lambda_ab(s) = epsilon <ds(q), X_a>, the derivative of s at q paired with X_a, with a
   universal sign epsilon. It does not depend on the minimal model, and it is nonzero exactly when s
   vanishes to order one at q.
2. Leibniz rule: lambda_ac(s s') = s(q) lambda_bc(s') + s'(q) lambda_ab(s).
3. Normal form: there are 1-jets at q of frames e_a of the M_a such that
   lambda_ab(s) = epsilon (d/dz)(s / (e_b e_a^{-1}))(q) for every s, z a coordinate at q. A change of minimal
   model changes the lambda_ab by s(q)(g_b - g_a) for scalars g_a, which is a change of these 1-jets, and every
   change of 1-jets arises in this way.

*Proof.* (1) When s(q) = 0, m_2(X_a, s) = 0 and m_2(s, ev_b) = 0, so m_3(X_a, s, ev_b) is the Toda bracket of
the three maps, up to a universal sign. Its indeterminacy is X_a Hom^{-1}(M_a, O_q) + Hom^0(O_q, M_b) ev_b = 0,
so it is well defined. Since ev_b s = 0, s factors through M_b(-q) -> M_b as s = t s~, and the bracket is the
scalar c with s~ X_a = c d in Ext^1(O_q, M_b(-q)), d the class of the triangle M_b(-q) -> M_b -> O_q. Now
s~ X_a = s~(q) X_a, and s~(q) in Hom(M_a|_q, M_b(-q)|_q) = (M_b M_a^{-1})|_q (x) T_q^* is ds(q).
(2) The A-infinity relation on (X_a, s, s', ev_c) has the terms m_3(m_2(X_a, s), s', ev_c),
-m_3(X_a, s s', ev_c), m_3(X_a, s, m_2(s', ev_c)), and two terms that vanish because m_3(X_a, s, s') lies in
Hom^0(O_q, M_c) = 0 and m_3(s, s', ev_c) in Hom^{-1}(M_a, O_q) = 0. (3) Choose any 1-jets of frames and let
D_ab(s) = epsilon (d/dz)(s/(e_b e_a^{-1}))(q). It satisfies the same Leibniz rule and agrees with lambda_ab on
s(q) = 0 by (1), so lambda_ab - D_ab = c_ab ev_q for scalars c_ab, and the two Leibniz rules, applied to
sections not vanishing at q (they exist when the degrees differ by at least one), give c_ac = c_ab + c_bc.
Put g_a = c_{0a} for the least degree 0; then c_ab = g_b - g_a, and replacing e_a by (1 - epsilon g_a z) e_a
changes D_ab by s(q)(g_b - g_a). An A-infinity isomorphism with f_1 = 1 changes m_3(X_a, s, ev_b) by
m_2(f_2(X_a, s), ev_b) + m_2(X_a, f_2(s, ev_b)) - f_2(m_2(X_a, s), ev_b) - f_2(X_a, m_2(s, ev_b)); the first
two vanish because Hom^0(O_q, M_b) = Hom^{-1}(M_a, O_q) = 0, and with g_a = f_2(X_a, ev_a) the rest is
-s(q)(g_b - g_a). Any scalars g_a define such an f_2. []

So on the curves C'_{j'} that carry one homotopy, a term of Lemma 20 sees the sections only through their
1-jets at the point q of order two, and only through the derivative once the frames are fixed. What is left
for five line bundles is to fix these frames compatibly with the homotopy transfer on E_0^6 (a change of
minimal model on one curve is an A-infinity isomorphism of the product, so the decision does not depend on
it) and the triple products of line bundles alone on the curves C_{i'}.

## Lemma 22 (the live chains of the eight configurations of rank +-2)

Take one of the 8 configurations of rank +-2 among the 31 of `e06_six_n8.json`, and an admissible set Z0 of
zero up edges whose live chains carry threefold pieces of both parities (the sets of `e06_six.refine`, 1132 live
chains over all of them). Then every live chain consists of up steps and of runs of two kinds only:

1. **The closing run**, of excess 3, from the line bundle L^{l_top} of greatest exponent on the chain down to the
   one L^{l_bot} of least exponent. It is always
   L^{l_top} -> O_T L^k -> O_{T'} L^{k'} -> L^{l_bot}, of degrees 0, 3, 3, with k >= l_top and k' <= l_bot:
   two threefold pieces, a section of L^{k - l_top} on T, a class in Ext^3(O_T L^k, O_{T'} L^{k'}) (twist going
   down), and a class in Ext^3(O_{T'} L^{k'}, L^{l_bot}).
2. **Middle runs**, of excess 1, increasing: L^{l} -> O_{T''} L^{k''} -> L^{l'} with l <= k'' <= l', of degrees
   0 and 3.

So a live chain has 4 line bundles (three up steps and the closing run) or 6 (two pairs of up steps joined by a
middle run, and the closing run); no live chain is simple in the sense of Lemma 20, and the threefold pieces of
a live chain come in the pair (T, T') of the closing run, at the same parity of shift, plus T'' at the other
parity when there is a middle run.

When T, T' (and T'') lie in one orbit O of Lemma 15, the model of Lemma 19 applies. Write T' = Z_{x'},
J = J(x') and d = |J|, the dimension of T cap T'. On the summand of T over q = 0 only the summands of T' with
q'_j = 0 for j in J meet it, and on each of the six curves the closing run has total degree 1: for j in J,
degree 1 on C_j (Hom(M(k), M(k')) with k' < k is an H^1) and 1 on C'_j (Ext^1(O_q, M(l_bot))); for j not in J,
degree 1 on C'_j (the class of T -> T') and 1 on C_j (the class of T' -> L^{l_bot}). The up steps and the step
into T have degree 0 on every curve. Hence, exactly as in Lemma 20 with sigma = 1, every term of the (i, j)
component of D(y)_{TT} along a 4-bundle chain is a planar binary tree with 6 leaves and 4 homotopies: none on
C_i and C'_j, where the factor is a composite in cohomology, and one on each of the four other curves. Along a
6-bundle chain the middle run adds degree 1 on C'_j (j with x''_j = zeta_j) or C_j (otherwise) on each pair, and
the tree has 9 leaves and 7 homotopies.

*Proof.* The first part is the enumeration of `e06_runs.py`: the runs that occur in the 1132 live chains have
excess 3 (decreasing) or 1 (increasing), and with the degrees of Lemma 3 their realisations are exactly the four
of item 1 (twist of T above or equal to l_top, of T' below or equal to l_bot) and the three of item 2. A
decreasing run of excess 3 with one threefold would need degrees adding to 5 on L^{l_top} -> O_T L^k ->
L^{l_bot}, and these sums are 0 + 6, 3 + 6, 3 + 3 for k above, between and below the exponents, and at least 6
when k equals one of them; two steps between threefolds of degree 2 would need the twist to rise, and then the
last step has degree 6. For the second part, T' restricted to the j-th pair is O_{C_j} x O_{q'_j} for j in J and
O_{q'_j} x O_{C'_j} otherwise (Lemma 19 (3)); it meets C_j x {0} only if q'_j = 0 for j in J. The degrees on
the six curves follow from the Kunneth formula, as in Lemma 20 (3): Ext^3 of T -> T' is 1 on C_j and 0 on C'_j
for j in J, and 0 on C_j and 1 on C'_j for j not in J, which adds to 3 only with degree 0 on C'_j for j in J;
Ext^3 of T' -> L^{l_bot} is 1 on C'_j for j in J and 1 on C_j otherwise. Each curve then has input degree 1,
and the (i, j) component has output degree 1 on C_i and C'_j and 0 elsewhere. []

So the eight configurations of rank +-2 are decided by the products along these chains: six-curve products
of line bundles of even degree with the skyscrapers of the points of order two, when the threefold pieces stay in
one orbit, and products through graphs C_{x_j} in C_j x C'_j otherwise.

## Lemma 23 (all four points of order two in one model)

Let O_{E[2]} = [O(-4 oo)[1] -> O] with differential y, the section of O(4 oo) with divisor E[2] - 4 oo. Then
Hom(O_{E[2]}, O_{E[2]}) is the algebra of functions on E[2], of dimension 4, and Ext^1(O_{E[2]}, O_{E[2]}) has
dimension 4. Its four primitive idempotents e_q are rational, and a morphism into (out of) O_{E[2]} splits as the
sum of its composites with the e_q. So one Cech model of E_0 holds the skyscrapers of all four points at once,
and mu^* O_T on the cover T x B of Lemma 19 is an external product of copies of O_{E[2]} and line bundles: every
summand q' of Lemma 19 is in the same model.

*Proof.* `e06_points.py` computes the algebra exactly over Q: the unit, the four idempotents (orthogonal,
adding up to the unit). The dimensions are those of sum_q Hom(O_q, O_q) and sum_q Ext^1(O_q, O_q). []

In this model the one-homotopy factors on a curve C_j (the step ev_q into the skyscraper, the step X_q out of it,
then sections back to the line bundle of T) are not all zero. For generic classes and every bracketing:

| twists k; l | oo | P0 | P1 | P-1 |
| --- | --- | --- | --- | --- |
| 5; 0, 2, 3, 4 | 0 of 308 | 154 of 308 | 0 of 308 | 0 of 308 |
| 4; 0, 1, 2, 3 | 0 of 308 | 0 of 308 | 0 of 308 | 0 of 308 |
| 6; -1, 1, 3, 5 | 0 of 308 | 240 of 308 | 0 of 308 | 0 of 308 |

(`e06_halftree_points.py`). So the vanishing of the closing-run products found with the skyscraper of oo alone
is a property of that point in this Cech model, not of the configurations: through P0 the (i, j) components with
i != j are reached. By Lemma 21 (3) these values are 1-jet data of frames at each point, and they change under an
A-infinity isomorphism; the TT test in one model excludes a configuration only when it fails there with every
chain and every summand computed in that model. No configuration of rank +-2 is excluded by this, and none is
shown to meet the test. What decides them is the rank of y -> D(y)_{TT} on the cover against ev_T(v), with the
K-invariant target, all four points included.

## What this does to the eight-line-bundle frontier

For a convolution E, let Lambda be the union of the components of Supp E that are not among the threefolds.
Off the threefolds, E restricts to a twisted complex of the line-bundle pieces, so Lambda is the closure of
the support of that twisted complex.

Lambda is not just the degeneracy locus of the components of delta between line bundles. The homotopy transfer
through the threefold pieces gives the twisted complex components in H^p(U, L^m), p >= 2, of the open
complement U, where H^p(U, L^m) = H^{p+1}_Z(L^m) != 0 for 2 <= p <= 5.

* The 8 configurations of rank +-2 have Supp E = A_0. By Proposition 18 no argument by semiregularity with
  supports can decide them, on any open set: only the products, through ob(v) in Ext^2(E, E), can.
* The 23 configurations of rank 0 meet the criterion with N != 0 only if either Supp E contains an ample
  divisor (where Proposition 18 again leaves only the products), or the following all hold:
  * Lambda has components of dimension at least three;
  * at every threefold with nonzero multiplicity, and in each of the three directions, Lambda meets every
    curve C_{x_j} x {y} or C_{-x_j} x {y} (Theorem 13);
  * at every threefold T with nonzero multiplicity, Lambda together with the neighbours of T in the support
    cuts out on T a set whose divisorial part is an ample divisor of T (Theorem 17);
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
  8 have rank +-2 and are open; by Proposition 18 they can be decided only through the products.
  By Lemma 22 their live chains close through two threefold pieces (T, T') joined by a class of
  Ext^3, with 4 or 6 line bundles, and inside one orbit their products are six-curve products on E_0^6.
* Twelve or more: also two or more pieces.
* In every case the decision is the rank of y -> (D(y)_{TT})_T against ev_T(TD), with the Fourier and twist
  conditions of Lemma 1 on the threefolds present. In addition, wherever E is supported on two threefolds
  near the generic curves of a coordinate direction, the multiplicity there is zero (Theorems 12 and 13), and
  at a threefold with nonzero multiplicity the rest of the support cuts out an ample divisor (Theorem 17).
* Once the support contains an ample divisor, the support and the Chern character say nothing more
  (Proposition 18); the products must be computed.
* At the principal weights, the products along chains that stay in one orbit are products on E_0^6 of line
  bundles of even degree and skyscrapers at points of order two (Lemma 19), so they can be computed on the
  elliptic curve E_0. Along a simple chain the products split over the six curves with a fixed number of
  homotopies on each, and with five line bundles every factor is a composite in cohomology or a triple product
  on E_0 (Lemma 20).
* Everything above holds at every discriminant (weights h).

## Checks

* `e06_points.py` and `e06_halftree_points.py k l_1,...` check Lemma 23.
* `e06_runs.py` checks Lemma 22: the runs of the 1132 live chains of the eight configurations of rank +-2 and
  their realisations by threefold pieces.
* `e06_tensor.py` computes the minimal A-infinity structure on products E_0^N of these objects by the tensor trick
  and checks the A-infinity relations on E_0^2 and E_0^3, also along chains through O_oo where they are not
  trivially satisfied.
* `e0_ainf.py` and `e0_twisted.py` compute the minimal A-infinity structure of D^b(E_0) on line bundles
  O(n oo) and the skyscraper of oo exactly over Q, for E_0: y^2 = x^3 - x, by two-chart Cech complexes whose
  spaces of sections are spanned by monomials, the basic perturbation lemma and a reduction over Q. They check the
  A-infinity relations up to n = 5 (with and without the skyscraper) and part 1 of Lemma 21: m_3(X, s, ev) is
  nonzero on a section vanishing at oo exactly when it vanishes to order one.
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
