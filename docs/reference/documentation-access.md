# Documentation Access in ForgeBase

## How Documentation is Distributed

### Original Problem

When you install ForgeBase via pip:
```bash
pip install git+https://github.com/symlabs-ai/forge_base.git
```

By default, only Python code is included, **NOT** markdown files from the project root.

### Solution Implemented

ForgeBase now embeds essential documentation **inside the package** for programmatic access.

## Structure

```
forge_base/
├── AI_AGENT_QUICK_START.md         # ← Original file at root
├── README.md
├── MANIFEST.in                      # ← Created: includes docs in sdist
│
└── src/forge_base/
    ├── _docs/                       # ← New: docs embedded in the package
    │   ├── __init__.py
    │   ├── AI_AGENT_QUICK_START.md  # ← Copy for distribution
    │   └── README.md                # ← Copy for distribution
    │
    └── dev/
        └── __init__.py              # ← Updated: access functions
```

## Programmatic Access API

### 1. Get the AI Agent Quick Start Guide

```python
from forge_base.dev import get_agent_quickstart

# Returns the full guide content
guide = get_agent_quickstart()

print(guide[:200])
# Output: # ForgeBase AI Agent Quick Start Guide...

# Use in AI agents to understand available APIs
if "QualityChecker" in guide:
    print("✅ Quality checking API available")
```

**Usage by AI Agents:**
```python
# Claude Code / Cursor / Aider can do:
from forge_base.dev import get_agent_quickstart

guide = get_agent_quickstart()

# Parse the guide to understand available APIs
# Extract examples, method signatures, etc.
```

### 2. Get the Documentation Path

```python
from forge_base.dev import get_documentation_path

docs_path = get_documentation_path()
print(docs_path)
# Output: /path/to/site-packages/forge_base/docs (if installed)
#         /path/to/project/docs (if dev mode)
```

## Packaging Configuration

### 1. MANIFEST.in (Project root)

```ini
# Include documentation files in source distribution
include README.md
include CHANGELOG.md
include CONTRIBUTING.md
include AI_AGENT_QUICK_START.md
include AGENT_ECOSYSTEM.md
include LICENSE

# Include all documentation
recursive-include docs *.md
recursive-include docs *.rst
recursive-include docs *.txt

# Include examples
recursive-include examples *.py
recursive-include examples *.yaml
recursive-include examples *.json
```

**Purpose:** Files included in the **source distribution** (`.tar.gz`)

### 2. pyproject.toml

```toml
[tool.setuptools.package-data]
forge_base = [
    "_docs/*.md",     # Embedded documentation
]
```

**Purpose:** Files included in the **wheel** (`.whl`) and **pip install**

## How It Works

### During Build

1. **MANIFEST.in** ensures that markdown files go into the `.tar.gz`
2. **package-data** ensures that `_docs/*.md` go into the `.whl`
3. Both are needed for complete coverage

### During Installation

When a user runs `pip install forge_base`:

```python
# In site-packages/forge_base/_docs/
AI_AGENT_QUICK_START.md  # ✅ Included
README.md                 # ✅ Included
```

### During Import

```python
from forge_base.dev import get_agent_quickstart

# The function tries (in order):
# 1. Read from forge_base._docs/ (package data) - pip install
# 2. Read from project root - development mode
# 3. Return a fallback with a link to GitHub
```

## Comparison: Before vs After

| Scenario | Before | After |
|----------|--------|-------|
| **pip install git+...** | No docs | Embedded docs |
| **Local development** | Docs available | Docs available |
| **Programmatic access** | Not available | `get_agent_quickstart()` |
| **AI Agents** | Need to download separately | Direct access via API |
| **Package size** | ~500KB | ~520KB (+20KB) |

## Benefits

### For AI Coding Agents

```python
# AI agent can discover APIs without internet
from forge_base.dev import get_agent_quickstart

guide = get_agent_quickstart()

# Parse guide to understand:
# - Which APIs exist
# - How to use them
# - Error codes and how to fix them
# - Returned data structures
```

