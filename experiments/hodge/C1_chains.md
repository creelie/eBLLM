# Convolutions with at most five line bundles at E_0^6 fail the criterion

Candidate C1 of the Hodge attack, part F2.4 of the Full Hodge plan ("four or more line bundles").
Everything below is proved by hand; the programs named at the end check the finite statements.

## Setting

A_0 = E_0^6, E_0 = C/Z[i], with K = Q(i) acting by i on z_1, z_2, z_3 and by -i on z_4, z_5, z_6, and L
the product polarisation, of class theta. For zeta in mu_4^3 with (zeta_1 zeta_2 zeta_3)^2 = 1 let
C_zeta = {z_j + zeta z_{3+j} = 0} in the j-th factor E_0^2 and Z_zeta = C_{zeta_1} x C_{zeta_2} x C_{zeta_3},
the 32 abelian threefolds of Appendix app:cmpoint of the Full Hodge paper. TD is the tangent space at A_0 of
the Weil family D_{3,3}: the symmetric K-linear maps v, with coordinates Y_mj = v_{3+m, j}, of dimension 9.

E is a convolution (an iterated cone) of pieces

* threefold pieces F_x = O_{Z_x} (x) L^{k_x} [s_x], Z_x among the Z_zeta, any twists k_x;
* line-bundle pieces L^{l} [t].

The polarised criterion asks dim Ext^2(E, E) = r = 57, that is, sigma_E injective, for E with
ch(E) = N (alpha + alphabar) + sum_m c_m theta^m, N != 0.

**Hypotheses (H).** No sheaf occurs twice (the threefolds Z_x are pairwise distinct, the exponents l are
pairwise distinct), and Ext^1 = 0 between threefold pieces at the same shift. (For the Z_zeta, two at the
same shift with the same value of zeta_1 zeta_2 zeta_3 differ in at least two coordinates, and then Ext^1 = 0
by Lemma lem:cmmeet(ii).)

## Lemma 1 (Chern characters)

Write eps_x = (-1)^{s_x} and, for e in {-1, 0, 1}^3, zeta^e = prod zeta_j^{e_j} and
M_p(e) = sum_x eps_x k_x^p zeta_x^e. Then ch(E) has the polarised shape with N != 0 if and only if

* M_0(e) = 0 for every e != +-(1,1,1), and N = M_0(1,1,1) != 0;
* M_1(e) = 0 for every e with at most two nonzero entries (e = 0 included);
* M_2(e) = 0 for every e with exactly one nonzero entry.

The line-bundle pieces never enter. In particular **sum_x eps_x = 0 and sum_x eps_x k_x = 0**: the threefold
pieces at even and at odd shifts are equal in number and in total twist.

*Proof.* ch(O_Z (x) L^k) = [Z] e^{k theta} (Lemma lem:cmext(i)) and [C_zeta] = a_j + b_j + zetabar c_j + zeta cbar_j
in H^2 of the j-th factor, with a_j, b_j the classes of the two coordinate curves and c_j, cbar_j the mixed
(1,1)-classes; theta = sum_j (a_j + b_j). Expanding the product,
[Z_zeta] = sum_e zeta^e X_e with X_e = prod_{e_j = 0}(a_j + b_j) prod_{e_j = 1} cbar_j prod_{e_j = -1} c_j, so

    ch(E) - (line bundles) = sum_{e, p} M_p(e) X_e theta^p / p!.

The classes X_e theta^p of different e have different mixed type, and the line bundles contribute only
powers of theta (type e = 0). Since a_j c_j = b_j c_j = 0, X_e theta^p is nonzero exactly for
p <= 3 - |supp e|. The Weil classes are X_{+-(1,1,1)}, so for
|supp e| = 1, 2 every nonzero X_e theta^p must have coefficient zero, which gives the conditions on M_0, M_1,
M_2. For e = 0, X_0 = prod(a_j + b_j) is not proportional to theta^3
(theta^3 = 6 prod(a_j + b_j) + 6 sum_{i != j} a_i b_i (a_j + b_j)) and X_0 theta is not proportional to
theta^4, while X_0 theta^2 and X_0 theta^3 are; so M_0(0) = M_1(0) = 0. Conversely these conditions leave
exactly N(alpha + alphabar) plus powers of theta. []

The lemma was checked against the exact Chern characters on 3000 configurations (`e06_chern.py`).

## Lemma 2 (diagonal classes and effective chains)

Order the pieces as in the iterated cone, so that the twisting cochain delta is strictly upper triangular.
Call a closed chain a = a_0 -> a_1 -> ... -> a_m = a of distinct pieces, with step a_i -> a_{i+1} in
Ext^{k_i}(F_{a_i}, F_{a_{i+1}}), k_i = 1 + s_{a_i} - s_{a_{i+1}} (so sum k_i = m), **effective** if every step
but one carries a nonzero component of delta.

