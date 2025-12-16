# ForgeProcess: Ciclo Cognitivo Completo

**O raciocínio que transforma intenção em execução e aprendizado.**

---

## 🌟 O Renascimento do Desenvolvimento Baseado em Valor

### Do Tempo aos Tokens: Uma Mudança de Paradigma

Durante anos, o desenvolvimento de software foi governado por metodologias que mediam esforço em **tempo** — horas, sprints, entregas. O **ForgeProcess** propõe uma inversão radical: **medir valor em tokens, não em tempo**.

```
Tradicional:    "Quantos dias leva?"
                 ↓
ForgeProcess:   "Quantos tokens de valor entregamos?"
```

#### O Que São Tokens de Valor?

**Token de Valor** = Unidade de comportamento significativo que entrega resultado ao cliente

Exemplos:
- ❌ "Implementamos 5 classes" → Esforço técnico
- ✅ "Reduzimos abandono de carrinho em 20%" → **Token de Valor**

- ❌ "Criamos 15 testes" → Atividade
- ✅ "Garantimos 0 erros em cálculo fiscal" → **Token de Valor**

#### A Mudança de Foco

| Métrica Tradicional | ForgeProcess |
|---------------------|--------------|
| Velocidade de entrega | **Direção de valor** |
| "Entregamos em 2 semanas" | "Aumentamos conversão em 15%" |
| Sprint points | **Value tokens** |
| Features implementadas | **Behaviors validados** |

> *"Não importa o quão rápido o time progrida, se estiver indo para o lado errado."*

---

## 🎯 Visão Geral

O **ForgeProcess** é o sistema de raciocínio arquitetural do Forge Framework. Ele não é apenas uma metodologia, mas um **ciclo cognitivo** que transforma:

```
Intenção (Valor) → Comportamento → Prova → Execução → Aprendizado → Mais Valor
```

O ForgeProcess opera em **5 fases integradas**, cada uma representando um nível de refinamento do pensamento:

```
┌─────────────────────────────────────────────────────┐
│ 1. MDD — Market Driven Development                  │
│    "PORQUÊ existir?"                                │
│    Intenção de Valor                                │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Tradução Cognitiva
                 │ (Valor → Comportamento)
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2. BDD — Behavior Driven Development                │
│    "O QUÊ fazer?"                                   │
│    Comportamento Verificável                        │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Especificação Técnica
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3. TDD — Test Driven Development                    │
│    "COMO fazer? (com prova)"                        │
│    Implementação Validada                           │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Manifestação Executável
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4. CLI — Interface Cognitiva                        │
│    "Executar e observar"                            │
│    Ambiente Simbólico                               │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Coleta de Evidências
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5. Feedback — Reflexão                              │
│    "Aprender e ajustar"                             │
│    Raciocínio Reflexivo                             │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Loop de Aprendizado
                 └─────────────────────┐
                                       │
                  ┌────────────────────┘
                  ▼
              Volta para MDD
             (Ciclo se fecha)
```

---

## 📖 As Cinco Fases do ForgeProcess

### 1️⃣ MDD — Market Driven Development

**"PORQUÊ este sistema deve existir?"**

#### Propósito
Definir o **valor de mercado** que o sistema entrega. É a fase onde a **estratégia de negócio** se transforma em **intenção arquitetural**.

#### Artefatos Principais
- **`forge.yaml`**: Documento declarativo de visão
- **ValueTracks**: Fluxos que entregam valor direto ao usuário (o que o cliente vê)
- **SupportTracks**: Fluxos que suportam a entrega de valor (o alicerce invisível)
- **Value KPIs**: Métricas que comprovam entrega de valor

#### ValueTracks vs SupportTracks: A Simbiose do Valor

