# Runs for a larger machine

These are the two runs that did not fit the 4-CPU container.
keep every output in `runs\device\` on this machine and report the numbers back.

Commands are for PowerShell from the folder that holds `eBLLM\`; use `python` or `py` for Python 3.10+.

## 0. Hardware check

    cd eBLLM
    python -m pip install numpy
    python scripts\check_hardware.py --path .

Report the `machine:` line and the lines for `ds-box` and `finetune`. Run only what the check allows.

## 1. Box Dobrushin–Shlosman scout for SU(2) Yang–Mills

`experiments\yangmills\ds_block.py` estimates, by coupled heat-bath chains, the influence sum of a
gauge-fixed block: `ratio = sum_k / |V|`, and the block condition holds when `ratio < 1`. This is a
Monte Carlo estimate, not a proof, and the coupling overestimates the Wasserstein distance: on a
single link (side 0) the exact value is 3 beta_W, while the estimate reads about 1.4 to 1.7 times
that. So report each block ratio together with the side-0 ratio at the same beta_W, and the
corrected value `ratio_block * (3 beta_W) / ratio_side0`.

Calibration (fast):

    python experiments\yangmills\ds_block.py --beta-w 0.30 0.333 0.40 0.50 --side 0 --perts small --replicas 64 --omegas 4 --sweeps 150 --burn 20 --workers N --out runs\device\ds0.json

Blocks, as far as time allows (side 1 has 24 links and 96 boundary links, side 2 has 162 and 378):

    python experiments\yangmills\ds_block.py --beta-w 0.30 0.40 0.50 --side 1 --perts small --replicas 32 --omegas 2 --sweeps 120 --burn 20 --workers N --out runs\device\ds1.json
    python experiments\yangmills\ds_block.py --beta-w 0.40 0.50 --side 2 --perts small --replicas 16 --omegas 1 --sweeps 80 --burn 15 --workers N --out runs\device\ds2.json

`N` = number of CPU cores minus one. Side 2 is the expensive one; start it only after side 1 and
estimate its time from the first row it prints.

## 2. Fine-tuning the local proposer on its checked successes

The examples are already exported in `experiments\finetune\data_train.jsonl` and `data_test.jsonl`
(1476 and 492 six-way choices from the memory of the agent loop; chance is 1/6).

With an NVIDIA GPU (8 GB or more):

    python -m pip install torch --index-url https://download.pytorch.org/whl/cu124
    python -m pip install transformers peft accelerate
    $env:EBLLM_RUN_DIR = "runs\device"; mkdir runs\device\finetune; copy experiments\finetune\data_*.jsonl runs\device\finetune\
    python experiments\finetune\finetune.py train --epochs 3

Without a GPU use the CPU wheel (`--index-url https://download.pytorch.org/whl/cpu`) and
`--epochs 1 --limit-train 300 --limit-eval 200`. The run writes `report.json` with the accuracy
before and after training on the held-out choices.

## 3. What to bring back

`runs\device\ds0.json`, `ds1.json`, `ds2.json` (if run), `finetune\report.json`, and the
hardware check output.
