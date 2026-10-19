# Third-party material

Anaxia's own code is under the MIT licence (`LICENSE`). This file lists what it takes from
others, under which licence, and how it is credited.

## Google DeepMind

`src/ebllm/bllm/data/deepmind/manifest.json` lists all 409 public repositories of
[github.com/google-deepmind](https://github.com/google-deepmind) as surveyed on 2026-10-19
(GitHub repository search org:google-deepmind (408 repositories) and org:google-deepmind fork:only (1)), with description, licence, stars, last push and one relevance tag:
22 `vendor`, 14 `related` and 373 `none` (robotics and MuJoCo,
reinforcement-learning environments, protein and genome models, language-model libraries,
vision, speech, weather and other work with no bearing on conjectures, proofs, constructions or
checking).

No DeepMind source file is copied into this repository. `anaxia fetch deepmind <name>` fetches a
pinned repository at its exact commit into `$ANAXIA_THIRD_PARTY` (default
`~/.cache/anaxia/deepmind`), and refuses a checkout found at another commit. A fetched repository
is data: nothing in it is imported, built or run by Anaxia. The indexers in
`src/ebllm/bllm/deepmind.py` read its text files and keep, for each item, a name, a kind, a short
statement (at most 400 characters, quoted from a docstring, a README or a problem page), a status
where the source records one, and a link to the file at the pinned commit. That index ships as
`src/ebllm/bllm/data/deepmind/index.json.gz`; `anaxia intake deepmind --memory <file>` writes it into
the shared memory (conjectures and problems as literature rows with their status, constructions
and proofs as library nodes of problem `external`), and `anaxia intake deepmind --search <text>`
is the open-or-solved check of construction mode.

The DeepMind repositories license their software under the Apache License 2.0 and, where they say
so, their other materials under CC-BY 4.0. The quoted statements in the index are short excerpts
with a link to their source and are credited to Google DeepMind and to the authors named in each
repository (formal-conjectures: The Formal Conjectures Authors).

### Vendored (pinned and indexed)

| repository | commit | licence | what Anaxia uses |
|---|---|---|---|
| [alphadev](https://github.com/google-deepmind/alphadev/tree/709dfb1b36f8efa6134145f0563bfb4cb3f8f923) | `709dfb1b36f8` | Apache-2.0 | sorting programs found by AlphaDev, with their correctness checks |
| [alphaevolve_repository_of_problems](https://github.com/google-deepmind/alphaevolve_repository_of_problems/tree/8f447457957deac61e28bf1676746f0753b3b2f8) | `8f447457957d` | Apache-2.0 | 67 construction problems of Georgiev, Gómez-Serrano, Tao and Wagner with AlphaEvolve's standing on each |
| [alphaevolve_results](https://github.com/google-deepmind/alphaevolve_results/tree/4226acbf237ff9ad10ba7673a2af127a2d8a5971) | `4226acbf237f` | Apache-2.0 | constructions found by AlphaEvolve (Novikov et al. 2025) |
| [alphageometry](https://github.com/google-deepmind/alphageometry/tree/6777cb586cbb46beed28db12dc72c69770b68337) | `6777cb586cbb` | Apache-2.0 | the DDAR deduction engine and AlphaGeometry prover for olympiad geometry |
| [alphageometry2](https://github.com/google-deepmind/alphageometry2/tree/251e7e16f0bba8ac7c83cdea789fccc195d0c0c7) | `251e7e16f0bb` | Apache-2.0 | the DDAR symbolic engine of AlphaGeometry2 |
| [alphaproof-nexus-results](https://github.com/google-deepmind/alphaproof-nexus-results/tree/0647711a71183c1ea492ad60860776617ce1ea88) | `0647711a7118` | Apache-2.0 | Lean proofs found by AlphaProof Nexus (Erdős problems, OEIS, AI-collaborator results) |
| [alphatensor](https://github.com/google-deepmind/alphatensor/tree/1949163da3bef7e3eb268a3ac015fd1c2dbfc767) | `1949163da3be` | Apache-2.0 | matrix multiplication tensor decompositions found by AlphaTensor |
| [alphatensor_quantum](https://github.com/google-deepmind/alphatensor_quantum/tree/3def81a2a42666416a4a8041eea6e1bc98bc8e9f) | `3def81a2a426` | Apache-2.0 | T-count optimised quantum circuits found by AlphaTensor-Quantum |
| [autonumerics_zero](https://github.com/google-deepmind/autonumerics_zero/tree/8acf6c8ae8dfb5c47d8b40fc56ec1b61228b28b8) | `8acf6c8ae8df` | Apache-2.0 | evolutionary program search for numerical routines |
| [cryptids](https://github.com/google-deepmind/cryptids/tree/38ae6721376cba31a4a3ca2d31f9aa93f52f966e) | `38ae6721376c` | Apache-2.0 | Turing machines whose halting encodes Goldbach, Riemann and ZF consistency, with certified reductions in Lean |
| [debate](https://github.com/google-deepmind/debate/tree/de3a6e500ae1a65dfeea2f91ef519ebad9704be0) | `de3a6e500ae1` | Apache-2.0 | Lean formalisation of stochastic doubly-efficient debate (a prover-refuter protocol) |
| [formal-conjectures](https://github.com/google-deepmind/formal-conjectures/tree/197f7f8dcc457f556754f826389d2ec7a0d85b92) | `197f7f8dcc45` | Apache-2.0 | Lean statements of open and solved conjectures (Erdős, OEIS, Millennium, Kourovka, arXiv, ...): the target catalogue and the open-or-solved check |
| [formal-imo](https://github.com/google-deepmind/formal-imo/tree/a85d84b97c8e88a352c136b1e29c355139609bea) | `a85d84b97c8e` | Apache-2.0 | Lean statements of IMO problems |
| [formal-putnam-like](https://github.com/google-deepmind/formal-putnam-like/tree/636c2d46b3a7d7e77a9f58209b0c17816f8d172b) | `636c2d46b3a7` | Apache-2.0 | Lean statements of Putnam-like problems |
| [funsearch](https://github.com/google-deepmind/funsearch/tree/cc53f274237d7ab05c19df939edbc1f9616a7c19) | `cc53f274237d` | Apache-2.0 | constructions found by FunSearch: cap sets, admissible sets, corner-free sets, independent sets of cycle powers |
| [levintreesearch_cm](https://github.com/google-deepmind/levintreesearch_cm/tree/53354f00bdd626bf1024a5313160bc1b745ee763) | `53354f00bdd6` | Apache-2.0 | Levin tree search with context models (search with a cost guarantee) |
| [mathematics_conjectures](https://github.com/google-deepmind/mathematics_conjectures/tree/8302f29101019434e5a0a25807a4e42cd9d96414) | `8302f2910101` | Apache-2.0 | the knot-theory and representation-theory notebooks of Davies et al. (Nature 2021) |
| [mathematics_dataset](https://github.com/google-deepmind/mathematics_dataset/tree/427f45075f84b8b9774950196ad63867ca20ffb3) | `427f45075f84` | Apache-2.0 | generator of school-level question and answer pairs (proposer warm-up data) |
| [mctx](https://github.com/google-deepmind/mctx/tree/428bfb7e1c931715cd3d74f9c65e9991afd86df8) | `428bfb7e1c93` | Apache-2.0 | Monte Carlo tree search in JAX (search over proof and construction trees) |
| [miniF2F](https://github.com/google-deepmind/miniF2F/tree/f0a20e14c1eeccd859d51bb4c2b3ee487889c303) | `f0a20e14c1ee` | Apache-2.0 | miniF2F in Lean 4 with corrected statements |
| [opro](https://github.com/google-deepmind/opro/tree/a76bdce2cbf6d4a0d1e570a6fcfe17be9c2abdd7) | `a76bdce2cbf6` | Apache-2.0 | language models as optimisers (prompted proposal loops) |
| [superhuman](https://github.com/google-deepmind/superhuman/tree/f78413ae6980b2bf61b3ab77d74e118b89bd19a8) | `f78413ae6980` | Apache-2.0 | Aletheia's research outputs, LEAP's AND-OR proof DAG design, IMO-Bench |

### Related (pinned, fetchable, not indexed)

| repository | commit | licence | what Anaxia uses |
|---|---|---|---|
| [abstract-reasoning-matrices](https://github.com/google-deepmind/abstract-reasoning-matrices/tree/6d8ae046f32fb30f6baae72a3dbab753ae111c99) | `6d8ae046f32f` | Apache-2.0 | progressive matrices dataset |
| [AQuA](https://github.com/google-deepmind/AQuA/tree/26b64ed1f22208c6742f47df547dfd65088ec30d) | `26b64ed1f222` | not stated (not used) | algebraic word problems with rationales |
| [bbeh](https://github.com/google-deepmind/bbeh/tree/80d12ca916b7158f22293fcf3144f4d3d854d4be) | `80d12ca916b7` | Apache-2.0 | BIG-Bench Extra Hard |
| [cartesian-frames](https://github.com/google-deepmind/cartesian-frames/tree/23f40b56bf7bf107e222613c882172baae1b5b7f) | `23f40b56bf7b` | Apache-2.0 | HOL formalisation of Cartesian frames |
| [clrs](https://github.com/google-deepmind/clrs/tree/6d5728b9efadf8648413c8c473929a733caacced) | `6d5728b9efad` | Apache-2.0 | algorithmic reasoning benchmark |
| [code_contests](https://github.com/google-deepmind/code_contests/tree/fa7a4f8139aab08362503f3344778eb86901709a) | `fa7a4f8139aa` | Apache-2.0 | competitive programming dataset |
| [exedec](https://github.com/google-deepmind/exedec/tree/ef046ce2cc3fcd024e32f5dfe00e69700dac82ed) | `ef046ce2cc3f` | Apache-2.0 | execution decomposition for program synthesis |
| [gemini_icpc2025](https://github.com/google-deepmind/gemini_icpc2025/tree/43507324739d7e3ac1c3e246be8b3c1829a4194d) | `43507324739d` | Apache-2.0 | ICPC 2025 solutions |
| [llms_can_learn_rules](https://github.com/google-deepmind/llms_can_learn_rules/tree/5c2c523690720a314932dcd8f77c321a3bd9c1f8) | `5c2c52369072` | Apache-2.0 | hypotheses-to-theories rule induction |
| [logical-entailment-dataset](https://github.com/google-deepmind/logical-entailment-dataset/tree/159e76834434c0d29b3588ce8b94e6004697f455) | `159e76834434` | Apache-2.0 | propositional entailment dataset |
| [neural_lns](https://github.com/google-deepmind/neural_lns/tree/103971f61f6083c7049e014682b20f5ee3802afc) | `103971f61f60` | Apache-2.0 | learned large neighbourhood search for integer programs |
| [padic-ml](https://github.com/google-deepmind/padic-ml/tree/53ffd9e79890e76b82ef2dc3c7230984053f9801) | `53ffd9e79890` | Apache-2.0 | p-adic neural networks |
| [tracr](https://github.com/google-deepmind/tracr/tree/9ce2b8c82b6ba10e62e86cf6f390e7536d4fd2cd) | `9ce2b8c82b6b` | Apache-2.0 | compiler from RASP programs to transformer weights |
| [unpuzzles_and_simple_reasoning](https://github.com/google-deepmind/unpuzzles_and_simple_reasoning/tree/39bc520a2f4c243eb04ce1cc27f28c7c61d12e42) | `39bc520a2f4c` | Apache-2.0 | simple reasoning tasks frontier models fail |

## advanced-reasoning-mcp

[creelie/advanced-reasoning-mcp](https://github.com/creelie/advanced-reasoning-mcp) at commit
`29bc37fb1118`, a copy of the Advanced Reasoning MCP server of Tyler Blaine Hall (MIT licence,
copyright 2025 Tyler Blaine Hall). Anaxia takes one idea from it and no code: the TF-IDF ranking of
its memory search (lower-case words without punctuation, words of three letters or more outside a
stop list, term frequency times smoothed inverse document frequency), reimplemented in Python in
`deepmind.Search`, with British spellings and plural endings folded and the score multiplied by
the share of query words found. Left out: the sequential-thinking tool with self-reported
confidence and quality fields, the hypothesis and evidence records and the JSON graph memory.
Anaxia's proposals are judged by programs and a refuter, and its benchmark found that soft scores
attached to proposals (the booster weights) do not reduce the number of checks; a confidence the
proposer reports about itself is not a check, and Anaxia's SQLite memory already keeps every
event with its checked outcome and the refuter's reason.

## Indexes shipped in the package

`src/ebllm/bllm/data/external/` holds two indexes written by `anaxia sources build`. Each item
keeps a statement of at most 400 characters, a status and a link to the file at the pinned commit;
no other text is copied.

| index | source | commit | licence | items |
|---|---|---|---|---|
| `openrefute.json.gz` | [creelie/trureturing-OpenRefute](https://github.com/creelie/trureturing-OpenRefute), a copy of trureturing (The Omega Institute): one dossier per published conjecture, with its Lean claim and kernel-checked resolution | `fa35d5b92f08` | Apache-2.0 | 782 dossiers |
| `openai-math.json.gz` | [creelie/math01-openAI](https://github.com/creelie/math01-openAI), a copy of [openai/math](https://github.com/openai/math): the manuscript abstracts and families | `adc7f1241b42` | Apache-2.0 | 722 manuscripts, all marked unrefereed |

The status of an OpenRefute item (refuted, proved, settled or open) is read from the Triage section
of its dossier by `sources.resolution`; it is the repository's own reading and unrefereed.

## obsidian-brain

[obsidian-brain](https://sweir1.github.io/obsidian-brain/) (npm package, Apache-2.0) contributes
one idea and no code: retrieval that returns each hit together with its link neighbours in the
vault graph. `Vault.search` does this with TF-IDF over the notes and gives each neighbour half the
score of the note it is linked to. Its vector index and its MCP server are left out.

## Other sources read at run time

`src/ebllm/bllm/corpus.py` reads local clones of github.com/openai/math (Apache-2.0) and of
AlphaProof Nexus results; nothing from them is vendored.
