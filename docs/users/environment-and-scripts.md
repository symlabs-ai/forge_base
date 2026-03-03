# Development Environment and Useful Scripts

This document describes how to set up the local ForgeBase environment, use the utility scripts, and integrate automatic quality checks with pre-commit and lint.

> Important repository rules: do not write anything to the root, do not push, create tags, or change version without explicit user request. The source of truth for version is `VERSION.MD`.

## Requirements

- Python 3.12 (recommended)
- Git
- pip (already included in venv when using Python 3.12)

Check the version:

```bash
python3.12 -V
```

## Quick Environment Setup

Create the `.venv` virtual environment with Python 3.12:

```bash
python3.12 -m venv .venv
```

Activate the virtual environment:

- Linux/macOS: `source .venv/bin/activate`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Windows (cmd): `.venv\Scripts\activate.bat`

Update basic tools and install development dependencies (linter + hooks):

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r scripts/dev-requirements.txt
```

Optional: install development extras (pytest, mypy, black, etc.) defined in `setup.py`:

```bash
pip install -e .[dev]
```

## Lint and Style (Ruff)

- Configuration: `scripts/ruff.toml`
- Check command:

```bash
bash scripts/lint.sh
```

- Apply automatic fixes when possible:

```bash
bash scripts/lint.sh --fix
```

Main active rules: pycodestyle (E), pyflakes (F), isort (I), bugbear (B), pyupgrade (UP), comprehensions (C4), simplify (SIM), return (RET), naming (N). Some rules are ignored for formatting compatibility (E203, E266, E501).

## Pre-commit Hooks

Hook configuration: `scripts/pre-commit-config.yaml`

Installation (with venv activated):

```bash
bash scripts/install_precommit.sh
```

Run on all files (baseline):

```bash
pre-commit run --config scripts/pre-commit-config.yaml --all-files
```

About the configured hooks:
- `pre-commit-hooks`: trailing whitespace, end-of-file, large files, YAML
- `ruff-pre-commit`: linter + auto-fix using `scripts/ruff.toml`

If you don't use Bash shell on Windows, you can install without the script:

```powershell
.venv\Scripts\pre-commit.exe install --config scripts/pre-commit-config.yaml
.venv\Scripts\pre-commit.exe run --config scripts/pre-commit-config.yaml --all-files
```

## Tests

Install the dev extras, if you haven't already:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest -q
```

With coverage:

```bash
pytest --cov=src/forge_base --cov-report=term-missing
```

Note: some SQL infrastructure tests are conditional (they only run if `sqlalchemy` is installed).

## Available Scripts

- `scripts/lint.sh`
  - Check (`bash scripts/lint.sh`) or fix (`bash scripts/lint.sh --fix`) with Ruff.
- `scripts/ruff.toml`
  - Central configuration for lint and import ordering.
- `scripts/dev-requirements.txt`
  - Minimal development dependencies (ruff, pre-commit).
- `scripts/pre-commit-config.yaml`
  - Pre-commit hooks (without writing config to the root).
- `scripts/install_precommit.sh`
  - Installs and sets up pre-commit using the configuration in `scripts/` and runs baseline.

## Troubleshooting

- `pip` not found in venv
  - Make sure the venv was created with Python 3.12 and run `python -m ensurepip --upgrade` inside the venv.
- Hooks fail by modifying files
  - This is expected during baseline. Commit the fixes and run again if needed.
- `ruff` flags empty methods in base classes (B027)
  - Make them `@abstractmethod` or add a minimal implementation. Alternatively, adjust the rule in `scripts/ruff.toml`.

## Important Notices

- Do not write to the repository root, do not push remotely, create tags, or change version without explicit request.
- The current version and history are in `VERSION.MD`.
