"""Is a newer Anaxia image published?

Every merge to main and every release tag rebuilds the image ghcr.io/creelie/bllm-engine and
publishes it as `latest` (and as the package version). The image index carries the version, the
commit and the build time as annotations, and the image itself carries the same three values in
its environment (ANAXIA_VERSION, ANAXIA_REVISION, ANAXIA_CREATED). Comparing them tells a running
copy whether `latest` is newer. Nothing here downloads an image: `anaxia update` prints the
command, and runs `docker pull` only when asked to and when docker is on the path.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from typing import Dict, List, Optional, Tuple

from . import __version__

IMAGE = "ghcr.io/creelie/bllm-engine"
_REPO = "creelie/bllm-engine"
_INDEX = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
])


def _get(url: str, token: Optional[str] = None, accept: Optional[str] = None, timeout: float = 3.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": f"anaxia/{__version__}"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if accept:
        req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def remote_state(timeout: float = 3.0) -> Dict:
    """The published tags and the annotations of `latest` (anonymous pull token; the image is public)."""
    token = json.loads(_get(f"https://ghcr.io/token?scope=repository:{_REPO}:pull", timeout=timeout))["token"]
    tags = json.loads(_get(f"https://ghcr.io/v2/{_REPO}/tags/list", token, timeout=timeout)).get("tags", [])
    index = json.loads(_get(f"https://ghcr.io/v2/{_REPO}/manifests/latest", token, _INDEX, timeout))
    ann = index.get("annotations", {})
    return dict(tags=tags, version=ann.get("org.opencontainers.image.version", ""),
                revision=ann.get("org.opencontainers.image.revision", ""),
                created=ann.get("org.opencontainers.image.created", ""))


def local_state() -> Dict:
    return dict(version=__version__, revision=os.environ.get("ANAXIA_REVISION", ""),
                created=os.environ.get("ANAXIA_CREATED", ""), in_image=os.environ.get("ANAXIA_IMAGE") == "1")


def _version_key(v: str) -> Optional[Tuple[int, ...]]:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return None


def newer(local: Dict, remote: Dict) -> Tuple[bool, str]:
    """Whether the published image is newer than the running copy, and why.

    A higher numbered tag than the local version is a newer release. With equal versions, a later
    build time of `latest` from another commit is a newer build of main. Without the build time on
    either side only the version can be compared."""
    mine = _version_key(local["version"])
    numbered = [k for k in (_version_key(t) for t in remote.get("tags", [])) if k is not None]
    if mine is not None and numbered and max(numbered) > mine:
        return True, "release " + ".".join(map(str, max(numbered))) + " is published"
    if (local.get("created") and remote.get("created") and remote["created"] > local["created"]
            and remote.get("revision") and remote["revision"] != local.get("revision")):
        return True, f"latest was rebuilt from commit {remote['revision'][:7]} on {remote['created']}"
    return False, "this copy is current"


def advice(in_image: bool) -> List[str]:
    if in_image:
        return [f"docker pull {IMAGE}:latest"]
    return [f"docker pull {IMAGE}:latest", "pip install --upgrade git+https://github.com/creelie/eBLLM"]


def notice(timeout: float = 2.0) -> Optional[str]:
    """One line for the start of the image when `latest` is newer; None otherwise or offline."""
    if os.environ.get("ANAXIA_NO_UPDATE_CHECK"):
        return None
    try:
        new, why = newer(local_state(), remote_state(timeout))
    except Exception:
        return None
    if not new:
        return None
    return f"anaxia: a newer image is published ({why}); update with: docker pull {IMAGE}:latest"


def cmd_update(args) -> int:
    loc = local_state()
    print(f"this copy:  anaxia {loc['version']}" + (f", commit {loc['revision'][:7]}" if loc["revision"] else "")
          + (f", built {loc['created']}" if loc["created"] else "") + (" (image)" if loc["in_image"] else ""))
    try:
        rem = remote_state(args.timeout)
    except Exception as e:
        print(f"could not reach ghcr.io: {e}")
        return 2
    print(f"published:  {IMAGE} tags {', '.join(sorted(rem['tags']))}"
          + (f"; latest from commit {rem['revision'][:7]}" if rem["revision"] else "")
          + (f", built {rem['created']}" if rem["created"] else ""))
    new, why = newer(loc, rem)
    print(why)
    if not new and not args.pull:
        return 0
    if args.pull:
        if shutil.which("docker") is None:
            print("docker is not on the path here; run on the host:")
            for line in advice(True):
                print("  " + line)
            return 1
        return subprocess.call(["docker", "pull", f"{IMAGE}:latest"])
    print("to update:")
    for line in advice(loc["in_image"]):
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(cmd_update(type("A", (), {"timeout": 5.0, "pull": False})()))
