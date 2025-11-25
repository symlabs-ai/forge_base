# ForgeBase Installation Guide

Complete guide for installing ForgeBase in different scenarios.

## 🎯 Quick Start

### For Production Use

```bash
# Install latest version from main
pip install git+https://github.com/symlabs-ai/forgebase.git
```

### For Development

```bash
# Clone and install in editable mode
git clone https://github.com/symlabs-ai/forgebase.git
cd forgebase
pip install -e ".[dev]"
```

### For AI Agents

```bash
# Install with all APIs (latest)
pip install git+https://github.com/symlabs-ai/forgebase.git

# Verify installation
python -c "from forgebase.dev.api import QualityChecker; print('✅ Ready!')"
```

## 📦 Installation Methods

### Method 1: Direct from GitHub

**Latest version from main branch:**
```bash
pip install git+https://github.com/symlabs-ai/forgebase.git
```

**Specific branch (optional):**
```bash
pip install git+https://github.com/symlabs-ai/forgebase.git@develop
```

**Specific commit (optional, pinned):**
```bash
pip install git+https://github.com/symlabs-ai/forgebase.git@5632a91
```

### Method 2: With Optional Dependencies

**Development tools (pytest, ruff, mypy, etc.) – latest:**
```bash
pip install "forgebase[dev] @ git+https://github.com/symlabs-ai/forgebase.git"
```

**SQL support (SQLAlchemy) – latest:**
```bash
pip install "forgebase[sql] @ git+https://github.com/symlabs-ai/forgebase.git"
```

**Everything – latest:**
```bash
pip install "forgebase[all] @ git+https://github.com/symlabs-ai/forgebase.git"
```

### Method 3: Editable Installation (Development)

**Clone and install:**
```bash
git clone https://github.com/symlabs-ai/forgebase.git
cd forgebase
pip install -e ".[dev]"
```

**Benefits:**
- Changes to source code are immediately available
- No need to reinstall after modifications
- Perfect for contributing or customization

## 📄 Dependency Management

### requirements.txt

```txt
# requirements.txt

# Core package (production, latest)
forgebase @ git+https://github.com/symlabs-ai/forgebase.git

# Or with dev dependencies (latest)
forgebase[dev] @ git+https://github.com/symlabs-ai/forgebase.git

# Or with all optional dependencies (latest)
forgebase[all] @ git+https://github.com/symlabs-ai/forgebase.git
```

Install:
```bash
pip install -r requirements.txt
```

### pyproject.toml

```toml
[project]
name = "my-project"
dependencies = [
    "forgebase @ git+https://github.com/symlabs-ai/forgebase.git"
]

[project.optional-dependencies]
dev = [
    "forgebase[dev] @ git+https://github.com/symlabs-ai/forgebase.git"
]
```

Install:
```bash
pip install -e .              # Core dependencies
pip install -e ".[dev]"       # With dev dependencies
```

### Poetry

```toml
[tool.poetry.dependencies]
python = "^3.11"
forgebase = {git = "https://github.com/symlabs-ai/forgebase.git"}

[tool.poetry.group.dev.dependencies]
# ForgeBase dev dependencies are included in the package
```

Install:
```bash
poetry install
```

### Pipenv

```bash
# Add to Pipfile
pipenv install "forgebase @ git+https://github.com/symlabs-ai/forgebase.git"

# Or directly via command
pipenv install git+https://github.com/symlabs-ai/forgebase.git#egg=forgebase
```

## ✅ Verification

### Check Installation

```bash
# Verify package is installed
pip show forgebase

# Check importability
python -c "import forgebase; print('✅ ForgeBase installed')"

# Check version (if available)
python -c "import forgebase; print(getattr(forgebase, '__version__', 'dev'))"
```

### Test Core Functionality

```bash
# Test domain layer
python -c "from forgebase.domain.entity_base import EntityBase; print('✅ Domain layer OK')"

# Test application layer
python -c "from forgebase.application.usecase_base import UseCaseBase; print('✅ Application layer OK')"

# Test infrastructure layer
python -c "from forgebase.infrastructure.repository.repository_base import RepositoryBase; print('✅ Infrastructure layer OK')"
```

### Test Dev APIs (AI Agents)

```bash
# Test quality checker
python -c "from forgebase.dev.api import QualityChecker; print('✅ QualityChecker available')"

# Test scaffold generator
python -c "from forgebase.dev.api import ScaffoldGenerator; print('✅ ScaffoldGenerator available')"

# Test component discovery
python -c "from forgebase.dev.api import ComponentDiscovery; print('✅ ComponentDiscovery available')"

# Test test runner
python -c "from forgebase.dev.api import TestRunner; print('✅ TestRunner available')"
```

