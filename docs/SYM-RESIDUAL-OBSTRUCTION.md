# Residual-dimension obstruction for null-projected SYM

Preceding preprint: [hexagon:2610.00471v1](https://hexagonmath.org/2610.00471v1). Original source and numerical checks: [creelie/cs-grav](https://github.com/creelie/cs-grav), commit `3b9a3767aa637295f79d6f2d21db2b2d4f5b3576`. Author: Deep Bhattacharjee. The 24 October 2026 revision was prepared with OpenAI Codex assistance.

The result is a necessary condition for the precisely defined class (N1)--(N5): a single chiral constrained gaugino, the stated transformation rules, nontrivial residual gauge variation and translation bracket, and absorption of the quadratic gaugino variation into a vector current. The revised definition makes the graded symmetry of the translation structure constant explicit.

For a Majorana-Weyl gaugino and a null frame of rank k, the proof gives:

- k <= min(s,t);
- residual dimension s+t-2k is 2 or 10;
- s-t belongs to {-8,0,8}.

`passes_signature_obstruction(s,t)` checks this necessary condition. The compatibility function `theory_allowed(s,t)` has the same limited meaning. A true return value does not construct a theory or prove sufficiency. Several gauginos, extra fields, nonlinear transformation rules or other realization mechanisms require a separate analysis.

The core converse is algebraic. Contracting the cubic gamma-matrix identity in two different pairs of spinor indices gives N-(d-2)=-2j(d-2) and jN=-(d-2). Hence N=2(d-2), j=-1/2. Clifford-module divisibility leaves d=3,4,6,10. The null-frame projection then leaves the ten-dimensional case for residual dimension greater than two.

The revised reduction constructs the residual vector structure explicitly through the nondegenerate pairing isomorphism iota. The source current is fixed directly by contraction, J^nu=-kappa(d-2)/N gamma^nu(S); no Schur-multiplicity argument is needed. In the ten-dimensional residual case this gives coefficient -kappa/2. Taking the non-residual components to vanish solves the absorption identity for every supersymmetry parameter, since both sides depend only on its empty-corner component. This solves that algebraic absorption condition, not the separate full transformation and closure construction.

A new written null-current lemma explains why the (k+1)-form current of constrained spinors is a wedge of the null-frame volume with a residual one-form. It supplies an explicit step in comparison with Nishino's equations, instead of relying on a numerical sample.

For one time, the independent massless-multiplet argument assumes a unitary positive-energy representation and vanishing tensor charges on the multiplet. With S real supercharges, the active algebra has S/4 complex creation operators, giving at least 2^(S/4) states. State counting alone does not exclude arbitrary multiplicities of low-spin fields. The revised manuscript also proves that these creation operators all raise a chosen transverse helicity by 1/2, giving helicity span at least S/8 for a finite helicity spectrum. Scalar, spinor and vector polarizations lie in [-1,1], so arbitrary finite multiplicities of those fields require S<=16.

`helicity_bound(n)` reports the exact resulting numbers in signature (9+8n,1). At n=1, S=256, there are 64 creation operators, and the helicity span is at least 32. This is a consequence of a written representation argument, not a numerical proof of general supersymmetry.

The archived 34 explicit gamma-matrix checks were freshly rerun on 24 October 2026 and all passed with NumPy 2.4.3 and SciPy 1.17.1. They are supplementary floating-point diagnostics. The engine retains formal=0 and human=0: it does not claim a full Lean formalisation or referee approval, and it does not convert necessary conditions into existence claims.
