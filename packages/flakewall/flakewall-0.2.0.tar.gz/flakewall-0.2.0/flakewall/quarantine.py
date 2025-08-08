from __future__ import annotations

from pathlib import Path
from typing import Set, Dict, Any, Tuple, List
import yaml

from .config import QUARANTINE_PATH


def _normalize_q(data: Dict[str, Any]) -> Tuple[Set[str], Dict[str, Any]]:
    items = data.get("quarantined", []) or []
    # Support either list[str] or list[dict]
    ids: Set[str] = set()
    ttl_map: Dict[str, Any] = {}
    for it in items:
        if isinstance(it, str):
            ids.add(it)
        elif isinstance(it, dict):
            tid = str(it.get("id"))
            ids.add(tid)
            ttl_map[tid] = {k: v for k, v in it.items() if k != "id"}
    return ids, ttl_map


def load_quarantined(path: Path | None = None) -> Set[str]:
    target_path = path or QUARANTINE_PATH
    if not target_path.exists():
        return set()
    data = yaml.safe_load(target_path.read_text()) or {}
    ids, _ = _normalize_q(data)
    return ids


def add_to_quarantine(
    test_ids: list[str], path: Path | None = None, ttl_runs: int | None = None
) -> None:
    target_path = path or QUARANTINE_PATH
    data: dict = {}
    if target_path.exists():
        data = yaml.safe_load(target_path.read_text()) or {}
    ids, ttl_map = _normalize_q(data)
    for tid in test_ids:
        ids.add(tid)
        if ttl_runs is not None:
            ttl_map[tid] = {"ttl_runs": ttl_runs, "remaining_runs": ttl_runs}
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Write as list of structured entries if TTL present
    if ttl_map:
        items: List[dict] = []
        for tid in sorted(ids):
            meta = ttl_map.get(tid)
            if meta:
                entry = {"id": tid}
                entry.update(meta)
                items.append(entry)
            else:
                items.append({"id": tid})
        payload = {"quarantined": items}
    else:
        payload = {"quarantined": sorted(ids)}
    target_path.write_text(yaml.safe_dump(payload, sort_keys=True))


def decrement_quarantine_ttl(path: Path | None = None) -> int:
    target_path = path or QUARANTINE_PATH
    if not target_path.exists():
        return 0
    data = yaml.safe_load(target_path.read_text()) or {}
    ids, ttl_map = _normalize_q(data)
    changed = False
    to_remove: Set[str] = set()
    for tid, meta in list(ttl_map.items()):
        rem = int(meta.get("remaining_runs", meta.get("ttl_runs", 0)))
        if rem > 0:
            meta["remaining_runs"] = rem - 1
            changed = True
            if meta["remaining_runs"] <= 0:
                to_remove.add(tid)
    ids -= to_remove
    for tid in to_remove:
        ttl_map.pop(tid, None)
    if changed or to_remove:
        if ttl_map:
            items: List[dict] = []
            for tid in sorted(ids):
                meta = ttl_map.get(tid)
                if meta:
                    entry = {"id": tid}
                    entry.update(meta)
                    items.append(entry)
                else:
                    items.append({"id": tid})
            payload = {"quarantined": items}
        else:
            payload = {"quarantined": sorted(ids)}
        target_path.write_text(yaml.safe_dump(payload, sort_keys=True))
    return len(to_remove)