If E meets the criterion, every threefold piece lies on an effective closed chain.

*Proof.* For v in TD, sigma_E(ev_E(v)) = v -| ch(E) = 0, since TD annihilates theta and the Weil plane; so the
criterion forces ev_E(v) = 0. In the minimal model, Ext^*(E, E) is the cohomology of the blocks
Ext^k(F_a, F_b) under D_delta(y) = sum m_n(delta, ..., delta, y, delta, ..., delta). The Atiyah class of the
twisted complex is block upper triangular with diagonal blocks At(F_a), and its off-diagonal part, like
delta, is strictly upper triangular; a term of the homotopy transfer that returns to a diagonal block needs a
closed path of such entries, and a closed path of strictly upper triangular entries does not exist. So the
diagonal components of the cocycle of ev_E(v) are exactly ev_{F_a}(v). A term of D_delta(y)_{aa} is a product
along a closed chain through a with y on one step and delta on the others, and it vanishes unless every
delta on it is nonzero. If a threefold piece a lies on no effective chain, D_delta(y)_{aa} = 0 for every y,
while ev_{F_a}(v) != 0 for some v in TD: its component in H^1(Z, N_Z) = Hom(Wbar, V/W) is the matrix
(Y_jm - zeta_m zetabar_j Y_mj), of rank 3 on TD for each of the 32 zeta (`e06_ev.py`; the kernel is the
diagonal of Y and one line in each pair). So ev_E(v) != 0 and sigma_E has a kernel. []

The same strict triangularity makes the Maurer-Cartan equation an exact sum over increasing paths: its
(a, c) component is sum m_n(delta_{a b_1}, ..., delta_{b_{n-1} c}) over a < b_1 < ... < c.

## Lemma 3 (degrees of the steps)

By Lemmas lem:cmext and lem:cmmeet:

