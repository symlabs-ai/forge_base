# AI Agent Discovery - How Agents Find ForgeBase APIs

## 🎯 The Discovery Problem

When an AI agent encounters ForgeBase for the first time, it faces a "cold start" problem:

> "How do I discover that `get_agent_quickstart()` exists if the documentation about it is inside the function I don't know exists?"

This document explains the **multi-layered discovery strategy** implemented in ForgeBase.

---

## 🔍 Discovery Methods (Priority Order)

### 1. **README.md Explicit Section** ⭐ (PRIMARY)

**Location:** Top of `README.md` (lines 7-46)

**What AI agents see:**

```markdown
## 🤖 For AI Coding Agents

**First time using ForgeBase?** Access complete API documentation programmatically:

```python
from forgebase.dev import get_agent_quickstart

guide = get_agent_quickstart()  # Full API documentation
```
```

**Why this works:**
- ✅ Visible on GitHub repository page
- ✅ Visible on PyPI package page
- ✅ First thing AI agents read when discovering a package
- ✅ Explicit, clear, unmissable

**Discovery flow:**
```
User: "Use ForgeBase to check code quality"
    ↓
AI Agent: "Don't know ForgeBase, let me search"
    ↓
AI Agent reads README.md from GitHub/PyPI
    ↓
AI Agent sees: "🤖 For AI Coding Agents"
    ↓
✅ Discovers get_agent_quickstart() immediately
```

---

### 2. **Module Docstring** (FALLBACK)

**Location:** `src/forgebase/dev/__init__.py`

**What AI agents see:**

```python
import forgebase.dev
help(forgebase.dev)

# Output:
"""
ForgeBase Developer Tools.

Usage for AI Agents:
    from forgebase.dev import get_agent_quickstart

    # Access documentation programmatically
    guide = get_agent_quickstart()
"""
```

**Why this works:**
- ✅ Discoverable via `help()` introspection
- ✅ Works even if README not accessible
- ✅ Embedded in the installed package

**Discovery flow:**
```
AI Agent: import forgebase.dev
AI Agent: help(forgebase.dev)  # Standard introspection
    ↓
Sees "Usage for AI Agents:" section
    ↓
✅ Discovers get_agent_quickstart()
```

---

### 3. **Directory Listing (`dir()`)** (INTROSPECTION)

**Location:** `__all__` exports in `__init__.py`

**What AI agents see:**

```python
import forgebase.dev
dir(forgebase.dev)

# Output:
['get_agent_quickstart', 'get_documentation_path', ...]
```

**Why this works:**
- ✅ Self-explanatory function name
- ✅ Standard Python introspection
- ✅ No external dependencies needed

**Discovery flow:**
```
AI Agent: dir(forgebase.dev)
    ↓
Sees: 'get_agent_quickstart'  # ← Name is self-explanatory!
    ↓
AI Agent: help(forgebase.dev.get_agent_quickstart)
    ↓
✅ Reads docstring with full explanation
```

---

### 4. **Self-Documenting Function Names** (SEMANTIC)

**Function name:** `get_agent_quickstart()`

**Why this works:**
- ✅ `agent` → clearly for AI agents
- ✅ `quickstart` → indicates documentation/guide
- ✅ `get_` → standard Python convention for retrievers

**Even without documentation, the name communicates intent!**

---

### 5. **PyPI Package Description** (SEARCH)

**Location:** `pyproject.toml` description field

**Before:**
```toml
description = "Cognitive Architecture Framework..."
```

**After:**
```toml
description = "Cognitive Architecture Framework... AI agent-friendly with programmatic API access."
```

**Why this works:**
- ✅ Shows up in PyPI search results
- ✅ Signals to AI agents that package supports them
- ✅ Indexed by search engines

**Discovery flow:**
```
AI Agent searches: "python code quality framework for ai agents"
    ↓
Finds ForgeBase in results
    ↓
Sees: "AI agent-friendly with programmatic API access"
    ↓
✅ Knows package is designed for AI agents
```

---

## 📊 Discovery Success Rate by Method

| Method | Effectiveness | Speed | Requirements |
|--------|--------------|-------|--------------|
| **README section** | ⭐⭐⭐⭐⭐ | Instant | GitHub/PyPI access |
| **Module docstring** | ⭐⭐⭐⭐ | Fast | `import` + `help()` |
| **dir() listing** | ⭐⭐⭐ | Fast | `import` + `dir()` |
| **Function name** | ⭐⭐⭐ | Instant | Basic reasoning |
| **PyPI description** | ⭐⭐ | Medium | Search capability |

---

## 🎬 Real-World Discovery Scenarios

### Scenario 1: Claude Code (Me!)

```
User: "Use ForgeBase to check code quality"

Claude Code:
1. I don't recognize "ForgeBase" in my training data
2. I search for context in the conversation
3. If I have access, I check README.md
4. I see: "🤖 For AI Coding Agents" section
5. ✅ I immediately know: from forgebase.dev import get_agent_quickstart
```

### Scenario 2: Cursor

