from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Tuple
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


def parse_junit_file(path: Path) -> List[CaseResult]:
    return parse_junit_files([path])


def parse_junit_files_grouped(paths: Iterable[Path]) -> Dict[Path, List[CaseResult]]:
    grouped: Dict[Path, List[CaseResult]] = {}
    for path in paths:
        grouped[path] = parse_junit_file(path)
    return grouped


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


@dataclass(frozen=True)
class FlakeMetrics:
    test_id: str
    total_runs: int
    pass_count: int
    fail_error_count: int
    skipped_count: int
    flips: int
    instability_index: float  # flips normalized by max possible flips
    longest_pass_streak: int
    longest_failerr_streak: int


def compute_flake_metrics(
    grouped_results: Dict[Path, List[CaseResult]],
    order: str = "name",  # name|mtime
) -> Dict[str, FlakeMetrics]:
    def status_key(status: str) -> int:
        return 1 if status in {"fail", "error"} else 0 if status == "pass" else 2

    # Order files deterministically
    files = list(grouped_results.keys())
    if order == "mtime":
        files.sort(key=lambda p: p.stat().st_mtime)
    else:
        files.sort(key=lambda p: str(p))

    # Build per-test status sequences across files
    test_to_sequence: Dict[str, List[str]] = {}
    counts: Dict[str, Dict[str, int]] = {}
    for path in files:
        for r in grouped_results.get(path, []):
            seq = test_to_sequence.setdefault(r.test_id, [])
            seq.append(r.status)
            bucket = counts.setdefault(
                r.test_id, {"total": 0, "pass": 0, "failerr": 0, "skipped": 0}
            )
            bucket["total"] += 1
            if r.status == "pass":
                bucket["pass"] += 1
            elif r.status in {"fail", "error"}:
                bucket["failerr"] += 1
            elif r.status == "skipped":
                bucket["skipped"] += 1

    metrics: Dict[str, FlakeMetrics] = {}
    for test_id, seq in test_to_sequence.items():
        if not seq:
            continue
        flips = 0
        longest_pass = 0
        longest_failerr = 0
        current_pass = 0
        current_failerr = 0
        prev_bucket = None
        for status in seq:
            bucket = status_key(status)
            if prev_bucket is not None and bucket != prev_bucket and 2 not in (bucket, prev_bucket):
                flips += 1
            if bucket == 0:  # pass
                current_pass += 1
                current_failerr = 0
            elif bucket == 1:  # fail/error
                current_failerr += 1
                current_pass = 0
            else:  # skipped
                # reset streaks on skipped
                current_pass = 0
                current_failerr = 0
            longest_pass = max(longest_pass, current_pass)
            longest_failerr = max(longest_failerr, current_failerr)
            prev_bucket = bucket

        total_runs = counts[test_id]["total"]
        max_possible_flips = max(0, total_runs - 1)
        instability = (flips / max_possible_flips) if max_possible_flips > 0 else 0.0
        metrics[test_id] = FlakeMetrics(
            test_id=test_id,
            total_runs=total_runs,
            pass_count=counts[test_id]["pass"],
            fail_error_count=counts[test_id]["failerr"],
            skipped_count=counts[test_id]["skipped"],
            flips=flips,
            instability_index=instability,
            longest_pass_streak=longest_pass,
            longest_failerr_streak=longest_failerr,
        )
    return metrics
