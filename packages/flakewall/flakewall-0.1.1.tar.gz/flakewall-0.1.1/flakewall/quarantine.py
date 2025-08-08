from __future__ import annotations

from pathlib import Path
from typing import Set
import yaml

from .config import QUARANTINE_PATH


def load_quarantined(path: Path | None = None) -> Set[str]:
    target_path = path or QUARANTINE_PATH
    if not target_path.exists():
        return set()
    data = yaml.safe_load(target_path.read_text()) or {}
    items = data.get("quarantined", []) or []
    return set(str(x) for x in items)


def add_to_quarantine(test_ids: list[str], path: Path | None = None) -> None:
    target_path = path or QUARANTINE_PATH
    data: dict = {}
    if target_path.exists():
        data = yaml.safe_load(target_path.read_text()) or {}
    quarantined = set(data.get("quarantined", []) or [])
    quarantined.update(test_ids)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(yaml.safe_dump({"quarantined": sorted(quarantined)}, sort_keys=True))


