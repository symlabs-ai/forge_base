# 📘 Documento Base — O que é o ForgeBase

## 🧭 Visão Geral

O **ForgeBase** é o núcleo técnico do **Forge Framework**, responsável por transformar raciocínio em execução.
Ele serve como o *corpo da mente* do ForgeProcess — a parte operacional que traduz intenções em código, comportamento e aprendizado contínuo.

Mais do que um framework, o ForgeBase é uma **arquitetura cognitiva**: ele pensa, mede e reflete sobre o próprio funcionamento.
Cada módulo foi projetado para garantir **reflexividade, autonomia e coerência cognitiva**, princípios fundadores do Forge.

> *“O ForgeBase é o corpo onde a ideia ganha forma e consciência.”*

---

## ⚙️ 1. Objetivo do Núcleo

O núcleo do ForgeBase foi criado para:

* Garantir **independência de domínio** (Clean Architecture).
* Facilitar a comunicação com múltiplas interfaces cognitivas (Hexagonal Architecture).
* Incorporar **observabilidade nativa**: logs, métricas e feedback automáticos.
* Prover infraestrutura reflexiva para *ValueTracks* e *SupportTracks*.
* Preservar a coerência entre **intenção (ForgeProcess)** e **execução (ForgeBase)**.

---

## 🧩 2. Estrutura de Pastas do Núcleo

A arquitetura modular do ForgeBase segue o padrão **Clean + Hexagonal + Observável**, permitindo expansão e rastreabilidade total.

```
forgebase/
├─ __init__.py
│
├─ domain/                          # Núcleo de entidades e invariantes
│  ├─ __init__.py
│  ├─ entity_base.py                # Classe base para entidades do domínio
│  ├─ value_object_base.py          # Objetos imutáveis de domínio
│  ├─ exceptions.py                 # Exceções e erros do domínio
│  └─ validators/                   # Regras e invariantes
│     ├─ __init__.py
│     └─ rules.py
│
├─ application/                     # Casos de uso e orquestração cognitiva
│  ├─ __init__.py
│  ├─ usecase_base.py               # Classe base para UseCases (ValueTracks)
│  ├─ port_base.py                  # Classe base para Ports (contratos cognitivos)
│  ├─ dto_base.py                   # DTOs padronizados (Data Transfer Objects)
│  ├─ error_handling.py             # Tratamento de erros padronizado
│  └─ decorators/                   # Decoradores de métricas e feedback
│     ├─ __init__.py
│     └─ track_metrics.py
│
├─ adapters/                        # Interfaces e conectores externos (Ports & Adapters)
│  ├─ __init__.py
│  ├─ adapter_base.py               # Classe base para Adapters (driven e driving)
│  ├─ cli/                          # Interface CLI
│  │  ├─ __init__.py
│  │  └─ cli_adapter.py
│  ├─ http/                         # Interface REST / HTTP
│  │  ├─ __init__.py
│  │  └─ http_adapter.py
│  └─ ai/                           # Adapters cognitivos (LLM, agentes IA)
│     ├─ __init__.py
│     └─ llm_adapter.py
│
├─ infrastructure/                  # Serviços técnicos e de suporte
│  ├─ __init__.py
│  ├─ repository/                   # Persistência e repositórios
│  │  ├─ __init__.py
│  │  ├─ repository_base.py
│  │  ├─ json_repository.py
│  │  └─ sql_repository.py
│  ├─ logging/                      # Logging e tracing estruturado
│  │  ├─ __init__.py
│  │  └─ logger_port.py
│  ├─ configuration/                # Carregamento de configurações
│  │  ├─ __init__.py
│  │  └─ config_loader.py
│  └─ security/                     # Sandbox, autenticação e segurança
│     ├─ __init__.py
│     └─ sandbox.py
│
├─ observability/                   # Núcleo de métricas e feedback
│  ├─ __init__.py
│  ├─ log_service.py                # Serviço de logs estruturados
│  ├─ track_metrics.py              # Métricas e telemetria
│  ├─ tracer_port.py                # Interface de tracing distribuído
│  └─ feedback_manager.py           # Integração Process ↔ Base
│
├─ testing/                         # Estrutura de testes e fakes cognitivos
│  ├─ __init__.py
│  ├─ forge_test_case.py            # Base de testes cognitivos
│  ├─ fakes/                        # Implementações falsas para simulação
│  │  ├─ __init__.py
│  │  └─ fake_logger.py
│  └─ fixtures/                     # Dados simulados para regressão
│     ├─ __init__.py
│     └─ sample_data.py
│
└─ core_init.py                     # Inicialização e boot cognitivo
```

