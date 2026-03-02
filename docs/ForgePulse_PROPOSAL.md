# Proposta Formal — Evolução do ForgeBase com CL/CE e Camada Opcional ForgePulse (ValueTracks)

## 1) Contexto e motivação

O ForgeBase hoje é usado com sucesso sem os conceitos formais de **ValueTracks** e sem uma fronteira explícita entre **núcleo estável** e **extensões por cliente/produto**. Isso resolve entrega, mas limita três objetivos estratégicos:

1. **Mensurar entrega de valor de forma objetiva**
   Sem ValueTracks, a gente mede “saúde técnica” solta (logs/métricas), mas não mede “valor entregue por eixo” (ex.: Governança de custo, Confiabilidade, Segurança, Qualidade de roteamento). Resultado: o roadmap vira narrativa.

2. **Padronizar instrumentação para dev + agent**
   Queremos que o dev e o agent implementem features já dentro de padrões que facilitem medir performance/custo/qualidade/complexidade/segurança por ValueTrack. Sem um padrão nativo, cada equipe mede do seu jeito — e comparar vira impossibilidade.

3. **Evoluir em produção com governança (sem quebrar core)**
   A instrumentação precisa ser configurável por níveis (como logs), por tenant, por ValueTrack, com sampling e budgets. Isso é extensão (CE), não deveria contaminar o core (CL).

**Princípio:** se ValueTrack não for mensurável, ele vira slogan.

---

## 2) CL/CE: o que é, e por que isso guia a mudança

### CL — Core Logic (núcleo estável)

Tudo que deve permanecer confiável, consistente e compatível ao longo do tempo:

* runtime de execução (engine)
* contratos (interfaces/tipos) e schema base
* propagação de contexto (correlation_id, tenant, versão)
* mecanismos de plugin/hook e governança
* compatibilidade retroativa e versionamento

**CL não deve conter regras específicas de cliente, política específica, exporter específico.**

### CE — Customer Extensions (extensões configuráveis)

Tudo que varia por projeto/tenant/produto/ambiente e deve ser plugável:

* mapeamentos de ValueTracks/SubTracks para UseCases (via spec)
* políticas de monitoramento (nível, sampling, budgets)
* exporters/sinks (OTEL/Prometheus/ClickHouse/Postgres/arquivo/etc.)
* relatórios customizados por produto/cliente
* classificações de risco e tags de segurança específicas

**CE não pode “furar” o CL. CE pluga via contrato.**

### Por que isso exige mudança no ForgeBase?

Porque hoje falta um **ponto oficial** no CL para:

* carregar um **ExecutionContext** consistente
* emitir eventos/métricas/traces com schema estável
* aplicar policy por níveis com fast-path
* permitir CE acoplar exporters/mapeamentos/relatórios sem mexer no core

Sem isso, cada produto cria instrumentação “ao lado”, duplicada, inconsistente e difícil de governar.

---

## 3) Objetivo da mudança

Adicionar ao ForgeBase uma **camada opcional** chamada **ForgePulse**, que instrumenta execuções por ValueTrack **sem quebrar compatibilidade**, preservando Clean Architecture e permitindo governança CL/CE.

**Importante:** isso não substitui o ForgeBase atual. É uma **extensão do runtime** que pode ser desligada (OFF) e habilitada por níveis.

---

## 4) Premissas e restrições

* **Compatibilidade total**: o ForgeBase atual deve continuar funcionando sem alteração de código do consumidor.
* **Opt-in**: nada de “decorator obrigatório”. Decorators (se existirem) são metadata opcional.
* **Clean Architecture intacta**: UseCases não dependem de exporters, OTEL, banco, etc. Instrumentação ocorre no composition root e adapters.
* **Overhead controlado**: níveis + sampling + budgets + buffer/drop.
* **Schema estável**: eventos/metrics/traces seguem versão e compatibilidade.

---

## 5) Visão geral da solução: ForgePulse como carapaça opcional

### Componentes (alto nível)

**ForgeBase (CL existente)**
→ permanece como motor

**ForgePulse (CL opcional)**
→ runtime de instrumentação: contexto, policy, coletores, reporter

**ForgePulse Extensions (CE)**
→ mapeamentos (spec), exporters, políticas específicas, relatórios customizados

### Onde a instrumentação acontece (para manter Clean)

* **UseCaseRunner/ExecutionRunner** (composition root): mede início/fim/erro, cria contexto
* **Adapters** (LLM/HTTP/DB): medem custo/latência/retry/fallback e geram spans/eventos
* UseCase continua “puro”

---

## 6) ExecutionContext universal (mesmo no legado)

