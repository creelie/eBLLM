<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-banner-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-banner-light.svg" alt="Anaxia, the BLLM engine" width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/creelie/eBLLM/releases/latest"><img src="https://img.shields.io/github/v/release/creelie/eBLLM?label=release&color=7c3aed" alt="latest release"></a>
  <a href="https://github.com/creelie/eBLLM/actions/workflows/ci.yml"><img src="https://github.com/creelie/eBLLM/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/creelie/eBLLM/actions/workflows/package.yml"><img src="https://github.com/creelie/eBLLM/actions/workflows/package.yml/badge.svg" alt="image build"></a>
  <a href="https://github.com/creelie/eBLLM/pkgs/container/bllm-engine"><img src="https://img.shields.io/badge/container-ghcr.io%2Fcreelie%2Fbllm--engine-0d9488" alt="container"></a>
  <img src="https://img.shields.io/badge/Lean%204-109%20theorems%2C%20axioms%20audited-6d28d9" alt="Lean 4, 109 theorems, axioms audited">
  <img src="https://img.shields.io/badge/python-3.9%20%7C%203.12%20%7C%203.13-3776ab" alt="Python 3.9, 3.12, 3.13">
  <a href="https://doi.org/10.5281/zenodo.23286641"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.23286641.svg" alt="DOI"></a>
  <a href="https://github.com/creelie/eBLLM/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-64748b" alt="MIT licence"></a>
</p>

```sh
docker pull ghcr.io/creelie/bllm-engine:latest
docker run --rm ghcr.io/creelie/bllm-engine --version
docker run --rm ghcr.io/creelie/bllm-engine modlog          # every failure, the rule it changed, the retry
docker run --rm -it --entrypoint bash ghcr.io/creelie/bllm-engine
```

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-numbers-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-numbers-light.svg" alt="21,515 composites bred, 64 survive; 46.4 checks with memory against 95.2 without; human ideas at 1.08 times the proposer bound against 1.5 to 4.3 for language models; every reflexive descent of a reflexive 4-polytope reaches a seed within 348 steps; 18 changes of its own rules after 20 attempts that did not close; 1 of 6 benchmarks crossed" width="100%">
  </picture>
</p>

Anaxia does not guess at proofs. It holds the constructions that mathematicians have already
made, each typed by what it gives and what it needs, and it breeds new candidates by plugging the
output of one into an input of another. A candidate counts only when a program checks it, a
refuter fails to break it, and whatever is stated as proved goes through the Lean kernel. Every
verdict is written to memory, so the engine never pays twice for the same question. And when an
attempt fails, the engine names the reason, changes one of its own rules, and tries again under
the new rule. The cards above are its measured record, the last one included.

## New in 3.1.0

- **It learns from its failures.** Every failed attempt now writes a record: what was tried, why
  it failed, which rule of the engine was changed (its old and its new value), what the change was
  meant to improve, and what the next attempt under the new rule did. `anaxia modlog` prints the
  log. The loop never makes the same change twice, so it stops; the bound is proved in Lean.
- **It crossed its mathematical-physics benchmark.** The Calabi–Yau seed conjecture closes.
  Shrink a reflexive 4-polytope to the next reflexive polytope inside it, never skipping one, and
  repeat until none fits: from any of the 473,800,776 polytopes of Kreuzer and Skarke, every such
  descent reaches a seed within 348 steps. Each step loses lattice points while the dual gains
  them, and the pairs of counts that occur in the classification allow no longer chain, so no
  descent had to be searched. The sharp constant is 5 in two dimensions and 11 in three; in four
  it lies between 9 and 348.
- **44 engine theorems in Lean.** Added: the bounds of the loop and of a descent of
  lattice-point counts (`lean/EBLLM/SelfMod.lean`), and the eight theorems of the Hodge gaps,
  which earlier releases carried but did not build. Every one depends only on `propext`,
  `Classical.choice` and `Quot.sound`.
- **A map of itself.** The diagrams below are read from the package: its parts and how they are
  wired, the loop and what it changed, and how the engine grew from release to release.

