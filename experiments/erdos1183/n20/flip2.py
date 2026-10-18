"""From a grid colouring of 2^[20] (dims 18, 2) with one bad (colour, base) pair, try every single and
every double flip of grid points and report any colouring with no monochromatic sublattice of 12."""
import itertools, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
GS = os.path.join(HERE, "..", "gridsearch")
bits = sys.argv[1]
def sc(b):
    return int(subprocess.run([GS, "check", "2", "18", "2", "12", b], capture_output=True, text=True).stdout)
def flip(b, idx):
    l = list(b)
    for i in idx:
        l[i] = "1" if l[i] == "0" else "0"
    return "".join(l)
print("start", sc(bits), flush=True)
n = len(bits)
for r in (1, 2):
    for idx in itertools.combinations(range(n), r):
        b = flip(bits, idx)
        s = sc(b)
        if s == 0:
            print("FOUND", idx, b, flush=True)
            sys.exit(0)
    print("no", r, "flip works", flush=True)
