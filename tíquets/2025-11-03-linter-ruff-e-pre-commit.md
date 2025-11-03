# Ticket: Ativação de Linter (Ruff) e Hooks de pre-commit

Responsável: time de dev
Status: novo
Data: 2025-11-03

## Contexto
Foi adicionado um pipeline local de qualidade com Ruff (linter/organização de imports) e hooks de pre-commit — sem criar configs na raiz. A configuração está em `scripts/`.

## O que mudou
- Linter: Ruff configurado em `scripts/ruff.toml`.
- Script de lint: `scripts/lint.sh` (suporta `--fix`).
- Hooks de pre-commit: `scripts/pre-commit-config.yaml` + instalador `scripts/install_precommit.sh`.
- Dependências de dev: `scripts/dev-requirements.txt` (ruff, pre-commit).

## Como preparar o ambiente (Python 3.12)
1) Criar/ativar venv:
- Linux/macOS:
  - `python3.12 -m venv .venv`
  - `source .venv/bin/activate`
- Windows PowerShell:
  - `python -m venv .venv`
  - `.venv\Scripts\Activate.ps1`

2) Instalar dependências de desenvolvimento:
- `pip install -r scripts/dev-requirements.txt`

3) (Opcional) Extras de dev do projeto:
- `pip install -e .[dev]`

## Como instalar os hooks de pre-commit
- `bash scripts/install_precommit.sh`
  - Instala o hook usando `scripts/pre-commit-config.yaml`.
  - Executa um baseline em todos os arquivos para mostrar e aplicar correções simples.

Para reexecutar manualmente em todos os arquivos:
- `.venv/bin/pre-commit run --config scripts/pre-commit-config.yaml --all-files`

## Como ver o “relatório” do linter e corrigir
- Execução direta do linter (checagem):
  - `bash scripts/lint.sh`
- Com correções automáticas (quando seguro):
  - `bash scripts/lint.sh --fix`
- Via hooks (mostra relatório dos hooks, incluindo o Ruff):
  - `pre-commit run --config scripts/pre-commit-config.yaml --all-files`

Erros comuns e como corrigir:
- B027: método vazio em classe abstrata sem `@abstractmethod`.
  - Solução: adicionar `@abstractmethod` ou implementar logicamente.
- B904: usar `raise ... from e` ao relançar em blocos `except`.
- F841: remover variáveis não utilizadas (ex.: atribuições em testes).
- SIM105: usar `contextlib.suppress(...)` em vez de try/except/pass.
- UP035: usar genéricos embutidos (`list`, `dict`) em vez de `typing.List`.
- RET504: remover atribuição desnecessária antes de `return`.

Arquivos onde o Ruff apontou problemas (exemplos):
- `src/forgebase/application/usecase_base.py` — métodos de lifecycle sem `@abstractmethod`.
- `src/forgebase/adapters/adapter_base.py` — `_instrument` sem `@abstractmethod`.
- `src/forgebase/infrastructure/repository/sql_repository.py` — `raise ... from e` em exceções.
- `tests/unit/**` — variáveis não usadas e pequenos ajustes de estilo.

## Como fazer commit com hooks ativos
1) Trabalhe nas correções e adições normalmente.
2) Adicione as mudanças: `git add -A` (ou selecione com `git add -p`).
3) Faça o commit: `git commit -m "mensagem"`.
   - Os hooks rodarão automaticamente. Se falhar, o Git bloqueará o commit e mostrará o relatório — corrija e tente de novo.

Observações importantes do repositório:
- Não gravar na raiz, não dar push/tag/alterar versão sem solicitação explícita.
- Existe outro dev atuando no backlog: evite alterar arquivos que ele esteja modificando. Coordene branch/escopo antes de qualquer commit.

## Referências
- Config do linter: `scripts/ruff.toml`
- Script de lint: `scripts/lint.sh`
- Hooks: `scripts/pre-commit-config.yaml`
- Instalador dos hooks: `scripts/install_precommit.sh`
- Dependências de dev: `scripts/dev-requirements.txt`
- Guia de ambiente e scripts: `docs/ambiente_e_scripts.md`