```
┌─────────────────────────────────────────────────────┐
│ VALUE TRACKS                                        │
│ "O que o cliente vê e experimenta"                  │
├─────────────────────────────────────────────────────┤
│ - Processar pedido em 1 clique                      │
│ - Reduzir abandono de carrinho em 20%              │
│ - Emitir nota fiscal sem erros                      │
│ - Rastreamento em tempo real                        │
│                                                     │
│ Medida: Impacto no negócio (KPIs)                  │
└─────────────────────────────────────────────────────┘
                       ▲
                       │ sustentado por
                       │
┌─────────────────────────────────────────────────────┐
│ SUPPORT TRACKS                                      │
│ "O que garante confiabilidade e qualidade"          │
├─────────────────────────────────────────────────────┤
│ - Testes automatizados BDD                          │
│ - CI/CD pipeline                                    │
│ - Monitoramento e observabilidade                   │
│ - Infraestrutura e escalabilidade                   │
│                                                     │
│ Medida: Confiabilidade técnica (Métricas)          │
└─────────────────────────────────────────────────────┘
```

**Fluxo Bidirecional**:
- **Value → Support**: "Precisamos de checkout 1-clique" gera necessidade de "Testes automatizados de pagamento"
- **Support → Value**: "Pipeline CI/CD robusto" permite "Entregas diárias sem medo"

**Exemplo Completo**:

| Tipo | Track | Token de Valor | Medida |
|------|-------|----------------|--------|
| VALUE | "Checkout 1-clique" | Redução de abandono em 20% | Conversão aumentou de 60% → 80% |
| SUPPORT | "Testes BDD automatizados" | 0 bugs em produção | 100% scenarios passando |
| VALUE | "Nota fiscal automática" | 0 erros fiscais | Multas evitadas: R$ 0 |
| SUPPORT | "CI/CD com validação fiscal" | Deploy seguro | 95% dos commits auto-validados |

> *"Cada comportamento de negócio precisa de sustentação técnica — e cada automação técnica deve justificar sua existência pelo valor que possibilita."*

#### Exemplo: forge.yaml

```yaml
# forge.yaml
project:
  name: "OrderManagement"
  vision: "Permitir que lojistas gerenciem pedidos de forma ágil e segura"

value_proposition:
  - "Reduzir tempo de processamento de pedidos em 50%"
  - "Eliminar erros manuais em emissão de notas"
  - "Aumentar satisfação do cliente com rastreamento em tempo real"

value_tracks:
  - name: "ProcessOrder"
    description: "Processar pedido completo do início ao fim"
    value_metric: "Tempo médio de processamento < 2 minutos"
    stakeholders:
      - "Lojista"
      - "Cliente final"

  - name: "IssueInvoice"
    description: "Emitir nota fiscal automaticamente"
    value_metric: "0 erros manuais em cálculo de impostos"
    stakeholders:
      - "Lojista"
      - "Contador"

support_tracks:
  - name: "ManageInventory"
    description: "Controlar estoque de produtos"
    supports: ["ProcessOrder"]

  - name: "CalculateTaxes"
    description: "Calcular impostos corretamente"
    supports: ["IssueInvoice"]

kpis:
  - metric: "Order Processing Time"
    target: "< 2 minutes"
    current: "4.5 minutes"

  - metric: "Invoice Error Rate"
    target: "0%"
    current: "3.2%"
```

#### Perguntas que o MDD Responde
- ✅ Qual problema estamos resolvendo?
- ✅ Para quem estamos resolvendo?
- ✅ Como medimos se estamos entregando valor?
- ✅ Qual o diferencial competitivo?

---

### 🔄 Transição Crítica: MDD → BDD

**O momento de tradução cognitiva: Valor → Comportamento**

Esta é a transição mais importante do ForgeProcess. Aqui, conceitos abstratos de valor se transformam em ações concretas e verificáveis.

#### Mapeamento

| Do MDD | Para o BDD |
|--------|------------|
| **Propósito**: "O sistema ajuda o usuário a processar pedidos rapidamente" | **Cenário**: "Dado que há um pedido válido, quando eu processá-lo, então ele deve ser concluído em < 2 minutos" |
| **ValueTrack**: "IssueInvoice" | **Feature**: "Emissão automática de nota fiscal com cálculo de impostos" |
| **Value KPI**: "0 erros em cálculo" | **Critério de Aceitação**: "Todos os impostos devem ser calculados corretamente" |

