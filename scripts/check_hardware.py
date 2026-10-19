"""Check this machine against HARDWARE.md before a run.

    python3 scripts/check_hardware.py [--path DIR] [--component NAME]

Prints one line per component: OK, or what is short (CPU, RAM, disk free at DIR, GPU, tools)."""
import argparse, os, shutil, subprocess, sys

# name: (cpus, ram_gb, disk_gb, gpu_vram_gb, tools)
SPECS = {
    "package": (1, 1, 0.2, 0, ["python3"]),
    "memory": (1, 1, 0.05, 0, ["python3"]),
    "construct": (1, 0.5, 0.01, 0, ["python3"]),
    "deepmind-fetch": (1, 0.5, 0.3, 0, ["python3", "git"]),
    "five-benchmark": (2, 2, 0.2, 0, ["python3"]),
    "loop": (2, 2, 1, 0, ["python3"]),
    "qwen-0.5b": (2, 1.5, 0.5, 0, ["python3"]),
    "qwen-1.5b": (4, 3, 1.2, 0, ["python3"]),
    "finetune": (8, 32, 20, 8, ["python3"]),
    "lean-package": (1, 1, 3, 0, ["lake"]),
    "lean-mathlib": (2, 8, 12, 0, ["lake"]),
    "openai-rebuild": (8, 32, 60, 0, ["lake", "git"]),
    "sat": (1, 2, 0.1, 0, ["python3"]),
    "gridsearch": (1, 0.05, 0.01, 0, ["cc"]),
    "ds-box": (2, 2, 0.1, 0, ["python3"]),
}
MODULES = {"ds-box": ["numpy"], "qwen-0.5b": ["llama_cpp"], "qwen-1.5b": ["llama_cpp"], "finetune": ["torch", "peft"], "sat": ["pysat"], "construct": ["networkx", "pysat"]}


def ram_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal"):
                return int(line.split()[1]) / 1024 ** 2
    except OSError:
        pass
    if sys.platform == "win32":
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("len", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                        ("avail", ctypes.c_ulonglong), ("tpage", ctypes.c_ulonglong), ("apage", ctypes.c_ulonglong),
                        ("tvirt", ctypes.c_ulonglong), ("avirt", ctypes.c_ulonglong), ("aext", ctypes.c_ulonglong)]
        m = MS(); m.len = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return m.total / 1024 ** 3
        return 0.0
    try:
        out = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout
        return int(out) / 1024 ** 3
    except Exception:
        return 0.0


def gpu_gb():
    if not shutil.which("nvidia-smi"):
        return 0.0
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.split()
    return max([int(x) / 1024 for x in out if x.isdigit()] or [0.0])


ALIASES = {"python3": ["python3", "python", "py"], "cc": ["cc", "gcc", "clang", "cl"]}


def has_tool(t):
    if t.startswith("python") and sys.executable:
        return True
    names = ALIASES.get(t, [t])
    return any(shutil.which(n) for n in names) or any(
        os.path.exists(os.path.expanduser(f"~/.elan/bin/{n}{ext}")) for n in names for ext in ("", ".exe"))


def has_module(m):
    import importlib.util
    return importlib.util.find_spec(m) is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=".")
    ap.add_argument("--component")
    a = ap.parse_args()
    cpus, ram = os.cpu_count() or 1, ram_gb()
    disk = shutil.disk_usage(a.path).free / 1024 ** 3
    gpu = gpu_gb()
    print(f"machine: {cpus} CPU, {ram:.1f} GB RAM, {disk:.1f} GB free at {os.path.abspath(a.path)}, GPU {gpu:.1f} GB")
    bad = 0
    for name, (c, r, d, g, tools) in SPECS.items():
        if a.component and name != a.component:
            continue
        short = []
        if cpus < c: short.append(f"CPU {cpus} < {c}")
        if ram < r: short.append(f"RAM {ram:.1f} < {r} GB")
        if disk < d: short.append(f"disk {disk:.1f} < {d} GB")
        if gpu < g: short.append(f"GPU {gpu:.1f} < {g} GB")
        short += [f"missing {t}" for t in tools if not has_tool(t)]
        short += [f"missing module {m}" for m in MODULES.get(name, []) if not has_module(m)]
        print(f"{name:16s} {'OK' if not short else 'SHORT: ' + '; '.join(short)}")
        bad += bool(short)
    sys.exit(1 if a.component and bad else 0)


if __name__ == "__main__":
    main()
