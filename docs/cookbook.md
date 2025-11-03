# ForgeBase Cookbook

> Receitas práticas para casos comuns de desenvolvimento

Este cookbook fornece soluções prontas para casos de uso frequentes no ForgeBase. Cada receita é autocontida e pode ser copiada/adaptada para seu projeto.

---

## 📑 Índice

1. [Como Criar uma Entity](#1-como-criar-uma-entity)
2. [Como Criar um ValueObject](#2-como-criar-um-valueobject)
3. [Como Criar um UseCase](#3-como-criar-um-usecase)
4. [Como Criar um Port](#4-como-criar-um-port)
5. [Como Criar um Adapter](#5-como-criar-um-adapter)
6. [Como Adicionar Observabilidade](#6-como-adicionar-observabilidade)
7. [Como Escrever Testes Cognitivos](#7-como-escrever-testes-cognitivos)
8. [Como Integrar com ForgeProcess](#8-como-integrar-com-forgeprocess)
9. [Como Criar um Repository Customizado](#9-como-criar-um-repository-customizado)
10. [Como Adicionar Validações Customizadas](#10-como-adicionar-validações-customizadas)
11. [Como Usar Dependency Injection](#11-como-usar-dependency-injection)
12. [Como Adicionar um Novo Adapter](#12-como-adicionar-um-novo-adapter)

---

## 1. Como Criar uma Entity

**Problema**: Preciso criar uma entidade de domínio com identidade e invariantes.

**Solução**:

```python
from forgebase.domain import EntityBase, ValidationError, BusinessRuleViolation
from datetime import datetime


class Order(EntityBase):
    """
    Order entity.

    Represents a customer order with items, total, and status.

    Business Rules:
        - Order must have at least one item
        - Total must be positive
        - Once paid, order cannot be modified
    """

    def __init__(
        self,
        customer_id: str,
        items: list[dict],
        total: float,
        id: str | None = None,
        status: str = "pending",
        paid_at: datetime | None = None
    ):
        super().__init__(id=id)
        self.customer_id = customer_id
        self.items = items
        self.total = total
        self.status = status
        self.paid_at = paid_at
        self.validate()

    def validate(self) -> None:
        """Validate order invariants."""
        if not self.customer_id:
            raise ValidationError("Order must have a customer")

        if not self.items:
            raise ValidationError("Order must have at least one item")

        if self.total <= 0:
            raise ValidationError("Order total must be positive")

        if self.status not in ["pending", "paid", "shipped", "cancelled"]:
            raise ValidationError(f"Invalid status: {self.status}")

    def mark_as_paid(self) -> None:
        """Mark order as paid."""
        if self.status == "cancelled":
            raise BusinessRuleViolation("Cannot pay a cancelled order")

        if self.paid_at is not None:
            raise BusinessRuleViolation("Order already paid")

        self.status = "paid"
        self.paid_at = datetime.now()

    def add_item(self, item: dict, price: float) -> None:
        """Add an item to the order."""
        if self.paid_at is not None:
            raise BusinessRuleViolation("Cannot modify paid order")

        self.items.append(item)
        self.total += price

    def __str__(self) -> str:
        return f"Order {self.id} ({self.status}) - ${self.total:.2f}"
```

**Pontos-Chave**:
- Herda de `EntityBase`
- `validate()` verifica invariantes
- Métodos de negócio (`mark_as_paid`, `add_item`)
- Exceções apropriadas (`ValidationError` vs `BusinessRuleViolation`)

---

## 2. Como Criar um ValueObject

**Problema**: Preciso de um objeto imutável que representa um valor (não tem identidade).

**Solução**:

```python
from forgebase.domain import ValueObjectBase, ValidationError
import re


class EmailAddress(ValueObjectBase):
    """
    Email address value object.

    Immutable value representing a validated email address.
    """

    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.validate()
        self._freeze()  # Torna imutável

    def validate(self) -> None:
        """Validate email format."""
        if not self.address:
            raise ValidationError("Email address cannot be empty")

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.address):
            raise ValidationError(f"Invalid email format: {self.address}")

    def to_dict(self) -> dict:
        return {"address": self.address}

    @classmethod
    def from_dict(cls, data: dict) -> 'EmailAddress':
        return cls(address=data["address"])

    def __str__(self) -> str:
        return self.address

    def __eq__(self, other) -> bool:
        if not isinstance(other, EmailAddress):
            return False
        return self.address == other.address

    def __hash__(self) -> int:
        return hash(self.address)


class Money(ValueObjectBase):
    """Money value object."""

    def __init__(self, amount: float, currency: str = "USD"):
        super().__init__()
        self.amount = amount
        self.currency = currency
        self.validate()
        self._freeze()

    def validate(self) -> None:
        if self.amount < 0:
            raise ValidationError("Money amount cannot be negative")

        if self.currency not in ["USD", "EUR", "BRL"]:
            raise ValidationError(f"Unsupported currency: {self.currency}")

    def add(self, other: 'Money') -> 'Money':
        """Add two money objects."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
```

**Pontos-Chave**:
- Herda de `ValueObjectBase`
- `_freeze()` garante imutabilidade
- Igualdade baseada em valor, não identidade
- Hashable (pode usar em sets/dicts)

---

## 3. Como Criar um UseCase

**Problema**: Preciso implementar um caso de uso de aplicação.

**Solução**:

```python
from forgebase.application import UseCaseBase, DTOBase


class PlaceOrderInput(DTOBase):
    """Input for placing an order."""

    def __init__(self, customer_id: str, items: list[dict]):
        self.customer_id = customer_id
        self.items = items

    def validate(self) -> None:
        if not self.customer_id:
            raise ValueError("Customer ID is required")
        if not self.items:
            raise ValueError("At least one item is required")

    def to_dict(self) -> dict:
        return {"customer_id": self.customer_id, "items": self.items}

    @classmethod
    def from_dict(cls, data: dict) -> 'PlaceOrderInput':
        return cls(
            customer_id=data["customer_id"],
            items=data["items"]
        )


class PlaceOrderOutput(DTOBase):
    """Output from placing an order."""

    def __init__(self, order_id: str, total: float, status: str):
        self.order_id = order_id
        self.total = total
        self.status = status

    def validate(self) -> None:
        pass

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "total": self.total,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PlaceOrderOutput':
        return cls(
            order_id=data["order_id"],
            total=data["total"],
            status=data["status"]
        )


class PlaceOrderUseCase(UseCaseBase):
    """
    Place a new order.

    Orchestrates:
        1. Validating customer exists
        2. Calculating order total
        3. Creating order entity
        4. Persisting order
        5. Sending confirmation notification
    """

    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        customer_repository: CustomerRepositoryPort,
        notification_service: NotificationServicePort
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.notification_service = notification_service

    def execute(self, input_dto: PlaceOrderInput) -> PlaceOrderOutput:
        """Execute order placement."""
        # 1. Validate input
        input_dto.validate()

        # 2. Validate customer exists
        customer = self.customer_repository.find_by_id(input_dto.customer_id)
        if customer is None:
            raise BusinessRuleViolation(
                f"Customer not found: {input_dto.customer_id}"
            )

        # 3. Calculate total
        total = sum(item["price"] * item["quantity"] for item in input_dto.items)

        # 4. Create order entity
        order = Order(
            customer_id=customer.id,
            items=input_dto.items,
            total=total
        )

        # 5. Validate business rules
        order.validate()

        # 6. Persist
        self.order_repository.save(order)

        # 7. Send notification
        self.notification_service.send(
            recipient=customer.email,
            subject="Order Confirmation",
            body=f"Your order {order.id} has been placed!"
        )

        # 8. Return output
        return PlaceOrderOutput(
            order_id=order.id,
            total=order.total,
            status=order.status
        )

    def _before_execute(self) -> None:
        """Hook before execution."""
        # Log, metrics, etc.
        pass

    def _after_execute(self) -> None:
        """Hook after execution."""
        pass

    def _on_error(self, error: Exception) -> None:
        """Hook on error."""
        # Error handling, rollback, etc.
        pass
```

**Pontos-Chave**:
- Herda de `UseCaseBase`
- Input/Output DTOs explícitos
- Dependencies injetadas via construtor
- Orquestração clara (steps numerados)
- Hooks para observabilidade

---

## 4. Como Criar um Port

**Problema**: Preciso definir um contrato de comunicação externa.

**Solução**:

```python
from abc import ABC, abstractmethod


class NotificationServicePort(ABC):
    """
    Port for sending notifications.

    Implementations can use email, SMS, push notifications, etc.
    """

    @abstractmethod
    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        **options
    ) -> None:
        """Send a notification."""
        pass

    @abstractmethod
    def send_bulk(
        self,
        recipients: list[str],
        subject: str,
        body: str
    ) -> dict[str, bool]:
        """
        Send notification to multiple recipients.

        Returns:
            Dict mapping recipient to success status
        """
        pass


class PaymentGatewayPort(ABC):
    """Port for processing payments."""

    @abstractmethod
    def charge(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str
    ) -> dict:
        """
        Charge a payment.

        Returns:
            Dict with transaction_id, status, etc.
        """
        pass

    @abstractmethod
    def refund(
        self,
        transaction_id: str,
        amount: float
    ) -> dict:
        """Issue a refund."""
        pass
```

**Pontos-Chave**:
- Herda de `ABC`
- Métodos `@abstractmethod`
- Docstring explicando contrato
- Foco em **o quê**, não **como**
- Type hints claros

---

## 5. Como Criar um Adapter

**Problema**: Preciso implementar um port com tecnologia específica.

**Solução**:

```python
import smtplib
from email.mime.text import MIMEText


class EmailNotificationAdapter(NotificationServicePort):
    """
    Email implementation of NotificationServicePort.

    Uses SMTP to send email notifications.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        **options
    ) -> None:
        """Send email notification."""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = recipient

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)

    def send_bulk(
        self,
        recipients: list[str],
        subject: str,
        body: str
    ) -> dict[str, bool]:
        """Send to multiple recipients."""
        results = {}
        for recipient in recipients:
            try:
                self.send(recipient, subject, body)
                results[recipient] = True
            except Exception:
                results[recipient] = False
        return results


class ConsoleNotificationAdapter(NotificationServicePort):
    """
    Console implementation (for testing/dev).

    Prints notifications to stdout instead of sending.
    """

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        **options
    ) -> None:
        print(f"[NOTIFICATION]")
        print(f"  To: {recipient}")
        print(f"  Subject: {subject}")
        print(f"  Body: {body}")

    def send_bulk(
        self,
        recipients: list[str],
        subject: str,
        body: str
    ) -> dict[str, bool]:
        for recipient in recipients:
            self.send(recipient, subject, body)
        return {r: True for r in recipients}
```

**Pontos-Chave**:
- Implementa o Port
- Recebe configuração via construtor
- Detalhes de implementação encapsulados
- Múltiplos adapters para mesmo port

---

## 6. Como Adicionar Observabilidade

**Problema**: Preciso de logs, métricas e tracing no meu UseCase.

**Solução**:

```python
from forgebase.observability import LogService, TrackMetrics
from forgebase.application.decorators import track_metrics


class PlaceOrderUseCase(UseCaseBase):
    def __init__(
        self,
        order_repository: OrderRepositoryPort,
        logger: LogService | None = None,
        metrics: TrackMetrics | None = None
    ):
        self.order_repository = order_repository
        self.logger = logger or LogService(name="place_order")
        self.metrics = metrics or TrackMetrics()

    @track_metrics(
        metric_name="place_order",
        track_duration=True,
        track_errors=True
    )
    def execute(self, input_dto: PlaceOrderInput) -> PlaceOrderOutput:
        # Log structured
        self.logger.info(
            "Placing order",
            customer_id=input_dto.customer_id,
            items_count=len(input_dto.items)
        )

        try:
            # ... lógica ...

            # Métricas customizadas
            self.metrics.increment("orders.placed", tags={"customer": input_dto.customer_id})
            self.metrics.gauge("order.total", total, tags={"customer": input_dto.customer_id})

            self.logger.info(
                "Order placed successfully",
                order_id=order.id,
                total=order.total
            )

            return PlaceOrderOutput(...)

        except Exception as e:
            self.logger.error(
                "Failed to place order",
                error=str(e),
                customer_id=input_dto.customer_id
            )
            self.metrics.increment("orders.errors")
            raise
```

**Com Context Manager para Performance:**

```python
def execute(self, input_dto):
    with self.metrics.measure("place_order.total"):
        # ... lógica ...

        with self.metrics.measure("place_order.validate_customer"):
            customer = self.customer_repository.find_by_id(...)

        with self.metrics.measure("place_order.create_order"):
            order = Order(...)

        with self.metrics.measure("place_order.persist"):
            self.order_repository.save(order)

    return output
```

**Pontos-Chave**:
- Logger e metrics injetados
- `@track_metrics` decorator para auto-instrumentação
- Logs estruturados (key-value pairs)
- Context managers para durations
- Error tracking

---

## 7. Como Escrever Testes Cognitivos

**Problema**: Preciso validar não apenas comportamento, mas também intenção.

**Solução**:

```python
from forgebase.testing import ForgeTestCase
from forgebase.testing.fakes import FakeRepository, FakeLogger, FakeMetricsCollector


class TestPlaceOrderUseCase(ForgeTestCase):
    def setUp(self):
        # Fakes
        self.fake_order_repo = FakeRepository()
        self.fake_customer_repo = FakeRepository()
        self.fake_logger = FakeLogger()
        self.fake_metrics = FakeMetricsCollector()

        # UseCase
        self.usecase = PlaceOrderUseCase(
            order_repository=self.fake_order_repo,
            customer_repository=self.fake_customer_repo,
            logger=self.fake_logger,
            metrics=self.fake_metrics
        )

        # Setup data
        self.customer = Customer(id="cust-123", name="Alice")
        self.fake_customer_repo.save(self.customer)

    def test_places_order_cognitive_validation(self):
        """Cognitive test: Validates intent, metrics, and performance."""
        # Captura intenção
        intent = "Place order for customer Alice with 2 items totaling $50"

        # Execute
        output = self.usecase.execute(PlaceOrderInput(
            customer_id="cust-123",
            items=[
                {"name": "Item 1", "price": 20, "quantity": 1},
                {"name": "Item 2", "price": 30, "quantity": 1}
            ]
        ))

        # 1. Validações tradicionais
        self.assertIsNotNone(output.order_id)
        self.assertEqual(output.total, 50.0)
        self.assertEqual(output.status, "pending")

        # 2. Validação cognitiva: Intent matches
        actual = f"Placed order {output.order_id} for customer Alice with total ${output.total}"
        self.assert_intent_matches(expected=intent, actual=actual, threshold=0.75)

        # 3. Validação de observabilidade: Métricas coletadas
        self.assert_metrics_collected({
            'place_order.duration': lambda v: v > 0,
            'place_order.count': lambda v: v == 1,
            'orders.placed': lambda v: v == 1
        })

        # 4. Validação de logs estruturados
        logs = self.fake_logger.get_logs(level='info')
        self.assertTrue(any('order placed' in log['message'].lower() for log in logs))
        self.assertTrue(any('order_id' in log.get('context', {}) for log in logs))

        # 5. Validação de performance
        self.assert_performance_within(
            lambda: self.usecase.execute(PlaceOrderInput(...)),
            max_duration_ms=100.0
        )

        # 6. Validação de persistência
        self.assertEqual(self.fake_order_repo.count(), 1)
        order = self.fake_order_repo.find_by_id(output.order_id)
        self.assertIsNotNone(order)
        self.assertEqual(len(order.items), 2)

    def test_rejects_invalid_customer(self):
        """Test business rule validation."""
        with self.assertRaises(BusinessRuleViolation) as ctx:
            self.usecase.execute(PlaceOrderInput(
                customer_id="invalid-id",
                items=[{"name": "Item", "price": 10, "quantity": 1}]
            ))

        self.assertIn("Customer not found", str(ctx.exception))

        # Validar métrica de erro
        self.assertEqual(self.fake_metrics.get_metric('orders.errors').value, 1)
```

**Pontos-Chave**:
- Herda de `ForgeTestCase`
- Usa fakes (não mocks)
- Validações em 6 níveis: behavior, intent, metrics, logs, performance, persistence
- Assertions cognitivas explícitas

---

## 8. Como Integrar com ForgeProcess

**Problema**: Preciso sincronizar specs YAML com código Python.

**Solução**:

### Passo 1: Criar Spec YAML

```yaml
# specs/place_order.yaml
version: "1.0"
usecase:
  name: PlaceOrder
  description: Place a new customer order

  inputs:
    - name: customer_id
      type: str
      required: true
    - name: items
      type: list
      required: true

  outputs:
    - name: order_id
      type: str
    - name: total
      type: float
    - name: status
      type: str

  business_rules:
    - Customer must exist
    - Order must have at least one item
    - Total must be calculated correctly
```

### Passo 2: Gerar Código

```python
from forgebase.integration import YAMLSync

sync = YAMLSync()

# Parse YAML
spec = sync.parse_yaml("specs/place_order.yaml")

# Generate code skeleton
code = sync.generate_code(spec)

# Write to file
with open("src/application/place_order_usecase.py", "w") as f:
    f.write(code)
```

### Passo 3: Validar Consistência

```python
# Detect drift
drift = sync.detect_drift(PlaceOrderUseCase, spec)

if drift:
    print("⚠️  Drift detected:")
    for issue in drift:
        print(f"  - {issue}")
else:
    print("✓ Code matches YAML spec")
```

### Passo 4: Intent Tracking

```python
from forgebase.integration import IntentTracker

tracker = IntentTracker()

# Capture intent (from ForgeProcess)
intent_id = tracker.capture_intent(
    description="Place order for customer Alice",
    expected_outcome="Order created successfully",
    source="forgeprocess"
)

# Execute
output = usecase.execute(input_dto)

# Record execution
tracker.record_execution(
    intent_id=intent_id,
    actual_outcome=f"Order {output.order_id} created",
    success=True
)

# Validate coherence
report = tracker.validate_coherence(intent_id)
print(f"Coherence: {report.coherence_level.value} ({report.similarity_score:.1%})")
```

**Pontos-Chave**:
- YAML define especificação
- YAMLSync gera código e valida
- IntentTracker valida coerência
- Feedback loop para ForgeProcess

---

## 9. Como Criar um Repository Customizado

**Problema**: Preciso implementar um repository para tecnologia específica (MongoDB, Redis, etc.).

**Solução**:

```python
from forgebase.infrastructure.repository import RepositoryBase
from pymongo import MongoClient


class MongoDBRepository(RepositoryBase[T]):
    """MongoDB implementation of RepositoryBase."""

    def __init__(
        self,
        connection_string: str,
        database: str,
        collection: str,
        entity_type: Type[T]
    ):
        self.client = MongoClient(connection_string)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.entity_type = entity_type

    def save(self, entity: T) -> None:
        entity.validate()

        doc = {
            "_id": entity.id,
            **entity.to_dict()
        }

        self.collection.replace_one(
            {"_id": entity.id},
            doc,
            upsert=True
        )

    def find_by_id(self, id: str) -> T | None:
        doc = self.collection.find_one({"_id": id})
        if doc is None:
            return None

        return self.entity_type.from_dict(doc)

    def find_all(self) -> list[T]:
        docs = self.collection.find()
        return [self.entity_type.from_dict(doc) for doc in docs]

    def delete(self, id: str) -> None:
        self.collection.delete_one({"_id": id})

    def exists(self, id: str) -> bool:
        return self.collection.count_documents({"_id": id}) > 0

    def close(self):
        """Cleanup connection."""
        self.client.close()


# Usage
repository = MongoDBRepository(
    connection_string="mongodb://localhost:27017",
    database="my_app",
    collection="orders",
    entity_type=Order
)
```

**Pontos-Chave**:
- Implementa `RepositoryBase[T]`
- Generic type para entidade
- Métodos CRUD completos
- Cleanup resources (close)

---

## 10. Como Adicionar Validações Customizadas

**Problema**: Preciso de validações reutilizáveis no domínio.

**Solução**:

```python
# src/domain/validators.py
from forgebase.domain import ValidationError


class DomainValidators:
    """Reusable domain validators."""

    @staticmethod
    def not_empty(value: str, field_name: str = "Field") -> None:
        """Validate string is not empty."""
        if not value or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str = "Field") -> None:
        """Validate minimum length."""
        if len(value) < min_len:
            raise ValidationError(
                f"{field_name} must be at least {min_len} characters"
            )

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "Field") -> None:
        """Validate maximum length."""
        if len(value) > max_len:
            raise ValidationError(
                f"{field_name} must be at most {max_len} characters"
            )

    @staticmethod
    def in_range(value: float, min_val: float, max_val: float, field_name: str = "Field") -> None:
        """Validate value is in range."""
        if not (min_val <= value <= max_val):
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}"
            )

    @staticmethod
    def positive(value: float, field_name: str = "Field") -> None:
        """Validate value is positive."""
        if value <= 0:
            raise ValidationError(f"{field_name} must be positive")

    @staticmethod
    def email_format(value: str, field_name: str = "Email") -> None:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError(f"Invalid {field_name} format: {value}")


# Usage in Entity
class Product(EntityBase):
    def __init__(self, name: str, price: float, description: str = ""):
        super().__init__()
        self.name = name
        self.price = price
        self.description = description
        self.validate()

    def validate(self) -> None:
        DomainValidators.not_empty(self.name, "Product name")
        DomainValidators.max_length(self.name, 100, "Product name")
        DomainValidators.positive(self.price, "Product price")

        if self.description:
            DomainValidators.max_length(self.description, 500, "Description")
```

**Pontos-Chave**:
- Validators centralizados e reutilizáveis
- Mensagens de erro consistentes
- Fácil testar isoladamente
- Composição em entities

---

## 11. Como Usar Dependency Injection

**Problema**: Preciso wirear dependências sem acoplamento.

**Solução**:

```python
# main.py com DI Container
from forgebase.infrastructure.di_container import DIContainer
from forgebase.infrastructure.configuration import ConfigLoader


def setup_dependencies(config: dict) -> DIContainer:
    """Setup DI container from configuration."""
    container = DIContainer()

    # Register logger
    container.register(
        LogService,
        lambda c: LogService(
            name="my-app",
            level=config.get("log_level", "INFO")
        ),
        singleton=True
    )

    # Register metrics
    container.register(
        TrackMetrics,
        lambda c: TrackMetrics(),
        singleton=True
    )

    # Register repositories
    container.register(
        OrderRepositoryPort,
        lambda c: JSONRepository(
            file_path=config.get("orders_file", "data/orders.json"),
            entity_type=Order,
            logger=c.resolve(LogService)
        ),
        singleton=True
    )

    container.register(
        CustomerRepositoryPort,
        lambda c: JSONRepository(
            file_path=config.get("customers_file", "data/customers.json"),
            entity_type=Customer,
            logger=c.resolve(LogService)
        ),
        singleton=True
    )

    # Register use cases
    container.register(
        PlaceOrderUseCase,
        lambda c: PlaceOrderUseCase(
            order_repository=c.resolve(OrderRepositoryPort),
            customer_repository=c.resolve(CustomerRepositoryPort),
            logger=c.resolve(LogService),
            metrics=c.resolve(TrackMetrics)
        )
    )

    return container


def main():
    # Load config
    config = ConfigLoader.load("config.yaml")

    # Setup DI
    container = setup_dependencies(config)

    # Resolve use case (dependencies auto-injected)
    usecase = container.resolve(PlaceOrderUseCase)

    # Execute
    output = usecase.execute(PlaceOrderInput(...))
    print(f"Order placed: {output.order_id}")


if __name__ == "__main__":
    main()
```

**Com Configuration-Based DI:**

```yaml
# config.yaml
dependencies:
  logger:
    type: stdout
    level: info

  repositories:
    orders:
      type: json
      path: data/orders.json
    customers:
      type: json
      path: data/customers.json

  metrics:
    type: prometheus
    endpoint: http://localhost:9090
```

**Pontos-Chave**:
- Centraliza wiring em um lugar
- Singleton para services compartilhados
- Factories com resolução recursiva
- Configuration-driven

---

## 12. Como Adicionar um Novo Adapter

**Problema**: Preciso adicionar um novo tipo de adapter (ex: gRPC, GraphQL).

**Solução**:

```python
# src/adapters/grpc/grpc_adapter.py
import grpc
from concurrent import futures
from forgebase.adapters import AdapterBase


class GRPCAdapter(AdapterBase):
    """
    gRPC adapter for exposing UseCases via gRPC.

    Maps gRPC service methods to UseCase executions.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10
    ):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self._usecases = {}

    def name(self) -> str:
        return "GRPCAdapter"

    def module(self) -> str:
        return "forgebase.adapters.grpc"

    def register_usecase(
        self,
        service_name: str,
        method_name: str,
        usecase: UseCaseBase
    ):
        """Register a UseCase to be exposed via gRPC."""
        key = f"{service_name}.{method_name}"
        self._usecases[key] = usecase

    def start(self):
        """Start gRPC server."""
        self.server.add_insecure_port(f"{self.host}:{self.port}")
        self.server.start()
        print(f"gRPC server listening on {self.host}:{self.port}")

    def stop(self):
        """Stop gRPC server."""
        self.server.stop(grace=5)


# Usage
adapter = GRPCAdapter(port=50051)

adapter.register_usecase(
    service_name="OrderService",
    method_name="PlaceOrder",
    usecase=place_order_usecase
)

adapter.start()
```

**Pontos-Chave**:
- Herda de `AdapterBase`
- Implementa `name()` e `module()`
- Encapsula tecnologia específica (gRPC)
- Registra UseCases dinamicamente

---

## 🎯 Próximos Passos

Explore mais:
- **[Getting Started Guide](getting-started.md)** — Tutorial completo
- **[Testing Guide](testing-guide.md)** — Testes cognitivos detalhados
- **[ADRs](adr/)** — Decisões arquiteturais
- **[Examples](../examples/)** — Exemplos completos executáveis

---

**Feliz Forjamento! 🔨**

*"Cada receita é uma história de transformar pensamento em estrutura."*
