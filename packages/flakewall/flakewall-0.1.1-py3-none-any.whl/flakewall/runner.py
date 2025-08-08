from __future__ import annotations

from dataclasses import dataclass
from typing import List
import subprocess
import shlex
import os


@dataclass
class RetryOutcome:
    test_id: str
    attempts: int
    first_attempt_passed: bool
    eventually_passed: bool

    @property
    def is_flaky(self) -> bool:
        return (not self.first_attempt_passed) and self.eventually_passed


def _pytest_expr_from_test_id(test_id: str) -> str:
    # Expect format "pkg.module.ClassName::test_name" or "ClassName::test_name" or just name
    expr_parts: List[str] = []
    if "::" in test_id:
        class_part, name_part = test_id.split("::", 1)
        # Use only the tail of the class (after last dot) to avoid needing file paths
        class_tail = class_part.split(".")[-1]
        if class_tail and class_tail != "<unknown>":
            expr_parts.append(class_tail)
        if name_part:
            expr_parts.append(name_part)
    else:
        expr_parts.append(test_id)
    # Combine with 'and' for stricter selection
    if not expr_parts:
        return test_id
    return " and ".join(expr_parts)


def _jest_args_from_test_id(test_id: str) -> List[str]:
    # Expect format "path/to/file.test.ts::test name" or "SuiteName::test name" or just name
    file_arg: str | None = None
    name_part: str = test_id
    if "::" in test_id:
        class_part, name_part = test_id.split("::", 1)
        if "/" in class_part or class_part.endswith(('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs')):
            file_arg = class_part
    args: List[str] = []
    if file_arg:
        args.append(file_arg)
    # Jest test name pattern
    args.extend(["-t", name_part])
    return args


def retry_tests_pytest(
    test_ids: List[str],
    max_retries: int = 1,
    base_cmd: str = "pytest -q",
    working_dir: str | None = None,
    dry_run: bool = False,
) -> List[RetryOutcome]:
    outcomes: List[RetryOutcome] = []
    for test_id in test_ids:
        expr = _pytest_expr_from_test_id(test_id)
        cmd = f"{base_cmd} -k {shlex.quote(expr)} -x"
        attempts = 0
        passed_once = False
        first_pass = None
        for attempt in range(0, max_retries + 1):
            attempts += 1
            if dry_run:
                print(f"DRY RUN: would run: {cmd}")
                # Simulate failure on first attempt only in dry-run; do not mark as flaky deterministically
                continue
            try:
                result = subprocess.run(shlex.split(cmd), cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                success = result.returncode == 0
            except FileNotFoundError:
                raise SystemExit("pytest not found on PATH; install it or provide a custom --cmd")
            if first_pass is None:
                first_pass = success
            if success:
                passed_once = True
                break
        outcomes.append(
            RetryOutcome(
                test_id=test_id,
                attempts=attempts,
                first_attempt_passed=bool(first_pass),
                eventually_passed=passed_once,
            )
        )
    return outcomes


def retry_tests_jest(
    test_ids: List[str],
    max_retries: int = 1,
    base_cmd: str = "jest -i",
    working_dir: str | None = None,
    dry_run: bool = False,
) -> List[RetryOutcome]:
    outcomes: List[RetryOutcome] = []
    for test_id in test_ids:
        jest_args = _jest_args_from_test_id(test_id)
        cmd_list = shlex.split(base_cmd) + jest_args
        attempts = 0
        passed_once = False
        first_pass = None
        for attempt in range(0, max_retries + 1):
            attempts += 1
            if dry_run:
                print("DRY RUN: would run:", " ".join(shlex.quote(p) for p in cmd_list))
                continue
            try:
                result = subprocess.run(cmd_list, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                success = result.returncode == 0
            except FileNotFoundError:
                raise SystemExit("jest not found on PATH; install it or provide a custom --cmd (e.g., 'npx jest -i')")
            if first_pass is None:
                first_pass = success
            if success:
                passed_once = True
                break
        outcomes.append(
            RetryOutcome(
                test_id=test_id,
                attempts=attempts,
                first_attempt_passed=bool(first_pass),
                eventually_passed=passed_once,
            )
        )
    return outcomes


def retry_tests(
    framework: str,
    test_ids: List[str],
    max_retries: int = 1,
    base_cmd: str | None = None,
    working_dir: str | None = None,
    dry_run: bool = False,
) -> List[RetryOutcome]:
    framework = framework.lower()
    if framework == "pytest":
        return retry_tests_pytest(
            test_ids=test_ids,
            max_retries=max_retries,
            base_cmd=base_cmd or "pytest -q",
            working_dir=working_dir,
            dry_run=dry_run,
        )
    elif framework == "jest":
        return retry_tests_jest(
            test_ids=test_ids,
            max_retries=max_retries,
            base_cmd=base_cmd or "jest -i",
            working_dir=working_dir,
            dry_run=dry_run,
        )
    else:
        raise SystemExit(f"Unsupported framework: {framework}")


