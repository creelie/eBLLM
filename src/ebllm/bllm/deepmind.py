"""What Anaxia takes from the public repositories of Google DeepMind.

The manifest (`data/deepmind/manifest.json`) lists every public repository of
github.com/google-deepmind on the day of the survey: its description, licence, stars, last push
and one relevance tag.

  vendor   pinned at an exact commit, fetched by `anaxia fetch deepmind <name>` and indexed:
           Lean statements of conjectures and their proofs, constructions found by program
           search, problem collections with their best known constructions, provers;
  related  listed and fetchable at the commit of the survey, not indexed: reasoning
           benchmarks, program synthesis, algorithmic reasoning;
  none     no bearing on conjectures, proofs, constructions or checking (robotics,
           reinforcement-learning environments, biology, vision, speech, weather, ...).

A fetched repository is data.  Nothing in it is imported, built or executed here: the indexers
read text files (Lean sources, notebooks as JSON, HTML pages, plain lists) and keep, for each
item, its name, its kind, a short statement, its status where the source gives one, and a link to
the file at the pinned commit.  The index of the pinned commits ships with the package
(`data/deepmind/index.json.gz`), so the memory can be filled without a network.

`search` ranks index items against a query by TF-IDF, after the retrieval of the
advanced-reasoning-mcp server of T. B. Hall (MIT licence): lower-case words without punctuation,
words of three letters or more outside a stop list, term frequency times smoothed inverse
document frequency, summed over the query words; here British spellings and plural endings are
folded, and the sum is multiplied by the share of query words the item contains.  It is the literature check of construction
mode ("is this still open?"): every hit carries its source and, for formal-conjectures, the
status (open or solved) recorded in the Lean file.
"""
from __future__ import annotations

import gzip
import html
import json
import math
import os
import re
import subprocess
from collections import Counter
from typing import Dict, Iterable, List, Optional, Sequence

ORG = "google-deepmind"
DATA = os.path.join(os.path.dirname(__file__), "data", "deepmind")
MANIFEST = os.path.join(DATA, "manifest.json")
INDEX = os.path.join(DATA, "index.json.gz")


def manifest() -> List[dict]:
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)["repositories"]


def pins() -> Dict[str, dict]:
    """The repositories with a pinned commit (tag vendor or related), by name."""
    return {r["name"]: r for r in manifest() if r.get("commit")}


def default_root() -> str:
    return os.environ.get("ANAXIA_THIRD_PARTY") or os.path.join(
        os.path.expanduser("~"), ".cache", "anaxia", "deepmind")


