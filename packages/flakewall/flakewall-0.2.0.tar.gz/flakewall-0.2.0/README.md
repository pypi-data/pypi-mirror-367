# flakewall

[![CI](https://github.com/Cicatriiz/flakewall/actions/workflows/ci.yml/badge.svg)](https://github.com/Cicatriiz/flakewall/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/flakewall.svg)](https://pypi.org/project/flakewall/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)

Language-agnostic flaky test guard for CI. Parse JUnit XML, score flakiness, quarantine known flakes, and selectively retry tests (pytest/jest) – all via a tiny CLI.

## What it does (simple explanation)
Flaky tests are tests that sometimes pass and sometimes fail without code changes. `flakewall` helps you:
- Identify flaky candidates by scanning JUnit XML across runs
- Prevent known flakes from breaking CI (quarantine)
- Optionally re-run failing tests to prove they’re flaky (then auto-quarantine)

## Why it’s useful
- Works with any language that can emit JUnit XML
- No vendor lock-in, no background service – just a small CLI
- Plays nicely with your existing CI and test runner

## Install
Pick one of the following (no PyPI required):

From source (recommended for dev):
```bash
git clone https://github.com/Cicatriiz/flakewall.git
cd flakewall
make dev   # creates venv and installs in editable mode
# or
python -m venv .venv && . .venv/bin/activate && pip install -e .[dev]
```

pipx (isolated, global CLI without polluting system site-packages):
```bash
pipx install git+https://github.com/Cicatriiz/flakewall.git
```

Docker (no local Python required):
```bash
docker run --rm -v "$PWD":/work -w /work python:3.11-slim bash -lc \
  "pip install git+https://github.com/Cicatriiz/flakewall.git && flakewall --help"
```

From PyPI (optional):
```bash
pip install flakewall
```

## Quick start
```bash
# 1) Generate JUnit XML in your test run
pytest --junitxml=reports/junit.xml

# 2) Initialize config files
flakewall init

# 3) Guard CI: exit non‑zero only if non‑quarantined failures exist
flakewall guard --junit "reports/**/*.xml"

# 4) Score flakiness across multiple reports (optional)
flakewall score --junit "reports/**/*.xml" --min-total 2 --json > flakewall_score.json

# 5) Retry specific failing tests (pytest/jest) and optionally auto‑quarantine
flakewall retry --framework pytest --from-junit "reports/**/*.xml" --max-retries 1 --auto-quarantine
```

## Commands
- `init` – creates `.flakewall/config.yml` and `.flakewall/quarantine.yml`
- `report` – lists current failing test IDs and marks quarantined ones
- `guard` – exits 0 if failures ⊆ quarantine; else exits 1. Flags: `--gh-annotations`, `--slack-webhook URL`
- `score` – detects pass/fail flips across JUnit files; supports `--json` and `--rich` (adds flips, instability index, and streaks)
- `auto-quarantine` – adds flip-prone tests above a `--threshold` to quarantine; optional `--ttl-runs N` to auto-unquarantine after N runs
- `retry` – re-runs tests up to `--max-retries`; can `--auto-quarantine` proofs of flakiness; supports `--json`; optional `--junit-out path` to write a merged JUnit

## Configuration
Files created by `init` under `.flakewall/`:
- `config.yml` – for example:
  ```yaml
  retries: 0
  report_glob: "**/junit*.xml"
  ```
- `quarantine.yml` – list of quarantined test IDs:
  ```yaml
  quarantined:
    - package.module::TestClass::test_name
  ```

## CI examples
- GitHub Actions: `examples/ci/github-actions.yml`
- GitLab CI: `examples/ci/gitlab-ci.yml`
- CircleCI: `examples/ci/circleci-config.yml`
- Azure Pipelines: `examples/ci/azure-pipelines.yml`
- Jenkins: `examples/ci/Jenkinsfile`

## Supported inputs and runners
- Input: JUnit XML (generic, from any language)
- Retry adapters:
  - pytest (default; `-k <Class and name>`)
  - jest (`-t <name>`; include file path via `path/to/test.spec.ts::test name` if needed)
  - vitest (`vitest run -t <name> [file]`)
  - go (`go test -run <name> ./...`)
  - dotnet (`dotnet test --filter FullyQualifiedName~<name>`)
  - shell (generic template; provide `--cmd '...{test}...'`)

## Notes and limitations
- Quarantine is a local YAML list – keep it under review in code review.
- TTL support: run `flakewall quarantine-tick` in CI to decrement TTL and auto-remove expired entries.
- Flake scoring is minimal (requires only JUnit XML). It doesn’t depend on long CI history.
- Jest retry selection uses `-t <name>`; include file path in test ID if multiple names collide.

## Contributing
See `CONTRIBUTING.md` for dev setup and releasing.

## License
MIT – see `LICENSE`.