---

## 🔧 3. Conceitos Raiz

### 🧱 Clean Architecture

* As dependências **sempre apontam para dentro**: o domínio não conhece a infraestrutura.
* A camada `domain/` define as regras e entidades fundamentais.
* `application/` orquestra o comportamento com base em contratos (Ports & UseCases).

### 🔷 Hexagonal Architecture

* Toda comunicação com o mundo externo ocorre via *Ports* e *Adapters*.
* Entradas (CLI, REST, IA) são *driving adapters*;
  saídas (DB, logs, mensageria) são *driven adapters*.

### 👁️ Observabilidade Nativa

* Cada *UseCase* e *Port* deve emitir logs, métricas e feedbacks cognitivos.
* Os módulos `observability/` e `testing/` são parte do núcleo, não extensões.

### 🧪 Testes Cognitivos

* O TDD serve como **memória viva** do raciocínio técnico.
* Testes explicam o *porquê* de cada decisão e garantem coerência ao longo do tempo.

---

## 🧠 4. O que deve ser preservado

| Princípio                   | Descrição                                                                           |
| --------------------------- | ----------------------------------------------------------------------------------- |
| **Isolamento de domínio**   | Nenhum módulo fora de `domain/` deve alterar entidades ou invariantes.              |
| **Consistência de imports** | Imports modulares, claros e explícitos: `from forgebase.[module] import ClassBase`. |
| **Coerência cognitiva**     | Código e documentação devem espelhar a mesma intenção.                              |
| **Feedback contínuo**       | Toda execução deve gerar dados de observação.                                       |
| **Testabilidade absoluta**  | Nenhum componente pode ser criado sem seus respectivos testes e métricas.           |
| **Explicabilidade**         | Cada classe deve conter docstrings descritivas com intenção e comportamento.        |

---

## 🧩 5. Recomendações de Implementação

1. **Padrão de herança**

   * `EntityBase`, `UseCaseBase`, `PortBase`, `AdapterBase` são obrigatórios.
   * Toda nova classe deve herdar de uma dessas bases, garantindo rastreabilidade e instrumentação.

2. **Estrutura de imports modularizada**

   * Sempre use importações explícitas para manter coerência cognitiva:

     ```python
     from forgebase.domain import EntityBase
     from forgebase.application import UseCaseBase, PortBase
     from forgebase.adapters import AdapterBase
     ```

3. **Observabilidade embutida**

   * Cada execução deve emitir logs e métricas via `track_metrics` e `LogService`.

4. **DTOs e contratos cognitivos**

   * Todos os dados trafegando entre camadas devem usar DTOs definidos em `dto_base.py`.

5. **Extensibilidade segura**

   * Novos adapters ou ports devem ser adicionados sem alterar o núcleo.
   * Cada módulo externo deve seguir o padrão Port/Adapter, respeitando o isolamento do domínio.

6. **Padronização de testes**

   * Os testes cognitivos devem validar raciocínio, não apenas retorno.
   * Todo módulo precisa ter um fake ou fixture associado em `testing/`.

---

## 📈 6. Benefícios Esperados

* **Escalabilidade modular**: fácil expansão sem acoplamento.
* **Transparência cognitiva**: execução e intenção visíveis no mesmo nível.
* **Rastreabilidade**: logs, métricas e testes conectados à intenção original.
* **Governança técnica**: a arquitetura se autoexplica e se audita.
* **Integração natural com IA**: suporte a agentes cognitivos e automação simbiótica.


---

## 🔗 7. Exemplo de Integração Prática entre Módulos

A seguir, um exemplo que demonstra como as principais camadas do ForgeBase se conectam entre si — do domínio à observabilidade — formando um fluxo cognitivo completo.

### 📘 Cenário: Tradução de Texto com Métricas e Logs