def _git(args: Sequence[str], cwd: Optional[str] = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def fetch(name: str, root: Optional[str] = None) -> str:
    """Fetch one pinned repository at its commit into root/name and return the path.

    An existing checkout at the pinned commit is reused; one at another commit is an error,
    so a checkout is never silently replaced."""
    rows = pins()
    if name not in rows:
        raise KeyError(f"{name} is not pinned; `anaxia fetch deepmind --list` shows the pinned repositories")
    row = rows[name]
    dest = os.path.join(root or default_root(), name)
    if os.path.isdir(os.path.join(dest, ".git")):
        head = _git(["rev-parse", "HEAD"], cwd=dest)
        if head != row["commit"]:
            raise RuntimeError(f"{dest} is at {head}, not at the pinned {row['commit']}")
        return dest
    os.makedirs(dest, exist_ok=True)
    _git(["init", "-q"], cwd=dest)
    _git(["remote", "add", "origin", f"https://github.com/{ORG}/{name}.git"], cwd=dest)
    _git(["fetch", "-q", "--depth", "1", "origin", row["commit"]], cwd=dest)
    _git(["checkout", "-q", "--detach", "FETCH_HEAD"], cwd=dest)
    head = _git(["rev-parse", "HEAD"], cwd=dest)
    if head != row["commit"]:
        raise RuntimeError(f"fetched {head}, expected {row['commit']}")
    return dest


# -- indexers: each reads text files of one repository and returns a list of items -----------

def _link(repo: str, commit: str, rel: str) -> str:
    return f"https://github.com/{ORG}/{repo}/blob/{commit}/{rel}"


def _clean(text: str, n: int = 300) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


DECL = re.compile(
    r"(?:/--(?P<doc>(?:(?!-/).)*)-/\s*)?@\[(?P<attr>[^\]]*category[^\]]*)\]\s*"
    r"(?:theorem|lemma|def|abbrev)\s+(?P<name>[^\s:({\[]+)", re.S)


def index_formal_conjectures(path: str, commit: str, repo: str = "formal-conjectures") -> List[dict]:
    """Every statement tagged `research open` or `research solved`, with its docstring and AMS codes."""
    items = []
    base = os.path.join(path, "FormalConjectures")
    for dirpath, _, files in os.walk(base):
        for fn in sorted(files):
            if not fn.endswith(".lean"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, path)
            with open(full, encoding="utf-8", errors="replace") as f:
                text = f.read()
            for m in DECL.finditer(text):
                attr = m.group("attr")
                cat = re.search(r"category\s+research\s+(open|solved)", attr)
                if not cat:
                    continue
                ams = re.findall(r"AMS\s+([\d\s]+)", attr)
                items.append(dict(
                    source=repo, kind="conjecture", name=m.group("name"), status=cat.group(1),
                    area=os.path.relpath(dirpath, base).split(os.sep)[0],
                    ams=" ".join(a.strip() for a in ams).split(),
                    statement=_clean(m.group("doc") or ""), link=_link(repo, commit, rel)))
    return items


def index_alphaevolve_problems(path: str, commit: str, repo: str = "alphaevolve_repository_of_problems") -> List[dict]:
    """The 67 problems of Georgiev, Gómez-Serrano, Tao and Wagner, with AlphaEvolve's standing."""
    with open(os.path.join(path, "status.json"), encoding="utf-8") as f:
        status = {n: k for k, ns in json.load(f).items() for n in ns}
    items = []
    pdir = os.path.join(path, "problems")
    for fn in sorted(os.listdir(pdir), key=lambda s: (len(s), s)):
        m = re.match(r"(\d+)\.html$", fn)
        if not m:
            continue
        with open(os.path.join(pdir, fn), encoding="utf-8", errors="replace") as f:
            text = f.read()
        title = re.search(r'title:\s*"(.*?)"', text)
        statement = re.search(r"statement:\s*`(.*?)`", text, re.S)
        if not title:
            continue
        body = html.unescape(re.sub(r"<[^>]+>", " ", statement.group(1) if statement else ""))
        body = body.replace("\\\\", "\\")
        n = int(m.group(1))
        items.append(dict(source=repo, kind="construction-problem", name=title.group(1),
                          status=status.get(n, "unrecorded"), statement=_clean(body, 400),
                          link=_link(repo, commit, f"problems/{fn}")))
    return items


def _notebook_headings(full: str) -> List[str]:
    with open(full, encoding="utf-8", errors="replace") as f:
        nb = json.load(f)
    heads = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        for line in "".join(cell.get("source", [])).splitlines():
            if re.match(r"#{1,3}\s", line):
                heads.append(_clean(line.lstrip("#"), 160))
    return heads


def index_alphaevolve_results(path: str, commit: str, repo: str = "alphaevolve_results") -> List[dict]:
    """The sections of the notebook of mathematical results of AlphaEvolve (Novikov et al., 2025)."""
    rel = "mathematical_results.ipynb"
    return [dict(source=repo, kind="construction", name=h, status="reported", statement=h,
                 link=_link(repo, commit, rel)) for h in _notebook_headings(os.path.join(path, rel))]


FUNSEARCH = {
    "cap_set": "a cap set in F_3^8 of size 512",
    "admissible_set": "admissible sets, giving lower bounds for the cap set capacity",
    "corner_free_set": "corner-free sets in F_2^4, F_3^2, F_3^3",
    "cyclic_graphs": "independent sets in strong powers of cycle graphs (Shannon capacity)",
    "bin_packing": "online bin-packing heuristics",
}


def index_funsearch(path: str, commit: str, repo: str = "funsearch") -> List[dict]:
    """The constructions of FunSearch (Romera-Paredes et al., Nature 2023), one item per file."""
    items = []
    for d, what in FUNSEARCH.items():
        full = os.path.join(path, d)
        if not os.path.isdir(full):
            continue
        for fn in sorted(os.listdir(full)):
            if fn.endswith(".txt") or fn.endswith(".ipynb"):
                items.append(dict(source=repo, kind="construction", name=f"{d}/{fn}", status="reported",
                                  statement=what, link=_link(repo, commit, f"{d}/{fn}")))
    return items


def index_alphaproof_nexus(path: str, commit: str, repo: str = "alphaproof-nexus-results") -> List[dict]:
    """The Lean proofs found by AlphaProof Nexus, and the Erdős statements it attempted."""
    items = []
    out = os.path.join(path, "APNOutputs")
    for dirpath, _, files in os.walk(out):
        for fn in sorted(files):
            if fn.endswith(".lean"):
                rel = os.path.relpath(os.path.join(dirpath, fn), path)
                items.append(dict(source=repo, kind="lean-proof", name=fn[:-5], status="proved in Lean",
                                  statement=os.path.relpath(dirpath, out), link=_link(repo, commit, rel)))
    att = os.path.join(path, "erdos_problems_attempted.txt")
    if os.path.exists(att):
        with open(att, encoding="utf-8") as f:
            names = [l.strip() for l in f if l.strip()]
        items.append(dict(source=repo, kind="attempt-list", name="erdos_problems_attempted",
                          status=f"{len(names)} statements attempted", statement=" ".join(names),
                          link=_link(repo, commit, "erdos_problems_attempted.txt")))
    return items


def index_lean_problems(path: str, commit: str, repo: str) -> List[dict]:
    """Olympiad and Putnam statements in Lean (formal-imo, formal-putnam-like, miniF2F)."""
    items = []
    for dirpath, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in (".git", ".lake")]
        for fn in sorted(files):
            if not fn.endswith(".lean"):
                continue
            full = os.path.join(dirpath, fn)
            with open(full, encoding="utf-8", errors="replace") as f:
                text = f.read()
            for m in re.finditer(r"^(?:theorem|lemma)\s+([^\s:({\[]+)", text, re.M):
                items.append(dict(source=repo, kind="lean-statement", name=m.group(1),
                                  status="sorry" if "sorry" in text else "proved",
                                  statement=os.path.relpath(full, path),
                                  link=_link(repo, commit, os.path.relpath(full, path))))
    return items