#### Exemplo de Tradução

**MDD (Intenção)**:
```yaml
value_tracks:
  - name: "CreateUser"
    description: "Permitir cadastro rápido e seguro de usuários"
    value_metric: "95% dos cadastros completados em < 30 segundos"
```

**BDD (Comportamento)**:
```gherkin
Feature: Cadastro rápido e seguro de usuários
  Para que usuários possam começar a usar o sistema rapidamente
  Como um visitante
  Eu quero me cadastrar de forma simples e segura

  Scenario: Cadastro bem-sucedido
    Given que eu estou na página de cadastro
    And eu preencho nome "Alice Silva"
    And eu preencho email "alice@example.com"
    And eu preencho senha válida
    When eu clico em "Criar conta"
    Then minha conta deve ser criada em menos de 30 segundos
    And eu devo receber um email de confirmação
    And o sistema deve validar que o email é único
```

#### Por que esta Transição é Cognitiva?

1. **Abstrato → Concreto**: Valor (abstrato) vira comportamento (concreto)
2. **Intenção → Ação**: Propósito vira cenário executável
3. **Métrica → Critério**: KPI vira critério de aceitação
4. **Estratégia → Tática**: Visão vira especificação

---

### 2️⃣ BDD — Behavior Driven Development

**"O QUÊ o sistema faz?"**

#### Propósito
Definir **comportamentos observáveis** do sistema em linguagem natural. Cada comportamento é um contrato entre stakeholders e desenvolvedores.

#### Artefatos Principais
- **Features**: Arquivos `.feature` em Gherkin
- **Scenarios**: Casos concretos de uso
- **Steps**: Given / When / Then
- **Business Rules**: Regras documentadas

#### Exemplo: Feature File

```gherkin
# features/issue_invoice.feature
Feature: Emissão de nota fiscal
  Para que lojistas possam faturar suas vendas
  Como um sistema de gestão
  Eu devo emitir notas fiscais automaticamente

  Background:
    Given que o sistema está configurado para emissão de NF-e
    And as credenciais da SEFAZ estão válidas

  Scenario: Emissão bem-sucedida de nota fiscal
    Given um pedido válido no valor de R$ 1000,00
    And o cliente tem CPF "123.456.789-00"
    And o produto é tributável com ICMS 18%
    When eu emitir a nota fiscal
    Then o sistema deve calcular ICMS de R$ 180,00
    And o XML da NF-e deve ser gerado
    And o log de auditoria deve registrar a emissão
    And a nota deve ser enviada para SEFAZ
    And o cliente deve receber o DANFE por email

  Scenario: Falha na emissão por produto sem tributação
    Given um pedido com produto sem código NCM
    When eu tentar emitir a nota fiscal
    Then o sistema deve rejeitar com erro "PRODUTO_SEM_NCM"
    And nenhuma nota deve ser gerada
    And o log deve registrar a tentativa falhada

  Business Rules:
    - Todos os produtos devem ter código NCM válido
    - ICMS deve ser calculado conforme tabela da UF
    - Notas devem ser numeradas sequencialmente
    - Falhas na SEFAZ devem ter retry automático (3x)
```

#### Como BDD se Conecta com ForgeBase

Cada **Scenario** gera:
1. **UseCase** no ForgeBase
2. **Testes de Aceitação** automatizados
3. **Documentação Viva** (specs são docs)

#### Ferramentas
- Behave (Python)
- Cucumber
- SpecFlow

#### BDD como Linguagem Universal do Forge

**Por que BDD é o idioma natural do ForgeProcess?**

```
Stakeholder (Negócio)  ──┐
                         │
Product Owner (Produto) ──┼──> TODOS FALAM GHERKIN
                         │
Developer (Código)      ──┤
                         │
QA (Testes)             ──┘
```

**Antes do BDD** (cada um fala um idioma):
- Negócio: "Precisamos aumentar vendas"
- Produto: "Vamos fazer checkout rápido"
- Dev: "Implementei um PaymentService com factory pattern"
- QA: "Testei 15 casos de teste do Jira"

