from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


def load_codeowners(repo_root: Path) -> Dict[str, str]:
    # Very small subset: lines like 'path/ @owner'
    owners: Dict[str, str] = {}
    for rel in [".github/CODEOWNERS", "CODEOWNERS"]:
        p = repo_root / rel
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                path_glob, owner = parts[0], parts[1]
                owners[path_glob] = owner
    return owners


def guess_owner(test_id: str, owners_map: Dict[str, str]) -> Optional[str]:
    # Heuristic: match class/module prefix to a path glob entry
    for pattern, owner in owners_map.items():
        # naive check; proper glob-to-class mapping is non-trivial
        if pattern in test_id:
            return owner
    return None
