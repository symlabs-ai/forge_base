# Ticket: Solicitação de Implementação — Tipagem Forte com Mypy (Strict) e Hook de pre-commit

Responsável: a designar
Status: Novo
Data: 2025-11-03
Prioridade: Alta (P1)

## Contexto
Ao programar com agentes RIA, tipagem forte ajuda a detectar erros cedo (antes de produção) e documenta contratos entre camadas (Domain, Application, Adapters, Infra). Propomos adotar verificação estática com Mypy em modo estrito, com rollout incremental para reduzir fricção.

## Objetivo
- Introduzir verificação estática (Mypy) com configuração “strict”, aplicada inicialmente ao módulo `domain/` e expandida gradualmente.
- Integrar o Mypy aos hooks de pre-commit (sem criar configuração na raiz), bloqueando commits com violações.
- Fornecer script simples para rodar type-check local (CI-ready).

## Escopo (Incremental)
- Fase 1 (este ticket): `src/forgebase/domain/**`
- Fase 2: `src/forgebase/application/**`
- Fase 3: `src/forgebase/adapters/**`, `src/forgebase/infrastructure/**`
- Tests: apenas warnings informativos no início; endurecer regras depois.

## Entregáveis
1) Configuração Mypy (sem tocar a raiz)
   - Adicionar `scripts/mypy.ini` com base em Python 3.12 e “strict mode”:
     - `python_version = 3.12`
     - `disallow_untyped_defs = True`
     - `disallow_any_generics = True`
     - `no_implicit_optional = True`
     - `warn_unused_ignores = True`
     - `warn_redundant_casts = True`
     - `strict_equality = True`
     - `files = src/forgebase/domain`
2) Script utilitário
   - `scripts/typecheck.sh` chamando: `mypy --config-file scripts/mypy.ini src tests`
3) Dependências de dev
   - Incluir `mypy` em `scripts/dev-requirements.txt` (e stubs conforme necessário conforme erros apontados).
4) Hook de pre-commit
   - Atualizar `scripts/pre-commit-config.yaml` adicionando o repo `https://github.com/pre-commit/mirrors-mypy` com `args: [--config-file, scripts/mypy.ini]`.
5) Documentação
   - Atualizar `docs/ambiente_e_scripts.md` com seção “Type checking (Mypy)”.

## Critérios de Aceite
- `mypy` instalado via `pip install -r scripts/dev-requirements.txt`.
- `bash scripts/typecheck.sh` executa sem erros para `src/forgebase/domain/**`.
- Hook do Mypy presente no pre-commit e rodando em `pre-commit run --config scripts/pre-commit-config.yaml --all-files`.
- Documentação atualizada com instruções de uso.

## Passos Técnicos Sugeridos
1. Criar `scripts/mypy.ini` com modo estrito e alvo inicial `src/forgebase/domain`.
2. Adicionar `mypy` a `scripts/dev-requirements.txt` e instalar.
3. Criar `scripts/typecheck.sh` (suporte a `--strict` opcional).
4. Incluir hook do Mypy em `scripts/pre-commit-config.yaml`.
5. Rodar `pre-commit run --config scripts/pre-commit-config.yaml --all-files` e ajustar anotações mínimas no domínio (se necessário) para passar.
6. Atualizar `docs/ambiente_e_scripts.md` com seção “Type checking (Mypy)”.

## Impacto Esperado
- Benefícios: detecção precoce de erros de contrato, refactors mais seguros, melhores sugestões de IDE, contratos claros entre Ports/Adapters/DTOs.
- Custos: esforço inicial para anotar/ajustar tipos; eventuais mudanças em testes; commits podem ser bloqueados até conformidade.
- Mitigação: rollout por pasta; permitir `# type: ignore[...]` com justificativa; budgets semanais de correções.

## Notas de Coordenação
- Existe outro dev atuando no backlog. Evitar mudanças nos arquivos sob modificação ativa.
- Adotar PRs pequenos por submódulo (começando por `domain/`).

## Comandos de Referência
- Instalação de dev:
  - `pip install -r scripts/dev-requirements.txt`
- Type check local:
  - `bash scripts/typecheck.sh`
- Hooks:
  - `bash scripts/install_precommit.sh`
  - `pre-commit run --config scripts/pre-commit-config.yaml --all-files`

## Referências
- Linter e hooks: `scripts/ruff.toml`, `scripts/pre-commit-config.yaml`, `scripts/install_precommit.sh`, `scripts/lint.sh`
- Guia de ambiente: `docs/ambiente_e_scripts.md`