❌ **Problema**: Ninguém garante que todos falam da mesma coisa!

**Com BDD** (todos falam a mesma língua):

```gherkin
FUNCIONALIDADE: Checkout em 1 clique
  PARA aumentar conversão em vendas          ← Negócio entende
  COMO um comprador recorrente               ← Produto entende
  QUERO finalizar compra com um clique       ← Todos entendem

  CENÁRIO: Compra rápida com cartão salvo
    DADO que tenho um cartão salvo           ← Dev implementa
    QUANDO clico em "Comprar agora"          ← QA testa
    ENTÃO vejo "Compra confirmada!"          ← Negócio valida
    E recebo email de confirmação            ← Todos verificam
```

✅ **Solução**: Uma única especificação que todos entendem, implementam e validam!

**Padrão Forge: Tags em MAIÚSCULO (Português)**

```gherkin
# ✅ CORRETO (padrão Forge)
FUNCIONALIDADE: Emissão de nota fiscal
  CENÁRIO: Cálculo de ICMS
    DADO pedido de R$ 1000 em SP
    QUANDO emitir nota
    ENTÃO ICMS deve ser R$ 180

# ❌ Evitar (inglês ou misturado)
Feature: Invoice issuance
  Scenario: ICMS calculation
    Given order of R$ 1000 in SP
    ...
```

**Por que maiúsculo e português?**
1. **Reduz ambiguidade**: DADO/QUANDO/ENTÃO são claramente tags estruturais
2. **Democratiza acesso**: Stakeholders brasileiros entendem sem barreira de idioma
3. **Documentação viva**: O código E a documentação são o mesmo artefato
4. **Rastreabilidade**: Cada linha de código rastreia até um behavior

**Ciclo de Vida de um Behavior**:

```
1. Stakeholder expressa valor
   "Quero reduzir abandono de carrinho"

2. PO escreve em Gherkin
   FUNCIONALIDADE: Checkout 1-clique
   CENÁRIO: Compra rápida

3. Dev implementa
   class QuickCheckoutUseCase(UseCaseBase):
       def execute(self, input):
           # Implementação baseada no CENÁRIO

4. QA valida automaticamente
   pytest features/checkout.feature
   ✅ CENÁRIO: Compra rápida.....PASSOU

5. Stakeholder confirma
   "Sim! Abandono caiu 20%"

6. Todos falam a mesma língua
   O behavior virou código virou teste virou valor
```

> *"BDD não é apenas testes. É a gramática que o Forge Process adota para que todos — produto, negócio, engenharia e QA — falem a mesma língua."*

---

### 3️⃣ TDD — Test Driven Development

**"COMO implementar? (com prova)"**

#### Propósito
Transformar comportamentos do BDD em **código testado**. Cada funcionalidade nasce com prova de que funciona.

#### Ciclo TDD (Red-Green-Refactor)

```
1. 🔴 RED: Escrever teste que falha
   ↓
2. 🟢 GREEN: Implementar código mínimo que passa
   ↓
3. 🔵 REFACTOR: Melhorar código mantendo testes verdes
   ↓
   Repetir
```

#### Exemplo: Do BDD ao TDD

**BDD Scenario**:
```gherkin
Scenario: Emissão bem-sucedida de nota fiscal
  Given um pedido válido no valor de R$ 1000,00
  When eu emitir a nota fiscal
  Then o ICMS deve ser R$ 180,00
```

**TDD Test (Red)**:
```python
# tests/unit/test_issue_invoice_usecase.py
import pytest
from forge_base.application.issue_invoice_usecase import IssueInvoiceUseCase

def test_should_calculate_icms_correctly():
    # Arrange
    usecase = IssueInvoiceUseCase()
    order = Order(value=1000.00, uf="SP")  # ICMS SP = 18%

    # Act
    invoice = usecase.execute(IssueInvoiceInput(order=order))

    # Assert
    assert invoice.icms == 180.00  # ❌ FALHA - código não existe ainda
```

