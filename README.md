# ForgeBase

**ForgeBase** é o núcleo técnico do Forge Framework — a infraestrutura cognitiva onde o raciocínio do ForgeProcess se transforma em código observável, reflexivo e modular.

## 🏗️ Estrutura do Repositório

```
forgebase/
├── agents/          # Definições de agentes (personas de desenvolvimento)
├── docs/            # Documentação técnica e guias de referência
├── scripts/         # Scripts de manutenção do repositório
├── src/             # Código-fonte do framework ForgeBase
├── temp/            # Arquivos temporários e simulações (não versionados)
└── README.md        # Este arquivo
```

### 📂 Detalhamento das Pastas

#### `agents/`
Contém as definições de agentes especializados que atuam no desenvolvimento:
- **jorge_theforge.md** — Arquiteto-desenvolvedor do núcleo ForgeBase
- **bill_review.md** — Revisor crítico que revela falhas de pensamento

#### `docs/`
Documentação completa do projeto:
- **BACKLOG.md** — Roadmap de desenvolvimento (8 fases, 54 componentes)
- **documentation_guide.md** — Padrões e práticas de docstrings extensivas
- **guides/forgebase_guide.md** — Guia fundacional da arquitetura
- **guides/forgebase_PRD.md** — Product Requirements Document

#### `scripts/`
Scripts de manutenção e automação do repositório.
**Nota:** Estes scripts são para gerenciamento do repo, não fazem parte do framework ForgeBase.

#### `src/`
Código-fonte do framework ForgeBase seguindo arquitetura Clean + Hexagonal:
- `domain/` — Entidades, objetos de valor, lógica de negócio
- `application/` — Casos de uso, portas, DTOs
- `adapters/` — Interfaces externas (CLI, HTTP, AI/LLM)
- `infrastructure/` — Implementações concretas (logging, config, repos)
- `observability/` — Sistema nativo de métricas e rastreamento

#### `temp/`
Workspace para arquivos temporários, experimentos e simulações.
**Esta pasta não é versionada** e serve como área de testes descartáveis.

---

## 🧠 Filosofia

> "Forjar é transformar pensamento em estrutura."

ForgeBase não é apenas um framework técnico — é uma **arquitetura cognitiva** que:
- **Pensa**: Cada componente carrega intenção e propósito
- **Mede**: Observabilidade nativa em todos os níveis
- **Explica**: Capacidade de auto-reflexão e documentação viva

### Princípios Fundamentais

1. **Reflexividade** — O código entende e explica seu próprio funcionamento
2. **Autonomia** — Módulos independentes com contratos bem definidos
3. **Coerência Cognitiva** — Padrões consistentes em toda a arquitetura

---

## 🚀 Status do Projeto

**Fase Atual:** Planejamento e Documentação ✓

**Backlog de Desenvolvimento:**
Consulte o [BACKLOG.md](/docs/BACKLOG.md) para o roadmap completo com 54 componentes organizados em 8 fases de desenvolvimento.

**Próximas Etapas:**
1. FASE 1: Implementação das classes base (EntityBase, UseCaseBase, PortBase)
2. FASE 2: Estruturação dos módulos core e infraestrutura
3. FASE 3: Sistema de observabilidade nativo
4. FASE 4: Framework de testes cognitivos

---

## 📖 Documentação

Para entender a arquitetura completa, consulte:
- [BACKLOG.md](/docs/BACKLOG.md) — Roadmap completo de desenvolvimento (8 fases, 54 componentes)
- [Documentation Guide](/docs/documentation_guide.md) — Padrões e práticas de docstrings extensivas
- [ForgeBase Guide](/docs/guides/forgebase_guide.md) — Referência técnica completa
- [ForgeBase PRD](/docs/guides/forgebase_PRD.md) — Requisitos e especificações
- [Ambiente & Scripts](/docs/ambiente_e_scripts.md) — Setup de venv, lint (Ruff) e hooks de pre-commit

---
## 🛠️ AVISOS IMPORTANTES
- Nunca grave nada na raíz sem solitacao explicita do usuario
- Nunca de push no repositorio remoto sem solitacao explicita do usuario
- Nunca crie tags ou aumente versao do forgebase sem solitacao explicita do usuario
- A fonte da verdade sobre a versao atual, bem como historico sintetico pode ser encontrada em VERSION.md

## 🛠️ Tecnologias

- **Python 3.11+**
- **Clean Architecture** + **Hexagonal Architecture**
- **Observabilidade Nativa** (Logging, Métricas, Tracing)
- **Test-Driven Development**

---
