<a href="https://creelie.github.io/eBLLM/seed-intervals.html">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-seed-explorer-dark.svg">
<img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-seed-explorer-light.svg" alt="Animated exact seed certificate preview: twelve constructions, shortest-depth bound 346 relative to the supplied census; the sharp constant remains open. Click for the interactive four-dimensional point-cloud explorer." width="100%">
</picture>
</a>

# Anaxia · the BLLM engine

[Browse the eight research manuscripts](https://creelie.github.io/eBLLM/research-manuscripts.html)

## Audited matrix-space result

[Nilpotent-free subspaces of M₃(𝔽₃): exact maximum **5**](https://github.com/creelie/eBLLM/blob/main/docs/NILPOTENT-FREE-F3.md) · [preprint](https://hexagonmath.org/2610.00480v1)

```console
anaxia construct nilpotent-free --full
```

Rebuilds an exact **3,109,888-node** exhaustive verifier and checks the five-dimensional construction. The control records the compiled-evaluation trust and pending review gates.

## New in 3.4.1rc1

**[Open the interactive certificate explorer](https://creelie.github.io/eBLLM/seed-intervals.html)** — rotate the exact points, select any of twelve cuts, inspect all bounds and download the data.

| Verified research result | Remaining construction |
|---|---|
| Twelve integer interval certificates; **22 ≤ D₄ ≤ 346** relative to the supplied census | The exact D₄ |
| Hodge graph enumeration: **31 survivors / 545,835 arrangements** | An actual Maurer–Cartan solution and semiregular object |
| Precise blow-up and finite-cover descent checks | Algebraic representatives for F2/F3′; an all-nine-condition GSC vacuum |

```console
anaxia construct seed-intervals
```

Research candidate. **The full closure benchmark remains open.** The release and source notes distinguish finite certificates from unproved universal statements.

[Proof and data attribution](https://github.com/creelie/eBLLM/blob/main/docs/SEED-INTERVALS.md) · [Engine checks](https://github.com/creelie/eBLLM/actions) · [Source](https://github.com/creelie/eBLLM/tree/main)

<details>
<summary>Technical documentation, verification ledger and archived DOI history</summary>

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
docker run --rm ghcr.io/creelie/bllm-engine skills          # each run as one hyperedge: what it credits, what it avoids
docker run --rm -it --entrypoint bash ghcr.io/creelie/bllm-engine
```

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-numbers-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-numbers-light.svg" alt="21,515 composites bred, 64 survive; 46.4 checks with memory against 95.2 without; human ideas at 1.08 times the proposer bound against 1.5 to 4.3 for language models; every reflexive descent of a reflexive 4-polytope reaches a seed within 348 steps; 89 changes of its own rules after 96 attempts that did not close; 0 of 4 target conjectures closed in full, the seed bound a sub-benchmark" width="100%">
  </picture>
</p>

Anaxia does not guess at proofs. It holds the constructions that mathematicians have already
made, each typed by what it gives and what it needs, and it breeds new candidates by plugging the
output of one into an input of another. A candidate counts only when a program checks it, a
refuter fails to break it, and whatever is stated as proved goes through the Lean kernel. Every
verdict is written to memory, so the engine never pays twice for the same question. And when an
attempt fails, the engine names the reason, changes one of its own rules, and tries again under
the new rule. The cards above are its measured record, the last one included.


## Research revision: twelve exact seed intervals

`anaxia construct seed-intervals` verifies twelve finite interval certificates with integer arithmetic. Relative to the supplied Kreuzer–Skarke census, these give **22 ≤ D₄ ≤ 346** for the maximum shortest descent. Every descent is still bounded by 348; the exact constant, Hodge and GSC remain open. This is a research candidate, with no new Lean formalization or release DOI claimed.

The [proof and data notes](https://github.com/creelie/eBLLM/blob/main/docs/SEED-INTERVALS.md) explain the census assumption and coordinate attribution. The [animated certificate explorer](https://github.com/creelie/eBLLM/blob/main/docs/seed-intervals.html) shows all twelve cuts, point clouds and actual numerical bounds.

## New in 3.4.0

### Super Yang–Mills with several times: the claim for (9+8n)+1 is refuted

Uploaded by a second agent on Tubai's command. A closure by refutation, recorded as a CANDIDATE
until refereed.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-multitime-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-multitime-light.svg" alt="Several times: a super Yang-Mills theory built in Nishino's manner lives only on the lines s - t = 8, 0, -8, so none exists in (9+8n)+1, (10+8n)+2, (11+8n)+3, (12+8n)+4 for n >= 1; 2(d-2) is a multiple of the Weyl dimension only at d = 3, 4, 6, 10; for one time every massless multiplet without tensor charges in (9+8n)+1 has at least 2^(2^(2+4n)) states" width="100%">
  </picture>
</p>

- **The claim.** Nishino built super Yang–Mills theories in the signatures (9+m)+(1+m) by
  restricting the gaugino to the kernel of k null vectors. Rios, Marrani and Chester (Phys. Rev.
  D 99 (2019) 046004, Sec. III A) state that his proofs "can be successfully repeated" in
  (9+8n)+1, (10+8n)+2, (11+8n)+3 and (12+8n)+4, which include the exceptional signatures 27+3 and
  19+3. In October 2026 no paper citing them constructs such a theory or tests the claim.
- **What is proved.** For every theory built in Nishino's manner (five axioms that his own
  construction satisfies) the null vectors can be real only if k ≤ min(s,t), and the cubic gaugino
  terms reduce to a Fierz identity on the residual spinors. That identity forces the spinors to
  have dimension 2(d−2) on a d-dimensional space, which happens only for d = 3, 4, 6, 10. So the
  residual dimension s+t−2k is 10 (or 2), s−t lies in {8, 0, −8}, and none of the four families
  with n ≥ 1 carries a theory. For one time, in (9+8n)+1 with n ≥ 1, every massless multiplet
  without tensor charges has at least 2^(2^(2+4n)) states, so there is no massless vector multiplet.
- **The construction.** [`construct/multitime_sym.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/multitime_sym.py)
  rebuilds the Witt bound, the dimension count and the single-time bound, and with explicit gamma
  matrices finds the cubic identity true to 10⁻¹⁶ in (9,1), (5,5), (1,9) and false by 0.38 in
  (17,1), (13,5), (9,9). Its two refuters are the shortcuts the paper rules out: the mod-8 rule of
  the claim and complex null frames. Each admits all eight claimed signatures with n = 1, 2, and the
  check rejects every one.
- **What failed, and the changes it forced.** The first reduction assumed that the cubic terms
  cancel on their own, which Nishino's own theories do not satisfy; the rule changed to his absorption
  of those terms by a field-dependent correction (axiom N5). Two overclaims were cut back: existence
  on the three lines (only their necessity is proved), and the single-time bound, now stated for
  multiplets without tensor charges. The run is `multitime-sym` of the modlog; the control is
  `multitime-sym-ten` (CANDIDATE: no Lean statement, not refereed).
- Paper, LaTeX source and code: [creelie/cs-grav](https://github.com/creelie/cs-grav), release
  [v1.0.0](https://github.com/creelie/cs-grav/releases/tag/v1.0.0),
  [10.5281/zenodo.23558751](https://doi.org/10.5281/zenodo.23558751).

The results, loop, numbers and growth figures were redrawn from the current data, and the DOIs of
releases 3.3.0 and 3.3.1 are recorded.

## New in 3.3.1

### The knot tables: a fourth pass, lower bounds from definite lattices

Uploaded by a second agent on Tubai's command. These are partial results on finite lists, not
named conjectures, and they are not refereed.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-knots-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-knots-light.svg" alt="The knot tables: a pinch move on a trefoil; the nonorientable four-genus settled for 2,537 of 3,525 open knots with 11 to 13 crossings, 444 of them in the fourth pass with 382 lower bounds from Donaldson's theorem; the bridge index settled for 243 of 536, with the walls it met" width="100%">
  </picture>
</p>

- **What failed, and the change it forced.** The third pass ended with the pinch search stalled:
  thirty diagrams and double pinches found nothing new on a sample of open knots (run
  `knot-tables-pass3`, attempt 2). The rule changed in kind, from upper bounds to lower bounds.
- **Lower bounds from Donaldson's theorem.** For an alternating knot both Goeritz forms are
  definite. If the knot bounded a Möbius band (or, when σ + 4 Arf ≡ 4 mod 8, a surface with
  b₁ = 2), gluing the double branched covers would give a closed definite four-manifold, whose
  form is diagonal by Donaldson's theorem (Jabuka and Kelly, Theorems 2.10 to 2.12). The new
  construction [`construct/goeritz_lattice.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/goeritz_lattice.py)
  computes the forms and the signature from a PD code and lists every embedding of the lattice
  in the standard lattice, up to signed permutations. It raises the lower end of 382 open
  KnotInfo entries (22 of them to γ₄ ≥ 3). Its refuter, σ with the wrong sign, claims γ₄ ≥ 2 for
  the trefoil, so the sign convention is tested, not assumed. In the repository the same check
  never exceeds a known value on 511 smaller knots, nor a pinch bound on 1,714 certified knots.
- **Pinches on twenty diagrams.** A wider band search found 84 more pinch certificates, all
  checked in Regina.
- **Together** they settle 2,537 of the 3,525 open knots (520 at γ₄ = 1, 1,995 at 2, 22 at 3),
  444 more than before; 988 stay open. The run is `knot-tables-pass4` of the modlog; the control
  `crosscap4d-13` is updated.
- Repository: [creelie/conjecture-to-choose](https://github.com/creelie/conjecture-to-choose), folder `crosscap4d`.

## New in 3.3.0

Uploaded by a second agent on Tubai's command. Version 3.3.0 brings the attempts of 21 October 2026 on
four of the engine's targets, each with its constructions, its walls and its records: three results
and five construction rounds on the Hodge inputs (F2) and (F3'), the proof that the mirror clause of
the Geometric Selection Conjecture is empty (a new partial control, `gsc-mirror-clause`), the literature
check of TheoPhysEval with two exact constructions, the final passes on Lehmer's totient problem
and the brane gas, and a third pass on the knot tables (the pinch construction, the nonorientable
four-genus settled for 2,093 of 3,525 open knots, a new partial control). None of the four target
conjectures is closed. The figures are redrawn from the
current data, and the attack chain of the strings target now carries the reduction.

### The knot tables: a third pass on the nonorientable four-genus

Uploaded by a second agent on Tubai's command. These are partial results on finite lists, not
named conjectures, and they are not refereed.

- **Four-genus, third pass.** KnotInfo 2026.10.5 leaves the nonorientable four-genus open for
  3,525 prime knots with 11 to 13 crossings. One pinch move (a nonorientable band) to a slice knot
  or to a knot of four-genus one now settles 2,093 of them, 139 more than before; 1,432 stay open.
  The old verifier compared knot complements from one simplified triangulation and missed true
  pinches; forty simplifications under fixed seeds find a common triangulation. That change of
  rule is the run `knot-tables-pass3` of the modlog. The construction is
  [`construct/pinch.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/pinch.py)
  with the 139 certificates; its refuter, the other smoothing of the same crossing, gives two
  components and fails.
- **Bridge index, two walls.** For the 293 open 13-crossing knots, colourings by Alexander
  quandles over F_p[t]/(g), p < 110, give at most three meridians, and none is the closure of a
  3-braid in Murasugi normal form in the range searched. Both routes are recorded as failures.
- Release: [conjecture-to-choose v1.1.0](https://github.com/creelie/conjecture-to-choose/releases/tag/v1.1.0).

### Hodge: three results of fermat-hodge- v2.7.0 and the analytic attempt

Uploaded by a second agent on Tubai's command. None of these closes (F2) or (F3'); the Hodge
conjecture stays open. They are in the barrier atlas as two walls and three routes
(`anaxia barriers --target hodge`).

- **Seven shifts on E₀⁸.** A convolution of the 128 Weil pieces whose shifts lie in seven
  consecutive integers fails the polarised criterion in 18 of the 28 arrangements, by hand;
  linear-programming bounds decide 9 more (least value 125.8 > 104). In the last one, with even
  shifts s, s−2, s−4, s−6 and odd shifts s−1, s−5, the bound vanishes, so it stays open.
- **An étale Prym map at genus four.** On x³ + y³ + 1 + λx³y³ = 0 with η = O(1, −1) of order
  three, H⁰(K+η) ⊗ H⁰(K−η) → H⁰(2K) is an isomorphism, so the period map of étale triple covers is
  a local isomorphism onto the nine-dimensional Weil domain of Q(√−3) at n = 3 (Faber 1988, here
  at an explicit curve). The construction is
  [`construct/genus_four_prym.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/genus_four_prym.py);
  its refuter, the products xⁱxʲ, spans five functions and fails.
- **Sextic CM fields.** Over twelve cubic fields no integral class has −χ ≤ 24, so the dimension
  count excludes nothing there.
- **Residues and mass, the analytic attempt.** Griffiths–Villaflor residues turn a cycle into a
  polynomial, and deciding its residue needs its periods. Mass-minimising currents exist in every
  class, and the minimum equals the calibrated volume exactly for effective algebraic cycles, so
  the conjecture for α is a vanishing mass gap of eα + khᵖ. A flow with surgery, in the manner of
  Perelman, can reach the minimiser but not the equality case, and Kollár's threefolds show that the
  multiplier e cannot be dropped.

### Hodge: one round on (F2) through the dichotomy

Uploaded by a second agent on Tubai's command. The main theorem of fermat-hodge- v2.7.0 says that
the algebraic locus of the Weil classes is dense in the domain of abelian varieties of Weil type and
is either the whole domain or meagre. This round asked whether the dichotomy can be decided without
a cycle, and stopped on the wall `countable-union-closed` (run `hodge-f2-dichotomy`): the algebraic
locus is a countable union of the closed algebraic subsets over which a relative cycle of one
component of the Chow varieties represents the classes, so it is not meagre exactly when one of
those subsets is the whole domain, that is when a cycle exists on the generic member. Every CM
point, Hecke orbit and escape sequence lies in the union and never forces that. The rule changed:
density and category arguments for (F2) are recorded as reformulations, not progress. (F2) and
(F3') remain open; the conjecture is not closed.

### Hodge: five construction rounds on (F3')

Uploaded by a second agent on Tubai's command. Each round learned from the one before, and all five
stopped on a wall; they are the run `hodge-f3prime` in the modlog (`anaxia modlog`), and the walls
`zero-cycles-core`, `odd-cross-classes`, `lefschetz-inverse` and `f3prime-needs-cycle` are in the
atlas. Small zero-cycles stop at the non-uniruled fourfolds. Products of varieties that satisfy
(F3') create cross classes, such as threefold × curve, that need the generalised Hodge conjecture
for level one. K3 and hyperkähler pieces land on the known multiplier walls. Reducing to the middle
degree needs standard conjecture B. And, by semisimplicity, (F3') with (F2) on a variety is the
Hodge conjecture on it, so only a new algebraic cycle on B × X can advance it. (F3') stays open.

### Strings: the mirror clause of the Geometric Selection Conjecture is empty

Uploaded by a second agent on Tubai's command. Theorem D of the strings paper says that the
Geometric Selection Conjecture holds exactly when a viable vacuum exists that is fixed by the mirror
involution wherever that involution is defined. The module
[`construct/gsc_mirror_fixed.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/gsc_mirror_fixed.py)
proves that the fixed-point clause is never met: a vacuum fixed by the mirror map is isomorphic to
its mirror, so h¹¹ = h²¹ and χ = 0; its component contains a (2,2) point, so c₃(V) = χ = 0, the
index c₃/2 vanishes on every free quotient, and (C2) fails. Hence the conjecture is equivalent to
the bare existence of one viable vacuum on a component that carries no standard embedding, with no
condition on mirror symmetry, in the compact-group reading as well; a three-family standard
embedding, such as the Tian–Yau quotient, is never the selected vacuum. The lemma and the corollary are proved (and checked on self-mirror and three-family
Hodge pairs); what they leave is the existence statement, and it is blocked by definition: (C7) to
(C9) are fixed by comparison with measurement, and the literature check of 21 October 2026 (wall
`no-model-has-c7-c9`) finds no published vacuum that establishes moduli stabilisation, the Yukawa
hierarchy and supersymmetry breaking together. The three rounds are the run `gsc-attempt` in the
modlog: a sharpening of Theorem D, no closure. The result is written up as a five-page note, "The Mirror
Clause of the Geometric Selection Conjecture Is Empty", by Deep Bhattacharjee and Ushashi Bhattacharya,
in [creelie/geometric-selection-conjecture](https://github.com/creelie/geometric-selection-conjecture)
([release 1.0.0](https://github.com/creelie/geometric-selection-conjecture/releases/tag/v1.0.0), with the
same check as `code/mirror_clause.py`, 511 checks), recorded as the partial control `gsc-mirror-clause`
(CANDIDATE: no Lean statement, no referee); the stage `s.mu-fixed-chi0` of the superstring chain now
holds the proof as a claim awaiting a check by someone other than its author.

### TheoPhysEval (arXiv:2610.16733): a literature check and two exact constructions

Uploaded by a second agent on Tubai's command. "TheoPhysEval: Assessing AI agents at autonomous
theoretical physics problem solving" ([arXiv:2610.16733](https://arxiv.org/abs/2610.16733),
9 October 2026) is a benchmark of fifty unpublished "turn-the-crank" problems with numerical
answers; the best agent solves 49 of them with web search and 46 without. It proves no theorem
and none of its problems is open, so it closes no gap of the engine's targets: it says nothing on
the Hodge inputs (F2) and (F3'), on Lehmer's totient problem, or on a definition of the brane-gas
theory beyond perturbation theory. The check is logged as the stopped run `theophyseval` in the
modlog. Two of its problems carry exact constructions, now in construction mode as
[`construct/theophys.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/theophys.py)
with their checks and refuters:

- **π from the Euler beta function.** π = 4 + Σ (1/n!)(1/(n+λ) − 4/(2n+1))((2n+1)²/(4(n+λ)) − n)ₙ₋₁,
  in exact rational arithmetic; after 40 terms the error is below 10⁻¹² at λ = 21/2. As λ → ∞
  each term tends exactly to the Madhava–Leibniz term 4(−1)ⁿ/(2n+1), and that limit is the
  refuter: its error after 40 terms is about 10⁻², so the parameter does real work.
- **Hidden zeros of a four-point residue.** A zero at backward scattering t = −k means z = −1, and
  Cⱼ^λ(−1) = (−1)ʲ(2λ)ⱼ/j!, so Σⱼ (−1)ʲ(2λ)ⱼ/j! cⱼ = 0 with λ = (d−3)/2, and the pole terms obey
  Σₘ (−k)ᵐ αₙ,ₘ = 0. The d = 4 relations of the problem follow; at d = 7, k = 3 the module gives
  c₃ = 13/4, αₙ,₃ = 26/27 and Ξ = 11219/27. A single Gegenbauer polynomial, which has no zero
  there, is the refuter.

### Lehmer and the brane gas: final passes and a results board

Uploaded by a second agent on Tubai's command: the final analytical passes on two of the
engine's targets before their journal releases, the walls they met, and the version DOI of
release 3.2.1, [10.5281/zenodo.23524945](https://doi.org/10.5281/zenodo.23524945), recorded in
`CITATION.cff` and in this README.

- **Lehmer's totient problem as one divisor.** A composite solution of φ(n) | n − 1 is n = A q
  with q its largest prime factor, A the product of the others, B = φ(A) and D = M B − A; the
  conjecture is equivalent to the assertion that 1 + (A − 1)/(M B − A) is never a prime above
  the other factors (Proposition 9.1 of the paper, [creelie/eLhmr](https://github.com/creelie/eLhmr),
  [release 1.4.0](https://github.com/creelie/eLhmr/releases/tag/v1.4.0)). The new module
  [`construct/lehmer_equiv.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/lehmer_equiv.py)
  checks the two constraints that the algebra gives, (q − 1) D = A − 1 and D odd with
  D ≡ −A (mod 2^|S|), on every candidate, and its refuter finds no solution on small sets while
  the same search on the companion equation φ(n) | n + 1 returns the Fermat chain 15, 255, 65535,
  4294967295. The pass closed nothing: congruences cannot force a number never to be prime, and
  the sixteen-prime case costs a million times the fifteen-prime one for one more unit of the
  bound. The controls `lehmer-totient` (open, with the barriers) and `lehmer-omega-16` (partial,
  journal version prepared for the International Journal of Number Theory) record this.
- **The brane gas beyond perturbation theory.** The manuscript of
  [creelie/brane-cluster-gases](https://github.com/creelie/brane-cluster-gases) [release 3.2.0](https://github.com/creelie/brane-cluster-gases/releases/tag/v3.2.0),
  is submitted to JHEP under the title
  "Cancellation of all ultraviolet divergences of quantum gravity by a scale-invariant gas of
  branes". The control `brane-gas-uv-finite` (CANDIDATE) now lists the barriers to a
  non-perturbative statement: the free Euclidean field is not reflection positive for any entire
  non-constant form factor without zeros, the conformal mode is unbounded below, and the loop
  expansion is large above an energy between 1.4 M and 1.9 M. The modlog records the pass and
  the rule it fixed: title, abstract and conclusion name the perturbative theorem and nothing more.
- **A results board.** [`docs/assets/make_results.py`](https://github.com/creelie/eBLLM/blob/main/docs/assets/make_results.py)
  draws every control with the verifiers it has passed and every attempt of the learn-from-failure
  log as an animated board, shown under "What Anaxia has proved"; the other figures were redrawn
  from the current data.

## New in 3.2.1

The version DOI of release 3.2.0, [10.5281/zenodo.23524665](https://doi.org/10.5281/zenodo.23524665),
recorded in `CITATION.cff` and in this README, uploaded by a second agent on Tubai's command. The
code, the Lean development and the paper are those of 3.2.0.

## New in 3.2.0

Four additions to the engine, each uploaded by a second agent on Tubai's command, and the
version DOI of release 3.1.1, [10.5281/zenodo.23484395](https://doi.org/10.5281/zenodo.23484395),
recorded in `CITATION.cff` and in this README (3.1.1 itself recorded the DOI of 3.1.0). The Lean
development is that of 3.1.0; the paper is not rewritten in this release.

### NexGenModule, the attack package for the four targets

Uploaded by a second agent on Tubai's command, from a read-only study of the four target
repositories, so that every copy of the engine knows the same walls. The entry point is
`anaxia barriers`; the modules are `bllm/barriers.py` (the ledger and the bypass search),
`bllm/atlas.py` with `bllm/data/atlas.json` (the walls, breakers and routes of each target) and
`construct/volume_chain.py` (the seed bound). It aims at the unconditional closure of the four
targets by naming, for each, what must be broken and what would break it; it closes none of them,
and every status in it says whether a statement is proved, conditional, proposed or open. Further
attack modules go into the same package.

- **It knows why a route fails.** A no-go theorem is now data
  ([`bllm/barriers.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/barriers.py)):
  its hypotheses as predicates on the library nodes of a composite, and for each hypothesis the
  nodes whose presence breaks it. A composite that satisfies every hypothesis of a wall is pruned
  before its check, with the wall as the reason, and the bypass search proposes the crossings that
  break a hypothesis; a hypothesis with no breaker in the library is reported as a gap, phrased as
  the construction that is missing. On the amplified library crossed three generations deep, 127 of
  the 538 closed composites are pruned (108 by the forest ceiling of the Dobrushin route, 16 by the
  missing convexity of the Polchinski flow, 3 by the Hodge walls), 448 bypass crossings are
  proposed, and six gaps are named.
- **The atlas of the four targets.** `anaxia barriers` prints, for Hodge, strings, the seed
  conjecture and Yang–Mills, every proved wall with its source, the hypothesis it rests on, the
  breaker, and the routes proposed against it, each with a status: established, conditional,
  proposed or open ([`bllm/data/atlas.json`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/data/atlas.json)).
  The verdicts: the seed constant is closable by brute force; the Geometric Selection Conjecture
  is blocked until (C7)–(C9) are stated as inequalities; the forest ceiling stops single-link
  Yang–Mills at β_W = 1/3 and blocks of links are the untried breaker; (F2) with (F3') is the Hodge
  conjecture itself, so the atlas names first instances (certified ranks on E_0^6, the transport
  intersection in the rank-18 family, lattice enumeration for other cubic fields) rather than a
  dissolution.
  A literature pass of 20 October 2026 added five Hodge walls and four routes: the three OpenAI
  preprints on split eightfolds, Kuga–Satake for K3 surfaces and products of K3 surfaces were
  withdrawn on 7 October 2026 (openai/math `history.md`), so every deduction from them is conditional
  on a withdrawn hypothesis; semiregularity is the limit of the secant-sheaf route (Markman
  2509.23079, Voisin 2026); the hyperkähler carriers reach discriminant 1 only; and the Fermat census
  of Jumagulov (2608.18134) and Saller's split polarisations on CM sixfolds are routes for F3' and F2.
- **A sharper chain bound for the seed constant.** Along a reflexive descent in dimension four the
  normalised volume |2Δ| − 3|Δ| + 2 falls strictly and the dual volume rises, and the volume
  depends on h_2, which the point counts do not see
  ([`construct/volume_chain.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/volume_chain.py)).
  The longest chain in (points, dual points, volume) bounds every descent and is never longer than
  the pair chain. Running it needs |2Δ| for the whole Kreuzer–Skarke list, a device run.
- The learn-from-failure log has a run `barrier-atlas` with the four records of the study, each
  with the rule it changed. No result here closes anything; every label stays as it was.

#### The superstring

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-superstring-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-superstring-light.svg" alt="The superstring: four attack chains (Hodge, strings, seed, Yang-Mills), each with its attackers, the stage where each one stops, and 0 of 4 targets closed" width="100%">
  </picture>
</p>

`anaxia superstring` runs one attack chain per target, with an attacker assigned to every zone
(a wall of the atlas, or the frontier) and every piece (the single finite or local question it
works on), each with its move, method, inputs, the certificate that would close it and its stop
rule ([`bllm/superstring.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/superstring.py),
[`bllm/data/attackers.json`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/data/attackers.json)).
A chain is run to its end and ends in a bypass stage, the last step: a search of everything the
engine holds for a result that already implies the target. The closure rule is the only rule: a
stage closes only on a certificate of kind lean, proved or computed, checked by someone other
than its producer; a claim, a conditional statement, an unrefereed input, a scout estimate or a
self-checked computation never closes a stage, and a target is closed exactly when every stage of
its chain is. That is what makes the agent unable to record a false closure. With the bundled
data no target is closed, and the chain says where each one stops:

| Target | Attackers | Stops at | What that stage needs |
| --- | --- | --- | --- |
| Hodge, (F2) and (F3') | 16 | `h.semiregular-jacobian` | one explicit object meeting the polarised semiregularity criterion at a CM point of a quartic CM field, its Ext profile certified exactly |
| Strings, GSC | 6 | `s.definition-repair` | (C7)–(C9) as inequalities with named constants, so that a vacuum can fail them |
| Seed, D₄ = 22 | 6 | `seed.farm-finisher` | the complete descent certificate at T = 22, checked by the second checker |
| Yang–Mills | 5 | `ym.cube4-certifier` | the rational inequality α_V < 1 for the unit 4-cube block, in Lean |

The Hodge chain also records what the papers' attack strategy leaves out, zone by zone (twelve
gaps, each with the attacker that fills it), and the strategy behind the chain: diagonalise (F2)
by Mumford–Tate type and attack the first open piece, Weil fourfolds of nontrivial discriminant;
pincer every open piece with a construction agent and a refuter agent, so that it ends either with
a certified object or with a proved wall; change the carrier, not the class, when the refuter
wins; push the class A of (F3') outward along proved reductions.

- **Blow-ups against the obstructions.** Two blow-ups, both exact
  ([`construct/blowup.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/blowup.py)).
  Blowing up the variety: by the blow-up formula H^k(Bl_Z X) = H^k(X) ⊕ ⊕_{i<c} H^{k−2i}(Z)(−i)
  the defect of the blow-up is the defect of X plus those of the centre, so a blow-up relocates
  an obstruction and never removes it (the wall `surgery-relocates`, now as a computation on
  Hodge numbers and defects). Blowing up the certified set: a Weil discriminant is a class in
  Q^*/N(K^*), read off by Hasse as the vector of Hilbert symbols (δ, −d)_v, and algebraicity is
  multiplicative under products (Schoen), so the certified classes span an F₂-subspace. From the
  single certified class 1 the span is {1} for every field: products buy nothing yet; one certified
  class, say 3 for Q(i), would at once give 3, 6, 15 and leave 7, 11, 21, each prime an
  independent class, so (F2) needs a construction uniform in the discriminant.
- **The Delsarte census.** [`construct/delsarte_degree.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/delsarte_degree.py)
  enumerates the Delsarte fourfold shapes in six variables of degree 3 to 40 (1,102 shapes),
  computes the lattice degree e of each, and matches it against the Fermat degrees whose Hodge
  conjecture is known: 51 non-Fermat shapes have their Hodge conjecture closed through the
  simplex-type reduction, 37 by the published theorems of Shioda and da Silva and 14 by
  Jumagulov's census (unrefereed); none of the 29 sextic shapes is reached.
- **The second attack pass** (Yang–Mills, strings, Hodge).
  [`bllm/ym_blocks.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/ym_blocks.py)
  is the block-of-links scout for the forest ceiling: a synchronous transport coupling in the
  forest gauge, calibrated on the single link (it reproduces β_W = 1/3), finds that the
  plaquette and the unit 3-cube barely move the crossing (about 0.35 and 0.37) and that the unit
  4-cube has no measured crossing up to 0.40; a scout, not a proof, which picks the block to
  certify. [`construct/monads.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/monads.py)
  scans the positive monads on the cyclic complete intersections in exact arithmetic: on free
  quotients of the quintic exactly two give three net families, the SU(5) one living on the Dwork
  pencil with the anomaly saturated, and both fail (C3), as in the literature.
  [`construct/k3frob.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/k3frob.py)
  counts points on the level-13 elliptic K3 surface of the Fricke route: ρ = 16 and a CM
  endomorphism field, so that route reaches real multiplication only by √2, √3, √5, √6, √7.
  The atlas gained the walls `fricke-levels`, `positive-monads-quintic`, `exact-depth-cost`,
  `small-blocks` and eight routes, the last-step bypasses among them, labelled conditional.
- **The third attack pass** (strings, Yang–Mills, seed).
  [`construct/vacuum_conditions.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/vacuum_conditions.py)
  states (C7) to (C9) of the strings target as numeric windows (moduli masses, Yukawa
  singular-value ratios at the GUT scale, the Cabibbo angle, the gravitino mass) with a checker and
  a refuter; every number is a proposal for the author to accept or edit, not the paper's, and a
  vacuum that passes is labelled numeric, never proved.
  [`construct/lbs_tetraquadric.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/lbs_tetraquadric.py)
  scans SU(5) line-bundle sums on the tetraquadric with entries in [−2, 2]: 372 pass c₁ = 0, the
  anomaly, polystability at an explicit Kähler point and index −3|G|; 228 pass the exact upstairs
  spectrum from Koszul line-bundle cohomology (checked against the index and Serre duality); ten
  classes up to permuting the factors, all candidates, since the downstairs spectrum, (C5) and
  (C6) are not checked. `bllm/ym_blocks.py` records the adversarial boundaries for the unit 4-cube
  at β_W = 0.36 (Haar, cold, ±1 signs: 0.967, 0.927, 0.977, all below 1), Monte Carlo estimates
  and not a certificate. The atlas gained the routes `tetraquadric-su5`, `c7-c9-proposal`,
  `gamma8-bfs` and `cube4-adversary-036`, all proposed.

### the bridge index of thirteen-crossing knots

Uploaded by a second agent on Tubai's command. KnotInfo (version 2026.10.5) lists the bridge
index of 536 prime knots with 13 crossings as [3,4]. For 243 of them the bridge index b(K) is 4
and equals the meridional rank μ(K), so the meridional rank conjecture of Cappell and Shaneson
(Kirby's problem list, Problem 1.11) holds for them; the other 293 stay open. This is a partial
result on a finite list and it is not refereed: the control `bridge-index-13` is a CANDIDATE,
blocked by the formal and human verifiers. The paper, the certificates and a standalone verifier
are in [creelie/conjecture-to-choose](https://github.com/creelie/conjecture-to-choose); the
construction is now part of construction mode as
[`construct/transvections.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/transvections.py).

- **The two bounds.** The KnotInfo diagram of each of the 243 knots has Wirtinger number 4, so
  b(K) ≤ 4 (Blair, Kjuchukova, Velazquez and Villanueva). For the lower bound, a representation of
  the knot group into GL(4, F_p) that sends the meridian to a pseudo-reflection, with no vector
  fixed by the whole image, gives μ(K) ≥ 4: k meridians fix the meet of k hyperplanes, which is
  nonzero for k ≤ 3. Transvections x ↦ x + ω(x, v)v of Sp(4, 3) settle 67 knots, those of Sp(4, 5)
  another 161, and reflections of O(4, 5) the last 15. The earlier lower bounds for these knots came
  from Coxeter quotients, where the meridians go to reflections of order 2.
- **The search.** Since g t_v g⁻¹ = t_gv, a transvection representation is a colouring of the arcs
  by vectors, and the colours of the four seed arcs form a basis. So `search_sp4` tries every
  nondegenerate Gram matrix of the seed vectors, p⁶ cases, and is complete for Sp(4, p) and the
  given seeds. It finds all 228 symplectic certificates again in about ten seconds, and none for
  the three-bridge knots 8_5, 9_35 and 10_120, as it must.
- **The check.** `check_certificate` works from the matrices alone. It checks five things: each
  matrix is constant along its arc, the Wirtinger relation holds at every crossing, each matrix is
  a pseudo-reflection, the common fixed space is zero, and the four seed arcs colour the whole
  diagram. The 243 certificates ship in
  [`construct/data/bridge13_certificates.json.gz`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/data/bridge13_certificates.json.gz) and all
  pass. A changed entry, three seeds, a reversed crossing or identity matrices make a certificate
  fail.
- **What stays open.** For the other 293 knots, listed in
  [`construct/data/bridge13_open.json`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/data/bridge13_open.json), exhaustive searches found no
  such representation with transvections of Sp(4, q) for q in {3, 4, 5, 7, 8, 9, 11}, reflections of
  O(4, q) for q in {3, 5, 7}, or pseudo-reflections of GL(4, 2) and GL(4, 3). Among 300 random
  diagrams of each knot, none had Wirtinger number 3.

### audits, triage and the figure critic

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/audits-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/audits-light.svg" alt="Audits, triage and the figure critic section strip" width="100%">
  </picture>
</p>

Uploaded by a second agent on Tubai's command. Five repositories were added to the project on
21 October; three gave the engine a part each, two gave nothing. None of the three closes a
conjecture, and nothing here changes a label.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-audit-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-audit-light.svg" alt="The audit of a de Sitter self-mass in nine stages, its findings by kind, the triage of five candidate problems and the figure critic loop" width="100%">
  </picture>
</p>

- **The audit** ([`bllm/audit.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/audit.py)),
  from E. O. Kahya's re-derivation of the one-loop graviton self-mass of a massless scalar on de
  Sitter space ([creelie/claude-audits-quantum-gravity](https://github.com/creelie/claude-audits-quantum-gravity), MIT).
  A published calculation is cut into the stages of its printed equations; each stage has a
  derivation, a separate code check and a comparison with the print, and every difference is one of
  five kinds, of which only a substantive one can change a conclusion. The stored record
  `desitter-scalar-self-mass` holds the source's counts: 4 substantive findings, 6 absorbed by
  counterterms, 23 typographical, 31 confirmed and 10 about the conclusion, which survives (no
  significant late-time correction to the mode function). `anaxia audit --golden DIR` is the
  source's golden-output runner: every check script must reproduce its stored output after a fixed
  normalisation, a stored output without its script is an error, and a script without one must
  print nothing. Rerun here with that runner on the source's own checks: 38 of 38 runs pass. An audit checks someone
  else's work; its label is "audit (not a closure)".
- **Triage before the attack** ([`bllm/triage.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/triage.py)),
  after the supplied-input opportunity comparison of MontrealAI's
  [AGI-Alpha-Agent](https://github.com/MontrealAI/AGI-Alpha-Agent-v0) (Apache-2.0). Each candidate
  is rated for value, closability, effort and risk; a candidate below the minimum closability or
  above the maximum risk is a no-go whatever its value, the rest are scored in exact rational
  arithmetic and the Pareto front is marked. `anaxia triage` runs the bundled example: of five
  candidates, the remaining 13-crossing bridge indices and 4D crosscap numbers are a go, the
  depth-23 seed search, the H = 22 Diophantine equation and (F2) are no-go. The ratings are
  judgements put in by hand; the triage makes the go/no-go explicit before any search starts.
- **The figure critic** ([`bllm/figcritic.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/figcritic.py)),
  after the critic agent of [PaperBanana](https://github.com/dwzhu-pku/PaperBanana) (ICML 2026,
  arXiv:2601.23265). The rules that can be decided on the vector source run as exact checks:
  labels inside the canvas, no overlapping labels on a line, no "Figure N:" caption inside the
  figure, alt text, the same text in the light and dark versions, and every CSS animation stopped
  under reduced motion. `anaxia figcritic` runs it, and a test runs it on every figure of this
  README, which pass.
- **More motion.** Every chart now draws itself: lines trace, bars rise, the newest point pings,
  and the stat cards carry a passing sheen. Each section below has an animated strip, and all
  motion stops for readers who ask for reduced motion.
- **Left out.** [Next-Concept Modeling](https://github.com/HazyResearch/ncm) is a text generator
  that needs trained weights and a GPU, and [ARTEMIS](https://github.com/google/artemis) drives
  Android phones; neither bears on proofs or constructions, so nothing was taken.

### ultraviolet finiteness of gravity from a scale-invariant gas of branes

Uploaded by a second agent on Tubai's command. The paper "Cancellation of all ultraviolet
divergences of quantum gravity by a scale-invariant gas of branes" (Deep Bhattacharjee and
Ushashi Bhattacharya, [creelie/brane-cluster-gases](https://github.com/creelie/brane-cluster-gases),
release 3.1.0, [10.5281/zenodo.23524276](https://doi.org/10.5281/zenodo.23524276)) proves that
a frozen Poisson gas of branes with no preferred size multiplies the graviton kinetic operator by
an entire function without zeros, exp[(n/2) Ein(□²/M⁴)] times a random factor with a limit at
high momentum, and that for n ≥ 4 the theory of gravity built on it has no ultraviolet divergence
at any order of perturbation theory: every graph with two or more loops converges, the three
one-loop poles are cancelled by three quartic operators with finite coefficients, Newton's
constant and the cosmological constant do not run, the zero-point energy is finite and the same
for every regulator, and the physical S matrix is unitary at every loop order. This is a theorem
within perturbation theory and it is not refereed: the control `brane-gas-uv-finite` is a
CANDIDATE, blocked by the formal and human verifiers (the Lean file of the paper proves the
integer statements behind the power counting and the tuning, not the analytic theorem). The
constructions of the proof are now part of construction mode as
[`construct/brane_formfactor.py`](https://github.com/creelie/eBLLM/blob/main/src/ebllm/construct/brane_formfactor.py),
each with its check and its refuter in the tests.

- **The response of one brane.** A brane multiplies the kinetic operator by exp(ϑ ψ(sz)) with
  ψ entire; the cell model gives ψ = 1 − exp(−w²). The module checks (S1) no effect on long
  modes, (S2) passivity, (S3) saturation on the real axis and (S4) saturation in a sector, and
  (S5), no zeros, holds for every exponent. The refuter is the obvious saturating factor
  2 − exp(−w²), which obeys (S1)–(S4) and vanishes at w² = −log 2 + 2πik: a gas of such branes
  has about nR²/(πM⁴) complex poles in |z| < R, Lee–Wick pairs that (S5) never produces. Every
  polynomial form factor, the other route to power growth, has zeros as well. This is the first
  record of the run in the log: a representation failure, repaired by writing the factor as an
  exponent.
- **Power counting.** The degree of an L-loop subgraph is bounded by
  ω̄(n, L) = 4L − (2n+2)(L−1) + 2(L − n − 1 + m)₊, negative for every L ≥ 2 exactly when n ≥ 4
  (the table of the paper is reproduced; at n = 3 the two-loop bound is 0). The merging lemma
  behind the bound is re-derived by exhaustive enumeration of every vertex-degree vector up to
  six loops, with no inequality assumed, and no vector beats it.
- **The one-loop tuning.** The pole matrix of the three quartic operators,
  (1/c)[[−12, −1, −8/3], [0, 1, 8], [0, 0, 2]], is triangular with determinant −24/c³, and the
  tuning t = (3b₁ + 3b₂ − 8b_E, −36b₂ + 144b_E, −18b_E)/36 cancels the three poles at once, in
  exact rational arithmetic for any poles b.
- **The vacuum energy.** ρ₁ = 3nM⁴/(64π²) and Λ₁ = 3nGM⁴/(8π); the Mellin identity
  ∫w^{s−1} Ein(w) dw = Γ(s)/s behind the regulator independence is checked in its strip.
- **Where the Euclidean picture stops.** The time-slice covariance F_q(t) of the free graviton
  of the gas turns negative near t = 12/M for q = M (about −8 × 10⁻⁷, on two grids), which the
  Laplace transform of a positive measure never does: the free Euclidean field is not reflection
  positive. The log records this as a missing mode and narrows the scope to perturbation theory.
- **Where perturbation theory stops.** From the one-loop bubble of the paper (data, not
  recomputed here), the graph overtakes the tree amplitude at E/M = 1.41 for M = 10⁻² M_P and
  1.88 for M = 10⁻⁴⁰ M_P; the loop expansion is an expansion in a small number only below that.
- **What the log learned.** The run adds three records (a representation failure repaired by
  the exponent, the closure, and the missing mode at the Euclidean boundary with the scope
  narrowed to perturbation theory). Since the trajectory closed, the skill memory now puts a
  narrower scope second after a missing mode, where the playbook puts a representation: the
  fourth diagnosis on which the two disagree. `anaxia skills` reports 30 trajectories.

## New in 3.1.0

- **It learns from its failures.** Every failed attempt now writes a record: what was tried, why
  it failed, which rule of the engine was changed (its old and its new value), what the change was
  meant to improve, and what the next attempt under the new rule did. `anaxia modlog` prints the
  log. The loop never makes the same change twice, so it stops; the bound is proved in Lean.
- **It credits a change by the whole run it belonged to.** A change can be needed without being
  enough: on Steinberg's gadget the new mode and the planar frames were each followed by a failed
  attempt, and the attempt that closed ran with both. The skill memory, after HyperSkill (Xu, Yang
  and Huang, arXiv:2608.16114), keeps each run as one hyperedge: changes in runs that closed or
  advanced become strategies, changes in runs that only failed become patterns to avoid, and a
  kind of change used three times with less than a fifth of its runs advancing is pruned.
  `anaxia skills` prints it.
- **It crossed a sub-benchmark.** The Calabi–Yau seed conjecture, in its uniform form, closes.
  Shrink a reflexive 4-polytope to the next reflexive polytope inside it, never skipping one, and
  repeat until none fits: from any of the 473,800,776 polytopes of Kreuzer and Skarke, every such
  descent reaches a seed within 348 steps. Each step loses lattice points while the dual gains
  them, and the pairs of counts that occur in the classification allow no longer chain, so no
  descent had to be searched. The sharp constant is 5 in two dimensions and 11 in three; in four
  it lies between 22 and 346, the lower bound from two skew bipyramids with 37 lattice points
  whose depth is exactly 22. The benchmark itself, across theoretical and mathematical physics,
  pure mathematics and cs.AI, counts as attained only when one of the four target conjectures
  (strings, seeds, Hodge, Yang–Mills) closes in full, and none has yet.
- **Its log holds the other attacks too.** Every attack of 19 October that used the engine logs
  its failures in the same format: simple zeros of the zeta function, the Erdős–Straus exceptional
  set, union-closed families, sixteen lonely runners, generations on the Dwork quintic, the
  gauge-fixed mass gaps of lattice Yang–Mills, and points in convex position in four dimensions.
  With the engine's own runs the log now holds 10 runs, 25 targets, 73 attempts and 57 rule
  changes; 29 of the 48 changes whose retry has run closed or advanced their target. The skill
  memory ranks the changes differently from the playbook after three diagnoses: after an
  overclaim it tries a check first where the playbook tries narrowing the scope, after a search
  too large it puts a larger budget third, and after a wrong representation it puts a check
  before a reduction.
- **It screens claimed steps against their counterexamples.** Rules taken from failures on open
  problems now run as exact checks. A bound on the Liouville correlations below the size that
  random signs would give is rejected: the collar bound of a Riemann-hypothesis route fails by a
  factor of 129 already at X = 6000, over 1,053 shifts. An Erdős–Straus normal form is tested
  against every solution of small cases, and 4/73 = 1/20 + 1/210 + 1/30660 breaks one. A
  constant given by a series over primes is quoted only with its tail added and only when two
  cutoffs a factor 10 apart agree. A definition may be replaced only by one that explains every changed example and carries more
  consequences, and a conditional result counts only with a witness that meets all its
  hypotheses and is not degenerate, the check that closed an empty hypothesis bundle in the Lean
  formalization of Landau damping.
- **44 engine theorems in Lean.** Added: the bounds of the loop and of a descent of
  lattice-point counts (`lean/EBLLM/SelfMod.lean`), and the eight theorems of the Hodge gaps,
  which earlier releases carried but did not build. Every one depends only on `propext`,
  `Classical.choice` and `Quot.sound`.
- **A map of itself.** The diagrams below are read from the package: its parts and how they are
  wired, the loop and what it changed, and how the engine grew from release to release.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-logo-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-logo-light.svg" alt="ANAXIA, the BLLM engine" width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/creelie/eBLLM/pkgs/container/bllm-engine"><img src="https://img.shields.io/badge/PULL%20THE%20IMAGE-ghcr.io%2Fcreelie%2Fbllm--engine-0d9488?style=for-the-badge&logo=docker&logoColor=white" alt="pull the image"></a>
  <a href="#the-superstring"><img src="https://img.shields.io/badge/SUPERSTRING-run%20the%20four%20chains-e11d48?style=for-the-badge" alt="the superstring"></a>
  <a href="https://github.com/creelie/eBLLM/blob/main/src/ebllm/bllm/data/atlas.json"><img src="https://img.shields.io/badge/BARRIER%20ATLAS-walls%2C%20breakers%2C%20routes-d97706?style=for-the-badge" alt="the barrier atlas"></a>
  <a href="#what-anaxia-has-proved"><img src="https://img.shields.io/badge/LEAN%204-kernel%20checked-6d28d9?style=for-the-badge" alt="proved in Lean"></a>
  <a href="#the-paper"><img src="https://img.shields.io/badge/THE%20PAPER-read%20it-2563eb?style=for-the-badge" alt="the paper"></a>
  <a href="#install-and-update"><img src="https://img.shields.io/badge/INSTALL-pip%20or%20docker-64748b?style=for-the-badge" alt="install"></a>
  <a href="https://github.com/creelie/eBLLM/releases"><img src="https://img.shields.io/badge/RELEASES-archived%20on%20Zenodo-7c3aed?style=for-the-badge" alt="releases"></a>
</p>

## Contents

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/contents-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/contents-light.svg" alt="Contents section strip" width="100%">
  </picture>
</p>

| Section | What it holds |
| --- | --- |
| [How it thinks](#how-it-thinks) | the typed library, crossing, checks, refuters, Lean, memory |
| [The round](#the-round) | the eight stations of one round, each with its measured number |
| [It learns from failure](#it-learns-from-failure) | the learn-from-failure log and the skill memory |
| [Point it at a conjecture](#point-it-at-a-conjecture) | tasks, attacks and the barrier atlas of the four targets |
| [The superstring](#the-superstring) | one attack chain per target, an attacker on every zone and piece, and where each stops |
| [What Anaxia has proved](#what-anaxia-has-proved) | the theorems of the engine, kernel-checked in Lean 4 |
| [What the runs show](#what-the-runs-show) | the measured record: composites, memory, agents, proposers |
| [It builds, too](#it-builds-too) | construction mode: gadgets, reflexive polytopes, definition repair |
| [How it grew](#how-it-grew) | each release and the failure that caused it |
| [What it draws on](#what-it-draws-on) | the sources, by part |
| [What it has not done](#what-it-has-not-done) | the four targets stay open, and why |
| [Install and update](#install-and-update) · [Commands](#commands) | pip, docker, and every `anaxia` command |
| [Add a target](#add-a-target) · [The paper](#the-paper) | how to point the engine at a new problem; the paper and its Lean |
| [Labels](#labels-of-the-recorded-results) · [Checks](#checks) · [Releases](#releases-and-the-closure-rule) | what a label means, what CI runs, how a release is cut |
| [Layout](#layout) · [Citing](#citing) · [Licence](#licence) | the tree, the DOI, MIT |

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

The next attempt is not the whole story, so the engine also keeps every run as one hyperedge of a
hypergraph, as HyperSkill keeps an agent's trajectories (Xu, Yang and Huang,
[arXiv:2608.16114](https://arxiv.org/abs/2608.16114)). The edge binds the diagnoses met on the way,
the changes made and the best outcome reached. Changes in runs that closed or advanced are
strategies, changes in runs that ran to the end and only failed are patterns to avoid, and runs
still waiting on a change, or ending in a stop because the target was settled or the attack moved
to a weaker target, count for neither.
A new failure ranks the kinds of change by how many retrieved strategies minus patterns used them
for the same diagnosis, then by the strategies of the same run, then by the playbook. A kind used
three times with less than a fifth of its runs advancing is pruned, and the exact change is
refused. The memory is computed from the log, so it cannot drift from it.

```console
$ anaxia skills
31 trajectories: 7 open, 1 pattern, 4 stopped, 19 strategy
  strategy  construction: Steinberg gadget (k = 5) (closed); missing-mode -> mode, filter-cost -> representation, generator -> strategy
  ...
  pattern   strings: Geometric Selection Conjecture (failed); generator -> reduction
  ...
changes whose own retry failed, inside a run that closed or advanced:
  construction: Steinberg gadget (k = 5) #1, missing-mode -> mode (mode)
  construction: Steinberg gadget (k = 5) #2, filter-cost -> representation (planarity)
  seed: Seed conjecture, uniform bound (d = 4) #1, representation -> representation (descent step)
  riemann: Proportion of simple zeros on the line #1, overclaim -> check (higher-order inputs)
  riemann: Proportion of simple zeros on the line #2, representation -> check (relaxations)
  riemann: Proportion of simple zeros on the line #3, overclaim -> check (constants)
  union-closed: Union-closed sets conjecture #1, overclaim -> retrieval (before a search)
  happy-ending: Lower bounds for g^(d)(8) #1, representation -> representation (score)
```

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/conjecture-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/conjecture-light.svg" alt="Point it at a conjecture section strip" width="100%">
  </picture>
</p>

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/proved-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/proved-light.svg" alt="What Anaxia has proved section strip" width="100%">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-results-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/anaxia-results-light.svg" alt="Results and progress of Anaxia: 109 attempts in 21 runs: 13 closed, 34 partial, 44 failed, 18 stopped; 14 closures and 9 partial results among the controls, none refereed; 9 targets open, 0 of the 4 superstring targets closed." width="100%">
  </picture>
</p>

The board above is drawn by [`docs/assets/make_results.py`](https://github.com/creelie/eBLLM/blob/main/docs/assets/make_results.py)
from the controls and the learn-from-failure log: each control with the verifiers it has passed,
and each attempt as a dot coloured by its outcome, the latest run last. The closures and partial
results are candidates until refereed; the targets in the right column are open.

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/builds-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/builds-light.svg" alt="It builds, too section strip" width="100%">
  </picture>
</p>

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/sources-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/sources-light.svg" alt="What it draws on section strip" width="100%">
  </picture>
</p>

`anaxia fetch deepmind` and `anaxia intake deepmind` hold the survey of all 409 public
repositories of Google DeepMind: 22 are pinned at exact commits for their mathematics (Formal
Conjectures, the AlphaProof Nexus results, AlphaEvolve's results and problem repository, FunSearch,
AlphaGeometry, the IMO, Putnam and miniF2F formalisations and others), 14 are recorded as related,
and the rest are left out with a reason. Their 5,035 items (1,471 open and 2,437 solved Formal
Conjectures statements among them) are indexed in the package and load into memory as literature,
so the engine asks whether a target is already settled before it attacks it. Nothing fetched is
executed. [`THIRD_PARTY.md`](https://github.com/creelie/eBLLM/blob/main/THIRD_PARTY.md) lists every source, its licence and what was taken.

Three of the repositories added on 21 October gave the engine a part each: the audit protocol and
golden-output runner of E. O. Kahya's de Sitter audit, the go/no-go triage of MontrealAI's
AGI-Alpha-Agent, and the figure critic after PaperBanana (Zhu et al., arXiv:2601.23265). Next-Concept
Modeling and ARTEMIS were read and nothing was taken from them.

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

<details><summary>The registry (38 entries)</summary>

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
| Landau damping in Lean | Methods | the witness gate: a conditional result counts only with a witness meeting every hypothesis and nondegeneracy… | src/ebllm/construct/reformulate.py (witness_gate, RULES) |
| Kontsevich on definitions | Methods | definition repair: a definition is replaced only when every changed example has a reason and the new one… | src/ebllm/construct/reformulate.py (repair) |
| OpenAI mathematics manuscript collection | OpenAI | the move statistics of the crossing network and an index of the manuscripts for the check that a target is… | src/ebllm/bllm/corpus.py (read_openai); src/ebllm/bllm/sources.py (index_openai) |
| OpenAI Navier-Stokes Lean proof | OpenAI | a literature row with its status; its build record applies the rule of Anaxia's Lean check (kernel check,… | src/ebllm/bllm/sources.py (registry) |
| trureturing (OpenRefute) | The Omega Institute | an index of the 782 problem dossiers (statement, resolution, Lean declaration, link): refuter data, since it… | src/ebllm/bllm/sources.py (index_openrefute); anaxia sources check |
| obsidian-brain | Memory | memory as a vault of linked notes, and retrieval that returns each hit with its link neighbours | src/ebllm/bllm/vault.py (Vault.write; Vault.search: TF-IDF over the notes plus… |
| claude-obsidian (lab009dm) | Memory | notes captured with their provenance and linked to what they were built from | src/ebllm/bllm/vault.py |
| HyperSkill | Memory | one hyperedge per trajectory, so a change is credited by the whole run it belongs to: strategies from runs… | src/ebllm/bllm/skills.py (SkillMemory: trajectory, rank, pruned, refused);… |
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

- It has attained none of its benchmarks. The seed bound for the Calabi–Yau seed conjecture is a
  sub-benchmark; the benchmark is attained only by the full closure of one of the four target
  conjectures, strings, seeds, Hodge and Yang–Mills. The five problems it started with stay open: the Yang–Mills mass
  gap, the Hodge conjecture, Grothendieck's standard conjecture B, Chowla's conjecture and Erdős
  problem 1183. In four dimensions the sharp seed constant, the fewest steps that suffice for every
  polytope, is not yet known; it lies between 22 and 346.
- It did not originate the step it is best known for. The composite for the β_W < 1/3 gap was
  first proposed by the language-model proposer and then entered in the library; the network
  reproduces it.
- Every survivor of the amplified round is a form of a range already proved, or (F2) in dimension
  at most five, which was known.
- The Hodge-only run of eleven rounds produced no survivor that was not already known and reached
  no target point (chart above).
- On the Hodge conjecture the latest rounds decided most of family (a) on E_0^6 negatively: every
  convolution with at most seven line bundles fails the criterion, by a parity count on the closed
  chains against the Chern character, a lemma that a zero step next to a nonzero one carries no
  deformation, and a search over every arrangement of shifts. Both arguments were made by hand and
  entered in the log as changes of the rules. The same holds at every discriminant (product
  polarisations with weights on the six factors), and a locality theorem shows that wherever the
  object is a shifted line bundle on a threefold near its generic point, it must stop being one along
  an ample divisor. A second argument, the semiregularity map with supports, shows that every
  object supported on the 32 Weil threefolds fails, at every discriminant and with any number of
  line bundles. With eight line bundles 31 arrangements of shifts are left, 8 of them with full
  support and 23 of rank zero, and no target point is reached.
- Nine changes of its log have no retry yet. Three are not built (search over planar
  arrangements, for Erdős's question and the Bordeaux conjecture, and a rank check that rejects a
  chain for sqrt 10 at admission); six are running or being built (the certification of the
  bound 50 for the seed constant, the nine-zero window for simple zeros, the SAT run with 13
  elements for union-closed families, five gates for the lonely runners, blocks of links for
  Yang–Mills, and the next bounds in convex position).
- No result of the project is refereed, so every one of them is labelled CANDIDATE.

## Install and update

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/install-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/install-light.svg" alt="Install and update section strip" width="100%">
  </picture>
</p>

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
pip install "ebllm[construct] @ git+https://github.com/creelie/eBLLM"   # with networkx, python-sat and numpy
anaxia --version                                       # ebllm and python -m anaxia are the same
```

The Lean library needs [elan](https://github.com/leanprover/elan); `lean/lean-toolchain` pins
Lean 4.34.1 and the library uses Lean core only.

## Commands

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/commands-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/commands-light.svg" alt="Commands section strip" width="100%">
  </picture>
</p>

```sh
anaxia tasks                 # stepwise records of solved and open problems (14 tasks)
anaxia attack hodge          # the open steps of a task, their ladders and the plan
anaxia controls              # closures, calibrations and open problems, with their labels
anaxia gap                   # the gap law on the human and language-model idea data
anaxia schedule 1,2,4        # the entropy-law schedule for given check costs
anaxia scan lean/            # Lean sources: sorry, axiom, native_decide, unsafe (comments ignored)
anaxia axioms audit.log 44   # only propext, Classical.choice and Quot.sound may appear
anaxia modlog --patterns     # the learn-from-failure log and what each kind of change achieved
anaxia skills                # the same log as a hypergraph of runs: strategies, patterns, pruning
anaxia barriers --target hodge  # the barrier atlas: walls, hypotheses, breakers, routes of a target
anaxia superstring --target hodge  # the attack chain of a target: attackers, gaps, where it stops
anaxia superstring --zone frontier  # the attackers of one zone across the four targets
anaxia construct steinberg   # construction mode (see above)
anaxia intake deepmind       # what the engine takes from Google DeepMind
anaxia sources check TEXT    # whether a statement is already settled (DeepMind, OpenRefute, OpenAI)
anaxia update                # whether a newer image is published
```

The continuous loops are `experiments/loop.py` (five problems) and `experiments/hodge_loop.py`
(Hodge only). [`docs/USAGE.md`](https://github.com/creelie/eBLLM/blob/main/docs/USAGE.md) explains the spec format and the Python interface.

## Add a target

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/target-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/target-light.svg" alt="Add a target section strip" width="100%">
  </picture>
</p>

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/paper-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/paper-light.svg" alt="The paper section strip" width="100%">
  </picture>
</p>

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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/labels-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/labels-light.svg" alt="Labels of the recorded results section strip" width="100%">
  </picture>
</p>

`anaxia controls` computes each label from the verifier factors stored in `src/ebllm/controls/`.
A result that has not been refereed is a CANDIDATE, however strong its formal evidence; open
problems are OPEN.

<details>
<summary>All 38 controls</summary>

| control | group | label | blocking verifiers |
|---|---|---|---|
| Cancellation of all ultraviolet divergences of quantum gravity by a scale-invariant gas of branes (theorem, every order of perturbation theory, n >= 4) | closure | CANDIDATE | formal, human |
| Gas-averaged graviton propagator of a Poisson brane gas has ghosts (theorem) | closure | CANDIDATE | formal, human |
| Lattice Golomb-Welch conjecture for Lee balls of radius three in dimensions 35 and 805 (proved) | closure | CANDIDATE | human |
| Graffiti.pc Conjectures 319, 352, 358, 359, 427 on domination (refuted) | closure | CANDIDATE | human |
| Gurvich-Naumova conjecture: {1,...,n} splits into parts of size <= 3 with power-of-3 sums (proved) | closure | CANDIDATE | human |
| Kourovka Notebook Problem 20.71(b): a graph with three card types and five vertex orbits (answered) | closure | CANDIDATE | human |
| Tran's Conjecture 8.6 on regular Morley tetrahedra (refuted) | closure | CANDIDATE | human |
| Rios-Marrani-Chester claim: Nishino's super Yang-Mills construction carries over to (9+8n)+1, (10+8n)+2, (11+8n)+3, (12+8n)+4 (refuted) | closure | CANDIDATE | formal, human |
| Fiujlaali-McDonald conjecture: every odd antihole is strongly chromatic-choosable (proved) | closure | CANDIDATE | human |
| Shankar's Conjecture 4.1 on even-intersecting lattice paths (proved) | closure | CANDIDATE | formal, human |
| Fomichev-Karev-Pavutnitskiy-Usanov conjecture: the sl(2) weight system at c = -3/32 extends to a graph 4-invariant (proved) | closure | CANDIDATE | human |
| Wang–Tian conjecture on tau_k-maximal graphs (proved) | closure | CANDIDATE | formal, human |
| Hou–Zhao Conjecture 4.10, Welch functions not third-order sum-free (proved) | closure | CANDIDATE | formal, human |
| Graffiti.pc / WOWII Conjecture 66, forest number (refuted) | closure | CANDIDATE | human |
| Book Ramsey number R(B_57, B_58) = 231, the case n = 58 of Wesley's conjecture (partial result) | partial | CANDIDATE | human |
| Meridional rank conjecture for 243 of the 536 thirteen-crossing knots with bridge index [3,4] (partial result) | partial | CANDIDATE | formal, human |
| Nonorientable four-genus of 2,537 of the 3,525 knots with 11 to 13 crossings left open by KnotInfo (partial result) | partial | CANDIDATE | formal, human |
| Densest packings of two translates of a lattice in R^4 (theorem; the 24-cell conjecture stays open) | partial | CANDIDATE | formal, human |
| Erdős Problem 1183: the lower bound of Theorem 1.4 | partial | CANDIDATE | human |
| Geometric Selection Conjecture: the mirror-fixed clause of Theorem D is empty, so GSC is equivalent to a viable vacuum outside L^mu (partial result) | partial | CANDIDATE | formal, sim, human |
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
| Erdős–Straus conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Hodge conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Lehmer's totient problem | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| P versus NP | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Riemann hypothesis | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Yang–Mills existence and mass gap | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |

</details>

## Checks

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/checks-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/checks-light.svg" alt="Checks section strip" width="100%">
  </picture>
</p>

`checks/run_all.sh` runs everything that CI runs:

- 320 Python tests (`tests/`), including the update check, the loop and its log, the skill memory, the reflexive
  polygons, their covers, descents and free sums, definition repair and the witness gate, the
  screens against their counterexamples, the six benchmarks, the audit, triage and figure critic, and this README against the package;
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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/releases-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/releases-light.svg" alt="Releases and the closure rule section strip" width="100%">
  </picture>
</p>

A closure is finished only when the engine and the paper both carry it: the library and the task
suite get the construction with its Lean proof, a release rebuilds the image and is archived on
Zenodo with a version DOI, and the paper is rewritten as one text that carries the result in its
place. The same rewrite is due whenever enough new measured data would change what the paper
says. The steps are in [`RELEASING.md`](https://github.com/creelie/eBLLM/blob/main/RELEASING.md).

## Layout

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/layout-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/layout-light.svg" alt="Layout section strip" width="100%">
  </picture>
</p>

| path | contents |
|---|---|
| `src/ebllm/` | the circuit: obligations, verifiers, ledger, release algebra, controls, update check |
| `src/ebllm/bllm/` | the network: schedules, crossing, memory, the learn-from-failure loop and its log, targets, attack channel, agents, proposers, connectome selector, benchmark, tasks, DeepMind intake |
| `src/ebllm/construct/` | construction mode: builder, exists-forall searches, gadget algebra, assembly, the independent checks, stored gadgets, the knot, brane-gas, TheoPhysEval and several-times super Yang–Mills constructions |
| `src/anaxia/` | the `anaxia` name of the same package |
| `lean/` | the engine's Lean library (44 theorems, Lean core): the circuit, the release algebra, the Hodge gaps, the loop and descent bounds |
| `paper/bllm/` | the paper, its Lean development (65 theorems, Mathlib) and its checks |
| `experiments/` | benchmark logs, the loops, the Hodge-only run, Erdős 1183 searches, the Yang–Mills scout, fine-tuning |
| `checks/` | Python, C, C++ and Julia checks |
| `docs/` | review, circuit v1.1, usage, artwork and the script that draws it |

[`HARDWARE.md`](https://github.com/creelie/eBLLM/blob/main/HARDWARE.md) says what each component needs and [`DEVICE_RUN.md`](https://github.com/creelie/eBLLM/blob/main/DEVICE_RUN.md)
which runs are meant for a larger machine.

## Citing

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/citing-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/citing-light.svg" alt="Citing section strip" width="100%">
  </picture>
</p>

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
- v3.1.0: [10.5281/zenodo.23484160](https://doi.org/10.5281/zenodo.23484160)
- v3.1.1: [10.5281/zenodo.23484395](https://doi.org/10.5281/zenodo.23484395)
- v3.2.0: [10.5281/zenodo.23524665](https://doi.org/10.5281/zenodo.23524665)
- v3.2.1: [10.5281/zenodo.23524945](https://doi.org/10.5281/zenodo.23524945)
- v3.3.0: [10.5281/zenodo.23548148](https://doi.org/10.5281/zenodo.23548148)
- v3.3.1: [10.5281/zenodo.23557319](https://doi.org/10.5281/zenodo.23557319)
- all versions (concept DOI): [10.5281/zenodo.23286641](https://doi.org/10.5281/zenodo.23286641)

The master zip [`BLLM_masterzipfinal2.zip`](https://github.com/creelie/eBLLM/raw/main/BLLM_masterzipfinal2.zip)
holds release v3.1.1 with the paper, its Hexagon upload and its JAIR submission.

## Licence

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/licence-dark.svg">
    <img src="https://raw.githubusercontent.com/creelie/eBLLM/main/docs/assets/sections/licence-light.svg" alt="Licence section strip" width="100%">
  </picture>
</p>

MIT, see [`LICENSE`](https://github.com/creelie/eBLLM/blob/main/LICENSE). The papers in `paper/` are their authors' and are included for
reference.


</details>