**TDD Implementation (Green)**:
```python
# src/forge_base/application/issue_invoice_usecase.py
from forge_base.application.usecase_base import UseCaseBase

class IssueInvoiceUseCase(UseCaseBase[IssueInvoiceInput, IssueInvoiceOutput]):
    """Emitir nota fiscal com cálculo automático de impostos."""

    def execute(self, input_dto: IssueInvoiceInput) -> IssueInvoiceOutput:
        # Validar entrada
        input_dto.validate()

        # Calcular ICMS
        icms_rate = self._get_icms_rate(input_dto.order.uf)
        icms_value = input_dto.order.value * icms_rate

        # Gerar XML
        xml = self._generate_nfe_xml(input_dto.order, icms_value)

        # Registrar log
        self._log_emission(input_dto.order, xml)

        return IssueInvoiceOutput(
            xml=xml,
            icms=icms_value,
            success=True
        )

    def _get_icms_rate(self, uf: str) -> float:
        """Obter alíquota de ICMS por UF."""
        icms_table = {"SP": 0.18, "RJ": 0.20, "MG": 0.18}
        return icms_table.get(uf, 0.17)  # Default 17%
```

**Test passes ✅**

#### Tipos de Testes no ForgeBase

1. **Unit Tests**: Testam UseCases isoladamente
2. **Integration Tests**: Testam UseCases com Repositories reais
3. **Property-Based Tests**: Testam propriedades gerais (Hypothesis)
4. **Contract Tests**: Validam interfaces (Ports)

---

### 4️⃣ CLI — Interface Cognitiva

**"Executar e observar"**

#### Propósito
Fornecer um **ambiente simbólico de teste** onde UseCases podem ser executados, observados e validados antes de uma interface gráfica.

O CLI não é apenas uma ferramenta de linha de comando, mas um **espaço cognitivo** onde:
- Humanos podem testar manualmente
- IA pode explorar comportamentos
- Logs e métricas são coletados
- Debugging é facilitado

#### Exemplo: CLI do ForgeBase

```bash
# Executar UseCase via CLI
forge_base execute IssueInvoiceUseCase \
  --input '{"order_id": "12345", "value": 1000.00, "uf": "SP"}' \
  --output invoice.json \
  --verbose

# Output:
# ⏱️  Starting IssueInvoiceUseCase...
# 📊 Metrics enabled: true
# 🔍 Tracing enabled: true
#
# [DEBUG] Validating input...
# [INFO] Fetching order 12345...
# [INFO] Calculating ICMS for UF=SP (18%)...
# [INFO] ICMS calculated: R$ 180.00
# [INFO] Generating NF-e XML...
# [SUCCESS] Invoice issued successfully!
#
# 📈 Metrics:
#   - Duration: 1.2s
#   - ICMS: R$ 180.00
#   - XML size: 2.5KB
#
# ✅ Output saved to invoice.json
```

#### Capacidades do CLI

1. **Execução Manual**: Testar UseCases sem GUI
2. **Simulação**: Rodar cenários com dados fake
3. **Observação**: Ver logs, métricas, traces em tempo real
4. **Debugging**: Inspecionar estado e fluxo
5. **Automação**: Scripts e CI/CD
6. **Exploração**: IA pode usar CLI para aprender

#### CLI como Ponte entre Humanos e IA

```python
# IA explorando via CLI
from forge_base.dev.api import ComponentDiscovery, TestRunner

# 1. IA descobre componentes
discovery = ComponentDiscovery()
components = discovery.scan_project()
print(f"Found {len(components.usecases)} UseCases")

# 2. IA executa cada UseCase via CLI
for usecase in components.usecases:
    result = subprocess.run([
        "forge_base", "execute", usecase.name,
        "--input", "sample_input.json"
    ])

    # 3. IA analisa resultado
    if result.returncode == 0:
        print(f"✅ {usecase.name} works!")
    else:
        print(f"❌ {usecase.name} failed!")
```

---

### 5️⃣ Feedback — Reflexão

**"Aprender e ajustar"**

#### Propósito
Coletar dados de execução e usá-los para **melhorar o raciocínio** do sistema. Feedback fecha o ciclo cognitivo.

