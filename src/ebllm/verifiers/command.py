"""The code verifier: run a program and require exit status 0 and an expected line of output."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass
class CommandVerifier:
    argv: Sequence[str]
    expect: Optional[str] = None      # a regular expression that must match some output line
    cwd: Optional[str] = None
    timeout: int = 3600
    last_output: str = field(default="", repr=False)

    def __call__(self) -> int:
        try:
            proc = subprocess.run(list(self.argv), cwd=self.cwd, capture_output=True, text=True,
                                  timeout=self.timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.last_output = str(exc)
            return 0
        self.last_output = proc.stdout + proc.stderr
        if proc.returncode != 0:
            return 0
        if self.expect is not None and not re.search(self.expect, self.last_output, re.M):
            return 0
        return 1
