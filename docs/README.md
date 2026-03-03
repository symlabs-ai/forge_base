# ForgeBase Documentation

> "To forge is to transform thought into structure."

This documentation is organized into three main sections, depending on your usage profile.

---

## Quick Navigation

### For Human Users
Developers who want to use ForgeBase in their projects.

| Document | Description |
|----------|-------------|
| [ForgeBase Rules](users/forgebase-rules.md) | **Complete guide to rules and practices** |
| [Quick Start](users/quick-start.md) | Installation and first use |
| [Recipes](users/recipes.md) | Patterns and practical examples |
| [Testing Guide](users/testing-guide.md) | How to write cognitive tests |
| [CLI First](users/cli-first.md) | CLI First development philosophy |
| [Environment and Scripts](users/environment-and-scripts.md) | Environment setup and tools |
| [Extending](users/extending-forgebase.md) | How to extend ForgeBase |
| [ForgePulse Quick Start](users/pulse_quick_start.md) | Native observability in 5 minutes |
| [ForgePulse Cookbook](users/pulse_cookbook.md) | Complete reference with recipes |

### For AI Agents
AI agents (Claude Code, Cursor, Aider, etc.) that interact with ForgeBase.

| Document | Description |
|----------|-------------|
| [Quick Start](ai-agents/quick-start.md) | Programmatic APIs for AI agents |
| [Complete Guide](ai-agents/complete-guide.md) | Full API reference |
| [Discovery](ai-agents/discovery.md) | How agents discover ForgeBase |
| [Ecosystem](ai-agents/ecosystem.md) | Integration with different agents |

### Technical Reference
Architecture documentation and design decisions.

| Document | Description |
|----------|-------------|
| [Architecture](reference/architecture.md) | Modular structure and principles |
| [ForgeProcess](reference/forge-process.md) | Complete cognitive cycle |
| [ForgeProcess Visual](reference/forge-process-visual.md) | Visual guide to the cycle |
| [Documentation Access](reference/documentation-access.md) | How docs are distributed |
| [Documentation Guide](reference/documentation_guide.md) | Docstring standards |

### Architectural Decision Records (ADRs)

| ADR | Decision |
|-----|----------|
| [001](adr/001-clean-architecture-choice.md) | Clean Architecture |
| [002](adr/002-hexagonal-ports-adapters.md) | Hexagonal (Ports & Adapters) |
| [003](adr/003-observability-first.md) | Observability First |
| [004](adr/004-cognitive-testing.md) | Cognitive Testing |
| [005](adr/005-dependency-injection.md) | Dependency Injection |
| [006](adr/006-forgeprocess-integration.md) | ForgeProcess Integration |
| [007](adr/007-opentelemetry-integration.md) | OpenTelemetry |

---

## Programmatic Access (AI Agents)

```python
from forge_base.dev import get_agent_quickstart

# Get the complete API guide for AI agents
guide = get_agent_quickstart()
print(guide)
```

---

## Version

- **ForgeBase**: v0.1.4
- **Documentation**: 2025-12
