# Erdős problems: counts, strategies and Lean solutions

Read from the database of T. Tao and contributors, [github.com/teorth/erdosproblems](https://github.com/teorth/erdosproblems) (`data/problems.yaml` at commit `09061949`, measured 2026-10-17), from the problem pages of [erdosproblems.com](https://www.erdosproblems.com) by T. Bloom, and from the wiki page *AI contributions to Erdős problems* (frozen 30 June 2026). The pages are downloaded by `experiments/fetch_erdos.py` and are not redistributed here; `src/ebllm/bllm/data/erdos_harvest.json` keeps only the counts and the per-problem labels that `corpus.summarise_erdos` derives.

## Counts

| quantity | number |
|---|---|
| problems | 1221 |
| settled (proved, disproved or solved) | 576 |
|   proved | 336 |
|   disproved | 139 |
|   solved | 101 |
| with a Lean solution | 318 |
|   of them settled | 313 |
|   of them still open (a partial result in Lean) | 5 |
| statements formalised (Google DeepMind formal-conjectures) | 872 |
| with a prize | 107 |
|   prizes settled | 50 |

## Growth

| month | solved | solved in Lean | statements in Lean |
|---|---|---|---|
| 2025-08 | 355 | 0 | 148 |
| 2025-09 | 379 | 3 | 178 |
| 2025-10 | 407 | 4 | 199 |
| 2025-11 | 410 | 16 | 241 |
| 2025-12 | 439 | 38 | 283 |
| 2026-01 | 476 | 69 | 352 |
| 2026-02 | 483 | 110 | 374 |
| 2026-03 | 492 | 124 | 386 |
| 2026-04 | 525 | 167 | 407 |
| 2026-05 | 544 | 186 | 430 |
| 2026-06 | 547 | 199 | 473 |
| 2026-07 | 559 | 207 | 509 |
| 2026-08 | 564 | 292 | 612 |
| 2026-09 | 579 | 317 | 786 |
| 2026-10 | 579 | 318 | 872 |

## Strategies of the settled problems

The commentary of 576 settled problems was read. A strategy is assigned when the commentary names it (keyword rules in `corpus.ERDOS_STRATEGIES`); 299 pages name none, usually because they give only the solver and the reference.

| strategy | settled | with a Lean solution | share in Lean |
|---|---|---|---|
| unlabelled | 299 | 146 | 0.49 |
| counterexample | 137 | 87 | 0.64 |
| construction | 110 | 74 | 0.67 |
| density-increment | 55 | 27 | 0.49 |
| known-machinery | 48 | 29 | 0.60 |
| probabilistic | 17 | 5 | 0.29 |
| computer-search | 7 | 4 | 0.57 |
| induction-descent | 5 | 4 | 0.80 |
| fourier | 3 | 2 | 0.67 |
| entropy | 2 | 1 | 0.50 |
| lp-sdp-certificate | 1 | 0 | 0.00 |

The commentary names an AI system (GPT, Gemini, AlphaProof, AlphaEvolve, Aristotle, Claude, Seed-Prover and others) for 60 settled problems, 46 of them with a Lean solution (0.77, against 0.54 over all settled problems).

## AI contributions (wiki)

538 entries on 405 problems; 115 problems have an entry marked as a full solution.

| outcome | entries | entries marked as checked in Lean |
|---|---|---|
| full | 137 | 33 |
| partial | 151 | 34 |
| incorrect | 19 | 0 |
| unverified | 43 | 3 |
| other | 188 | 0 |

No entry marked as checked in Lean is marked incorrect: the 19 incorrect AI contributions all lack a Lean check.

## Use in the package

`benchmark.corpus_prior(stats, harvest=...)` averages, for every move, the Lean-formalised share of the OpenAI manuscripts that use it with the Lean-solved share of the settled Erdős problems that use it (`benchmark.ERDOS_TO_MOVE` maps the strategies to moves), and gives the router ten pseudo-counts of that rate. `experiments/benchmark_curve.py` measures what the prior changes.
