"""Write the list of Appendix D (what the engine draws on) from the registry of the package.

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


def entry(x):
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
    return r"\sourceentry{%s}{%s}{%s}{%s}" % (name, status, taken, left)


def main():
    items = json.load(open(SRC, encoding="utf-8"))
    groups = []
    for x in items:
        if x["group"] not in groups:
            groups.append(x["group"])
    # A list set in the running columns: it breaks between and inside entries like ordinary
    # text, so it needs neither a one-column passage nor the longtable package.
    lines = [r"% written by figures/src/make_sources_table.py from src/ebllm/bllm/data/sources.json",
             r"\par\begingroup\footnotesize\raggedright\setlength{\parindent}{0pt}\setlength{\parskip}{2pt plus 1pt}%",
             r"\def\sourcegroup#1{\par\addvspace{4pt}\textbf{#1}\par\nobreak}%",
             r"\def\sourceentry#1#2#3#4{\par\hangindent=1em\hangafter=1 \textbf{#1}, #2. \emph{Takes:} #3 \emph{Leaves:} #4\par}%"]
    for g in groups:
        lines.append(r"\sourcegroup{%s}" % tex(g))
        lines += [entry(x) for x in items if x["group"] == g]
    lines += [r"\par\endgroup", ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{OUT}: {len(items)} sources in {len(groups)} groups")


if __name__ == "__main__":
    main()
