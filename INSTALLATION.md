# ForgeBase Installation

## Quick Installation

```bash
pip install git+https://github.com/symlabs-ai/forge_base.git
```

## Development Installation

```bash
git clone https://github.com/symlabs-ai/forge_base.git
cd forge_base
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Full Documentation

- **[Quick Start](docs/users/quick-start.md)** — Installation, first use, and examples
- **[Environment and Scripts](docs/users/environment-and-scripts.md)** — venv setup, lint (Ruff), pre-commit hooks