#### Dois Tipos de Feedback

##### 1. Feedback Operacional

**Origem**: Métricas, logs, exceções, performance
**Função**: Melhorar desempenho técnico

```python
# Coleta automática de métricas
@track_metrics
class IssueInvoiceUseCase(UseCaseBase):
    def execute(self, input_dto):
        # Métricas coletadas automaticamente:
        # - Tempo de execução
        # - Taxa de erro
        # - Throughput
        # - Latência de dependências
        ...

# Análise de métricas
metrics = MetricsCollector.get_metrics("IssueInvoiceUseCase")
print(f"Avg duration: {metrics.avg_duration}ms")
print(f"Error rate: {metrics.error_rate}%")
print(f"P95 latency: {metrics.p95_latency}ms")

# IA analisa e sugere melhorias
if metrics.error_rate > 0.05:
    print("⚠️ High error rate detected!")
    print("💡 Suggestion: Add retry logic for SEFAZ calls")
```

##### 2. Feedback de Valor

**Origem**: Stakeholders, usuários, KPIs
**Função**: Ajustar propósito e realinhar valor

```python
# Análise de Value KPIs
value_tracker = ValueKPITracker()

# KPI do MDD: "0 erros em cálculo de impostos"
kpi_result = value_tracker.measure_kpi(
    kpi="Invoice Error Rate",
    usecase="IssueInvoiceUseCase",
    period="last_30_days"
)

print(f"Target: 0%")
print(f"Current: {kpi_result.current_value}%")

if kpi_result.current_value > 0:
    print("❌ KPI não atingido!")

    # Feedback para o MDD: revisar ValueTrack
    feedback = FeedbackReport(
        kpi="Invoice Error Rate",
        target=0.0,
        actual=kpi_result.current_value,
        recommendation="Revisar regras de cálculo de ICMS para casos especiais"
    )

    # Exportar para ForgeProcess
    feedback_manager.export_to_forgeprocess(feedback)
```

#### Feedback Loop Completo

```python
# src/forge_base/observability/feedback_manager.py
class FeedbackManager:
    """Gerencia feedback loops entre ForgeBase e ForgeProcess."""

    def collect_comprehensive_feedback(
        self,
        usecase_name: str,
        time_window: str = "last_7_days"
    ) -> FeedbackReport:
        """Coleta feedback completo de um UseCase."""

        # 1. Métricas operacionais
        metrics = self.metrics_collector.get_metrics(usecase_name, time_window)

        # 2. Logs de erro
        errors = self.log_service.query_errors(usecase_name, time_window)

        # 3. Value KPIs
        kpis = self.value_tracker.measure_all_kpis(usecase_name, time_window)

        # 4. Intent tracking (coerência)
        coherence = self.intent_tracker.measure_coherence(usecase_name, time_window)

        # 5. Análise de IA
        insights = self.ai_analyzer.analyze(metrics, errors, kpis, coherence)

        return FeedbackReport(
            usecase=usecase_name,
            operational_metrics=metrics,
            errors=errors,
            value_kpis=kpis,
            coherence=coherence,
            ai_insights=insights,
            recommendations=self._generate_recommendations(insights)
        )

    def export_to_forgeprocess(self, report: FeedbackReport):
        """Exporta feedback para ForgeProcess aprender."""
        # Salvar em formato estruturado
        learning_data = {
            "usecase": report.usecase,
            "timestamp": datetime.now().isoformat(),
            "metrics": report.operational_metrics.to_dict(),
            "kpis": [kpi.to_dict() for kpi in report.value_kpis],
            "recommendations": report.recommendations
        }

        # Exportar para ForgeProcess
        with open(f"/var/learning/{report.usecase}_feedback.jsonl", "a") as f:
            f.write(json.dumps(learning_data) + "\n")

        # ForgeProcess pode ler e ajustar forge.yaml ou .feature files
```

---

## 🔄 O Ciclo Completo na Prática

### Exemplo Real: ValueTrack "IssueInvoice"

#### Fase 1: MDD

