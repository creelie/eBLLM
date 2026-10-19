Version 3.1.0 of eBLLM and of Anaxia, the BLLM engine. It passes the sixth benchmark, one open
conjecture of mathematical physics proved without conditions, and it learns from its failures.

- **The seed conjecture for reflexive 4-polytopes.** Shrink a reflexive 4-polytope to the next
  reflexive polytope inside it, a cover, and repeat until no reflexive polytope fits: every such
  descent reaches a seed within 348 steps, for all 473,800,776 polytopes of the Kreuzer-Skarke list.
  Each step lowers the lattice points of the polytope and raises those of its dual, and the pairs
  of the two counts in the list admit no longer chain. The sharp constants are 5 in dimension two
  and 11 in dimension three; in dimension four the sharp constant lies between 22 and 348. Depth
  adds under free sums, and two skew bipyramids with 37 lattice points have depth exactly 22,
  computed from the complete lists of their covers. The largest polytope of the list, the simplex
  with 680 lattice points, reaches a seed in 31 steps. `src/ebllm/construct/reflexive.py` computes
  duals, covers in any dimension, descents, free sums and the chain bound.
- **The learn-from-failure loop.** A failed attempt writes a record that names the part that failed
  with its measured evidence, a diagnosis of one of nine kinds and a change of one rule of the
  engine; the next attempt runs under the changed rule and closes the record. The loop never makes
  the same change twice on a target, so it stops, and both bounds are proved in Lean
  (`lean/EBLLM/SelfMod.lean`). The log (`src/ebllm/bllm/data/modlog.json`, `anaxia modlog`) now
  holds 10 runs, 25 targets, 73 attempts and 57 rule changes; 29 of the 48 changes whose retry has
  run closed or advanced their target, and 10 targets closed.
- **Credit by the whole run.** A change can be needed without being enough, so the skill memory
  (`src/ebllm/bllm/skills.py`, `anaxia skills`) keeps each run as one hyperedge, an idea taken from
  HyperSkill (Xu, Yang and Huang, arXiv:2608.16114; no code is copied). Changes in runs that closed
  or advanced are strategies, changes in runs that only failed are patterns to avoid, and a kind of
  change used three times with less than a fifth of its runs advancing is pruned. On the present
  log it ranks the changes differently from the playbook after an overclaim, a search too large
  for its budget, and a wrong representation.
- **The other attacks of 19 October** log their failures in the same format, and their results are
  cited in the paper: simple zeros of the zeta function, more than 67.319 percent of them simple and
  on the critical line (mh-phys 1.1.0, doi:10.5281/zenodo.23483313); the Erdos-Straus exceptional
  set, whose exponent the engine's centre strips raise from 0.6608 to at least 0.6657, and numerically
  to 0.6792 (ErdosProblem1 3.0.0, doi:10.5281/zenodo.23483694); union-closed families at the entropy limit
  (eUUR 1.0.0, doi:10.5281/zenodo.23480219); generations on the Dwork quintic (strings 1.0.2,
  doi:10.5281/zenodo.23483470); the seed bounds (seed 1.0.1, doi:10.5281/zenodo.23483443); sixteen
  lonely runners; gauge-fixed mass gaps for lattice Yang-Mills; and points in convex position in
  four dimensions. None of these settles its conjecture.
