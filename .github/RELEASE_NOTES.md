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
