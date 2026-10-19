"""Numbers and tables of the paper that are read from the package, so that the text cannot go stale.

Reads data/brain/anatomy.json and data/brain/growth.json (collect_brain.py) and the learn-from-failure
log src/ebllm/bllm/data/modlog.json, and writes three files that main.tex inputs:

    sections/gen_numbers.tex    macros: modules, lines, imports, tests, Lean theorems, log counts;
    sections/gen_releases.tex   the table of releases (tab:releases);
    sections/gen_modlog.tex     the table of every rule change of the log (tab:modlog).

    python3 collect_brain.py <UTC time> && python3 make_tables_round7.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "brain")
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
SECTIONS = os.path.abspath(os.path.join(HERE, "..", "..", "sections"))
MODLOG = os.path.join(REPO, "src", "ebllm", "bllm", "data", "modlog.json")
TREE_VERSION = "3.1.0"

# Version DOIs of the archived releases (concept DOI 10.5281/zenodo.23286641).
DOI = {
    "1.0.0": "23286642", "2.0.0": "23455686", "2.0.1": "23456124", "2.1.0": "23462639",
    "3.0.0": "23464390", "3.0.1": "23464490", "3.0.2": "23466863", "3.0.3": "23467113",
    "3.0.4": "23467544", "3.0.5": "23469389", "3.1.0": "",
}
# The stages in which the engine was built: the archived versions that changed it, with what each built.
STAGES = ("1.0.0", "2.0.0", "2.1.0", "3.0.0", "3.1.0")
ADDED = {
    "1.0.0": "the verified-release core: schedules of the entropy law, checks, a generator interface",
    "2.0.0": "the crossing network, boosters, memory, target points, agents, the five benchmarks and the "
             "searches of Erd\\H{o}s problem 1183",
    "2.1.0": "the Hodge agent, the container image, the command \\texttt{anaxia} and the Lean development of the paper",
    "3.0.0": "construction mode, the DeepMind intake, the tower $B^{n}$ of builders, the registry of sources",
    "3.1.0": "the learn-from-failure loop and its log, the screens, covers, descents and free sums of reflexive "
             "polytopes, the seed benchmark",
}
NAMES = {
    "core": "Core", "laws": "Laws", "proposers": "Proposers", "crossing": "Crossing", "memory": "Memory",
    "knowledge": "Knowledge", "benchmarks": "Benchmarks", "construction": "Construction",
    "interface": "Interface",
}


def load(p):
    with open(p) as f:
        return json.load(f)


def fmt(n):
    return f"{n:,}".replace(",", "{,}")


def tex(s):
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
            .replace("_", "\\_").replace(">=", "$\\ge$").replace("\u2265", "$\\ge$").replace("->", "$\\to$")
            .replace("\u0151", "\\H{o}").replace("Kral'", "Kr\\'al'").replace("Erdos", "Erd\\H{o}s")
            .replace("E\\_0^6", "$E_0^6$").replace("sqrt 10", "$\\sqrt{10}$"))


def numbers(anat, rows, runs):
    mods = anat["modules"]
    sof = {m["module"]: m["subsystem"] for m in mods}
    imports = sum(len(m["imports"]) for m in mods)
    within = sum(1 for m in mods for t in m["imports"] if sof.get(t) == m["subsystem"])
    indeg = collections.Counter(t for m in mods for t in m["imports"])
    hub, hubn = indeg.most_common(1)[0]
    tree = [r for r in rows if r["label"] == "tree"][-1]
    first = rows[0]
    out = {
        "brainModules": len(mods), "brainImports": imports, "brainWithin": within, "brainBetween": imports - within,
        "brainLines": fmt(sum(m["loc"] for m in mods)), "brainTests": tree["tests"],
        "brainLeanPaper": tree["lean_paper"], "brainLeanEngine": tree["lean_engine"],
        "brainCommands": tree["commands"], "brainFigures": tree["figures"], "brainLibrary": tree["library"],
        "brainRegistry": tree["registry"], "brainFirstLines": fmt(first["loc_total"]),
        "brainFirstModules": first["modules"], "brainFirstTests": first["tests"],
        "brainHub": hub.replace("_", "\\_"), "brainHubIn": hubn,
        "brainGrowth": f"{sum(m['loc'] for m in mods) / first['loc_total']:.1f}",
    }
    for s in NAMES:
        ms = [m for m in mods if m["subsystem"] == s]
        out["brainMod" + NAMES[s]] = len(ms)
        out["brainLoc" + NAMES[s]] = fmt(sum(m["loc"] for m in ms))
    recs = [r for run in runs for r in run["records"]]
    out["modRuns"] = len(runs)
    out["modTargets"] = len({(run["run"], r["target"]) for run in runs for r in run["records"]})
    out["modAttempts"] = len(recs)
    out["modChanges"] = sum(1 for r in recs if r.get("change"))
    out["modBuilt"] = sum(1 for r in recs if r.get("change") and r.get("retry"))
    out["modAdvanced"] = sum(1 for r in recs if r.get("change") and r.get("retry") in ("closed", "partial"))
    out["modClosed"] = sum(1 for r in recs if r["outcome"] == "closed")
    out["modRetryClosed"] = sum(1 for r in recs if r.get("change") and r.get("retry") == "closed")
    out["modRetryPartial"] = sum(1 for r in recs if r.get("change") and r.get("retry") == "partial")
    seed = json.load(open(os.path.join(REPO, "src", "ebllm", "construct", "data", "seed_summary.json"),
                          encoding="utf-8"))["numbers"]
    out.update({"seedBound": seed["bound"], "seedChain": seed["bound"] + 1, "seedLow": seed["low"],
                "seedDelta": seed["delta680_steps"], "seedTwo": seed["c2"], "seedThree": seed["c3"],
                "seedCount": fmt(seed["polytopes"]), "seedCountThree": fmt(seed["polytopes3"])})
    for run in runs:
        rs = run["records"]
        tag = "".join(w.capitalize() for w in run["run"].split())
        out["mod" + tag + "Attempts"] = len(rs)
        out["mod" + tag + "Changes"] = sum(1 for r in rs if r.get("change"))
        out["mod" + tag + "Advanced"] = sum(1 for r in rs if r.get("change") and r.get("retry") in ("closed", "partial"))
    kinds = collections.Counter(r["change"]["kind"] for r in recs if r.get("change"))
    out["modTopKind"], out["modTopKindN"] = kinds.most_common(1)[0]
    lines = ["% generated by figures/src/make_tables_round7.py; do not edit"]
    for k, v in out.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    return "\n".join(lines) + "\n"


def releases(rows):
    last = {}
    for r in rows:
        if r.get("release") == "tree":
            last[TREE_VERSION] = dict(r, version=TREE_VERSION)
        elif r.get("release"):
            last[r["release"]] = r
    body = []
    for k, v in enumerate(STAGES):
        r = last[v]
        doi = DOI.get(v, "")
        d = "19 Oct"
        if r["label"] != "tree":
            from datetime import datetime, timezone
            d = datetime.fromisoformat(r["date"]).astimezone(timezone.utc).strftime("%d %b").lstrip("0")
        doi_cell = f"\\href{{https://doi.org/10.5281/zenodo.{doi}}}{{{doi}}}" if doi else "\\anaxiaDOIshort"
        body.append(f"\\rr {'I II III IV V'.split()[k]} ({v}) & \\rr {d} & \\rr {r['modules']} & "
                    f"\\rr {fmt(r['loc_total'])} & \\rr {r['tests']} & \\rr {r['lean_paper']}/{r['lean_engine']} & "
                    f"\\rr {ADDED[v]} & \\rr {doi_cell} \\\\")
    head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{The five stages in which Anaxia was built, each read from the repository at the commit archived for it. Lines are non-blank lines of Python in the package; tests are test methods; Lean counts the theorems of the paper and of the engine. The last column gives the record number $N$ of the DOI \texttt{10.5281/zenodo.}$N$ under which the stage is archived.}
\label{tab:releases}
\centering
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{@{}p{0.075\textwidth}p{0.05\textwidth}p{0.062\textwidth}p{0.055\textwidth}p{0.04\textwidth}p{0.055\textwidth}p{0.445\textwidth}p{0.07\textwidth}@{}}
\toprule
\rr Stage & \rr Date & \rr Modules & \rr Lines & \rr Tests & \rr Lean & \rr What it built & \rr Archive \\
\midrule
"""
    return head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"


