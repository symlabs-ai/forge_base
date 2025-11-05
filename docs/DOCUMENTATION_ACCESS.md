# Documentation Access in ForgeBase

## 📦 Como a Documentação é Distribuída

### Problema Original

Quando você instala ForgeBase via pip:
```bash
pip install git+https://github.com/forgeframework/forgebase.git
```

Por padrão, apenas código Python é incluído, **NÃO** arquivos markdown na raiz do projeto.

### ✅ Solução Implementada

ForgeBase agora embute documentação essencial **dentro do package** para acesso programático.

## 🎯 Estrutura

```
forgebase/
├── AI_AGENT_QUICK_START.md         # ← Arquivo original na raiz
├── README.md
├── MANIFEST.in                      # ← Criado: inclui docs no sdist
│
└── src/forgebase/
    ├── _docs/                       # ← Novo: docs embutidos no package
    │   ├── __init__.py
    │   ├── AI_AGENT_QUICK_START.md  # ← Cópia para distribuição
    │   └── README.md                # ← Cópia para distribuição
    │
    └── dev/
        └── __init__.py              # ← Atualizado: funções de acesso
```

## 📚 API de Acesso Programático

### 1. Obter AI Agent Quick Start Guide

```python
from forgebase.dev import get_agent_quickstart

# Retorna o conteúdo completo do guia
guide = get_agent_quickstart()

print(guide[:200])
# Output: # ForgeBase AI Agent Quick Start Guide...

# Use em AI agents para entender APIs disponíveis
if "QualityChecker" in guide:
    print("✅ Quality checking API available")
```

**Uso por AI Agents:**
```python
# Claude Code / Cursor / Aider podem fazer:
from forgebase.dev import get_agent_quickstart

guide = get_agent_quickstart()

# Parse the guide to understand available APIs
# Extract examples, method signatures, etc.
```

### 2. Obter Caminho para Documentação

```python
from forgebase.dev import get_documentation_path

docs_path = get_documentation_path()
print(docs_path)
# Output: /path/to/site-packages/forgebase/docs (se instalado)
#         /path/to/project/docs (se dev mode)
```

## 🔧 Configuração de Packaging

### 1. MANIFEST.in (Raiz do projeto)

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

**Propósito:** Arquivos incluídos em **source distribution** (`.tar.gz`)

### 2. pyproject.toml

```toml
[tool.setuptools.package-data]
forgebase = [
    "_docs/*.md",     # Embedded documentation
]
```

**Propósito:** Arquivos incluídos em **wheel** (`.whl`) e **instalação via pip**

## 🚀 Como Funciona

### Durante o Build

1. **MANIFEST.in** garante que markdown files vão para o `.tar.gz`
2. **package-data** garante que `_docs/*.md` vão para o `.whl`
3. Ambos são necessários para cobertura completa

### Durante a Instalação

Quando usuário faz `pip install forgebase`:

```python
# Em site-packages/forgebase/_docs/
AI_AGENT_QUICK_START.md  # ✅ Incluído
README.md                 # ✅ Incluído
```

### Durante o Import

```python
from forgebase.dev import get_agent_quickstart

# Função tenta (em ordem):
# 1. Ler de forgebase._docs/ (package data) - pip install
# 2. Ler de raiz do projeto - development mode
# 3. Retornar fallback com link para GitHub
```

## 📊 Comparação: Antes vs Depois

| Cenário | Antes | Depois |
|---------|-------|--------|
| **pip install git+...** | ❌ Sem docs | ✅ Docs embutidos |
| **Desenvolvimento local** | ✅ Docs disponíveis | ✅ Docs disponíveis |
| **Acesso programático** | ❌ Não disponível | ✅ `get_agent_quickstart()` |
| **AI Agents** | ⚠️ Precisam baixar separado | ✅ Acesso direto via API |
| **Tamanho do package** | ~500KB | ~520KB (+20KB) |

## 🎯 Benefícios

### Para AI Coding Agents