## 🔄 Updating

### Update to Latest Version

```bash
# Update to latest main
pip install --upgrade git+https://github.com/symlabs-ai/forgebase.git

# Update to specific tagged version (optional)
pip install --upgrade git+https://github.com/symlabs-ai/forgebase.git@vX.Y.Z
```

### Force Reinstall (latest)

```bash
pip install --force-reinstall git+https://github.com/symlabs-ai/forgebase.git
```

## 🗑️ Uninstallation

```bash
pip uninstall forgebase
```

## 🐳 Docker Installation

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install ForgeBase (latest)
RUN pip install git+https://github.com/symlabs-ai/forgebase.git

# Copy your application
COPY . .

# Install your dependencies
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  app:
    build: .
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
```

## 🌍 Virtual Environments

### venv (Standard Library)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install ForgeBase (latest)
pip install git+https://github.com/symlabs-ai/forgebase.git
```

### conda

```bash
# Create conda environment
conda create -n forgebase python=3.11

# Activate
conda activate forgebase

# Install ForgeBase (latest)
pip install git+https://github.com/symlabs-ai/forgebase.git
```

## ⚙️ Configuration After Installation

### For AI Agents

After installing, agents should:

1. **Read instructions:**
   ```bash
   # Clone docs if needed
   git clone https://github.com/symlabs-ai/forgebase.git /tmp/forgebase
   cat /tmp/forgebase/AI_AGENT_QUICK_START.md
   ```

2. **Import APIs:**
   ```python
   from forgebase.dev.api import (
       QualityChecker,
       ScaffoldGenerator,
       ComponentDiscovery,
       TestRunner
   )
   ```

3. **Test functionality:**
   ```python
   checker = QualityChecker()
   result = checker.run_ruff(["."])
   print(f"✅ Quality check: {result.passed}")
   ```

### For Developers

After installing, developers should:

1. **Check available commands:**
   ```bash
   # If installed in dev mode
   python scripts/devtool.py --help
   ```

2. **Run tests:**
   ```bash
   pytest tests/
   ```

3. **Check code quality:**
   ```bash
   ruff check src/
   mypy src/
   ```

## 🚨 Troubleshooting

### Issue: "No module named 'forgebase'"

**Solution:**
```bash
# Verify installation
pip list | grep forgebase

# If not found, reinstall latest
pip install git+https://github.com/symlabs-ai/forgebase.git
```

### Issue: "git: command not found"

**Solution:**
```bash
# Install git first
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/
```

### Issue: Import errors for dev APIs

**Solution:**
```bash
# Install with dev dependencies (latest)
pip install "forgebase[dev] @ git+https://github.com/symlabs-ai/forgebase.git"
```

### Issue: Permission denied

**Solution:**
```bash
# Use --user flag with latest
pip install --user git+https://github.com/symlabs-ai/forgebase.git

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install git+https://github.com/symlabs-ai/forgebase.git
```

### Issue: SSL certificate errors

**Solution:**
```bash
# Temporary workaround (not recommended for production)
pip install --trusted-host github.com git+https://github.com/symlabs-ai/forgebase.git

# Better: Fix SSL certificates
pip install --upgrade certifi
```

## 📊 Installation Summary

| Scenario | Command |
|----------|---------|
| **Production** | `pip install git+https://github.com/symlabs-ai/forgebase.git` |
| **Development** | `git clone ... && pip install -e ".[dev]"` |
| **AI Agents** | `pip install git+https://github.com/symlabs-ai/forgebase.git` |
| **With SQL** | `pip install "forgebase[sql] @ git+..."` |
| **Everything** | `pip install "forgebase[all] @ git+..."` |
| **Latest** | `pip install git+https://github.com/symlabs-ai/forgebase.git` |
| **Update** | `pip install --upgrade git+...` |

## 📚 Next Steps

After installation:

1. **For Users**: Read `README.md`
2. **For AI Agents**: Read `AI_AGENT_QUICK_START.md`
3. **For Developers**: Read `CONTRIBUTING.md` (if available)
4. **For Examples**: Check `examples/` directory

## 🔗 Resources

- **Repository**: https://github.com/symlabs-ai/forgebase
- **Documentation**: https://github.com/symlabs-ai/forgebase/blob/main/README.md
- **AI Agent Guide**: https://github.com/symlabs-ai/forgebase/blob/main/AI_AGENT_QUICK_START.md
- **Changelog**: https://github.com/symlabs-ai/forgebase/blob/main/CHANGELOG.md

---

**Version**: 0.1.4
**Last Updated**: 2025-11-04
**Python**: 3.11+
