"""Compute the profiles of local open-weight models on a stream of sequence problems and run the
BLLM comparison of the paper.  Usage:
    python experiments/live_brain.py MODEL.gguf [MODEL2.gguf ...] --problems 800 --out results.json
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from ebllm.bllm import brain, gap

ap = argparse.ArgumentParser()
ap.add_argument("models", nargs="+")
ap.add_argument("--problems", type=int, default=800)
ap.add_argument("--seed", type=int, default=3)
ap.add_argument("--out", default="live_brain.json")
args = ap.parse_args()

need = gap.load_idea_gap()["shares"]["Human"]["opportunity"]
stream = brain.make_stream(need, args.problems, seed=args.seed)
profiles, decode, evals, names = {}, {}, {}, []
for path in args.models:
    b = brain.LocalBrain(path)
    nm = b.name.replace("-instruct-q4_k_m.gguf", "")
    names.append(nm)
    profiles[nm] = [b.profile(p.shown) for p in stream]
    # the time to draw one more sample from the cached prompt: one decode step
    t0 = time.perf_counter()
    for _ in range(20):
        b.llm.eval([b.letter_ids[0]])
    decode[nm] = (time.perf_counter() - t0) / 20
    evals[nm] = sum(b.eval_seconds) / len(b.eval_seconds)
    print(nm, "eval s", evals[nm], "decode s", decode[nm], flush=True)
    del b
json.dump({"need": need, "stream": [p.__dict__ for p in stream], "profiles": profiles,
           "decode_seconds": decode, "eval_seconds": evals}, open(args.out, "w"))
print("saved", args.out)