def index_cryptids(path: str, commit: str, repo: str = "cryptids") -> List[dict]:
    """Turing machines whose halting encodes a conjecture, with certified reductions in Lean."""
    items = []
    for sub in ("Cryptids", "BusyBeaver"):
        d = os.path.join(path, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".lean"):
                items.append(dict(source=repo, kind="lean-machine", name=f"{sub}/{fn[:-5]}", status="Lean",
                                  statement="conjecture-checking machine" if sub == "Cryptids" else "busy beaver",
                                  link=_link(repo, commit, f"{sub}/{fn}")))
    return items


def index_superhuman(path: str, commit: str, repo: str = "superhuman") -> List[dict]:
    """Aletheia's research outputs (one item per bullet of its README) and the IMO benchmarks."""
    items = []
    readme = os.path.join(path, "aletheia", "README.md")
    if os.path.exists(readme):
        with open(readme, encoding="utf-8") as f:
            for line in f:
                if line.startswith("* ") and "[" in line:
                    items.append(dict(source=repo, kind="research-output", name=_clean(line[2:].split(":")[0], 160),
                                      status="reported", statement=_clean(re.sub(r"\(.*?\)|\[|\]", "", line[2:]), 300),
                                      link=_link(repo, commit, "aletheia/README.md")))
    bench = os.path.join(path, "imobench")
    if os.path.isdir(bench):
        for fn in sorted(os.listdir(bench)):
            if fn.endswith("_v2.csv") or fn == "gradingbench.csv":
                with open(os.path.join(bench, fn), encoding="utf-8", errors="replace") as f:
                    rows = sum(1 for _ in f) - 1
                items.append(dict(source=repo, kind="benchmark", name=f"imobench/{fn}", status=f"{rows} rows",
                                  statement="IMO-Bench", link=_link(repo, commit, f"imobench/{fn}")))
    return items


def index_readme(path: str, commit: str, repo: str) -> List[dict]:
    """One item for a repository indexed by its README only (provers, search, datasets)."""
    for fn in ("README.md", "readme.md", "README.rst"):
        full = os.path.join(path, fn)
        if os.path.exists(full):
            with open(full, encoding="utf-8", errors="replace") as f:
                lines = [l.strip() for l in f if l.strip() and not l.lstrip().startswith(("[!", "![", "<", "```"))]
            return [dict(source=repo, kind="tool", name=repo, status="code",
                         statement=_clean(" ".join(lines[:8]), 400), link=_link(repo, commit, fn))]
    return []


INDEXERS = {
    "formal-conjectures": index_formal_conjectures,
    "alphaevolve_repository_of_problems": index_alphaevolve_problems,
    "alphaevolve_results": index_alphaevolve_results,
    "funsearch": index_funsearch,
    "alphaproof-nexus-results": index_alphaproof_nexus,
    "formal-imo": lambda p, c: index_lean_problems(p, c, "formal-imo"),
    "formal-putnam-like": lambda p, c: index_lean_problems(p, c, "formal-putnam-like"),
    "miniF2F": lambda p, c: index_lean_problems(p, c, "miniF2F"),
    "cryptids": index_cryptids,
    "superhuman": index_superhuman,
}


