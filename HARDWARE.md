# Hardware

All measured figures come from one cloud container: 4 vCPU (x86-64), 15 GB RAM, no GPU, about 40 GB of writable disk. Where a figure was not measured it says so, and it is an estimate. Run `python3 scripts/check_hardware.py` before a run; it checks the machine against the minimum column for each component, and with `--component NAME` against that row only.

| Component | Minimum | Recommended | Measured here |
|---|---|---|---|
| Python package, tests, crossing network, boosters | 1 CPU, 1 GB RAM, 200 MB disk | 4 CPU, 4 GB RAM | 58 unit tests in seconds; the boosters study (200 seeds) in minutes |
| Memory store (SQLite) | 50 MB disk | 1 GB disk for long loops | 156 KB after 5 rounds of one seed; grows by one row per checked composite |
| Five-benchmark run (`experiments/superbrain.py 60 5`) | 2 CPU, 2 GB RAM | 4 CPU, 4 GB RAM | 330 s for 60 seeds × 5 rounds × 5 arms on 4 vCPU (shared with three annealing jobs) |
| Continuous loop (`experiments/loop.py`) | as above | as above, plus the local model | a few seconds per round without the model |
| Local model, Qwen2.5 0.5B Instruct Q4_K_M (llama.cpp, CPU) | 2 CPU, 1.5 GB RAM, 0.5 GB disk | 4 CPU, 2 GB RAM | file 469 MB; peak RSS 784 MB; 41 tokens/s on 4 vCPU |
| Local model, Qwen2.5 1.5B Instruct Q4_K_M | 4 CPU, 3 GB RAM, 1.2 GB disk | 8 CPU or a GPU with 4 GB VRAM | file 1.1 GB; peak RSS 2.1 GB; 16 tokens/s on 4 vCPU |
| Fine-tuning the local model on its verified successes (LoRA, expert iteration) | not run here: needs torch and peft | estimate: GPU with 16 GB VRAM for 1.5B, or 8 GB for 0.5B; 32 GB RAM | torch is not installed in this container; not measured |
| Lean, package library (`lean/`, no Mathlib) | 1 GB RAM, 3 GB disk (toolchain) | 2 GB RAM | cold build 1.8 s, peak RSS 523 MB; toolchain v4.34.1 is 3.0 GB |
| Lean, paper library with Mathlib (creelie/D7 `BLLM/lean`) | 8 GB RAM, 12 GB disk | 16 GB RAM, 20 GB disk | Mathlib package 7.2 GB, toolchain 2.9 GB, build 87 MB; cached check of 8721 jobs 6.1 s, peak RSS 921 MB |
| OpenAI math corpus, full Lean rebuild (1539-file two-point Chowla closure and the rest) | not met here | estimate: 32 GB RAM, 60 GB free disk, 8+ CPU, several hours | source 1.8 GB (121,734 .lean files in the corpus, 3.1 GB with git history). The rebuild did not fit: the container had 3.1 GB free before cleanup and 7.8 GB after, and Mathlib at v4.34.1 alone needs about 7 GB besides the build outputs. Not rebuilt here. |
| SAT certificates (Erdős 1183, pysat) | 1 CPU, 2 GB RAM | 4 CPU, 8 GB RAM | n = 12, s = 8: 20 min 31 s on one core; RAM not measured |
| Grid colourings (`experiments/erdos1183/gridsearch.c`) | 1 CPU, 50 MB RAM | 4+ CPU (one annealing run per core) | one check of a colouring of 2^[20] takes 0.01 to 8 s; a 4000-step annealing run takes about 3.5 min per core |
| Interval-arithmetic Dobrushin–Shlosman check on a gauge-fixed box (Yang–Mills) | not run | estimate: a cluster; side-2 boxes have 48 SU(2) variables per boundary condition | not attempted in this container |

## Disk, by component (measured)

| Item | Size |
|---|---|
| Lean toolchain (each version) | 2.9–3.0 GB |
| Mathlib package with its cache | 7.2 GB |
| Mathlib cache download (`~/.cache/mathlib`) | 440 MB (deleted after unpacking) |
| OpenAI math corpus clone | 3.1 GB (1.8 GB Lean source) |
| Qwen2.5 0.5B / 1.5B Q4_K_M | 469 MB / 1.1 GB |
| SAT and LRAT certificates (n ≤ 12) | under 1 MB of logs; LRAT proofs were not kept |
| Memory store | 156 KB per 5 rounds of one seed |

## Which runs need a bigger machine

The full Lean rebuild of the OpenAI corpus, fine-tuning the local model, and the interval-arithmetic Yang–Mills check do not fit this container. They should run on a machine with the recommended figures above, such as the owner's own computer through a Remote Control session. Everything else runs here.
