# ForgeBase Installation Guide

Complete guide for installing ForgeBase in different scenarios.

## 🎯 Quick Start

### For Production Use

```bash
# Install specific version (recommended)
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

### For Development

```bash
# Clone and install in editable mode
git clone https://github.com/palhanobrazil/forgebase.git
cd forgebase
pip install -e ".[dev]"
```

### For AI Agents

```bash
# Install with all APIs
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Verify installation
python -c "from forgebase.dev.api import QualityChecker; print('✅ Ready!')"
```

## 📦 Installation Methods

### Method 1: Direct from GitHub

**Latest version from main branch:**
```bash
pip install git+https://github.com/palhanobrazil/forgebase.git
```

**Specific version (recommended for production):**
```bash
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

**Specific branch:**
```bash
pip install git+https://github.com/palhanobrazil/forgebase.git@develop
```

**Specific commit:**
```bash
pip install git+https://github.com/palhanobrazil/forgebase.git@5632a91
```

### Method 2: With Optional Dependencies

**Development tools (pytest, ruff, mypy, etc.):**
```bash
pip install "forgebase[dev] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
```

**SQL support (SQLAlchemy):**
```bash
pip install "forgebase[sql] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
```

**Everything:**
```bash
pip install "forgebase[all] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
```

### Method 3: Editable Installation (Development)

**Clone and install:**
```bash
git clone https://github.com/palhanobrazil/forgebase.git
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

# Core package (production)
forgebase @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Or with dev dependencies
forgebase[dev] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Or with all optional dependencies
forgebase[all] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
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
    "forgebase @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
]

[project.optional-dependencies]
dev = [
    "forgebase[dev] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
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
forgebase = {git = "https://github.com/palhanobrazil/forgebase.git", tag = "v0.1.3"}

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
pipenv install "forgebase @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"

# Or directly via command
pipenv install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3#egg=forgebase
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
pip install --upgrade git+https://github.com/palhanobrazil/forgebase.git

# Update to specific new version
pip install --upgrade git+https://github.com/palhanobrazil/forgebase.git@v0.1.4
```

### Force Reinstall

```bash
pip install --force-reinstall git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
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

# Install ForgeBase
RUN pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

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

# Install ForgeBase
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

### conda

```bash
# Create conda environment
conda create -n forgebase python=3.11

# Activate
conda activate forgebase

# Install ForgeBase
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

## ⚙️ Configuration After Installation

### For AI Agents

After installing, agents should:

1. **Read instructions:**
   ```bash
   # Clone docs if needed
   git clone https://github.com/palhanobrazil/forgebase.git /tmp/forgebase
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

# If not found, reinstall
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
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
# Install with dev dependencies
pip install "forgebase[dev] @ git+https://github.com/palhanobrazil/forgebase.git@v0.1.3"
```

### Issue: Permission denied

**Solution:**
```bash
# Use --user flag
pip install --user git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Or use virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3
```

### Issue: SSL certificate errors

**Solution:**
```bash
# Temporary workaround (not recommended for production)
pip install --trusted-host github.com git+https://github.com/palhanobrazil/forgebase.git@v0.1.3

# Better: Fix SSL certificates
pip install --upgrade certifi
```

## 📊 Installation Summary

| Scenario | Command |
|----------|---------|
| **Production** | `pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3` |
| **Development** | `git clone ... && pip install -e ".[dev]"` |
| **AI Agents** | `pip install git+https://github.com/palhanobrazil/forgebase.git@v0.1.3` |
| **With SQL** | `pip install "forgebase[sql] @ git+..."` |
| **Everything** | `pip install "forgebase[all] @ git+..."` |
| **Latest** | `pip install git+https://github.com/palhanobrazil/forgebase.git` |
| **Update** | `pip install --upgrade git+...` |

## 📚 Next Steps

After installation:

1. **For Users**: Read `README.md`
2. **For AI Agents**: Read `AI_AGENT_QUICK_START.md`
3. **For Developers**: Read `CONTRIBUTING.md` (if available)
4. **For Examples**: Check `examples/` directory

## 🔗 Resources

- **Repository**: https://github.com/palhanobrazil/forgebase
- **Documentation**: https://github.com/palhanobrazil/forgebase/blob/main/README.md
- **AI Agent Guide**: https://github.com/palhanobrazil/forgebase/blob/main/AI_AGENT_QUICK_START.md
- **Changelog**: https://github.com/palhanobrazil/forgebase/blob/main/CHANGELOG.md

---

**Version**: 0.1.3
**Last Updated**: 2025-11-04
**Python**: 3.11+