### For Users

```python
# Documentation always available offline
import forge_base.dev
guide = forge_base.dev.get_agent_quickstart()

# No need to open a browser or GitHub
print(guide)
```

### For CI/CD

```bash
# In air-gapped environments
pip install forge_base-0.1.4.whl

# Documentation still accessible programmatically
python -c "from forge_base.dev import get_agent_quickstart; print(get_agent_quickstart())"
```

## Tests

### Manual Test

```bash
# 1. Build the package
python -m build

# 2. Install in clean environment
pip install dist/forge_base-*.whl

# 3. Test documentation access
python -c "from forge_base.dev import get_agent_quickstart; print(len(get_agent_quickstart()))"
# Expected: > 8000 (characters)
```

### Automated Test

```python
# tests/test_documentation_access.py
def test_agent_quickstart_embedded():
    """Test AI Agent Quick Start is accessible."""
    from forge_base.dev import get_agent_quickstart

    guide = get_agent_quickstart()

    assert len(guide) > 100
    assert "ForgeBase AI Agent" in guide
    assert "QualityChecker" in guide
```

## Maintenance

### Updating Documentation

When updating `AI_AGENT_QUICK_START.md`:

```bash
# 1. Edit the file at root
vim AI_AGENT_QUICK_START.md

# 2. Copy to package
cp AI_AGENT_QUICK_START.md src/forge_base/_docs/

# 3. Commit both
git add AI_AGENT_QUICK_START.md src/forge_base/_docs/AI_AGENT_QUICK_START.md
git commit -m "docs: Update AI Agent Quick Start"
```

**Automation (recommended):**

Create `scripts/sync_docs.sh`:
```bash
#!/bin/bash
# Sync root docs to embedded _docs

cp AI_AGENT_QUICK_START.md src/forge_base/_docs/
cp README.md src/forge_base/_docs/

echo "✅ Docs synced"
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: sync-docs
        name: Sync embedded docs
        entry: scripts/sync_docs.sh
        language: script
        files: '(AI_AGENT_QUICK_START\.md|README\.md)'
```

## Troubleshooting

### Documentation not found after installation

**Symptom:**
```python
from forge_base.dev import get_agent_quickstart
guide = get_agent_quickstart()
# Returns: "Documentation not found in package..."
```

**Possible causes:**
1. Package was built before adding MANIFEST.in
2. package-data is not in pyproject.toml
3. `_docs/` folder is empty

**Solution:**
```bash
# Rebuild package
rm -rf dist/ build/ *.egg-info
python -m build

# Verify contents
unzip -l dist/forge_base-*.whl | grep _docs
# Should show: forge_base/_docs/AI_AGENT_QUICK_START.md
```

### Docs out of sync

**Symptom:** Docs at root differ from `_docs/`

**Solution:**
```bash
# Use sync script
./scripts/sync_docs.sh

# Or manually
cp AI_AGENT_QUICK_START.md src/forge_base/_docs/
```

## References

- **Python Packaging Guide:** https://packaging.python.org/
- **setuptools package_data:** https://setuptools.pypa.io/en/latest/userguide/datafiles.html
- **MANIFEST.in format:** https://packaging.python.org/guides/using-manifest-in/
- **importlib.resources:** https://docs.python.org/3/library/importlib.resources.html

## Best Practices

### DO:

1. **Keep docs synced** - Automate with pre-commit hooks
2. **Test after build** - Verify docs are included
3. **Use API access** - Programmatic > manual file reading
4. **Keep docs small** - Only essential files embedded

### DON'T:

1. **Don't embed large files** - Images, videos → keep on GitHub
2. **Don't duplicate everything** - Only critical docs
3. **Don't forget to sync** - Root and `_docs/` must match
4. **Don't hardcode paths** - Use `get_agent_quickstart()` API

---

**Version:** ForgeBase 0.1.4+
**Updated:** 2025-11-05
**Author:** ForgeBase Development Team
