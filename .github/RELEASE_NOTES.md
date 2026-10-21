Version 3.3.0 of eBLLM and of Anaxia, the BLLM engine, uploaded by a second agent on Tubai's command.
It carries the attempts of 21 October 2026 on four of the engine's targets, each with its
constructions, walls and records. None of the four target conjectures is closed.

- **Hodge: three results and five construction rounds.** Seven shifts on E₀⁸ (18 of 28 arrangements
  by hand, 9 by linear programming, one open), an étale Prym map at genus four that is a local
  isomorphism onto the Weil domain of Q(√−3) at n = 3 (`construct/genus_four_prym.py`), the sextic
  CM fields over twelve cubic fields, the residue-and-mass reading of the conjecture, and five rounds
  on (F3') that each learned from the one before and stopped on the walls `zero-cycles-core`,
  `odd-cross-classes`, `lefschetz-inverse` and `f3prime-needs-cycle`: only a new algebraic cycle on
  B × X can advance (F3').
- **Strings: the mirror clause of the Geometric Selection Conjecture is empty.** A vacuum of L^μ
  fixed by the mirror involution is isomorphic to its mirror, so χ(X) = 0, c₃(V) = 0 on its
  component and the index c₃/2 vanishes: it has no net families and fails (C2). Hence the conjecture
  is equivalent to the existence of a viable vacuum on a component carrying no standard embedding,
  and no standard embedding is ever selected (`construct/gsc_mirror_fixed.py`; the note of
  creelie/geometric-selection-conjecture 1.0.0, by Deep Bhattacharjee and Ushashi Bhattacharya).
  Control `gsc-mirror-clause`, a partial result, CANDIDATE; the stage `s.mu-fixed-chi0` of the
  superstring chain holds the proof as a claim. The existence statement stays open: (C7) to (C9)
  are fixed by comparison with measurement and no published model establishes all three (wall
  `no-model-has-c7-c9`).
- **TheoPhysEval (arXiv:2610.16733).** The benchmark proves no theorem and closes no gap; two of its
  problems carry exact constructions, π from the Euler beta function and the hidden zeros of a
  four-point residue, now in `construct/theophys.py` with checks and refuters.
- **Lehmer and the brane gas.** Lehmer's problem as one divisor (`construct/lehmer_equiv.py`, the
  Fermat chain as refuter of the companion equation), the barriers to a non-perturbative brane-gas
  statement, and the animated results board (`docs/assets/make_results.py`).
- **Counts.** 281 unit tests, 36 controls, 39 trajectories in the skill memory; the Lean development
  is that of 3.2.0. The version DOI of release 3.2.1, 10.5281/zenodo.23524945, is recorded in
  `CITATION.cff` and in the README. The paper is not rewritten in this release.