* L^l -> L^{l'}: degree 0 if l' > l, degree 6 if l' < l.
* L^l -> O_Z L^k: degree 0 if k > l, 3 if k < l, any of 0..3 if k = l.
* O_Z L^k -> L^l: degree 3 if l > k, 6 if l < k, any of 3..6 if l = k.
* O_Z L^k -> O_{Z'} L^{k'} (Z != Z'): never degree 0; degree 1 excluded by (H); degree at least 3 when k' < k.

## Lemma 4 (the excess identity)

On a closed chain the excess sum (k_i - 1) is zero, and only steps of degree 0 have negative excess. Cut the
chain at its line bundles: there are u steps L -> L up (excess -1), w steps L -> L down (excess 5), and R runs
L -> Z -> ... -> Z -> L through threefold pieces, of excess b each. Then

    sum_runs b + 5w = u,    R + u + w = l,

l the number of line bundles on the chain. A run of excess b changes the shift by -b. By Lemma 3:

* every run has b >= r, r its number of threefold pieces;
* a **decreasing** run (exit exponent below entry exponent) has b >= 3, with equality only for the *special
  run*: entry of degree 0 into O_T L^k (k >= l), one internal step of degree 3 down to O_B L^{k'} (k' < k),
  exit of degree 3 to L^{l'} with l' >= k'.

(If the entry has degree 0, then k_1 >= l > l' and an exit of excess 2 needs k_r <= l', so some internal step
lowers the twist and costs at least 2; if the entry has degree at least 1 the run costs at least 4, by the
same table.) A closed chain must lower the exponent somewhere, so w >= 1 or some run decreases. Hence:

* w >= 1 or two decreasing runs gives l >= 8; for l <= 7 there is no down step and exactly one decreasing run,
  and then l >= 2R + 2.
* **l <= 3**: no closed chain through a threefold piece.
* **l = 4** (shape B): R = 1, the run is special, and the chain is
  L^{l_1}[t] -> L^{l_2}[t+1] -> L^{l_3}[t+2] -> L^{l_4}[t+3] -> O_T L^k [t+4] -> O_B L^{k'} [t+2] -> L^{l_1}[t],
  l_1 < l_2 < l_3 < l_4 <= k, k' <= l_1. Both threefold pieces sit at shifts of the parity of t.
* **l = 5**: R = 1 and the four up steps form the path of the five line bundles at consecutive shifts
  t, ..., t+4 in the order of their exponents.

## Lemma 5 (Maurer-Cartan on consecutive line bundles)

Let E have at most five line bundles, at pairwise distinct shifts, and let L_i, L_{i+1}, L_{i+2} be line
bundles at consecutive shifts with increasing exponents. Then delta_{i,i+1} delta_{i+1,i+2} = 0, so one of
the two is zero.

*Proof.* The Maurer-Cartan component (L_i, L_{i+2}) lies in Hom(L_i, L_{i+2}) and is a sum over increasing
paths of n steps and total Ext degree n - 2, that is, of excess -2. Counting as in Lemma 4 along a path with p
line bundles (ends included), u up steps, w down steps and R runs, u = 2 + 5w + sum b and
p - 1 = u + w + R >= 2 + 6w + 2R. With p <= 5 this leaves w = 0 and either R = 0, p = 3, the path
L_i -> L_{i+1} -> L_{i+2} (L_{i+1} is the only line bundle at its shift), or R = 1, p = 5, three up steps and
one run of excess 1, which lowers the shift by one; then the five line bundles of the path cannot have five
different shifts, whatever the position of the run. So the component is delta_{i,i+1} delta_{i+1,i+2}, the
product of two sections of powers of L on the integral variety A_0, and it is zero only if a factor is. []

## Theorem 6

Under (H), if ch(E) has the polarised shape with N != 0 and E has at most five line-bundle pieces, then E does
not meet the criterion: dim Ext^2(E, E) >= 58. This holds for every choice of twists of the threefold pieces.

*Proof.* There is a threefold piece, since N != 0. By Lemma 2 every threefold piece must lie on an effective
chain, and by Lemma 4 such a chain has l = 4 or 5 line bundles.

* With at most three line bundles there is no chain.
* With four, every chain has shape B on the four line bundles, so every threefold piece on a chain has a
  shift of the parity of t. Then all eps_x are equal and sum eps_x != 0, against Lemma 1.
* With five, an effective chain with l = 5 puts the five line bundles at consecutive shifts (Lemma 4) and
  needs nonzero delta on at least three of the four steps of the path L_1 -> ... -> L_5, while Lemma 5 allows
  at most two (no two consecutive). So every effective chain has
  shape B on a *window*: four of the five line bundles at consecutive shifts in exponent order. Two windows
  share three line bundles, at three different shifts in [t, t+3] and [t', t'+3]; if t and t' have different
  parity this forces t' = t +- 1, and all five line bundles sit at consecutive shifts in exponent order; window {1,2,3,4} is then effective only if
  delta_12, delta_34 != 0 and delta_23 = 0, window {2,3,4,5} only if delta_23, delta_45 != 0 and
  delta_34 = 0 (Lemma 5), so at most one is. Hence all effective chains have the same parity of t, and the
  argument for four line bundles applies. []

## Consequences

* **The C1 record fails.** The 32 threefolds at twist 0 (shift 0 for zeta_1 zeta_2 zeta_3 = 1, shift 1 for -1)
  with L^1[-2], L^2[-1], L^3[0], L^4[1]: the window has t = -2, so the threefold pieces at shift 1 lie on no
  closed chain, and ev_E(v) != 0. No sixfold Massey product is needed.
* **Configuration (a) of the Full Hodge paper is decided negatively** for four and five line bundles.
  Proposition prop:e06count(iv) and the paragraph after it say that (a) stands or falls with the rank of m_6
  along the chain of length six; Theorem 6 decides it without m_6.

## What remains open in F2.4

* **Six or more line bundles.** Chains with l = 6 have two runs or one run of excess 5, and the
  Maurer-Cartan components between line bundles two shifts apart can pass through a second line bundle at
  the same shift, so products can cancel and Lemma 5 fails.
* Pieces outside (H): a threefold at several twists (configuration (c), candidate C2, part F2.3 of the Full
  Hodge plan), a sheaf at two shifts, two threefolds at one shift meeting along a surface (Ext^1 != 0).
* Abelian threefolds other than the Z_zeta (Lemma lem:cmext(i) allows any): Lemmas 2 to 5 hold as they stand;
  only the parity of Lemma 1 uses the Z_zeta.

## Checks

* `e06_ev.py`: ev_Z has rank 3 on TD for each of the 32 threefolds, exactly over Q(i); the 32 together have
  rank 6 (the diagonal of Y is invisible to all of them).
* `e06_chern.py`: Lemma 1 agrees with the exact Chern character test on 3000 configurations (286 polarised).
* `e06_chainclass.py`: closed chains in the superset graph of all 32 threefolds at every admissible shift,
  over every order pattern of the exponents and twists (1 to 6 line bundles at one twist, 1 to 5 at two
  twists, 1 to 4 at three twists): the shapes of Lemma 4 hold with no exception
  (log in `/mnt/project-files/ai-paper/hodge-attack/e06_chainclass.log`).
* `e06_orphans.py`: the same classification by node-level search with the excess bound.
