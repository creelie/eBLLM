"""Fetch the erdosproblems.com pages of the problems whose database status is not open, at most
about two pages a second.  Usage: python -I experiments/fetch_erdos.py PROBLEMS.yaml OUTDIR
(PROBLEMS.yaml is data/problems.yaml of github.com/teorth/erdosproblems).  The pages are read by
ebllm.bllm.corpus.summarise_erdos and are not redistributed."""
import os, sys, time, yaml, urllib.request
db, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
probs = yaml.safe_load(open(db))
want = [p["number"] for p in probs if p["status"]["state"] not in ("open",)]
print(len(want), "pages to fetch", flush=True)
for i, n in enumerate(want):
    path = os.path.join(out, f"{n}.html")
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        continue
    for attempt in range(4):
        try:
            req = urllib.request.Request(f"https://www.erdosproblems.com/{n}", headers={"User-Agent": "research-survey"})
            data = urllib.request.urlopen(req, timeout=40).read()
            open(path, "wb").write(data)
            break
        except Exception as e:
            time.sleep(2 ** attempt)
    time.sleep(0.4)
    if i % 50 == 0:
        print(i, n, flush=True)
print("done", flush=True)
