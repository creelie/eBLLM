"""Data for the anatomy and growth figures of Anaxia, read from the package itself.

anatomy.json   every module of src/ebllm in the working tree: its subsystem, its lines of code and
               the modules it imports (internal imports only, read with ast);
growth.json    one row per merge of the main branch and one for the working tree: date, version,
               modules, lines of code per subsystem, test methods, Lean theorems (paper and engine),
               library constructions, registry entries, figures of the paper and commands of the CLI.

Run from the root of the repository:  python3 paper/bllm/paper/figures/src/collect_brain.py
The growth table needs the git history; without it the existing growth.json is kept and only the
row of the working tree is replaced.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
OUT = os.path.join(os.path.dirname(__file__), "data", "brain")

# The parts of the engine, in the order of the anatomy figure.
SUBSYSTEMS = (
    ("core", "verified-release core (the VSI circuit of version 1)"),
    ("laws", "schedules and laws: checks, entropy schedules, the gap law"),
    ("proposers", "proposers, agents and the spiking selector"),
    ("crossing", "crossing network, boosters, targets and the attack channel"),
    ("memory", "memory, vault and the learn-from-failure log"),
    ("knowledge", "corpora, stepwise records and the registry of sources"),
    ("benchmarks", "the five-problem benchmark"),
    ("construction", "construction mode, the tower and lattice polytopes"),
    ("interface", "command line and image updates"),
)

MAP = {
    "laws": {"bllm/schedules.py", "bllm/checks.py", "bllm/gap.py", "bllm/bostrom.py", "bllm/polys.py",
             "bllm/__init__.py"},
    "proposers": {"bllm/proposers.py", "bllm/brain.py", "bllm/neuro.py", "bllm/agents.py", "bllm/coordinator.py"},
    "crossing": {"bllm/crossing.py", "bllm/boosters.py", "bllm/hyperlib.py", "bllm/targets.py", "bllm/hodge.py",
                 "bllm/attackflow.py", "bllm/frontier.py", "bllm/certificates.py"},
    "memory": {"bllm/memory.py", "bllm/vault.py", "bllm/selfmod.py"},
    "knowledge": {"bllm/corpus.py", "bllm/tasks.py", "bllm/deepmind.py", "bllm/sources.py"},
    "benchmarks": {"bllm/benchmark.py", "bllm/superbrain.py"},
    "interface": {"cli.py", "update.py", "__main__.py"},
}


def subsystem(rel: str) -> str:
    if rel.startswith("construct/"):
        return "construction"
    for k, names in MAP.items():
        if rel in names:
            return k
    return "core" if not rel.startswith("bllm/") else "crossing"


def loc(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def imports(rel: str, text: str) -> list:
    """Internal modules imported by the module at src/ebllm/<rel>."""
    pkg = rel.split("/")[:-1]
    out = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg[:len(pkg) - node.level + 1] if node.level > 1 else pkg[:]
                parts = base + (node.module.split(".") if node.module else [])
            elif node.module and node.module.startswith("ebllm"):
                parts = node.module.split(".")[1:]
            else:
                continue
            names = [a.name for a in node.names]
            for cand in ([parts + [n] for n in names] + [parts]):
                p = "/".join(cand)
                if p and (p + ".py") != rel:
                    out.add(p)
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("ebllm."):
                    out.add("/".join(a.name.split(".")[1:]))
    return sorted(out)


def resolve(target: str, modules: set) -> str:
    for c in (target + ".py", target + "/__init__.py"):
        if c in modules:
            return c
    return ""


def anatomy() -> dict:
    src = os.path.join(ROOT, "src", "ebllm")
    mods = {}
    for d, _, files in os.walk(src):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(d, f)
                rel = os.path.relpath(path, src).replace(os.sep, "/")
                with open(path) as fh:
                    mods[rel] = fh.read()
    names = set(mods)
    out = []
    for rel in sorted(mods):
        deps = sorted({resolve(t, names) for t in imports(rel, mods[rel])} - {"", rel})
        out.append(dict(module=rel, subsystem=subsystem(rel), loc=loc(mods[rel]), imports=deps))
    return dict(subsystems=[dict(key=k, label=v) for k, v in SUBSYSTEMS], modules=out)


def git(*args) -> str:
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, check=True).stdout


def row_from_files(files: dict, date: str, label: str, pr: str) -> dict:
    """files maps repository paths to text (only the paths the row needs)."""
    sub = {k: 0 for k, _ in SUBSYSTEMS}
    nmod = 0
    for p, text in files.items():
        if p.startswith("src/ebllm/") and p.endswith(".py"):
            nmod += 1
            sub[subsystem(p[len("src/ebllm/"):])] += loc(text)
    tests = sum(len(re.findall(r"^\s*def test_", t, re.M)) for p, t in files.items()
                if p.startswith("tests/") and p.endswith(".py"))
    lean_paper = sum(1 for line in files.get("paper/bllm/lean/axioms.txt", "").splitlines() if "depends on axioms" in line)
    lean_engine = sum(len(re.findall(r"^\s*theorem\s", t, re.M)) for p, t in files.items()
                      if p.startswith("lean/") and p.endswith(".lean") and "/.lake/" not in p)

    def jlen(p):
        try:
            return len(json.loads(files[p])) if p in files else 0
        except ValueError:
            return 0

    version = ""
    m = re.search(r'^version\s*=\s*"([^"]+)"', files.get("pyproject.toml", ""), re.M)
    if m:
        version = m.group(1)
    figs = sum(1 for p in files if re.match(r"paper/bllm/paper/figures/fig_[^/]+\.png$", p))
    cmds = len(re.findall(r"sub\.add_parser\(", files.get("src/ebllm/cli.py", "")))
    return dict(label=label, pr=pr, date=date, version=version, modules=nmod, loc=sub, loc_total=sum(sub.values()),
                tests=tests, lean_paper=lean_paper, lean_engine=lean_engine,
                library=jlen("src/ebllm/bllm/data/knowledge.json"), registry=jlen("src/ebllm/bllm/data/sources.json"),
                figures=figs, commands=cmds)


WANT = re.compile(r"^(src/ebllm/.*\.py|tests/.*\.py|lean/.*\.lean|paper/bllm/lean/axioms\.txt|pyproject\.toml|"
                  r"src/ebllm/bllm/data/(knowledge|sources)\.json|paper/bllm/paper/figures/fig_[^/]+\.png)$")


def files_at(commit: str) -> dict:
    out = {}
    for p in git("ls-tree", "-r", "--name-only", commit).splitlines():
        if WANT.match(p) and "/.lake/" not in p:
            out[p] = "" if p.endswith(".png") else git("show", f"{commit}:{p}")
    return out


def files_now() -> dict:
    out = {}
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in (".git", ".lake", "__pycache__", "node_modules")]
        for f in files:
            p = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
            if WANT.match(p):
                if p.endswith(".png"):
                    out[p] = ""
                else:
                    with open(os.path.join(ROOT, p), errors="replace") as fh:
                        out[p] = fh.read()
    return out


def growth(now_date: str) -> list:
    rows = []
    try:
        log = git("log", "--first-parent", "--reverse", "--format=%H %cI %s", "HEAD").splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        log = []
    tags = {}
    try:
        for t in git("tag", "-l", "v*").split():
            tags[git("rev-list", "-n1", t).strip()] = t[1:]
    except subprocess.CalledProcessError:
        pass
    for line in log:
        h, date, subject = line.split(" ", 2)
        m = re.search(r"\(#(\d+)\)\s*$", subject) or re.search(r"pull request #(\d+)", subject)
        if not m:
            continue
        row = row_from_files(files_at(h), date, h[:7], m.group(1))
        row["release"] = tags.get(h, "")
        rows.append(row)
    if not rows:
        path = os.path.join(OUT, "growth.json")
        if os.path.exists(path):
            with open(path) as f:
                rows = [r for r in json.load(f)["rows"] if r["label"] != "tree"]
    rows.append(dict(row_from_files(files_now(), now_date, "tree", ""), release="tree"))
    return rows


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    now_date = argv[0] if argv else "2026-10-19T00:00:00+00:00"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "anatomy.json"), "w") as f:
        json.dump(anatomy(), f, indent=1)
    with open(os.path.join(OUT, "growth.json"), "w") as f:
        json.dump(dict(rows=growth(now_date)), f, indent=1)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
