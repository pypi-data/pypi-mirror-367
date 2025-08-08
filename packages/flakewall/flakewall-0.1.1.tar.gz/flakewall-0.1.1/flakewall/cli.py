from __future__ import annotations

from pathlib import Path
from typing import Optional
import glob
import sys
import json

import typer

from .config import FlakewallConfig, ensure_default_files, CONFIG_PATH
from .junit import parse_junit_files, failing_ids, compute_flake_stats
from .quarantine import load_quarantined, add_to_quarantine
from .runner import retry_tests
from . import __version__

app = typer.Typer(add_completion=False, help="Guard CI from flaky tests via JUnit XML and quarantine")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def init() -> None:
    """Create .flakewall config and quarantine files."""
    ensure_default_files()
    typer.echo(f"Initialized config at {CONFIG_PATH}")


@app.command()
def report(
    junit: Optional[str] = typer.Option(None, help='Glob of JUnit XML, e.g. "**/junit*.xml"'),
) -> None:
    cfg = FlakewallConfig.load()
    pattern = junit or cfg.report_glob
    files = [Path(p) for p in glob.glob(pattern, recursive=True)]
    results = parse_junit_files(files)
    failed = failing_ids(results)
    quarantined = load_quarantined()

    typer.echo(f"Files: {len(files)} | Cases: {len(results)} | Failures: {len(failed)}")
    if failed:
        typer.echo("Failing test IDs:")
        for test_id in failed:
            mark = " [quarantined]" if test_id in quarantined else ""
            typer.echo(f" - {test_id}{mark}")


@app.command()
def guard(
    junit: Optional[str] = typer.Option(None, help='Glob of JUnit XML, e.g. "**/junit*.xml"'),
    auto_quarantine: bool = typer.Option(False, help="Add newly detected failing tests to quarantine"),
) -> None:
    cfg = FlakewallConfig.load()
    pattern = junit or cfg.report_glob
    files = [Path(p) for p in glob.glob(pattern, recursive=True)]
    results = parse_junit_files(files)
    failed = failing_ids(results)

    if not failed:
        typer.echo("No failing tests detected.")
        raise typer.Exit(code=0)

    quarantined = load_quarantined()
    non_quarantined = [test_id for test_id in failed if test_id not in quarantined]

    if non_quarantined:
        typer.echo("Non-quarantined failures detected:")
        for test_id in non_quarantined:
            typer.echo(f" - {test_id}")
        raise typer.Exit(code=1)

    typer.echo("Only quarantined tests failed; passing guard.")

    if auto_quarantine and failed:
        add_to_quarantine(failed)
        typer.echo("Updated quarantine list.")

    raise typer.Exit(code=0)


