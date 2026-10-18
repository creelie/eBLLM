"""Expert iteration for the local-model proposer: fine-tune it with LoRA on the choices the checks confirmed.

The local-model proposer is shown a list of candidate crosses and names one (superbrain.LocalModel.pick).
Training examples are rebuilt from what the checks decided: each example lists one composite that the
check accepted and k-1 closed composites of the same problem that it rejected or stopped, in random order,
and the answer is the number of the accepted one.  The split into training and test examples is by the
accepted composite, so no test answer is seen in training.  Accuracy is measured before and after
training on the test examples by the most likely answer number; chance is 1/k.

    python3 finetune.py export  [--k 6] [--per-positive 12]          # needs only the package data
    python3 finetune.py train   [--model Qwen/Qwen2.5-0.5B-Instruct] [--epochs 3] [--device auto]
                                                                       # needs torch, transformers, peft
Outputs in experiments/finetune/ (or $EBLLM_RUN_DIR/finetune/): data_train.jsonl, data_test.jsonl,
report.json, adapter/.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import random
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
OUT = os.path.join(os.environ.get("EBLLM_RUN_DIR", EXP), "finetune")

PROMPT = ("You choose which construction to try next on an open mathematical problem.\n"
          "Past attempts (from memory):\n{notes}\nOptions:\n{options}\nAnswer with the number only: ")


def load_decisions():
    """(problem, composite id, accepted?) for every closed composite the checks decided."""
    rows = []
    f = os.path.join(EXP, "amplify", "composites.json.gz")
    if os.path.exists(f):
        for e in json.load(gzip.open(f)):
            if e.get("closed") and e.get("outcome") in ("accepted", "rejected", "stopped"):
                rows.append(("yang-mills", e["child"], e["outcome"] == "accepted", e.get("statement", "")))
    for db in ("brain.sqlite", "loop.sqlite"):
        p = os.path.join(EXP, "memory", db)
        if not os.path.exists(p):
            continue
        try:
            c = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=30)
            for prob, seq, outcome, surv, st in c.execute(
                    "SELECT problem, seq, outcome, survived, statement FROM events"):
                rows.append((prob, "(" + "<-".join(seq.split()) + ")", bool(surv), st or ""))
            c.close()
        except sqlite3.Error as ex:
            print(f"skipping {db}: {ex}", file=sys.stderr)
    seen, out = set(), []
    for r in rows:
        if (r[0], r[1]) not in seen:
            seen.add((r[0], r[1])); out.append(r)
    return out


def export(k: int, per_positive: int, seed: int = 0, test_share: float = 0.25):
    rng = random.Random(seed)
    dec = load_decisions()
    pos = [d for d in dec if d[2]]
    neg = {}
    for d in dec:
        if not d[2]:
            neg.setdefault(d[0], []).append(d)
    pos = [p for p in pos if len(neg.get(p[0], [])) >= k - 1]
    rng.shuffle(pos)
    n_test = max(1, int(len(pos) * test_share))
    splits = {"test": pos[:n_test], "train": pos[n_test:]}
    os.makedirs(OUT, exist_ok=True)
    counts = {}
    for name, ps in splits.items():
        with open(os.path.join(OUT, f"data_{name}.jsonl"), "w") as fh:
            n = 0
            for p in ps:
                for _ in range(per_positive):
                    opts = rng.sample(neg[p[0]], k - 1) + [p]
                    rng.shuffle(opts)
                    notes = [f"- {o[1]}: {o[3][:90]}" for o in rng.sample(neg[p[0]], 3)]
                    prompt = PROMPT.format(notes="\n".join(notes),
                                           options="\n".join(f"{i}. {o[1]}" for i, o in enumerate(opts)))
                    fh.write(json.dumps(dict(prompt=prompt, answer=str(opts.index(p)), k=k, problem=p[0])) + "\n")
                    n += 1
            counts[name] = n
    rep = dict(decisions=len(dec), accepted=sum(d[2] for d in dec), positives_used=len(pos), k=k, examples=counts)
    print(json.dumps(rep))
    return rep


def train(model_name: str, epochs: int, device: str, lr: float, rank: int, limit_eval: int, limit_train: int = 0):
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32).to(device)
    data = {s: [json.loads(l) for l in open(os.path.join(OUT, f"data_{s}.jsonl"))] for s in ("train", "test")}
    digit_ids = [tok.encode(str(i), add_special_tokens=False)[0] for i in range(10)]

    def accuracy(m, rows):
        m.eval(); ok = 0
        with torch.no_grad():
            for r in rows:
                ids = tok(r["prompt"], return_tensors="pt").input_ids.to(device)
                logits = m(ids).logits[0, -1]
                pick = int(torch.argmax(logits[digit_ids[: r["k"]]]))
                ok += pick == int(r["answer"])
        return ok / max(1, len(rows))

    test = data["test"][:limit_eval] if limit_eval else data["test"]
    t0 = time.time()
    before = accuracy(model, test)
    model = get_peft_model(model, LoraConfig(r=rank, lora_alpha=2 * rank, lora_dropout=0.05,
                                             target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                                             task_type="CAUSAL_LM"))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    rng = random.Random(1)
    losses = []
    for ep in range(epochs):
        model.train()
        rows = data["train"][:]
        rng.shuffle(rows)
        if limit_train:
            rows = rows[:limit_train]
        tot = 0.0
        for r in rows:
            p = tok(r["prompt"], add_special_tokens=False).input_ids
            a = tok(r["answer"], add_special_tokens=False).input_ids
            ids = torch.tensor([p + a], device=device)
            labels = torch.tensor([[-100] * len(p) + a], device=device)
            loss = model(input_ids=ids, labels=labels).loss
            loss.backward(); opt.step(); opt.zero_grad()
            tot += loss.item()
        losses.append(tot / max(1, len(rows)))
        print(json.dumps(dict(epoch=ep + 1, loss=round(losses[-1], 4), seconds=round(time.time() - t0, 1))), flush=True)
    after = accuracy(model, test)
    model.save_pretrained(os.path.join(OUT, "adapter"))
    k = data["test"][0]["k"] if data["test"] else 0
    rep = dict(model=model_name, device=device, epochs=epochs, train_examples=min(len(data["train"]), limit_train or len(data["train"])),
               test_examples=len(test), chance=round(1 / k, 4) if k else None, accuracy_before=round(before, 4),
               accuracy_after=round(after, 4), losses=[round(x, 4) for x in losses],
               seconds=round(time.time() - t0, 1),
               peak_gpu_gb=round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if device == "cuda" else None)
    json.dump(rep, open(os.path.join(OUT, "report.json"), "w"), indent=1)
    print(json.dumps(rep))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "train"])
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--per-positive", type=int, default=12)
    ap.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=8)
    ap.add_argument("--limit-eval", type=int, default=0)
    ap.add_argument("--limit-train", type=int, default=0, help="train on the first N shuffled examples (smoke test)")
    a = ap.parse_args()
    if a.cmd == "export":
        export(a.k, a.per_positive)
    else:
        if not os.path.exists(os.path.join(OUT, "data_train.jsonl")):
            export(a.k, a.per_positive)
        train(a.model, a.epochs, a.device, a.lr, a.rank, a.limit_eval, a.limit_train)


if __name__ == "__main__":
    main()
