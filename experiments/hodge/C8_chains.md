# Convolutions with at most seven line bundles at E_0^6 fail the criterion

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

## What C8 now asks

* Eight to eleven line bundles: one piece with at least eight line bundles must carry both parities; with
  eight the 31 configurations above.
* Twelve or more: also two or more pieces.
* In every case the decision is the rank of y -> (D(y)_{TT})_T against ev_T(TD), with the Fourier and twist
  conditions of Lemma 1 on the threefolds present.

## Checks

* `e06_six.py N` for N = 4 to 8; log in `e06_six.log`. The run table
  it prints (threefold shifts allowed in a run of each excess) agrees with Lemma 4: excess 1 puts the
  threefold at s + 1, the decreasing run of excess 3 puts its two threefolds at s + 1 and s - 1.
* It reproduces Theorem 6: no configuration with four or five line bundles keeps a live chain.
