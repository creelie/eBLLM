"""What Anaxia draws on from other work on AI and mathematics, in one registry.

`data/sources.json` lists every system, corpus and method the engine takes from: who made it, the
reference, what was taken, the module that implements it, what Anaxia adds and what was left out.
It is written by scripts/make_sources.py and read by `anaxia sources`.

Two corpora are indexed here in the item format of the DeepMind index (source, name, kind,
statement, status, link):

  openrefute   the problem dossiers of trureturing (The Omega Institute): a published conjecture,
               its Lean claim and its kernel-checked resolution;
  openai-math  the manuscripts of OpenAI's collection, every one marked unrefereed.

`check` searches these indexes and the DeepMind index together: the step run before a target is
attacked, to see whether it is already settled, and the refuter's list of conjectures that fell to
an explicit instance.  Nothing in an index is ever used as a lemma by a check.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import subprocess
from typing import Dict, List, Optional

from . import deepmind as D

HERE = os.path.dirname(__file__)
REGISTRY = os.path.join(HERE, "data", "sources.json")
EXTERNAL = os.path.join(HERE, "data", "external")
STATEMENT = 400


def registry() -> List[dict]:
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def get(sid: str) -> dict:
    for r in registry():
        if r["id"] == sid:
            return r
    raise KeyError(sid)


def table(rows: Optional[List[dict]] = None) -> str:
    rows = rows if rows is not None else registry()
    out, group = [], None
    for r in rows:
        if r["group"] != group:
            group = r["group"]
            out.append(f"\n{group}")
        out.append(f"  {r['id']:<24} {r['name'][:38]:<38} {r['status'][:40]}")
    return "\n".join(out).lstrip("\n")


def _commit(root: str) -> str:
    try:
        return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _clip(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= STATEMENT else text[: STATEMENT - 1].rsplit(" ", 1)[0] + "…"


def _section(text: str, name: str) -> str:
    m = re.search(rf"^## {name}\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def resolution(triage: str, kind: str, slug: str = "") -> str:
    """The resolution a dossier records: refuted, proved, settled (a theorem whose triage names
    neither), or open when the triage is not a theorem."""
    if kind != "theorem":
        return "open"
    first = triage.split("\n\n", 1)[0]
    m = re.search(r"\b(refuted|proved)\b", first, re.I)
    if m:
        return m.group(1).lower()
    if "refutation" in slug or re.search(r"\brefut(e|es|ed|ation)\b", triage, re.I):
        return "refuted"
    if re.search(r"\bproved\b", triage, re.I):
        return "proved"
    return "settled"


def index_openrefute(root: str, repo: str = "creelie/trureturing-OpenRefute") -> dict:
    commit = _commit(root)
    items = []
    folder = os.path.join(root, "Problems")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            text = f.read()
        front = text.split("---", 2)[1] if text.startswith("---") else ""
        meta = dict(re.findall(r"^(\w+): (.+)$", front, re.M))
        title = re.search(r"^# (.+)$", text, re.M)
        gids = re.findall(r"^\s+- (D5/\S+)$", front, re.M)
        kind = meta.get("triage", "")
        items.append(dict(
            source="openrefute", name=meta.get("slug", name[:-3]), kind=kind or "dossier",
            statement=_clip((title.group(1) + ". " if title else "") + _section(text, "Problem")),
            status=resolution(_section(text, "Triage"), kind, meta.get("slug", name)),
            lean=gids, doi=meta.get("doi", ""), paper=meta.get("url", ""),
            link=f"https://github.com/{repo}/blob/{commit}/Problems/{name}" if commit else name))
    return dict(source="openrefute", repo=repo, commit=commit, items=items)


def index_openai(root: str, repo: str = "creelie/math01-openAI") -> dict:
    from .corpus import read_openai
    commit = _commit(root)
    c = read_openai(root)
    items = []
    for m in c["manuscripts"]:
        fam = c["families"].get(m["family"], {})
        items.append(dict(
            source="openai-math", name=m["title"], kind="manuscript",
            statement=_clip(m["abstract"]), status="unrefereed",
            family=f"{m['family']}. {fam.get('title', '')}", formalized=m["formalized"],
            link=f"https://github.com/{repo}/blob/{commit}/{m['path']}" if commit else m["path"]))
    return dict(source="openai-math", repo=repo, commit=commit, items=items)


def write_index(index: dict, folder: str = EXTERNAL) -> str:
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, index["source"] + ".json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return path


def load_external(folder: str = EXTERNAL) -> List[dict]:
    items = []
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if name.endswith(".json.gz"):
                with gzip.open(os.path.join(folder, name), "rt", encoding="utf-8") as f:
                    items.extend(json.load(f)["items"])
    return items


def summary(items: List[dict]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for it in items:
        s = out.setdefault(it["source"], {})
        s[it["status"]] = s.get(it["status"], 0) + 1
    return out


class Check:
    """One search over the DeepMind index and the external indexes."""

    def __init__(self, folder: str = EXTERNAL):
        self.items = D.load_index()["items"] + load_external(folder)
        self.search = D.Search(self.items)

    def __call__(self, text: str, k: int = 10, source: Optional[str] = None,
                 status: Optional[str] = None) -> List[dict]:
        return self.search(text, k, source=source, status=status)


def check(text: str, k: int = 10, **kw) -> List[dict]:
    return Check()(text, k, **kw)
