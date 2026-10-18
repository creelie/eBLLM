#!/bin/sh
# Builds the TikZ figures and writes 300 dpi PNG copies next to the data plots.
set -e
here=$(cd "$(dirname "$0")" && pwd)
cd "$here"
python3 gen_branchtree.py >/dev/null
python3 gen_history.py
for f in fig_architecture fig_history fig_kraft3d fig_gatingflow fig_regimes fig_branchtree; do
  pdflatex -interaction=nonstopmode -halt-on-error "$f.tex" >/dev/null
  pdftoppm -png -r 300 -singlefile "$f.pdf" "../../$f"
done
rm -f ./*.aux ./*.log
