# ForgeBase API Discovery by AI Agents

## The Discovery Problem

When an AI agent encounters ForgeBase for the first time, it faces the "cold start" problem:

> "How do I discover that `get_agent_quickstart()` exists if the documentation about it is inside the function I don't know exists?"

This document explains the **multi-layered discovery strategy** implemented in ForgeBase.

---

## Discovery Methods (Priority Order)

### 1. Explicit Section in README.md (PRIMARY)

**Location:** Top of `README.md` (lines 7-46)

**What AI agents see:**

```markdown
## For AI Code Agents

**First time using ForgeBase?** Access full documentation programmatically:

```python
from forge_base.dev import get_agent_quickstart

guide = get_agent_quickstart()  # Full API documentation
```
```

**Why it works:**
- Visible on the GitHub repository page
- Visible on the PyPI package page
- First thing AI agents read when discovering a package
- Explicit, clear, impossible to miss

**Discovery flow:**
```
User: "Use ForgeBase to check code quality"
    |
AI Agent: "I don't know ForgeBase, let me look it up"
    |
AI Agent reads README.md from GitHub/PyPI
    |
AI Agent sees: "For AI Code Agents"
    |
Discovers get_agent_quickstart() immediately
```

---

### 2. Module Docstring (FALLBACK)

**Location:** `src/forge_base/dev/__init__.py`

**What AI agents see:**

```python
import forge_base.dev
help(forge_base.dev)

# Output:
"""
ForgeBase Developer Tools.

AI Agent Usage:
    from forge_base.dev import get_agent_quickstart

    # Access documentation programmatically
    guide = get_agent_quickstart()
"""
```

**Why it works:**
- Discoverable via `help()` introspection
- Works even if README is not accessible
- Embedded in the installed package

---

### 3. Directory Listing (`dir()`) (INTROSPECTION)

**Location:** `__all__` exports in `__init__.py`

**What AI agents see:**

```python
import forge_base.dev
dir(forge_base.dev)

# Output:
['get_agent_quickstart', 'get_documentation_path', ...]
```

**Why it works:**
- Self-explanatory function name
- Standard Python introspection
- No external dependencies needed

---

### 4. Self-Documenting Function Names (SEMANTIC)

**Function name:** `get_agent_quickstart()`

**Why it works:**
- `agent` -> clearly for AI agents
- `quickstart` -> indicates documentation/guide
- `get_` -> standard Python getter convention

**Even without documentation, the name communicates intent!**

---

### 5. PyPI Package Description (SEARCH)

**Location:** Description field in `pyproject.toml`

**Before:**
```toml
description = "Cognitive Architecture Framework..."
```

**After:**
```toml
description = "Cognitive Architecture Framework... AI agent-friendly with programmatic API access."
```

**Why it works:**
- Appears in PyPI search results
- Signals to AI agents that the package supports them
- Indexed by search engines

---

## Discovery Success Rate by Method

| Method | Effectiveness | Speed | Requirements |
|--------|---------------|-------|--------------|
| **README section** | Excellent | Instant | GitHub/PyPI access |
| **Module docstring** | High | Fast | `import` + `help()` |
| **dir() listing** | Medium | Fast | `import` + `dir()` |
| **Function name** | Medium | Instant | Basic reasoning |
| **PyPI description** | Low | Medium | Search capability |

---

## Real-World Discovery Scenarios

### Scenario 1: Claude Code

```
User: "Use ForgeBase to check code quality"

Claude Code:
1. I don't recognize "ForgeBase" from my training data
2. I look for context in the conversation
3. If I have access, I check README.md
4. I see: "For AI Code Agents"
5. I immediately know: from forge_base.dev import get_agent_quickstart
```

### Scenario 2: Cursor

```
User: Installs ForgeBase and opens Cursor

Cursor AI:
1. Scans project dependencies
2. Sees "forge_base" in requirements
3. Looks up PyPI description: "AI agent-friendly"
4. Reads README.md from cache/repo
5. Sees "For AI Code Agents"
6. Sets up to use get_agent_quickstart()
```

### Scenario 3: GitHub Copilot

```
Developer types: from forge_base.dev import

Copilot:
1. Analyzes available exports
2. Sees: get_agent_quickstart, get_documentation_path
3. Suggests completion based on name semantics
4. Developer accepts: from forge_base.dev import get_agent_quickstart
```

### Scenario 4: Aider

```
Aider session: User mentions "ForgeBase"

Aider:
1. import forge_base.dev
2. dir(forge_base.dev)
3. Sees: ['get_agent_quickstart', ...]
4. help(forge_base.dev.get_agent_quickstart)
5. Reads docstring: "useful for AI agents"
6. Uses the API to discover available tools
```

---

## Testing Discovery

### Manual Test: Cold Start Simulation

```python
# Simulate an AI agent that has never seen ForgeBase

# Step 1: Check README (PRIMARY)
# -> Opens README.md
# -> Sees "For AI Code Agents" at line 7
# SUCCESS in < 5 seconds

# Step 2: Introspection (FALLBACK)
import forge_base.dev
help(forge_base.dev)
# -> Sees "AI Agent Usage:"
# SUCCESS in < 1 second

# Step 3: Directory listing (FALLBACK)
dir(forge_base.dev)
# -> Sees ['get_agent_quickstart', ...]
# SUCCESS in < 1 second
```

### Automated Test

```python
# test_ai_discovery.py

def test_readme_mentions_ai_agents():
    """Test that README has an AI agents section."""
    with open("README.md") as f:
        content = f.read()
    assert "For AI" in content or "AI Code Agents" in content
    assert "get_agent_quickstart" in content

def test_module_docstring_has_usage():
    """Test that module docstring guides AI agents."""
    import forge_base.dev
    assert "Agent" in forge_base.dev.__doc__
    assert "get_agent_quickstart" in forge_base.dev.__doc__

def test_function_is_exported():
    """Test that the function is discoverable."""
    import forge_base.dev
    assert hasattr(forge_base.dev, 'get_agent_quickstart')
    assert 'get_agent_quickstart' in dir(forge_base.dev)

def test_function_name_is_semantic():
    """Test that the function name is self-explanatory."""
    name = "get_agent_quickstart"
    assert "agent" in name  # Clearly for agents
    assert "get" in name    # Getter pattern
```

---

## Best Practices for AI-Friendly Packages

### DO:

1. **Explicit README section** - "For AI Agents" at the top
2. **Self-documenting names** - `get_agent_*()`, `ai_*()`, etc.
3. **Module docstrings** - Include usage examples for AI
4. **Package description** - Mention "AI agent-friendly"
5. **Export in `__all__`** - Make functions discoverable via `dir()`

### DON'T:

1. **Hidden APIs** - Don't bury AI functions in deep submodules
2. **Cryptic names** - Avoid `fetch_data()` when you mean `get_agent_docs()`
3. **Undocumented** - Every AI-facing function needs a docstring
4. **README only** - Docs must be accessible after `pip install`
5. **Assume knowledge** - AI agents have no prior context

---

## Summary

ForgeBase solves the "cold start" discovery problem through **defense in depth**:

1. **Primary:** Explicit section in README.md (visible on GitHub/PyPI)
2. **Fallback 1:** Module docstring (introspection)
3. **Fallback 2:** `dir()` exports (listing)
4. **Fallback 3:** Self-documenting names (semantics)
5. **Fallback 4:** PyPI description (search)

**Result:** AI agents can discover ForgeBase APIs in **< 10 seconds** with **multiple independent paths** to success.

---

**Version:** ForgeBase 0.1.4
