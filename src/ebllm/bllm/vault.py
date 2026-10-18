"""Memory as an Obsidian vault.

Every kept result is a Markdown note with YAML front matter and [[links]] to the results it was
built from, so the memory is a graph: open the folder in Obsidian (or any Markdown editor) and the
graph view shows which results were reused.  Failures are kept too, one residue note per problem,
because a complete record of what failed is the part of a run a later proposer can build on.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .checks import Candidate


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")


@dataclass
class Vault:
    root: Optional[str] = None
    notes: Dict[str, dict] = field(default_factory=dict)
    residues: Dict[str, List[dict]] = field(default_factory=dict)
    problems: Dict[str, dict] = field(default_factory=dict)

    def add_problem(self, pid: str, title: str, statement: str, notes: str = "") -> None:
        self.problems[pid] = dict(id=pid, title=title, statement=statement, notes=notes)

    def keep(self, cand: Candidate, detail: str, cost: float) -> dict:
        note = dict(id=cand.id, problem=cand.statement.get("problem", ""), kind=cand.kind,
                    agent=cand.agent, move=cand.move, parents=list(cand.parents),
                    rationale=cand.rationale, check=detail, cost=round(cost, 3),
                    lhs=cand.statement.get("lhs", ""), rhs=cand.statement.get("rhs", ""),
                    status="kept")
        self.notes[cand.id] = note
        return note

    def record_failure(self, cand: Candidate, detail: str) -> dict:
        r = dict(id=cand.id, problem=cand.statement.get("problem", ""), move=cand.move,
                 agent=cand.agent, rhs=cand.statement.get("rhs", ""), detail=detail[:300])
        if "tactic" in cand.statement:
            r["tactic"] = cand.statement["tactic"]
        self.residues.setdefault(r["problem"], []).append(r)
        return r

    def propose_unchecked(self, cand: Candidate, why: str) -> dict:
        note = dict(id=cand.id, problem=cand.statement.get("problem", ""), kind=cand.kind,
                    agent=cand.agent, move=cand.move, parents=list(cand.parents),
                    rationale=cand.rationale, check=why, cost=0.0,
                    lhs=cand.statement.get("lhs", ""), rhs=cand.statement.get("rhs", ""),
                    text=cand.statement.get("text", ""), status="proposal (unchecked)")
        self.notes[cand.id] = note
        return note

    def search_identities(self) -> List[dict]:
        return [n for n in self.notes.values() if n["status"] == "kept" and n["kind"] in ("identity", "univariate")]

    def all_residues(self) -> List[dict]:
        return [r for rs in self.residues.values() for r in rs]

    # -- writing the vault -------------------------------------------------------------------
    def write(self, root: Optional[str] = None) -> str:
        root = root or self.root
        if not root:
            raise ValueError("no vault directory")
        os.makedirs(os.path.join(root, "results"), exist_ok=True)
        os.makedirs(os.path.join(root, "problems"), exist_ok=True)
        os.makedirs(os.path.join(root, "residues"), exist_ok=True)
        for n in self.notes.values():
            links = "\n".join(f"- built from [[{_slug(p)}]]" for p in n["parents"]) or "- built from nothing kept"
            body = [
                "---", f"id: {n['id']}", f"problem: {n['problem']}", f"agent: {n['agent']}",
                f"move: {n['move']}", f"status: {n['status']}", f"cost: {n['cost']}",
                f"tags: [bllm, {n['move']}, {n['status'].split()[0]}]", "---", "",
                f"# {n['id']}", "", f"Problem: [[{_slug(n['problem'])}]]", "",
            ]
            if n.get("lhs") and n.get("rhs"):
                body += ["```", f"{n['lhs']}", f"  = {n['rhs']}", "```", ""]
            if n.get("text"):
                body += [n["text"], ""]
            body += [f"Rationale: {n['rationale']}", "", f"Check: {n['check']}", "", "## Links", links, ""]
            open(os.path.join(root, "results", _slug(n["id"]) + ".md"), "w", encoding="utf-8").write("\n".join(body))
        for pid, p in self.problems.items():
            kept = [n for n in self.notes.values() if n["problem"] == pid]
            lines = ["---", f"id: {pid}", "tags: [bllm, problem]", "---", "", f"# {p['title']}", "",
                     "```", p["statement"], "```", "", p.get("notes", ""), "", "## Results"]
            lines += [f"- [[{_slug(n['id'])}]] ({n['status']}, {n['move']})" for n in kept] or ["- none yet"]
            lines += ["", f"## Residues", f"- [[residues-{_slug(pid)}]] ({len(self.residues.get(pid, []))} failures)", ""]
            open(os.path.join(root, "problems", _slug(pid) + ".md"), "w", encoding="utf-8").write("\n".join(lines))
            rs = self.residues.get(pid, [])
            rl = ["---", f"problem: {pid}", "tags: [bllm, residue]", "---", "", f"# Residues of [[{_slug(pid)}]]", "",
                  f"{len(rs)} failed candidates. The first 200:", ""]
            rl += [f"- {r['move']}: `{r['rhs'][:120]}` ({r['detail'][:120]})" for r in rs[:200]]
            open(os.path.join(root, "residues", f"residues-{_slug(pid)}.md"), "w", encoding="utf-8").write("\n".join(rl) + "\n")
        idx = ["# BLLM memory", "", "Open this folder as an Obsidian vault; the graph view shows how results were reused.", "",
               "## Problems"] + [f"- [[{_slug(p)}]]" for p in self.problems] + ["", "## Kept results"]
        idx += [f"- [[{_slug(n['id'])}]] ({n['move']})" for n in self.notes.values() if n["status"] == "kept"]
        open(os.path.join(root, "BLLM index.md"), "w", encoding="utf-8").write("\n".join(idx) + "\n")
        json.dump(dict(notes=self.notes, residues=self.residues, problems=self.problems),
                  open(os.path.join(root, "memory.json"), "w", encoding="utf-8"), indent=1)
        return root

    @classmethod
    def load(cls, root: str) -> "Vault":
        d = json.load(open(os.path.join(root, "memory.json"), encoding="utf-8"))
        return cls(root, d["notes"], d["residues"], d["problems"])