- **The Hodge round, continued.** On E_0^6, family (a): every convolution with at most seven line
  bundles fails the criterion at every discriminant, and so does every object supported on the 32
  Weil threefolds, by the semiregularity map with supports (`experiments/hodge/C8_chains.md`). With
  eight line bundles 31 arrangements of shifts are left. (F2) and (F3') remain open.
- **Screens and two gates.** Rules left by failures on open problems run as exact checks
  (`src/ebllm/bllm/screens.py`). A bound on the Liouville correlations below the random-model size
  is rejected: the claimed bound of one route to the Riemann hypothesis is 129 times too small at
  X = 6000. An Erdos-Straus normal form is tested against every solution of small cases (4/73 has
  four solutions of type I), and every claimed existence of a parameter is tested on small cases
  (it fails at p = 97, q = 7). A constant defined by a series over primes is quoted only with a
  tail estimate added and agreement at two cutoffs a factor 10 apart. Construction mode gains
  definition repair, which accepts a new definition only when every changed example has a reason
  and the new one carries more consequences, and the witness gate, which admits a conditional
  result only with a witness that meets every hypothesis and is not degenerate
  (`src/ebllm/construct/reformulate.py`).
- **Six benchmarks.** The mathematical-physics benchmark joins the five open problems; it is the
  only one passed, so the superbrain label of the package is not claimed.
- **The paper** is rewritten as one text around these results, with sections on the anatomy of the
  engine and how it grew, on learning from failure, its screens and gates, and on the seed
  conjecture, and with figures and tables drawn from the package and its log. 163 unit tests pass,
  and the engine's Lean library has 44 theorems.
- **The README** is also the page of the image on ghcr.io, with its artwork drawn from the log.

What 3.0.5 brought:

Version 3.0.5 of eBLLM and of Anaxia, the BLLM engine. The paper says "makes errors" where it
said "errs": in the first sentence of the abstract, which now reads "so a check that makes errors
lets mistakes pile up", and in the sentences on checks that are wrong in both directions
(Sections 2, 4 and 11). The layout, the engine, its data and its Lean development are those of
3.0.4.

What 3.0.4 brought:

Version 3.0.4 of eBLLM and of Anaxia, the BLLM engine. It mends the layout of the appendices of
the paper. The registry of Appendix D is now a list set in the running columns
(`figures/src/make_sources_table.py`), so the one-column passage that overprinted the heading of
Appendix E is gone, and so is the page break before it, which had left the tables of Appendices B
and C on pages of their own. The REVTeX version keeps its columns ragged at the foot instead of
stretching the space between paragraphs, and the JAIR version accepts a page of floats from 60
percent full, so that its figures stay with their sections. A pass of the REVTeX version on TeX
Live 2026 takes 4.3 seconds. The version DOI of 3.0.3, 10.5281/zenodo.23467113, is recorded in
`CITATION.cff` and in the README. The engine, its data and its Lean development are those of 3.0.2.

What 3.0.3 brought:

Version 3.0.3 of eBLLM and of Anaxia, the BLLM engine. The paper compiles about two and a half
times faster: `paper/bllm/paper/figures/src/compact_figures.py` flattens the PNG figures onto white,
scales them to 1600 pixels across and gives them a 256-colour palette (with pngquant), so that
pdflatex embeds them without re-encoding. A pass of the REVTeX version on TeX Live 2026 takes
4.5 seconds instead of 11, and the figures take 3.6 MB instead of 13 MB. The text, the engine, its
data and its Lean development are those of 3.0.2.

What 3.0.2 brought:

Version 3.0.2 of eBLLM and of Anaxia, the BLLM engine. The paper (`paper/bllm`, both the REVTeX
and the JAIR version) now compiles on TeX Live 2026: the table of Appendix D no longer uses the
longtable package, whose 2026 version conflicts with the patch of it in revtex4-2 4.2f, and
`figures/src/make_sources_table.py` writes it as one tabular per row. The abstract is rewritten in
plain words, the keywords are printed on the title page, and one PDF bookmark is fixed. The
compiled paper `preprintBLLM/BLLM.pdf` is rebuilt on TeX Live 2026. The engine, its data and its
Lean development are those of 3.0.0.

What 3.0.1 recorded:

Version 3.0.1 of eBLLM and of Anaxia, the BLLM engine. It records the version DOI of release
3.0.0, 10.5281/zenodo.23464390, in the paper (`paper/bllm`, both the REVTeX and the JAIR version,
and `preprintBLLM/BLLM.pdf`), in `CITATION.cff` and in the README. The engine, its data and its
Lean development are those of 3.0.0.

What 3.0.0 brought:

Version 3.0.0 of eBLLM and of Anaxia, the BLLM engine, came with the rewritten paper of D. Bhattacharjee
and U. Bhattacharya, *BLLM: Beyond the LLM with Deep Human-Mind-AI* (`paper/bllm`).

- **Construction mode.** The engine writes down a new object together with the argument for what
  it forces and keeps it only after an independent gate. From the rules of Steinberg's problem
  alone it rebuilds the 15-vertex gadget of Cohen-Addad, Hebdige, Kral', Li and Salgado (2016),
  the 42-vertex gadget built from it, and the 166-vertex counterexample. These are rediscoveries
  of a published construction; on Erdos's question for cycles of length 4 to 6 it finds nothing.
- **Layer towers.** Builders stacked in depth, wired as a ladder or a mesh, with a bench that runs
  them at equal numbers of checks. Six Lean theorems (`paper/bllm/lean/BLLM/Tower.lean`) bound
  what depth can buy: n verified layers sharing one budget cost at least n log(n/theta), and past a
  finite depth every tower costs more than any fixed amount. The bench (120 runs) finds that depth
  pays once: on Steinberg's second gadget the builder alone never reaches the goal, a second layer
  that first builds an easier gadget and keeps it as a lemma reaches it on 7 of 10 runs, a third
  layer adds nothing (6 of 10), and the mesh shortens the step after the lemma (median 308 checks
  against 2,342). The crossing loop finds no gadget at 13 to 20 times the budget, and nothing is
  found on Erdos's question.
- **The Hodge round.** Twelve rounds of the network pointed at the Hodge conjecture alone,
  including a burst round. Every gap stays where it was: (F2) and (F3') remain open. Counting
  excludes two configurations on E_0^6 and reduces two others to explicit Massey products.
- **Sources.** A registry of every system, method and collection the engine draws on, what it
  takes from each and what it leaves, with unrefereed claims marked as such. No model weights are
  shipped in the package or in the image.
- **The paper**, rewritten as one text: the entropy law of sound self-improvement, the proposer
  bound, the tower law, construction mode, the Hodge round, hardware and reproduction, and a JAIR
  version (`main_jair.tex`). Its Lean development has 65 theorems in fifteen files, with Mathlib
  and the standard axioms only.

None of the five benchmark problems is solved. 99 unit tests, C, C++ and Julia checks, and 95 Lean
theorems in all (65 in the paper, 30 in the engine's library), each depending only on the
standard axioms.
