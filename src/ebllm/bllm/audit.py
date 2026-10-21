"""The audit of a published calculation: re-derive it stage by stage, check each stage with code kept
apart from the derivation, and sort every difference from the printed text by what it does to the
result.

Uploaded by a second agent on Tubai's command.  Taken from E. O. Kahya's re-derivation of a one-loop
quantum gravity calculation on de Sitter space (https://github.com/creelie/claude-audits-quantum-gravity,
MIT), whose method is general and whose checks run without a model:

    stages     the calculation is cut into stages that follow the printed equations in order; each
               stage has an analytic derivation, an independent code check, and a comparison with the
               printed equations;
    findings   every difference is one of five kinds (below), and only the substantive kind can
               change a conclusion;
    golden     every check script has a stored output, and a run passes only if its output agrees
               with the stored one after a fixed normalisation (line endings, trailing spaces,
               trailing blank lines, lines that only report a time).  A stored output whose script
               is missing is an error, a script without a stored output must print nothing, so no
               check is skipped in silence;
    global     a closed form is tested against the brute-force direct sum at several points with
               many digits; agreement only after every correction is applied is evidence that the
               list of corrections is complete.

An audit is a check of someone else's work, not a proof of anything new: ``verdict`` can say that a
printed conclusion survives the audit, never that the audit closed an open problem.  The stored
audit (``data/audits/*.json``) records the source's own counts and the result of rerunning its
checks here; the engine does not re-derive the physics.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

AUDITS = Path(__file__).parent / "data" / "audits"

# The five kinds of finding, in the order of the source's tables A to E.
KINDS = {
    "substantive": "changes a printed result; the only kind that can change a conclusion",
    "absorbable": "a finite error absorbed by a free parameter (a counterterm, a convention); no physical effect",
    "typo": "a typographical error; no effect",
    "confirmed": "checked and found as printed",
    "conclusion": "a result about the conclusion itself, re-derived with the corrected inputs",
}

TIMING_LINE = re.compile(
    r"^\s*[\[(]?\s*(runtime|elapsed|time|took|wall(\s*time)?|cpu(\s*time)?)\b[^=]*?[:=]?\s*"
    r"[0-9]+(\.[0-9]+)?\s*(s|sec|secs|seconds|ms|min)\.?\s*[\])]?\s*$",
    re.IGNORECASE,
)
PARAM_FILE = re.compile(r"^(?P<stem>.+)_N(?P<n>\d+)\.txt$")


# --------------------------------------------------------------------------------------- findings
@dataclass
class Finding:
    id: str
    kind: str
    stage: str = ""
    statement: str = ""
    consequence: str = ""
    changes_conclusion: bool = False

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"{self.id}: kind {self.kind!r} is not one of {sorted(KINDS)}")
        if self.changes_conclusion and self.kind != "substantive":
            raise ValueError(f"{self.id}: only a substantive finding can change a conclusion")


def verdict(findings: List[Finding]) -> Dict[str, object]:
    """Counts by kind, and whether the printed conclusion survives: it does exactly when no finding
    changes it.  Nothing here can return 'closed'."""
    counts = {k: 0 for k in KINDS}
    for f in findings:
        counts[f.kind] += 1
    broken = [f.id for f in findings if f.changes_conclusion]
    return {"counts": counts, "conclusion_survives": not broken, "changed_by": broken,
            "label": "audit (not a closure)"}


# ----------------------------------------------------------------------------------------- golden
def normalise(text: str) -> List[str]:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    lines = [ln for ln in lines if not TIMING_LINE.match(ln)]
    while lines and not lines[-1]:
        lines.pop()
    return lines


@dataclass
class Job:
    folder: str
    script: str
    args: List[str] = field(default_factory=list)
    expected: Optional[Path] = None  # None: a helper, which must print nothing


def collect(folder: Path) -> List[Job]:
    """The runs of one folder: a script with ``expected_output/<stem>.txt`` runs once, one with
    ``<stem>_N<n>.txt`` runs once per n with the argument n, any other script is a helper, and a
    stored output with no script becomes a run that fails."""
    folder = Path(folder)
    exp = folder / "expected_output"
    stored = {p.name for p in exp.glob("*.txt")} if exp.is_dir() else set()
    jobs, used = [], set()
    for script in sorted(folder.glob("*.py")):
        stem = script.stem
        if f"{stem}.txt" in stored:
            jobs.append(Job(folder.name, script.name, [], exp / f"{stem}.txt"))
            used.add(f"{stem}.txt")
            continue
        params = sorted((int(m.group("n")), name) for name in stored
                        if (m := PARAM_FILE.match(name)) and m.group("stem") == stem)
        for n, name in params:
            jobs.append(Job(folder.name, script.name, [str(n)], exp / name))
            used.add(name)
        if not params:
            jobs.append(Job(folder.name, script.name))
    for name in sorted(stored - used):
        m = PARAM_FILE.match(name)
        stem, args = (m.group("stem"), [m.group("n")]) if m else (name[:-4], [])
        jobs.append(Job(folder.name, f"{stem}.py", args, exp / name))
    return jobs


def compare(out: str, expected: str) -> List[str]:
    """The unified diff of two outputs after normalisation; empty when they agree."""
    got, want = normalise(out), normalise(expected)
    if got == want:
        return []
    return list(difflib.unified_diff(want, got, "expected", "actual", lineterm="", n=1))


def run(job: Job, root: Path, timeout: float = 3600.0) -> Dict[str, object]:
    t0 = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, job.script, *job.args], cwd=Path(root) / job.folder,
                           capture_output=True, timeout=timeout,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1"))
    except subprocess.TimeoutExpired:
        return {"run": f"{job.folder}/{job.script}", "status": "TIMEOUT", "seconds": timeout}
    dt = round(time.perf_counter() - t0, 2)
    name = f"{job.folder}/{job.script}" + "".join(" " + a for a in job.args)
    if p.returncode:
        return {"run": name, "status": "ERROR", "seconds": dt,
                "detail": p.stderr.decode("utf-8", "replace").strip().splitlines()[-3:]}
    want = job.expected.read_text(encoding="utf-8") if job.expected else ""
    diff = compare(p.stdout.decode("utf-8", "replace"), want)
    return {"run": name, "status": "FAIL" if diff else "PASS", "seconds": dt, "detail": diff[:20]}


def golden(root: str, folders: Optional[List[str]] = None, timeout: float = 3600.0) -> Dict[str, object]:
    """Run every check under ``root`` (or the named subfolders) against its stored output."""
    root = Path(root)
    dirs = [root / f for f in folders] if folders else sorted(
        p for p in root.iterdir() if p.is_dir() and (p / "expected_output").is_dir())
    results = [run(j, root, timeout) for d in dirs for j in collect(d)]
    tally: Dict[str, int] = {}
    for r in results:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
    return {"results": results, "tally": tally, "passed": bool(results) and tally.get("PASS", 0) == len(results)}


# ---------------------------------------------------------------------------------- stored audits
def load(name: str) -> dict:
    with open(AUDITS / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def names() -> List[str]:
    return sorted(p.stem for p in AUDITS.glob("*.json"))


def findings_of(audit: dict) -> List[Finding]:
    out = []
    for f in audit["findings"]:
        out.append(Finding(f["id"], f["kind"], f.get("stage", ""), f.get("statement", ""),
                           f.get("consequence", ""), f.get("changes_conclusion", False)))
    for kind, ids in audit.get("other_ids", {}).items():
        out.extend(Finding(i, kind) for i in ids)
    return out


def report(name: str) -> str:
    a = load(name)
    v = verdict(findings_of(a))
    lines = [a["title"], f"  source: {a['source']['repo']}", f"  papers: " + "; ".join(a["source"]["papers"]),
             f"  stages: {len(a['stages'])}  ({'; '.join(s['name'] for s in a['stages'])})"]
    lines.append("  findings: " + ", ".join(f"{k} {n}" for k, n in v["counts"].items()))
    lines.append(f"  conclusion survives: {'yes' if v['conclusion_survives'] else 'no, changed by ' + ', '.join(v['changed_by'])}")
    rr = a.get("rerun")
    if rr:
        lines.append(f"  checks rerun here: {rr['passed']} of {rr['runs']} pass ({rr['environment']}, {rr['date']})")
    lines.append(f"  label: {v['label']}")
    return "\n".join(lines)