```python
# AI agent pode descobrir APIs sem internet
from forgebase.dev import get_agent_quickstart

guide = get_agent_quickstart()

# Parse guide para entender:
# - Quais APIs existem
# - Como usá-las
# - Códigos de erro e como corrigir
# - Estruturas de dados retornadas
```

### Para Usuários

```python
# Documentação sempre disponível offline
import forgebase.dev
guide = forgebase.dev.get_agent_quickstart()

# Não precisa abrir browser ou GitHub
print(guide)
```

### Para CI/CD

```bash
# Em ambientes sem internet (air-gapped)
pip install forgebase-0.1.3.whl

# Documentação ainda acessível programaticamente
python -c "from forgebase.dev import get_agent_quickstart; print(get_agent_quickstart())"
```

## 🧪 Testes

### Teste Manual

```bash
# 1. Build the package
python -m build

# 2. Install in clean environment
pip install dist/forgebase-*.whl

# 3. Test documentation access
python -c "from forgebase.dev import get_agent_quickstart; print(len(get_agent_quickstart()))"
# Expected: > 8000 (characters)
```

### Teste Automatizado

```python
# tests/test_documentation_access.py
def test_agent_quickstart_embedded():
    """Test AI Agent Quick Start is accessible."""
    from forgebase.dev import get_agent_quickstart

    guide = get_agent_quickstart()

    assert len(guide) > 100
    assert "ForgeBase AI Agent" in guide
    assert "QualityChecker" in guide
```

## 📝 Manutenção

### Atualizando Documentação

Quando atualizar `AI_AGENT_QUICK_START.md`:

```bash
# 1. Editar arquivo na raiz
vim AI_AGENT_QUICK_START.md

# 2. Copiar para package
cp AI_AGENT_QUICK_START.md src/forgebase/_docs/

# 3. Commit ambos
git add AI_AGENT_QUICK_START.md src/forgebase/_docs/AI_AGENT_QUICK_START.md
git commit -m "docs: Update AI Agent Quick Start"
```

**Automação (recomendado):**

Criar `scripts/sync_docs.sh`:
```bash
#!/bin/bash
# Sync root docs to embedded _docs

cp AI_AGENT_QUICK_START.md src/forgebase/_docs/
cp README.md src/forgebase/_docs/

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

## 🔍 Troubleshooting

### Documentação não encontrada após instalação

**Sintoma:**
```python
from forgebase.dev import get_agent_quickstart
guide = get_agent_quickstart()
# Returns: "Documentation not found in package..."
```

**Causas possíveis:**
1. Package foi buildado antes de adicionar MANIFEST.in
2. package-data não está no pyproject.toml
3. `_docs/` folder vazio

**Solução:**
```bash
# Rebuild package
rm -rf dist/ build/ *.egg-info
python -m build

# Verify contents
unzip -l dist/forgebase-*.whl | grep _docs
# Should show: forgebase/_docs/AI_AGENT_QUICK_START.md
```

### Docs desincronizados

**Sintoma:** Docs na raiz diferem de `_docs/`

**Solução:**
```bash
# Use sync script
./scripts/sync_docs.sh

# Ou manual
cp AI_AGENT_QUICK_START.md src/forgebase/_docs/
```

## 📚 Referências

- **Python Packaging Guide:** https://packaging.python.org/
- **setuptools package_data:** https://setuptools.pypa.io/en/latest/userguide/datafiles.html
- **MANIFEST.in format:** https://packaging.python.org/guides/using-manifest-in/
- **importlib.resources:** https://docs.python.org/3/library/importlib.resources.html

## 🎓 Best Practices

### ✅ DO:

1. **Keep docs synced** - Automate with pre-commit hooks
2. **Test after build** - Verify docs are included
3. **Use API access** - Programmatic > manual file reading
4. **Keep docs small** - Only essential files embedded

### ❌ DON'T:

1. **Don't embed large files** - Images, videos → keep on GitHub
2. **Don't duplicate everything** - Only critical docs
3. **Don't forget to sync** - Root and `_docs/` must match
4. **Don't hardcode paths** - Use `get_agent_quickstart()` API

---

**Version:** ForgeBase 0.1.3+
**Updated:** 2025-11-05
**Author:** ForgeBase Development Team