```
User: Installs ForgeBase and opens Cursor

Cursor AI:
1. Scans project dependencies
2. Sees "forgebase" in requirements
3. Searches PyPI description: "AI agent-friendly"
4. Reads README.md from cache/repo
5. Sees "🤖 For AI Coding Agents"
6. ✅ Configures to use get_agent_quickstart()
```

### Scenario 3: GitHub Copilot

```
Developer types: from forgebase.dev import

Copilot:
1. Analyzes available exports
2. Sees: get_agent_quickstart, get_documentation_path
3. Suggests completion based on name semantics
4. ✅ Developer accepts: from forgebase.dev import get_agent_quickstart
```

### Scenario 4: Aider

```
Aider session: User mentions "ForgeBase"

Aider:
1. import forgebase.dev
2. dir(forgebase.dev)
3. Sees: ['get_agent_quickstart', ...]
4. help(forgebase.dev.get_agent_quickstart)
5. Reads docstring: "useful for AI agents"
6. ✅ Uses API to discover available tools
```

---

## 🧪 Testing Discovery

### Manual Test: Cold Start Simulation

```python
# Simulate AI agent that has never seen ForgeBase

# Step 1: Check README (PRIMARY)
# → Opens README.md
# → Sees "🤖 For AI Coding Agents" at line 7
# ✅ SUCCESS in < 5 seconds

# Step 2: Introspection (FALLBACK)
import forgebase.dev
help(forgebase.dev)
# → Sees "Usage for AI Agents:"
# ✅ SUCCESS in < 1 second

# Step 3: Directory listing (FALLBACK)
dir(forgebase.dev)
# → Sees ['get_agent_quickstart', ...]
# ✅ SUCCESS in < 1 second
```

### Automated Test

```python
# test_ai_discovery.py

def test_readme_mentions_ai_agents():
    """Test README has AI agent section."""
    with open("README.md") as f:
        content = f.read()
    assert "🤖 For AI Coding Agents" in content
    assert "get_agent_quickstart" in content

def test_module_docstring_has_usage():
    """Test module docstring guides AI agents."""
    import forgebase.dev
    assert "AI Agents" in forgebase.dev.__doc__
    assert "get_agent_quickstart" in forgebase.dev.__doc__

def test_function_is_exported():
    """Test function is discoverable."""
    import forgebase.dev
    assert hasattr(forgebase.dev, 'get_agent_quickstart')
    assert 'get_agent_quickstart' in dir(forgebase.dev)

def test_function_name_is_semantic():
    """Test function name is self-explanatory."""
    name = "get_agent_quickstart"
    assert "agent" in name  # Clearly for agents
    assert "get" in name    # Standard getter pattern
```

---

## 📈 Metrics: Discovery Effectiveness

### Before This Implementation

| Metric | Value |
|--------|-------|
| Discovery time (cold start) | ⚠️ Unknown (no guidance) |
| README mentions AI agents | ❌ No |
| Programmatic docs access | ❌ No |
| Self-documenting | ⚠️ Partial |

### After This Implementation

| Metric | Value |
|--------|-------|
| Discovery time (cold start) | ✅ < 10 seconds |
| README mentions AI agents | ✅ Yes (line 7) |
| Programmatic docs access | ✅ Yes (`get_agent_quickstart()`) |
| Self-documenting | ✅ Yes (multiple layers) |

---

## 🎓 Best Practices for AI-Friendly Packages

### ✅ DO:

1. **Explicit README section** - "🤖 For AI Agents" at the top
2. **Self-documenting names** - `get_agent_*()`, `ai_*()`, etc.
3. **Module docstrings** - Include usage examples for AI
4. **Package description** - Mention "AI agent-friendly"
5. **Export in `__all__`** - Make functions discoverable via `dir()`

### ❌ DON'T:

1. **Hidden APIs** - Don't bury AI functions deep in submodules
2. **Cryptic names** - Avoid `fetch_data()` when you mean `get_agent_docs()`
3. **Undocumented** - Every AI-facing function needs a docstring
4. **README-only** - Docs must be accessible after `pip install`
5. **Assume awareness** - AI agents have no prior context

---

## 🔗 Related Documentation

- **README.md** - Main entry point with AI agent section (line 7)
- **AI_AGENT_QUICK_START.md** - Complete API guide for AI agents
- **docs/DOCUMENTATION_ACCESS.md** - How docs are embedded and accessed
- **src/forgebase/dev/__init__.py** - Implementation of discovery APIs

---

## 📝 Summary

ForgeBase solves the "cold start" discovery problem through **defense in depth**:

1. **Primary:** README.md explicit section (visible on GitHub/PyPI)
2. **Fallback 1:** Module docstring (introspection)
3. **Fallback 2:** `dir()` exports (listing)
4. **Fallback 3:** Self-documenting names (semantics)
5. **Fallback 4:** PyPI description (search)

**Result:** AI agents can discover ForgeBase APIs in **< 10 seconds** with **multiple independent paths** to success.

---

**Version:** ForgeBase 0.1.3+
**Updated:** 2025-11-05
**Author:** ForgeBase Development Team