def build_index(root: Optional[str] = None, names: Optional[Iterable[str]] = None) -> dict:
    """Index the fetched vendor repositories under root (fetching the missing ones)."""
    rows = {r["name"]: r for r in manifest() if r["tag"] == "vendor"}
    items: List[dict] = []
    for name in sorted(names or rows):
        row = rows[name]
        path = fetch(name, root)
        indexer = INDEXERS.get(name) or (lambda p, c, n=name: index_readme(p, c, n))
        items.extend(indexer(path, row["commit"]))
    return {"surveyed": json.load(open(MANIFEST, encoding="utf-8"))["surveyed"], "items": items}


def write_index(index: dict, path: str = INDEX) -> None:
    raw = json.dumps(index, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write(raw)


def load_index(path: str = INDEX) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


# -- retrieval --------------------------------------------------------------------------------

STOP = frozenset("""the and for are but not you all any can had her was one our out has his how
its may new now old see two way who did get let put say she too use with that this from they will
would there their what about which when make like than then them these some into more only over
such also each other where after many most must well very just been have were your does should
could being every given there here those both same under while
conjecture conjectures problem problems question theorem lemma prove show true false""".split())
# the last line: words every statement of the index uses, which would rank short items first


def _stem(w: str) -> str:
    w = w.replace("colour", "color").replace("neighbour", "neighbor")
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def tokenize(text: str) -> List[str]:
    words = re.sub(r"[^\w\s]", " ", text.lower().replace("_", " ")).split()
    return [_stem(w) for w in words if len(w) > 2 and w not in STOP]


class Search:
    """TF-IDF over the name, statement and file of each item, times the share of query words found."""

    def __init__(self, items: Sequence[dict]):
        self.items = list(items)
        self.docs = [tokenize(f"{i['name']} {i['statement']} {i['link'].rsplit('/', 1)[-1]}") for i in self.items]
        self.df = Counter(w for d in self.docs for w in set(d))
        self.n = len(self.docs)

    def score(self, query: Sequence[str], doc: List[str]) -> float:
        if not doc:
            return 0.0
        c = Counter(doc)
        found = [t for t in set(query) if c[t]]
        tfidf = sum(c[t] / len(doc) * (math.log(self.n / (self.df[t] + 1)) + 1) for t in found)
        return tfidf * len(found) / len(set(query))

    def __call__(self, query: str, k: int = 10, source: Optional[str] = None,
                 status: Optional[str] = None) -> List[dict]:
        q = tokenize(query)
        hits = []
        for item, doc in zip(self.items, self.docs):
            if source and item["source"] != source or status and item["status"] != status:
                continue
            s = self.score(q, doc)
            if s > 0:
                hits.append((s, item))
        hits.sort(key=lambda t: -t[0])
        return [dict(item, score=round(s, 4)) for s, item in hits[:k]]


def search(query: str, k: int = 10, **kw) -> List[dict]:
    return Search(load_index()["items"])(query, k, **kw)


# -- memory -----------------------------------------------------------------------------------

def load_into_memory(mem, index: Optional[dict] = None) -> Dict[str, int]:
    """Write the index into the shared memory: every conjecture and problem as a literature row
    (claim, source, link, status), every construction and proof as a library node of problem
    `external` that gives its name and needs nothing.  Returns the counts written."""
    index = index or load_index()
    lit, nodes = 0, []
    for it in index["items"]:
        if it["kind"] in ("conjecture", "construction-problem", "lean-statement", "attempt-list"):
            path = it["link"].split("/blob/", 1)[-1].split("/", 1)[-1]
            mem.cite(f"{it['source']}:{path}:{it['name']}", it["statement"] or it["name"], it["link"], it["status"])
            lit += 1
        else:
            nodes.append(_Node(f"dm.{it['source']}.{it['name']}", "external", it["name"], frozenset(), it["link"]))
    mem.add_nodes(nodes)
    mem.commit()
    return {"literature": lit, "nodes": len(nodes)}


class _Node:
    __slots__ = ("id", "problem", "gives", "needs", "source")

    def __init__(self, id, problem, gives, needs, source):
        self.id, self.problem, self.gives, self.needs, self.source = id, problem, gives, needs, source


def summary(index: Optional[dict] = None) -> Dict[str, Counter]:
    index = index or load_index()
    out: Dict[str, Counter] = {}
    for it in index["items"]:
        out.setdefault(it["source"], Counter())[it["status"] if it["kind"] == "conjecture" else it["kind"]] += 1
    return out