ForgePulse introduz `ExecutionContext` **sempre presente**, mesmo que o código não declare ValueTrack.

Campos mínimos:

* `correlation_id`
* `tenant_id`
* `value_track`
* `subtrack`
* `feature`
* `use_case`
* `version` (build/git sha)
* `environment` (dev/stg/prod)

### Fallback legado (compatibilidade)

Se não houver mapeamento nem decorators:

* `value_track="legacy"`
* `subtrack="legacy"`
* `feature/use_case` inferidos por classe/módulo/rota

**Resultado:** o legado vira observável sem refatorar.

---

## 7) Níveis de monitoramento (policy) e controle de performance

ForgePulse deve suportar:

* **OFF**: no-op real (fast path)
* **BASIC**: tempo total + sucesso/erro + contadores
* **STANDARD**: + latência por adapter + erros por etapa (amostrado)
* **DETAILED**: + tracing + custo (tokens/cpu) (amostragem agressiva)
* **DIAGNOSTIC**: profiling/payload redigido (somente por flag/tenant/correlation_id)

Regras obrigatórias:

* **decidir nível antes** de alocar/serializar
* sampling por `value_track`, `tenant`, `endpoint`
* budgets por execução (limite de spans/eventos/bytes)
* buffer assíncrono + drop controlado (não derrubar o sistema por telemetria)

---

## 8) ValueTracks/SubTracks: como mapear sem obrigar o time

Ordem de resolução (prioridade):

1. **Spec/Registry (CE)** — recomendado (não mexe no código)
2. **Decorators opcionais (metadata only)** — quando fizer sentido
3. **Heurística legado** — fallback

Exemplo (CE) `forgepulse.value_tracks.yml`:

* mapeia `use_case` → `value_track`/`subtrack`
* permite tags (domínio, risco, etc.)

Isso permite adoção gradual e governada.

---

## 9) ECM — Extension Compatibility Matrix (governança de extensões)

### O que é ECM

ECM é a matriz formal de compatibilidade entre:

* versão do ForgeBase (CL)
* versão do ForgePulse Schema (CL)
* versões de extensões (CE): exporters, pacotes de mapeamento, reporters

**Função:** impedir que uma extensão CE incompatível entre em produção por acidente.

### Comportamento esperado

* no startup: runtime valida ECM
* se incompatível: desabilita a extensão (ou falha hard, conforme policy)
* registra evento/alerta de incompatibilidade

---

## 10) Relatórios (outputs mínimos)

ForgePulse deve gerar, no mínimo:

### Relatório Operacional (técnico)

* Top ValueTracks por latência (p95/p99)
* Top por taxa de erro
* Gargalos por adapter/subtrack (quando disponível)
* Regressão vs baseline por versão

### Relatório Estratégico (produto/exec)

* Custo por ValueTrack (tokens/CPU quando habilitado)
* Adoção/uso por ValueTrack e por tenant
* Proxy de complexidade (spans/subtracks/calls externas)
* Exposição/risco (policy denies, acessos inválidos, etc.)

Formato: **Markdown + JSON**.

---

## 11) Critérios de aceitação

1. Com ForgePulse **OFF**, todo o ForgeBase atual roda igual (testes passam).
2. Em **BASIC**, overhead é mínimo e não cria gargalo perceptível.
3. `ExecutionContext` existe sempre (mesmo legado com `legacy/*`).
4. Policy funciona: níveis, sampling, budgets, toggles por tenant/correlation_id.
5. ECM é validado e impede extensão incompatível.
6. Relatórios gerados (operacional + estratégico) ao menos para `legacy` e para tracks mapeados.
7. Clean Architecture preservada: use cases não dependem de infra.

---

## 12) Plano de adoção (sem trauma)

* **Fase 0**: integrar ForgePulse como no-op (OFF)
* **Fase 1**: ligar BASIC/STANDARD com heurística para legado → primeiros relatórios
* **Fase 2**: adicionar mapeamento por spec (CE) → ValueTracks reais sem mexer no código
* **Fase 3**: decorators opcionais em módulos novos → precisão de subtracks/traces
* **Fase 4**: strict mode por escopo (somente onde controlado)

---

## 13) Benefícios diretos (por que vale mexer)

* Roadmap deixa de ser narrativa: vira evidência por ValueTrack
* Agent e dev passam a codar dentro de padrões mensuráveis
* Governança CL/CE evita “telemetria acoplada” e gambiarra por produto
* Diagnóstico rápido com níveis (microscópio quando precisa, leve no dia a dia)
* Comparação de versões e regressão vira rotina, não caçada