**Objetivo:** Demonstrar como um `UseCaseBase` usa um `PortBase` implementado por um `AdapterBase`, com observabilidade integrada.

---

### 1. Domínio — Entidade Fundamental

```python
# forgebase/domain/texto.py
from forgebase.domain import EntityBase

class Texto(EntityBase):
    def __init__(self, conteudo: str):
        self.conteudo = conteudo
```

A entidade `Texto` representa o dado bruto — um conceito puro, sem dependências externas.

---

### 2. Porta (PortBase) — Contrato Cognitivo

```python
# forgebase/application/ports/tradutor_port.py
from forgebase.application import PortBase

class TradutorPort(PortBase):
    def traduzir(self, texto: str) -> str:
        """Traduz texto para outro idioma."""
        raise NotImplementedError
```

A `TradutorPort` define o contrato semântico entre a aplicação e qualquer módulo externo que realize tradução.

---

### 3. Adapter (AdapterBase) — Implementação do Contrato

```python
# forgebase/adapters/ai/dummy_translator.py
from forgebase.adapters import AdapterBase
from forgebase.application.ports.tradutor_port import TradutorPort

class DummyTranslator(AdapterBase, TradutorPort):
    def traduzir(self, texto: str) -> str:
        return texto.upper()
```

O `DummyTranslator` cumpre o contrato definido pelo port e pode ser substituído por qualquer outro tradutor (IA, API, etc.).

---

### 4. Caso de Uso (UseCaseBase) — Inteligência da Aplicação

```python
# forgebase/application/usecases/traduzir_texto.py
from forgebase.application import UseCaseBase
from forgebase.observability import TrackMetrics

class TraduzirTexto(UseCaseBase):
    def __init__(self, tradutor, logger):
        self.tradutor = tradutor
        self.logger = logger

    def execute(self, texto: str):
        metrics = TrackMetrics("TraduzirTexto")
        metrics.start()

        traducao = self.tradutor.traduzir(texto)
        self.logger.info(f"Texto traduzido: {traducao}")

        metrics.stop(success=True)
        metrics.report()
        return traducao
```

O caso de uso `TraduzirTexto` orquestra a operação, medindo tempo e sucesso — a lógica de negócio está desacoplada do adapter e do logger.

---

### 5. Observabilidade — Logs e Métricas

```python
# forgebase/observability/log_service.py
class LogService:
    def info(self, message: str):
        print(f"[INFO] {message}")

# forgebase/observability/track_metrics.py
import time

class TrackMetrics:
    def __init__(self, name: str):
        self.name = name
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self, success=True):
        self.duration = time.time() - self.start_time
        self.success = success

    def report(self):
        print(f"[METRIC] {self.name} | Time: {self.duration:.3f}s | Success: {self.success}")
```

Os módulos de observabilidade registram o comportamento cognitivo do sistema — o ForgeBase não apenas executa, ele *sabe o que fez*.

---

### 6. Execução Integrada

```python
# forgebase/examples/run_translation.py
from forgebase.adapters.ai.dummy_translator import DummyTranslator
from forgebase.application.usecases.traduzir_texto import TraduzirTexto
from forgebase.observability.log_service import LogService

tradutor = DummyTranslator()
logger = LogService()
use_case = TraduzirTexto(tradutor, logger)

resultado = use_case.execute("olá mundo")
print(f"Resultado final: {resultado}")
```

**Saída esperada:**

```
[INFO] Texto traduzido: OLÁ MUNDO
[METRIC] TraduzirTexto | Time: 0.001s | Success: True
Resultado final: OLÁ MUNDO
```

---

## 🧭 8. Conclusão 

Este fluxo demonstra a filosofia central do ForgeBase:

1. **O domínio pensa o problema.**
2. **O caso de uso raciocina a execução.**
3. **O adapter fala com o mundo.**
4. **A observabilidade conta a história.**

O ForgeBase é o centro vital da engenharia do Forge Framework.
Sua modularização garante que o sistema permaneça **limpo, coerente e evolutivo**, permitindo que ideias se tornem código sem perder o sentido original.

> *“Forjar o núcleo é dar forma à consciência da engenharia.”*




