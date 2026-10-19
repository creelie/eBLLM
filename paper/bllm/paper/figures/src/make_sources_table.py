"""Write the table of Appendix D (what the engine draws on) from the registry of the package.

    python3 make_sources_table.py        # reads src/ebllm/bllm/data/sources.json, writes
                                         # paper/bllm/paper/sections/appD_sources_table.tex
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SRC = os.path.join(ROOT, "src", "ebllm", "bllm", "data", "sources.json")
OUT = os.path.join(HERE, "..", "..", "sections", "appD_sources_table.tex")

CITE = {
    "funsearch": "RBN24", "alphaevolve": "NVE25", "alphaproof": "HMS25", "alphageometry": "TWL24",
    "alphageometry2": "CTO25", "formal-conjectures": "FCA25", "mathematics-dataset": "SGH19",
    "alphatensor": "FBH22", "alphadev": "MMZ23", "davies-2021": "DVB21", "successive-halving": "JT16",
    "hebb": "Heb49", "postnikov": "Hat02", "openai-math": "OAI26b", "openai-navier-stokes": "OAI26",
    "openrefute": "OIT26", "obsidian-brain": "Wei26", "deepseek-prover-v2": "RSX25",
    "kimina-prover": "WUL25", "goedel-prover": "LTL25", "qwen-math": "YZH24", "htps": "LLL22",
    "leandojo": "YSG23", "seed-prover": "CGH25", "aristotle": "ABB25",
}


def tex(s):
    out = []
    for ch in s:
        out.append({"&": r"\&", "%": r"\%", "_": r"\_", "#": r"\#", "~": r"\textasciitilde{}",
                    "^": r"\textasciicircum{}", "$": r"\$", "{": r"\{", "}": r"\}"}.get(ch, ch))
    return "".join(out).replace("--", "-{}-").replace("Erdos", r"Erd\H{o}s").replace(
        "Kral'", r"Kr\'al'").replace(" -> ", r" $\to$ ")


def sentence(s):
    s = s.strip()
    if not s:
        return "---"
    s = s[0].upper() + s[1:]
    return s if s.endswith(".") else s + "."


def row(x):
    name = tex(x["name"])
    if x["id"] in CITE:
        name += r" \cite{%s}" % CITE[x["id"]]
    elif x.get("url"):
        url = x["url"].replace("https://", "")
        name += r", \nolinkurl{%s}" % url.rstrip("/")
    status = tex(x["status"])
    taken = tex(sentence(x["taken"]))
    if x.get("where"):
        taken += r" \emph{In:} " + tex(x["where"].strip().rstrip(".")) + "."
    left = tex(sentence(x["left"]))
    if x.get("weights"):
        left += " Weights: " + tex(x["weights"]) + "."
    return r"\rr %s & \rr %s & \rr %s & \rr %s \\" % (name, status, taken, left)


def main():
    items = json.load(open(SRC, encoding="utf-8"))
    groups = []
    for x in items:
        if x["group"] not in groups:
            groups.append(x["group"])
    # One tabular per row, stacked without interline glue, so that the table breaks between rows
    # without the longtable package (whose current version conflicts with the patch in revtex4-2).
    cols = r"@{}p{0.17\textwidth}p{0.13\textwidth}p{0.40\textwidth}p{0.26\textwidth}@{}"
    head = r"\rr Source & \rr Status & \rr What the engine takes & \rr What it leaves \\"
    rows = [r"\toprule " + head + r" \midrule"]
    for g in groups:
        rows.append(r"\multicolumn{4}{@{}l}{\emph{%s}}\\" % tex(g))
        rows += [row(x) for x in items if x["group"] == g]
    rows[-1] += r" \bottomrule"
    lines = [r"% written by figures/src/make_sources_table.py from src/ebllm/bllm/data/sources.json",
             r"\par\begingroup\scriptsize\setlength{\tabcolsep}{3pt}\setlength{\parskip}{0pt}\setlength{\parindent}{0pt}%",
             r"\expandafter\def\csname @captype\endcsname{table}%",
             r"\caption{The registry of Anaxia: every system, method and collection the engine draws on, what it takes, where in the package, and what it leaves. ``Status'' is that of the source; an unrefereed claim stays unrefereed in the engine.}\label{tab:sources}\par",
             r"\def\sourcerow#1{\par\nointerlineskip\noindent\begin{tabular}{%s}#1\end{tabular}\par}%%" % cols]
    lines += [r"\sourcerow{%s}" % r for r in rows]
    lines += [r"\par\endgroup", ""]
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{len(items)} sources in {len(groups)} groups -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
