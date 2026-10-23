# Exact interval certificates for reflexive descents

This research revision gives a shortest-descent upper bound of 346 relative to the supplied Kreuzer–Skarke point-pair census. It does not determine the sharp constant D4. The pre-existing arbitrary-descent bound is 348 and the pre-existing lower bound is 22. Neither Hodge nor GSC is closed.

Run `anaxia construct seed-intervals`, or `python -m ebllm.construct.seed_intervals` with `PYTHONPATH=src`. No third-party Python package is required. The proof and table are integrated in `paper/bllm/paper/sections/sec10i_seed.tex`.

The independent checker recomputes exact supporting hyperplanes, primal and polar lattice-point sets, the pair dynamic program, strict containment, interval costs, and complete coverage of all pairs above 346. Distinct determinant spectra separate the two representatives with pair (520,26). It rejects incomplete coverage, altered cuts and altered costs. The numerical global bound still uses the supplied histogram and published classification; this revision did not regenerate that histogram by scanning all 473,800,776 coordinate records.

## Data attribution

Vertex coordinates derive from Maximilian Kreuzer and Harald Skarke's classification, *Complete classification of reflexive polyhedra in four dimensions*, Advances in Theoretical and Mathematical Physics 4 (2000), 1209–1230, DOI 10.4310/ATMP.2000.v4.n6.a2. Coordinates were retrieved from https://huggingface.co/datasets/calabi-yau-data/polytopes-4d (CC BY-SA 4.0). The derivative coordinate/certificate data `seed_top346.json` retain CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . Source URLs and file digests are recorded in the bundle. The histogram `seed_point_pairs.csv` was copied from creelie/seed's existing census. The engine's code license is not a relicensing of these data.

The construction search proposed cuts with a floating-point hull routine. The retained witnesses were checked afresh by integer facet enumeration, and the floating-point hull is not used by the verifier. This separation is essential: the verifier does not trust a proposer assertion that a cut is a cover. Instead a self-contained finite-interval lemma supplies a chain of genuine covers with a certified cost.