```yaml
# forge.yaml
value_tracks:
  - name: "IssueInvoice"
    description: "Emitir nota fiscal automaticamente"
    value_metric: "0 erros em cálculo de impostos"
    stakeholders: ["Lojista", "Contador"]
```

#### Fase 2: BDD

```gherkin
# features/issue_invoice.feature
Feature: Emissão de nota fiscal
  Scenario: Cálculo correto de ICMS
    Given um pedido de R$ 1000 em SP
    When emitir nota
    Then ICMS deve ser R$ 180
```

#### Fase 3: TDD

```python
# tests/test_issue_invoice.py
def test_icms_calculation():
    usecase = IssueInvoiceUseCase()
    result = usecase.execute(IssueInvoiceInput(order_value=1000, uf="SP"))
    assert result.icms == 180.00  # ✅
```

#### Fase 4: CLI

```bash
forge_base execute IssueInvoiceUseCase \
  --input '{"order_value": 1000, "uf": "SP"}' \
  --verbose

# ✅ ICMS: R$ 180.00
# ✅ XML generated
# ✅ Duration: 1.2s
```

#### Fase 5: Feedback

```python
# Análise após 30 dias
feedback = feedback_manager.collect_comprehensive_feedback("IssueInvoiceUseCase")

# KPI: 0 erros → ATUAL: 0.1% erros
# Recomendação: Adicionar validação para casos especiais de substituição tributária

# Feedback volta para MDD: Ajustar ValueTrack
# Feedback volta para BDD: Adicionar scenarios para ST
```

---

## 🎯 Benefícios do Ciclo Cognitivo

### 1. Rastreabilidade Completa

```
Valor (MDD) → Comportamento (BDD) → Código (TDD) → Execução (CLI) → Aprendizado (Feedback)
```

Todo código pode ser rastreado até a intenção de valor original.

### 2. Documentação Viva

- **forge.yaml** documenta o porquê
- **.feature** documenta o quê
- **Testes** documentam o como
- **Logs** documentam o aconteceu
- **Feedback** documenta o aprendizado

### 3. Evolução Guiada por Valor

O sistema não evolui aleatoriamente, mas guiado por:
- Value KPIs (estamos entregando valor?)
- Operational Metrics (estamos funcionando bem?)
- Coherence Tracking (estamos cumprindo intenções?)

### 4. Ambiente Cognitivo para IA

IA pode:
- Ler **forge.yaml** e entender propósito
- Executar **.features** e validar comportamentos
- Analisar **métricas** e sugerir melhorias
- Usar **CLI** para explorar e testar
- Gerar **feedback** para auto-melhoria

---

## 📚 Próximos Passos

### Para Desenvolvedores

1. Leia o **forge.yaml** do seu projeto
2. Entenda os **ValueTracks** (o que entrega valor?)
3. Escreva **.features** para cada ValueTrack
4. Implemente com **TDD** (testes primeiro)
5. Teste via **CLI** (observe e valide)
6. Analise **feedback** (aprenda e melhore)

### Para Agentes de IA

1. Parse **forge.yaml** → Entenda propósito
2. Parse **.features** → Entenda comportamentos
3. Execute via **CLI** → Valide funcionamento
4. Colete **métricas** → Analise performance
5. Gere **feedback** → Sugira melhorias

### Para Product Owners

1. Defina **Value KPIs** claros
2. Acompanhe métricas de valor
3. Use feedback para ajustar roadmap
4. Valide que features entregam valor

---

## 🔗 Documentos Relacionados

- **ADR-006**: ForgeProcess Integration (detalhes técnicos)
- **AGENT_ECOSYSTEM.md**: Como IA usa ForgeProcess
- **AI_AGENT_QUICK_START.md**: APIs para agentes
- **forgebase_PRD.md**: Visão do produto

---

## 🌟 A Filosofia Forge: Tokens de Valor, Não Dias de Sprint

### O Que Estamos Realmente Medindo?

O ForgeProcess propõe algo mais profundo que velocidade: **clareza, coerência e confiança**.

