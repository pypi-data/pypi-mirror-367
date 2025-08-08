from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class CaseResult:
    test_id: str
    status: str  # pass|fail|error|skipped
    classname: str | None = None
    name: str | None = None


def parse_junit_files(paths: Iterable[Path]) -> List[CaseResult]:
    results: List[CaseResult] = []
    for path in paths:
        if not path.exists():
            continue
        tree = ET.parse(str(path))
        root = tree.getroot()
        for testcase in root.iter("testcase"):
            classname = testcase.attrib.get("classname")
            name = testcase.attrib.get("name")
            test_id = _format_id(classname, name)
            status = "pass"
            if testcase.find("failure") is not None:
                status = "fail"
            elif testcase.find("error") is not None:
                status = "error"
            elif testcase.find("skipped") is not None:
                status = "skipped"
            results.append(
                CaseResult(test_id=test_id, status=status, classname=classname, name=name)
            )
    return results


def failing_ids(results: Iterable[CaseResult]) -> List[str]:
    return [r.test_id for r in results if r.status in {"fail", "error"}]


def _format_id(classname: str | None, name: str | None) -> str:
    if classname and name:
        return f"{classname}::{name}"
    if name:
        return name
    return classname or "<unknown>"


@dataclass(frozen=True)
class FlakeStats:
    test_id: str
    total_runs: int
    pass_count: int
    fail_error_count: int
    skipped_count: int

    @property
    def has_flip(self) -> bool:
        return self.pass_count > 0 and self.fail_error_count > 0

    @property
    def fail_ratio(self) -> float:
        if self.total_runs == 0:
            return 0.0
        return self.fail_error_count / self.total_runs


def compute_flake_stats(results: Iterable[CaseResult]) -> Dict[str, FlakeStats]:
    counts: Dict[str, Dict[str, int]] = {}
    for r in results:
        bucket = counts.setdefault(r.test_id, {"total": 0, "pass": 0, "failerr": 0, "skipped": 0})
        bucket["total"] += 1
        if r.status == "pass":
            bucket["pass"] += 1
        elif r.status in {"fail", "error"}:
            bucket["failerr"] += 1
        elif r.status == "skipped":
            bucket["skipped"] += 1
    stats: Dict[str, FlakeStats] = {}
    for test_id, c in counts.items():
        stats[test_id] = FlakeStats(
            test_id=test_id,
            total_runs=c["total"],
            pass_count=c["pass"],
            fail_error_count=c["failerr"],
            skipped_count=c["skipped"],
        )
    return stats