def modlog(runs):
    body = []
    for run in runs:
        body.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{tex(run.get('title', run['run']))}}}}} \\\\")
        for r in run["records"]:
            c = r.get("change")
            if not c:
                continue
            retry = r.get("retry") or "not yet built"
            body.append(f"\\rr {tex(r['target'])} & \\rr {r['attempt']} & \\rr {tex(r['diagnosis'])} & "
                        f"\\rr {tex(c['kind'])}: {tex(c['old'])} $\\to$ {tex(c['new'])} & \\rr {tex(c['improves'])} & "
                        f"\\rr {retry} \\\\")
    head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{Every rule change in the log of the learn-from-failure loop (file \texttt{modlog.json} of the package). A row is one failed attempt: the target, the attempt, the diagnosis, the rule that was changed with its old and new value, the measurement the change was meant to improve, and the outcome of the retry under the changed rules. Records of attempts that closed carry no change and are not listed.}
\label{tab:modlog}
\centering
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}p{0.15\textwidth}p{0.03\textwidth}p{0.09\textwidth}p{0.415\textwidth}p{0.19\textwidth}p{0.06\textwidth}@{}}
\toprule
\rr Target & \rr Try & \rr Diagnosis & \rr Rule changed: old $\to$ new & \rr Meant to improve & \rr Retry \\
\midrule
"""
    return head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"


def main():
    anat = load(os.path.join(DATA, "anatomy.json"))
    rows = load(os.path.join(DATA, "growth.json"))["rows"]
    runs = load(MODLOG)["runs"]
    with open(os.path.join(SECTIONS, "gen_numbers.tex"), "w") as f:
        f.write(numbers(anat, rows, runs))
    with open(os.path.join(SECTIONS, "gen_releases.tex"), "w") as f:
        f.write(releases(rows))
    with open(os.path.join(SECTIONS, "gen_modlog.tex"), "w") as f:
        f.write(modlog(runs))
    print("wrote", SECTIONS)


if __name__ == "__main__":
    main()
