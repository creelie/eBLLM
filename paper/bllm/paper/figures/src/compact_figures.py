"""Prepare the PNG figures of the paper for a fast pdflatex run.

    python3 compact_figures.py            # rewrites paper/bllm/paper/figures/*.png in place

Figures that are already opaque palette images of at most 1600 pixels are skipped, so the program
can be run after any figure program without quantizing the other figures again.

Run it after the figure programs. Every figure is set at the full text width (about 7 inches),
so each PNG is flattened onto white, scaled to at most 1600 pixels across (about 230 dpi on the
page), and reduced to a 256-colour palette with pngquant when it is installed. pdfTeX then embeds
the image data without re-encoding it, which keeps a pass of the REVTeX version near 5 seconds and
the figures near 4 MB; with transparent 300 dpi originals a pass took 11 seconds and the figures
12 MB.
"""
import glob
import os
import shutil
import subprocess

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..")
MAX_WIDTH = 1600


def flatten(path):
    im = Image.open(path)
    im.load()
    rgba = im.convert("RGBA")
    out = Image.new("RGB", rgba.size, (255, 255, 255))
    out.paste(rgba, mask=rgba.split()[3])
    if out.width > MAX_WIDTH:
        out = out.resize((MAX_WIDTH, round(out.height * MAX_WIDTH / out.width)), Image.LANCZOS)
    out.save(path, optimize=True)


def compacted(path):
    """True for a PNG this program has already written: an opaque palette image at most MAX_WIDTH
    across. Those are left alone, so that running the program again does not quantize them twice."""
    with Image.open(path) as im:
        return im.mode == "P" and im.width <= MAX_WIDTH and "transparency" not in im.info


def main():
    every = sorted(glob.glob(os.path.join(FIG, "*.png")))
    files = [f for f in every if not compacted(f)]
    for f in files:
        flatten(f)
    quant = shutil.which("pngquant")
    if quant and files:
        subprocess.run([quant, "--force", "--ext", ".png", "--quality", "80-98", "--speed", "1",
                        "--strip", *files], check=True)
    total = sum(os.path.getsize(f) for f in every)
    print(f"{len(every)} figures ({len(files)} compacted now), {total / 2**20:.1f} MB, "
          f"palette: {'yes' if quant else 'no (pngquant not found)'}")


if __name__ == "__main__":
    main()
