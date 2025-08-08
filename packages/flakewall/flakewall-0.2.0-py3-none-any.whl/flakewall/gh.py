from __future__ import annotations

import os
import sys
from typing import Iterable


def write_step_summary(lines: Iterable[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as fh:
            for line in lines:
                fh.write(line)
                if not line.endswith("\n"):
                    fh.write("\n")
    except Exception:
        # Silent no-op if file is not writable
        return


def annotate(level: str, message: str) -> None:
    # GitHub workflow command, levels: notice|warning|error
    sys.stdout.write(f"::{level}::{message}\n")
    sys.stdout.flush()