```
Metodologia Tradicional           ForgeProcess
═══════════════════════           ════════════

"Entregamos 20 story points"      "Reduzimos abandono em 20%"
"Completamos 15 tasks"            "Garantimos 0 bugs fiscais"
"Sprint concluída em 2 semanas"   "Cliente economizou R$ 50k/mês"
"5 features implementadas"        "5 comportamentos validados"

Mede: ATIVIDADE                   Mede: IMPACTO
```

### Por Que "Tokens de Valor"?

**Token de Valor** = A menor unidade de comportamento que entrega resultado mensurável

Cada token é:
1. **Rastreável**: Do forge.yaml até o código
2. **Verificável**: BDD scenarios automatizados
3. **Mensurável**: KPIs claros de impacto
4. **Valioso**: Cliente percebe diferença

### A Corrente de Valor Verificável

```
MDD (Intenção de Valor)
    ↓
BDD (Comportamento Verificável)
    ↓
TDD (Prova Automatizada)
    ↓
CLI (Observação em Tempo Real)
    ↓
Feedback (Medição de Impacto)
    ↓
Mais Valor (Ciclo Contínuo)
```

Cada elo dessa corrente é **verificável**:
- ✅ Valor definido? (forge.yaml)
- ✅ Comportamento especificado? (.feature)
- ✅ Código testado? (pytest)
- ✅ Funciona em produção? (CLI + métricas)
- ✅ KPI atingido? (feedback)

### A Simbiose Value ↔ Support

O ForgeProcess estabelece um contrato:

**VALUE TRACKS** entregam impacto
**SUPPORT TRACKS** garantem confiabilidade

```
       VALUE                        SUPPORT
   ┌──────────┐                ┌──────────┐
   │ Checkout │                │ Tests    │
   │ 1-clique │ ←──────────→  │ BDD auto │
   │          │   sustentação  │          │
   │ -20%     │                │ 100%     │
   │ abandono │                │ coverage │
   └──────────┘                └──────────┘
```

Sem VALUE TRACKS, o sistema não tem propósito.
Sem SUPPORT TRACKS, o valor não se sustenta.

### O Renascimento

**Num mundo saturado de entregas rápidas e resultados rasos**, o ForgeProcess propõe:

- 🔄 **Ciclo cognitivo** em vez de workflow mecânico
- 🎯 **Direção de valor** em vez de velocidade cega
- 🗣️ **Linguagem universal** (BDD) em vez de silos técnicos
- 📊 **Tokens de valor** em vez de story points
- ✅ **Comportamentos validados** em vez de features "prontas"
- 🔗 **Rastreabilidade completa** do porquê até o código

### O Código se Reconciliando com o Propósito

```
Tradicional:                    ForgeProcess:
"Feature pronta!"              "Valor entregue!"
    ↓                              ↓
Mas funciona?                  Sim, está testado.
    ↓                              ↓
Mas entrega valor?             Sim, KPI mostra.
    ↓                              ↓
Como sabemos?                  Comportamento validado.
    ↓                              ↓
🤷 "Achamos que sim"            ✅ "Temos evidência"
```

---

## 💡 Citações

> *"O código do ForgeBase é o corpo de uma mente que pensa em software."*

> *"O ForgeProcess é o ciclo em que o pensamento se transforma em comportamento, o comportamento em prova, e a prova em aprendizado."*

> *"MDD → BDD: O momento em que estratégia vira função."*

> *"Não importa o quão rápido o time progrida, se estiver indo para o lado errado."*

> *"Cada comportamento de negócio precisa de sustentação técnica — e cada automação técnica deve justificar sua existência pelo valor que possibilita."*

> *"BDD é a gramática que todos — produto, negócio, engenharia e QA — usam para falar a mesma língua."*

> *"O progresso se mede em tokens de valor, não em dias de sprint."*

> *"É o código se reconciliando com o propósito."*

---

**Author**: ForgeBase Development Team
**Version**: 1.1
**Date**: 2025-11-04
**Updated**: 2025-11-04 - Adicionado conceitos de Tokens de Valor e ValueTracks vs SupportTracks