@app.command()
def score(
    junit: Optional[str] = typer.Option(None, help='Glob of JUnit XML across multiple runs, e.g. "reports/**/junit*.xml"'),
    min_total: int = typer.Option(2, help="Only show tests with at least this many total runs"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON output"),
) -> None:
    """Compute minimal flake stats from a set of JUnit XML files and print tests that flipped."""
    cfg = FlakewallConfig.load()
    pattern = junit or cfg.report_glob
    files = [Path(p) for p in glob.glob(pattern, recursive=True)]
    results = parse_junit_files(files)
    stats = compute_flake_stats(results)

    flippers = [s for s in stats.values() if s.total_runs >= min_total and s.has_flip]
    flippers.sort(key=lambda s: (-(s.fail_ratio), s.test_id))

    if json_out:
        payload = {
            "files_count": len(files),
            "cases_count": len(results),
            "flaky_candidates_count": len(flippers),
            "flaky_candidates": [
                {
                    "test_id": s.test_id,
                    "total_runs": s.total_runs,
                    "pass_count": s.pass_count,
                    "fail_error_count": s.fail_error_count,
                    "skipped_count": s.skipped_count,
                    "has_flip": s.has_flip,
                    "fail_ratio": s.fail_ratio,
                }
                for s in flippers
            ],
        }
        typer.echo(json.dumps(payload, indent=2))
        return
    else:
        typer.echo(f"Files: {len(files)} | Cases: {len(results)} | Flaky candidates: {len(flippers)}")
        for s in flippers:
            typer.echo(f" - {s.test_id}: runs={s.total_runs} pass={s.pass_count} fail+error={s.fail_error_count} skipped={s.skipped_count} fail_ratio={s.fail_ratio:.2f}")


@app.command()
def auto_quarantine(
    junit: Optional[str] = typer.Option(None, help='Glob of JUnit XML across multiple runs'),
    threshold: float = typer.Option(0.10, help="Minimum fail ratio to consider flaky (0.0-1.0)"),
    min_total: int = typer.Option(2, help="Minimum total runs to consider"),
    dry_run: bool = typer.Option(False, help="Print changes without writing"),
) -> None:
    """Add tests to quarantine if they show flip behavior and meet threshold criteria."""
    cfg = FlakewallConfig.load()
    pattern = junit or cfg.report_glob
    files = [Path(p) for p in glob.glob(pattern, recursive=True)]
    results = parse_junit_files(files)
    stats = compute_flake_stats(results)

    candidates = [s for s in stats.values() if s.total_runs >= min_total and s.has_flip and s.fail_ratio >= threshold]
    if not candidates:
        typer.echo("No candidates met the threshold.")
        raise typer.Exit(code=0)

    ids = [s.test_id for s in candidates]
    if dry_run:
        typer.echo("DRY RUN: would add to quarantine:")
        for tid in ids:
            typer.echo(f" - {tid}")
        raise typer.Exit(code=0)

    add_to_quarantine(ids)
    typer.echo(f"Added {len(ids)} tests to quarantine.")


@app.command()
def retry(
    framework: str = typer.Option("pytest", help="Test framework to use (pytest)"),
    tests: Optional[str] = typer.Option(None, help="Comma-separated test ids to retry (classname::name)"),
    from_junit: Optional[str] = typer.Option(None, help='Glob of JUnit XML to pick failing tests from'),
    max_retries: int = typer.Option(1, help="Max retries per test"),
    cmd: Optional[str] = typer.Option(None, help="Base command to run tests (default depends on framework)"),
    working_dir: Optional[str] = typer.Option(None, help="Working directory for the test command"),
    auto_quarantine: bool = typer.Option(False, help="Quarantine tests that flip from fail to pass"),
    dry_run: bool = typer.Option(False, help="Print commands without executing"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON output"),
) -> None:
    """Retry selected tests and quarantine those that prove flaky (fail then pass)."""
    selected: list[str] = []
    if tests:
        selected.extend([t.strip() for t in tests.split(",") if t.strip()])
    if from_junit:
        files = [Path(p) for p in glob.glob(from_junit, recursive=True)]
        failed = failing_ids(parse_junit_files(files))
        selected.extend([t for t in failed if t not in selected])

    if not selected:
        typer.echo("No tests to retry. Provide --tests or --from-junit.")
        raise typer.Exit(code=0)

    outcomes = retry_tests(
        framework=framework,
        test_ids=selected,
        max_retries=max_retries,
        base_cmd=cmd,
        working_dir=working_dir,
        dry_run=dry_run,
    )

    flaky_ids = [o.test_id for o in outcomes if o.is_flaky]
    if json_out:
        payload = {
            "outcomes": [
                {
                    "test_id": o.test_id,
                    "attempts": o.attempts,
                    "first_attempt_passed": o.first_attempt_passed,
                    "eventually_passed": o.eventually_passed,
                    "flaky": o.is_flaky,
                }
                for o in outcomes
            ],
            "flaky_ids": flaky_ids,
        }
        typer.echo(json.dumps(payload, indent=2))
    else:
        for o in outcomes:
            typer.echo(
                f" - {o.test_id}: attempts={o.attempts} first_pass={o.first_attempt_passed} eventually_passed={o.eventually_passed} flaky={o.is_flaky}"
            )

    if auto_quarantine and flaky_ids and not dry_run:
        add_to_quarantine(flaky_ids)
        typer.echo(f"Quarantined {len(flaky_ids)} flaky tests.")

if __name__ == "__main__":  # pragma: no cover
    app()