**Contents:** [How it thinks](#how-it-thinks) · [The round](#the-round) ·
[It learns from failure](#it-learns-from-failure) · [Point it at a conjecture](#point-it-at-a-conjecture) ·
[Proved](#what-anaxia-has-proved) · [Measured](#what-the-runs-show) ·
[It builds](#it-builds-too) · [How it grew](#how-it-grew) · [Draws on](#what-it-draws-on) ·
[Not done](#what-it-has-not-done) · [Install and update](#install-and-update) ·
[Commands](#commands) · [Add a target](#add-a-target) · [The paper](#the-paper) ·
[Labels](#labels-of-the-recorded-results) · [Checks](#checks) ·
[Releases](#releases-and-the-closure-rule) · [Layout](#layout) · [Citing](#citing)

## How it thinks

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-brain-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-brain-light.svg" alt="The parts of Anaxia as a brain: sensing (knowledge and proposers), integrating (laws and the crossing network), acting (construction mode, benchmarks, core and interface), and memory feeding the result of each attempt back into the next" width="100%">
  </picture>
</p>

The engine has nine parts, and a problem passes through them in the order of a brain. It
**senses** through its knowledge (the libraries of published constructions and the indexes of
settled problems) and its proposers. It **integrates** through the laws that schedule the checks
and the crossing network that combines constructions by type. It **acts** through construction
mode, the benchmarks, the verified core and the command line. And it **feeds back** through
memory, which keeps every verdict and, since this release, every rule change. The size of each
part on the diagram is its number of modules and lines of code, counted from the source.

## The round

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-round-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-round-light.svg" alt="One round of Anaxia: target point, channel, proposers, check, refuter, Lean, memory and boosters, each with a measured number" width="100%">
  </picture>
</p>

A round starts from a **target point**, the one statement that would settle the problem, and ends
with its distance measured again. In between, the **channel** hands the proposers everything the
memory holds on that target, the **proposers** fill typed inputs, a **check** program decides each
closed composite, the **refuter** tries to break what was accepted, and **Lean** certifies what is
stated as proved. Verdicts go to **memory**; **boosters** reweight the synapses between
constructions for the next round. Every tag on the diagram is a measured number.

## It learns from failure

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-loop-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-loop-light.svg" alt="The learn-from-failure loop: attempt, fail, record, change one rule, retry; with the kinds of rule that were changed and what the retries did" width="100%">
  </picture>
</p>

An attempt that fails is not thrown away. The engine writes one record for it: the target, the
evidence, a diagnosis of which part failed (the generator, the filter, the scale of the search,
the arrangement, the retrieval, or a mode the engine did not have), and one change to its own
rules, with the old value, the new value and the number the change is meant to move. The next
attempt runs under the changed rules, and its outcome is written back into the record as the
result of the change. A change it has already made on the same target is refused, so a retry is
never the same attempt again.

```console
$ anaxia modlog
construction: 17 attempts, 13 rule changes, 3 retries closed or advanced; outcomes {'closed': 3, 'partial': 0, 'failed': 11, 'stopped': 3}
  Steinberg gadget (k = 5) #1: missing-mode -> mode (mode: crossing and construction (exists-forall SAT over graphs)) -> failed
  Steinberg gadget (k = 5) #2: filter-cost -> representation (planarity: planar frames: gadgets glued at terminals on one face) -> failed
  Steinberg gadget (k = 5) #3: generator -> strategy (generation: goal-directed builder: grow the forcing argument with the graph) -> closed
  SAT search, profile (3, 3, 4) #1: filter-cost -> representation (planarity: 2-page book embedding along a fixed spine) -> closed
  level-two gadget (contact distances ≥ 4) #1: rules-silent -> library (lemmas: every stored forcer is a lemma rule, applied by case split) -> closed
  Erdős's question, k = 6 #1: generator -> reduction (target: one gadget: not-all-equal, no 4-, 5-, 6-cycles, contact distances (3, 3, 5) or (5, 5, 3)) -> failed
  Erdős's question, k = 6 #2: scale -> representation (search: compressed search: each proved gadget is one hub node) -> failed
  Erdős's question, k = 6 #3: arrangement -> representation (moves: face-aware moves on one face of the current drawing) -> failed
  Erdős's question, k = 6 #4: arrangement -> strategy (search space: search over planar arrangements of the forcing argument) -> not yet built
  ...
```

`anaxia modlog --patterns` ranks the kinds of change by what they achieved, and the loop uses
that ranking when it picks the next change. Two theorems in
[`lean/EBLLM/SelfMod.lean`](https://github.com/creelie/eBLLM/blob/main/lean/EBLLM/SelfMod.lean)
say why it stops: the changes form a list without repetitions inside the finite set of changes
the playbook can propose, so there are at most as many changes as that set has members
(`loop_changes_le`) and one more attempt than changes (`loop_attempts_le`).

## Point it at a conjecture

The Hodge library holds the constructions of the Hodge papers and the literature around them.
Five crosses, each filling one typed input, take the reduction of (F2) to its lift from CM points
down to a closed composite, and the check says exactly what is missing:

```python
from ebllm.bllm import hodge as H
from ebllm.bllm.targets import cross

lib = {c.id: c for c in H.LIB}
c = lib["p.propagation"]                    # (F2) iff algebraicity lifts from CM points
for part in ["p.criterion", "p.product", "h8.markman", "p.cmpoint"]:
    c = cross(c, lib[part])                 # fill one typed input at a time
print(c.gives, sorted(c.needs))
r = H.check_hodge(c)
print(r.outcome, r.node)
print(r.statement)
```

```text
f2-lift []
stopped H.F2.lift
the product object has the polarised shape and Hankel rank 3, so the criterion asks dim Ext^2 = 57 at a CM point; this is the E_0^6 target, not yet met
```

The composite is well typed and closed, and it reaches the node of the target point, but it stops:
the semiregular object it needs does not exist yet. That is the shape of most of what Anaxia
returns on an open problem, a precise statement of the one missing input, recorded so that no later
round checks it again. `anaxia attack hodge` prints the open steps of the task, their ladders of
known cases, and the plan.

## What Anaxia has proved

The theorems of the paper and of the engine, each with its Lean proof (only `propext`,
`Classical.choice` and `Quot.sound`; the audits are `paper/bllm/lean/axioms.txt` for the paper,
which uses Mathlib, and `lean/Audit.lean` for the engine, which uses Lean core only).

| result | statement | proof |
|---|---|---|
| Entropy law | certifying self-modifications of total cost A with at most θ expected false acceptances costs (A/log ε⁻¹)(H(p) + log θ⁻¹), up to an additive A that cannot be lowered | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/EntropyLaw.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `entropy_lower`, `verification_lower` |
| Huffman schedules | for ε = 1/D and θ = D⁻ᵏ the sound schedules are prefix codes shifted by k, so the optimum is a Huffman code | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Kraft.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `kraft_of_schedule`, `schedule_of_kraft`, `shifted_cost` |
| Rényi law | checks of polynomial order s cost A θ⁻ˢ e^{s H_α(p)} at the optimum, α = 1/(1+s) | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Renyi.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `renyi_lower`, `renyi_attain` |
| Proposer bound | a proposer needs at least (Σ √πᵢ)² = e^{H½(π)} proposals in expectation, and square-root sampling attains it | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Gap.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `search_lower`, `search_optimal` |
| Sound singularities | a sound infinite self-improvement of finite cost exists exactly when Σ aₙ log(1/aₙ) converges | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Singularity.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `sound_schedule_iff` |
| False acceptances | finitely many almost surely exactly when Σ ε^{rₙ} converges | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Soundness.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `false_accepts_finite`, `false_accepts_infinite` |
| Branching takeoff | a fixed false-acceptance rate, however small, makes the kept errors of an explosive takeoff diverge; amplified checks keep them finite | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Branching.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `contamination_diverges`, `amplified_summable` |
| Gating | outcome gating costs (1−ρ)^{−(n−1)} times step gating with perfect checks | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Gating.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `step_precision`, `separation` |
| Weak before strong | the optimal number of cheap checks before an expensive one, with matching bounds | <a href="https://github.com/creelie/eBLLM/blob/main/paper/bllm/lean/BLLM/Agents.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `cascade_lower`, `cascade_upper` |
| The loop stops | a loop that never repeats a change for a target makes at most as many changes as the playbook can propose, and one attempt more | <a href="https://github.com/creelie/eBLLM/blob/main/lean/EBLLM/SelfMod.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `loop_changes_le`, `loop_attempts_le` |
| Short descents | a descent in which every step moves an integer strictly up, or strictly down, inside [lo, hi] has at most hi − lo steps | <a href="https://github.com/creelie/eBLLM/blob/main/lean/EBLLM/SelfMod.lean"><img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-lean.svg" alt="Lean 4, kernel-checked" height="20"></a> `descent_steps_le`, `descent_steps_le_of_decreasing` |
| Seed descents | every reflexive descent of a reflexive 4-polytope reaches a seed within 348 steps, so the Calabi–Yau seed conjecture holds; the sharp constants are 5 in two dimensions and 11 in three | <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-text.svg" alt="proof in the text" height="20"> the counting step is `descent_steps_le_of_decreasing` |
| Lattice SU(2) gap | four-dimensional SU(2) lattice Yang–Mills has a mass gap for β_W < 1/3, and 1/3 is the ceiling of the method; not yet refereed | <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/badge-text.svg" alt="proof in the text" height="20"> finite parts in `lean/EBLLM/GaugeFix.lean` |

## What the runs show

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-amplified-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-amplified-light.svg" alt="The amplified round: 21,515 bred, 1,466 closed, 99 accepted, 64 survive" width="49%">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-memory-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-memory-light.svg" alt="Memory halves the checks to the plateau" width="49%">
  </picture>
</p>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-agents-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-agents-light.svg" alt="Five agents reach 24 survivors for 250 checks, one loop 27 for 797" width="49%">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-proposers-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-proposers-light.svg" alt="Human ideas at 1.08 times the proposer bound, language models at 1.5 to 4.3" width="49%">
  </picture>
</p>

- **Typing does the work.** Random pairing wastes 45 of 48 crosses on ill-typed pairs; only typed
  crossing reached the composite for the β_W < 1/3 gap, in every run.
- **Memory halves the cost** of reaching what the libraries can reach, and does not raise the
  plateau: every arm ends between 6.0 and 6.4 survivors, all of them known results.
- **Agents are cheaper and reach no further** than a single loop.
- **Human research ideas sit within 8% of the proposer bound**; nine language models need 1.5 to
  4.3 times the optimum number of proposals.
- **Hebbian boosters add nothing:** 12 and 14 of 200 runs reached the step, against 21 without
  them. The channel saves 3% of the checks.

Every chart is drawn by [`docs/assets/make_art.py`](https://github.com/creelie/eBLLM/blob/main/docs/assets/make_art.py) from the data files of
the runs.

## It builds, too

The crossing network only combines constructions it already holds. **Construction mode** writes
down a new object together with the argument for what it forces, and then checks the object with
code that shares nothing with the search: planarity by networkx, short cycles by depth-first
search, distances by breadth-first search, colourability by backtracking and by three SAT solvers.

The calibration target is Steinberg's conjecture, refuted in 2016 by Cohen-Addad, Hebdige, Kráľ,
Li and Salgado with a 15-vertex gadget G1 and a 42-vertex gadget G2 built from it. Construction
mode was given the rules (no 4- or 5-cycles, planar with the contacts on one face, contact
distances) and nothing about the answer.

| target | method | outcome |
|---|---|---|
| gadget with contact distances 3, 3, 4 | random planar frames filled with library gadgets | none in 2.45 million frames |
| the same | goal-directed builder, rules only | Steinberg's G1, contacts matched, on try 116 after 11 s |
| the same | exists-forall SAT search over 2-page book embeddings | a 15-vertex, 23-edge gadget in 2.5 s |
| contact distances all at least 4 | builder, rules only | out of reach: from contacts this far apart the rules derive nothing |
| the same | builder with G1 and a triangle gadget as lemmas | Steinberg's G2, contacts matched, on seeds 6 and 8 (tries 13 and 9); a 48-vertex gadget with distances 5, 4, 5 on seed 5 (try 8, 3.5 s) |
| the whole counterexample | `construct assemble` on the rediscovered G1 | 166 vertices, planar, cycles of length at most 6 only 3 and 6, not 3-colourable by CaDiCaL, Glucose and MiniSat |
| Erdős's question (no 4-, 5- or 6-cycles) | all of the above | nothing found; it stays open |

These are rediscoveries of a known counterexample, not a new theorem; they show that the engine
can invent a construction it was not given. Each run needs one CPU and about 40 MB.

```sh
anaxia construct steinberg                       # rebuild the 2016 counterexample and check it
anaxia construct list                            # the stored gadgets and their checks
anaxia construct build --forbid 4 5 --dist 0,1,3 0,2,3 1,2,4 --max-n 40 --tries 116 --seed 1
anaxia construct build --forbid 4 5 --dist 0,1,4 0,2,4 1,2,4 --max-n 80 --max-steps 400 \
    --lemmas rediscovered_n15 T --tries 9 --seed 8     # G2 from G1 used as a lemma
anaxia construct assemble rediscovered_n15 --forbid-max 5
```

### Layers of builders

`anaxia construct tower` stacks the builder into a tower of depth n. Layer 1 is the builder above.
Layer 2 evolves the builder's policy (which rule to apply first, how far to grow, which stored
gadgets to try as lemmas) and scores each policy by exact checks, as FunSearch evolves programs
against an evaluator; it also solves the target's weaker contact profiles first and keeps what they
yield, as AlphaProof's curriculum does. Layer k ≥ 3 runs successive halving over the policies of
layer k − 1. In a **ladder** each copy keeps its own library and passes only results up; in a
**mesh** all layers read and write one library of found gadgets, and Hebbian weights on the kinds
of move, strengthened by the moves of every gadget found and decaying otherwise, bias the
policies of every layer. Every gadget a layer passes up goes through the independent gate first,
and the budget of every run is counted in exact SAT checks, so depths and wirings are compared at
equal cost. `anaxia construct bench` runs depths 1, 2 and 3, ladder and mesh, against the crossing
loop of the network on Steinberg's G1 and G2 and on Erdős's question, five seeds each.

The bench (120 runs, 5.6 processor-hours; raw rows in
`src/ebllm/construct/data/tower_bench.jsonl`, summary in `tower_bench_summary.json`) gave this:

| Target, budget | Crossing loop | Depth 1 | Depth 2 (ladder / mesh) | Depth 3 (ladder / mesh) |
|---|---|---|---|---|
| G1, distances 3,3,4, 10,000 checks | 0/5, also at ~128,000 checks | 5/5, median 1,635 | 5/5 / 5/5, median 766 | 5/5 / 5/5, median 759 |
| G2, distances ≥ 4, 25,000 checks | 0/5, also at ~410,000 | 0/5 | 3/5 / 4/5 | 3/5 / 3/5 |
| Erdős, 3,3,5, no 4- to 6-cycles, 20,000 checks | 0/5 | 0/5 | 0/5 / 0/5 | 0/5 / 0/5 |

Depth paid once. On G2 the builder alone never reaches the goal; layer 2 first builds a gadget
with the profile 3,3,4, keeps it as a lemma and reaches the goal from it on 7 of 10 runs, and
layer 3 adds nothing (6 of 10). After the lemma the mesh needs a median of 308 checks to the goal
against 2,342 for the ladder, fewer on 6 of 7 paired runs. On G1 five seeds do not separate the
depths, and on Erdős's question nothing is found by any configuration.

Six theorems in `paper/bllm/lean/BLLM/Tower.lean` bound what depth can buy. With a total
false-accept budget θ shared by n verified layers, certification costs at least n log(n/θ)
(`tower_cost_lower`, and `tower_checks_lower` in checks); each added layer raises the bound by at
least log((n+1)/θ) (`tower_increment`), without limit (`tower_increment_unbounded`); so past a
finite depth a deeper tower costs more than any fixed cost (`tower_saturates`), and along an
infinite tower with summable budgets the cost of a single stage tends to infinity
(`stage_cost_diverges`). The tower is read as a Postnikov tower in one precise sense, the
increment of cost per stage; the rest of that picture is an analogy.

```sh
anaxia construct tower steinberg-g2 --depth 2 --mesh --budget 25000 --seeds 1
anaxia construct bench --targets steinberg-g1 steinberg-g2 erdos-k6 --seeds 1,2,3,4,5 --jobs 3
```

## How it grew

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-growth-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-growth-light.svg" alt="Lines of Python in each part of Anaxia at each minor release, with the tests and Lean theorems of each" width="100%">
  </picture>
</p>

Each release added a new kind of part rather than more of an old one, and each part was written
after a run of the previous release failed in a way its log could name. The crossing network came
because single proposers drew ill-typed pairs; construction mode, because crossing has nothing to
combine where an object is missing; the tower of builders, because one builder stalled at the
second gadget of Steinberg's counterexample; and the loop of this release, because until now those
failures and their repairs were written in prose. From 3.1.0 on they are records the engine
reads.

## What it draws on

`anaxia fetch deepmind` and `anaxia intake deepmind` hold the survey of all 409 public
repositories of Google DeepMind: 22 are pinned at exact commits for their mathematics (Formal
Conjectures, the AlphaProof Nexus results, AlphaEvolve's results and problem repository, FunSearch,
AlphaGeometry, the IMO, Putnam and miniF2F formalisations and others), 14 are recorded as related,
and the rest are left out with a reason. Their 5,035 items (1,471 open and 2,437 solved Formal
Conjectures statements among them) are indexed in the package and load into memory as literature,
so the engine asks whether a target is already settled before it attacks it. Nothing fetched is
executed. [`THIRD_PARTY.md`](https://github.com/creelie/eBLLM/blob/main/THIRD_PARTY.md) lists every source, its licence and what was taken.

Every system, corpus and method the engine takes from is in one registry,
`src/ebllm/bllm/data/sources.json`, with its reference, its status (refereed, preprint, software,
unrefereed), what was taken, the module that implements it, what Anaxia adds and what was left
out. `anaxia sources check` searches the DeepMind index together with two more: the 782 problem
dossiers of OpenRefute (The Omega Institute), each a published conjecture with its kernel-checked
resolution, and the 722 manuscripts of OpenAI's mathematics collection, every one marked
unrefereed. No model weights are bundled in the package or the image.

```sh
anaxia sources list                              # the registry, by group
anaxia sources show funsearch                    # one entry in full
anaxia sources check "planar graph without cycles of length 4 and 5 is 3-colourable"
anaxia sources summary                           # statuses in the indexes
```

<details><summary>The registry (35 entries)</summary>

| source | group | taken | where in Anaxia |
|---|---|---|---|
| FunSearch | Google DeepMind | evolve and evaluate: a population of strategies, each scored by an exact evaluator; the better ones are kept… | src/ebllm/construct/tower.py (Layer2); the funsearch constructions are indexed… |
| AlphaEvolve | Google DeepMind | the evaluation cascade: cheap tests discard most candidates before the expensive test, and the evaluator,… | src/ebllm/construct/proof_builder.py (try_add: forbidden cycles, contact… |
| AlphaProof | Google DeepMind | a curriculum: easier variants of the target are solved first and what they yield is kept for the target | src/ebllm/construct/tower.py (Layer2.profile: the target's weaker contact… |
| AlphaGeometry | Google DeepMind | deduction run to a fixed point, with a construction proposed only when deduction stalls | src/ebllm/construct/proof_builder.py (status: the shared colour spreads by… |
| AlphaGeometry2 | Google DeepMind | nothing beyond AlphaGeometry's division of labour; pinned and fetchable | anaxia fetch deepmind alphageometry2 |
| Formal Conjectures | Google DeepMind | the statements with their open or solved status: the target catalogue and the check that a target is still… | src/ebllm/bllm/deepmind.py (index, Search); anaxia intake deepmind --search |
| Mathematics dataset | Google DeepMind | pinned as a generator of warm-up questions for a local proposer | anaxia fetch deepmind mathematics_dataset; experiments/ fine-tuning script |
| AlphaTensor | Google DeepMind | the decompositions, indexed as library constructions | src/ebllm/bllm/deepmind.py |
| AlphaDev | Google DeepMind | the sorting programs, indexed | src/ebllm/bllm/deepmind.py |
| Mathematics conjectures (Davies et al.) | Google DeepMind | the notebooks, indexed | src/ebllm/bllm/deepmind.py |
| Aletheia and LEAP (superhuman) | Google DeepMind | the generate, verify and revise loop with a verifier independent of the generator, which is the refuter… | src/ebllm/bllm/superbrain.py and hodge.py (the refuter pass);… |
| Successive halving | Methods | keep the better half of the arms after each round | src/ebllm/construct/tower.py (LayerK) |
| Hebbian learning | Methods | a connection used in a success is strengthened and every connection decays | src/ebllm/construct/tower.py (Mesh.reinforce, Mesh.bias) |
| Postnikov towers | Methods | the framing of the layer tower: stage n is the engine cut at depth n and each stage is the one below with… | paper; Lean BLLM.tower_increment states the precise part (each added layer… |
| OpenAI mathematics manuscript collection | OpenAI | the move statistics of the crossing network and an index of the manuscripts for the check that a target is… | src/ebllm/bllm/corpus.py (read_openai); src/ebllm/bllm/sources.py (index_openai) |
| OpenAI Navier-Stokes Lean proof | OpenAI | a literature row with its status; its build record applies the rule of Anaxia's Lean check (kernel check,… | src/ebllm/bllm/sources.py (registry) |
| trureturing (OpenRefute) | The Omega Institute | an index of the 782 problem dossiers (statement, resolution, Lean declaration, link): refuter data, since it… | src/ebllm/bllm/sources.py (index_openrefute); anaxia sources check |
| obsidian-brain | Memory | memory as a vault of linked notes, and retrieval that returns each hit with its link neighbours | src/ebllm/bllm/vault.py (Vault.write; Vault.search: TF-IDF over the notes plus… |
| claude-obsidian (lab009dm) | Memory | notes captured with their provenance and linked to what they were built from | src/ebllm/bllm/vault.py |
| RealMythos | Memory | nothing: its content is vulnerability analysis; its staged layout (data, model, environment, traces) is… | not used |
| Advanced Reasoning MCP | Memory | the TF-IDF ranking of its memory search | src/ebllm/bllm/deepmind.py (Search) |
| ultra-mathematician | Agents | the closure policy: closed only after a kernel-checked Lean endpoint with an audited statement and allowed… | the labels of anaxia controls and the release rule |
| mathcode | Agents | only a strict check of one fully qualified declaration certifies completion, and stored assumptions are… | the Lean verifier and the axiom audit (anaxia axioms) |
| open co-scientist (lab007dm) | Agents | nothing in code: the tournament of hypotheses was considered and not built, since the checks and the refuter… | not used |
| OpenConjecture (lab010dm) | Corpora | the candidate pool for conjecture attacks; six Hodge-related conjectures entered the Hodge library | experiments/hodge/absorb_sources.py |
| DeepSeek-Prover-V2 | Provers and models | can serve as the proposer through an OpenAI-compatible server; its subgoal decomposition is the split of an… | src/ebllm/bllm/proposers.py (provider local) |
| Kimina-Prover | Provers and models | can serve as the proposer through the local connector | src/ebllm/bllm/proposers.py (provider local) |
| Goedel-Prover | Provers and models | can serve as the proposer through the local connector | src/ebllm/bllm/proposers.py (provider local) |
| Qwen2.5-Math | Provers and models | can serve as the proposer through the local connector; experiments/finetune/finetune.py fine-tunes a Qwen2.5… | src/ebllm/bllm/proposers.py (provider local) |
| Mathstral | Provers and models | can serve as the proposer through the local connector or the mistral provider | src/ebllm/bllm/proposers.py (providers local, mistral) |
| HyperTree Proof Search (Meta AI) | Provers and models | search over an AND-OR tree of goals, which is the shape of Anaxia's obligation graph | src/ebllm/obligations.py |
| LeanDojo | Provers and models | premise retrieval: proposals are prompted with retrieved library nodes | src/ebllm/bllm/memory.py (retrieval) |
| Seed-Prover | Provers and models | lemma-style proving, in which proved lemmas are kept and reused: the same shape as the lemma library of… | src/ebllm/construct/tower.py (Library) |
| Aristotle (Harmonic) | Provers and models | informal reasoning checked step by step in Lean, which is the contract of Anaxia's verifier | not used |
| Language-model APIs | Provers and models | proposers behind one interface; keys come from the environment | src/ebllm/bllm/proposers.py |

</details>

```sh
anaxia fetch deepmind --list                     # the pinned repositories, commits and licences
anaxia fetch deepmind formal-conjectures         # a checkout at the pinned commit
anaxia intake deepmind --search "minimum degree 3 cycle of length a power of two" --status open
anaxia intake deepmind --memory memory.db        # the index as literature rows
```

## What it has not done

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-hodge-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/chart-hodge-light.svg" alt="The Hodge-only run: checks per round and no new result" width="49%">
  </picture>
</p>

- Of its six benchmarks it has crossed one, the mathematical-physics benchmark, with the
  Calabi–Yau seed conjecture. The five problems it started with stay open: the Yang–Mills mass
  gap, the Hodge conjecture, Grothendieck's standard conjecture B, Chowla's conjecture and Erdős
  problem 1183. In four dimensions the sharp seed constant, the fewest steps that suffice for every
  polytope, is not yet known; it lies between 9 and 348.
- It did not originate the step it is best known for. The composite for the β_W < 1/3 gap was
  first proposed by the language-model proposer and then entered in the library; the network
  reproduces it.
- Every survivor of the amplified round is a form of a range already proved, or (F2) in dimension
  at most five, which was known.
- The Hodge-only run of eleven rounds produced no survivor that was not already known and reached
  no target point (chart above).
- Two changes of its log are not yet built (search over planar arrangements, for Erdős's
  question and the Bordeaux conjecture), so those retries have not run.
- No result of the project is refereed, so every one of them is labelled CANDIDATE.

## Install and update

The image holds the installed package, the Lean library built with its pinned toolchain, the C and
C++ checks with a compiler, the agents and memory, the task suite and the experiments, with numpy,
python-sat, networkx and pyyaml. Julia and the GPU stack of `experiments/finetune` are not in it.

**It keeps itself current.** Every merge to `main` and every release rebuilds the image and
publishes it as `latest` and as the package version, after the version, the command line and the
Lean axiom audit pass inside the new image. A running image compares its own version, commit and
build time with those of `latest` and prints one line with the pull command when a newer one is
published. The check never blocks, stays silent offline, and is turned off by
`ANAXIA_NO_UPDATE_CHECK=1`.

```sh
docker run --rm ghcr.io/creelie/bllm-engine update   # this copy, the published one, and how to update
```

Without docker:

```sh
pip install git+https://github.com/creelie/eBLLM     # Python 3.9 or later, no dependencies
pip install "ebllm[construct] @ git+https://github.com/creelie/eBLLM"   # with networkx and python-sat
anaxia --version                                       # ebllm and python -m anaxia are the same
```

The Lean library needs [elan](https://github.com/leanprover/elan); `lean/lean-toolchain` pins
Lean 4.34.1 and the library uses Lean core only.

## Commands

```sh
anaxia tasks                 # stepwise records of solved and open problems (14 tasks)
anaxia attack hodge          # the open steps of a task, their ladders and the plan
anaxia controls              # closures, calibrations and open problems, with their labels
anaxia gap                   # the gap law on the human and language-model idea data
anaxia schedule 1,2,4        # the entropy-law schedule for given check costs
anaxia scan lean/            # Lean sources: sorry, axiom, native_decide, unsafe (comments ignored)
anaxia axioms audit.log 44   # only propext, Classical.choice and Quot.sound may appear
anaxia modlog --patterns     # the learn-from-failure log and what each kind of change achieved
anaxia construct steinberg   # construction mode (see above)
anaxia intake deepmind       # what the engine takes from Google DeepMind
anaxia sources check TEXT    # whether a statement is already settled (DeepMind, OpenRefute, OpenAI)
anaxia update                # whether a newer image is published
```

The continuous loops are `experiments/loop.py` (five problems) and `experiments/hodge_loop.py`
(Hodge only). [`docs/USAGE.md`](https://github.com/creelie/eBLLM/blob/main/docs/USAGE.md) explains the spec format and the Python interface.

## Add a target

A target is a library of constructions, a check, a refuter and a target point.

```python
from ebllm.bllm.targets import Con, cross

criterion = Con("p.criterion", "hodge", gives="semiregular-object", needs=frozenset({"object"}))
product   = Con("p.product",   "hodge", gives="object",             needs=frozenset({"weil4"}))
cross(criterion, product)   # gives semiregular-object, now needs weil4
```

`cross(a, b)` fills one input of `a` with the output of `b` when the types match and returns
`None` otherwise. Write the check that decides a closed composite and the refuter that attacks an
accepted one, add the statement that would settle the problem to the agent's `TARGETS`, and the
agent joins the round. A closure enters the task suite as a JSON record with its Lean proof
(`src/ebllm/bllm/tasks/`).

## The paper

D. Bhattacharjee and U. Bhattacharya, *BLLM: Beyond the LLM with Deep Human-Mind-AI*. Its source,
its Lean development of 65 theorems and its checks are in [`paper/bllm/`](https://github.com/creelie/eBLLM/tree/main/paper/bllm/); the compiled
paper is [`preprintBLLM/BLLM.pdf`](https://github.com/creelie/eBLLM/blob/main/preprintBLLM/BLLM.pdf). Earlier versions, under the title *BLLM: The
Entropy Cost of Sound Self-Improvement and a Typed Crossing Network Tested on Five Open Problems*, were
released from creelie/D7 (DOI [10.5281/zenodo.23449604](https://doi.org/10.5281/zenodo.23449604)).
The VSI circuit the package started from is Deep Bhattacharjee, *Synthetic Neuromorphic
Superintelligence for Verifier-Gated Conjecture Closure* (15 May 2026),
[`paper/VSI-verifier-gated-conjecture-closure-2026-05-15.pdf`](https://github.com/creelie/eBLLM/blob/main/paper/VSI-verifier-gated-conjecture-closure-2026-05-15.pdf);
[`docs/REVIEW.md`](https://github.com/creelie/eBLLM/blob/main/docs/REVIEW.md) reviews its numbered results, six of which are false as stated
with counterexamples proved in Lean, and [`docs/CIRCUIT-v1.1.md`](https://github.com/creelie/eBLLM/blob/main/docs/CIRCUIT-v1.1.md) lists the
corrections the package implements.

## Labels of the recorded results

`anaxia controls` computes each label from the verifier factors stored in `src/ebllm/controls/`.
A result that has not been refereed is a CANDIDATE, however strong its formal evidence; open
problems are OPEN.

<details>
<summary>All 25 controls</summary>

| control | group | label | blocking verifiers |
|---|---|---|---|
| Graffiti.pc Conjectures 319, 352, 358, 359, 427 on domination (refuted) | closure | CANDIDATE | human |
| Tran's Conjecture 8.6 on regular Morley tetrahedra (refuted) | closure | CANDIDATE | human |
| Shankar's Conjecture 4.1 on even-intersecting lattice paths (proved) | closure | CANDIDATE | formal, human |
| Wang–Tian conjecture on tau_k-maximal graphs (proved) | closure | CANDIDATE | formal, human |
| Hou–Zhao Conjecture 4.10, Welch functions not third-order sum-free (proved) | closure | CANDIDATE | formal, human |
| Graffiti.pc / WOWII Conjecture 66, forest number (refuted) | closure | CANDIDATE | human |
| Densest packings of two translates of a lattice in R^4 (theorem; the 24-cell conjecture stays open) | partial | CANDIDATE | formal, human |
| Erdős Problem 1183: the lower bound of Theorem 1.4 | partial | CANDIDATE | human |
| Hodge conjecture for Fermat fourfolds of odd degree (Theorem F) | partial | CANDIDATE | formal, human |
| Blowup above alpha = 1/3 in viscous Katz–Pavlović dyadic models with small shell ratios | partial | CANDIDATE | formal, human |
| Lehmer's totient problem: a Lehmer number has at least 16 prime factors (partial result) | partial | CANDIDATE | formal, human |
| Fermat's Last Theorem | calibration | THEOREM | — |
| Kepler conjecture (sphere packing in dimension 3) | calibration | THEOREM | — |
| Navier–Stokes breakdown, alternatives (C) and (D) (OpenAI) | calibration | CANDIDATE | risk, human |
| Poincaré conjecture | calibration | THEOREM | — |
| Sphere packing in dimension 24 | calibration | THEOREM | — |
| Sphere packing in dimension 8 | calibration | THEOREM | — |
| Birch and Swinnerton-Dyer conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Collatz conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Densest packing in R^4 (D4 / 24-cell conjecture) | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Hodge conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Lehmer's totient problem | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| P versus NP | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Riemann hypothesis | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Yang–Mills existence and mass gap | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |

</details>

## Checks

`checks/run_all.sh` runs everything that CI runs:

- 131 Python tests (`tests/`), including the update check, the loop and its log, the reflexive
  polygons and their descents, the six benchmarks, and this README against the package;
- `checks/c/sandtile.c`: the conservative two-site run does not stabilize in 10⁶ topplings, the
  dissipative run with absorbed share 1/N needs exactly N topplings for N up to 10⁴, and
  chip-firing is abelian on 200 random graphs;
- `checks/cpp/scope_playbook.cpp`: all 9,710 pairs of partial maps on at most three points, and
  4,340 playbook updates;
- `checks/julia/release_accuracy.jl`: all 2⁸ factor assignments of the release algebra, and
  Proposition 21.1 on 20,000 random steps;
- the Lean library: `lake build`, the source scan, the axiom audit of all 44 theorems
  (`lean/Audit.lean`), and an independent replay with `leanchecker --fresh`;
- the example run, whose label must be CANDIDATE with only the human factor blocking.

The paper's 55,271 numerical checks and its 65 Lean theorems run with
`bash paper/bllm/checks/run_all.sh`.

## Releases and the closure rule

A closure is finished only when the engine and the paper both carry it: the library and the task
suite get the construction with its Lean proof, a release rebuilds the image and is archived on
Zenodo with a version DOI, and the paper is rewritten as one text that carries the result in its
place. The same rewrite is due whenever enough new measured data would change what the paper
says. The steps are in [`RELEASING.md`](https://github.com/creelie/eBLLM/blob/main/RELEASING.md).

## Layout

| path | contents |
|---|---|
| `src/ebllm/` | the circuit: obligations, verifiers, ledger, release algebra, controls, update check |
| `src/ebllm/bllm/` | the network: schedules, crossing, memory, the learn-from-failure loop and its log, targets, attack channel, agents, proposers, connectome selector, benchmark, tasks, DeepMind intake |
| `src/ebllm/construct/` | construction mode: builder, exists-forall searches, gadget algebra, assembly, the independent checks, stored gadgets |
| `src/anaxia/` | the `anaxia` name of the same package |
| `lean/` | the engine's Lean library (44 theorems, Lean core): the circuit, the release algebra, the Hodge gaps, the loop and descent bounds |
| `paper/bllm/` | the paper, its Lean development (65 theorems, Mathlib) and its checks |
| `experiments/` | benchmark logs, the loops, the Hodge-only run, Erdős 1183 searches, the Yang–Mills scout, fine-tuning |
| `checks/` | Python, C, C++ and Julia checks |
| `docs/` | review, circuit v1.1, usage, artwork and the script that draws it |

[`HARDWARE.md`](https://github.com/creelie/eBLLM/blob/main/HARDWARE.md) says what each component needs and [`DEVICE_RUN.md`](https://github.com/creelie/eBLLM/blob/main/DEVICE_RUN.md)
which runs are meant for a larger machine.

## Citing

See [`CITATION.cff`](https://github.com/creelie/eBLLM/blob/main/CITATION.cff). Each release is archived on Zenodo.

- v1.0.0: [10.5281/zenodo.23286642](https://doi.org/10.5281/zenodo.23286642)
- v2.0.0: [10.5281/zenodo.23455686](https://doi.org/10.5281/zenodo.23455686)
- v2.0.1: [10.5281/zenodo.23456124](https://doi.org/10.5281/zenodo.23456124)
- v2.1.0: [10.5281/zenodo.23462639](https://doi.org/10.5281/zenodo.23462639)
- v3.0.0: [10.5281/zenodo.23464390](https://doi.org/10.5281/zenodo.23464390)
- v3.0.1: [10.5281/zenodo.23464490](https://doi.org/10.5281/zenodo.23464490)
- v3.0.2: [10.5281/zenodo.23466863](https://doi.org/10.5281/zenodo.23466863)
- v3.0.3: [10.5281/zenodo.23467113](https://doi.org/10.5281/zenodo.23467113)
- v3.0.4: [10.5281/zenodo.23467544](https://doi.org/10.5281/zenodo.23467544)
- v3.0.5: [10.5281/zenodo.23469389](https://doi.org/10.5281/zenodo.23469389)
- all versions (concept DOI): [10.5281/zenodo.23286641](https://doi.org/10.5281/zenodo.23286641)

The master zip [`BLLM_masterzipfinal2.zip`](https://github.com/creelie/eBLLM/raw/main/BLLM_masterzipfinal2.zip)
holds release v3.0.5 with the paper, its Hexagon upload and its JAIR submission.

## Licence

MIT, see [`LICENSE`](https://github.com/creelie/eBLLM/blob/main/LICENSE). The papers in `paper/` are their authors' and are included for
reference.
