# Releasing Anaxia

## The closure rule

A closure of a conjecture is finished only when the engine and the paper both carry it, in the
same round of work:

1. **Engine.** The construction that closes it enters the library of its agent
   (`src/ebllm/bllm/`), its check program and its refuter run in the tests, and the task suite gets
   a record with the Lean proof (`src/ebllm/bllm/tasks/<name>.json`, and the Lean file in the
   development that the record names). `anaxia controls` gets the control with its verifier
   factors, so that the label is computed, not written.
2. **Release.** The version in `pyproject.toml`, `src/ebllm/__init__.py`, `CITATION.cff` and
   `.zenodo.json` goes up, `.github/RELEASE_NOTES.md` says what was closed, and after the PR is
   merged the `release` workflow is run from the Actions tab with the tag `v<version>`. It tags
   the commit, publishes the GitHub release, and starts the `package` workflow for the tag, which
   publishes the image `ghcr.io/creelie/bllm-engine:<version>` and `latest`. Zenodo archives the
   release with a version DOI.
3. **Paper.** The paper (`paper/bllm/paper/`) is rewritten as one integrated text that carries
   the closure in its place, not given an appended section: the introduction, the results, the
   tables and the figures (redrawn from the run data) are revised together so that the text reads
   as one account from the first line to the last. The data availability paragraph names the
   release and its DOI. The DOI exists only after the release, so it is recorded in a patch
   release (`v<version>` + 0.0.1) together with the rebuilt paper.

The same integrated rewrite of the paper, with a release of the engine, is also due whenever
enough new measured data has accumulated to change what the paper says: a new benchmark run, a
new arm of an experiment, or a new negative result on a target point, once its numbers would
alter a table, a figure or a sentence of the abstract or the introduction. A run that only
repeats a measured plateau does not count.

A result that has not been refereed is a CANDIDATE, whatever its formal evidence, and is
described as such in the engine, the release notes and the paper.

## Every merge

Every merge to `main` rebuilds the image and publishes it as `latest` and as the current
version, after the version, the command line and the Lean axiom audit pass inside it. Running
copies notice the new build at start and print the pull command (`anaxia update`).

## Checks before a release

- `bash checks/run_all.sh` (the Python tests, the C, C++ and Julia checks, the Lean build, scan,
  axiom audit and kernel replay, and the example run);
- `bash paper/bllm/checks/run_all.sh` and `latexmk -pdf main.tex` in `paper/bllm/paper`;
- `git log --format='%an %cn'` names only the author.
