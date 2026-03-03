# ForgeBase - Practical Recipes

> Ready-made solutions for common development cases

This cookbook provides practical solutions for frequent use cases in ForgeBase. Each recipe is self-contained and can be copied/adapted for your project.

---

## Table of Contents

1. [How to Create an Entity](#1-how-to-create-an-entity)
2. [How to Create a ValueObject](#2-how-to-create-a-valueobject)
3. [How to Create a UseCase](#3-how-to-create-a-usecase)
4. [How to Create a Port](#4-how-to-create-a-port)
5. [How to Create an Adapter](#5-how-to-create-an-adapter)
6. [How to Add Observability](#6-how-to-add-observability)
7. [How to Write Cognitive Tests](#7-how-to-write-cognitive-tests)
8. [How to Integrate with ForgeProcess](#8-how-to-integrate-with-forgeprocess)
9. [How to Create a Custom Repository](#9-how-to-create-a-custom-repository)
10. [How to Add Custom Validations](#10-how-to-add-custom-validations)
11. [How to Use Dependency Injection](#11-how-to-use-dependency-injection)
12. [How to Add a New Adapter](#12-how-to-add-a-new-adapter)

---

## 1. How to Create an Entity

**Problem**: I need to create a domain entity with identity and invariants.

**Solution**:

```python
from forge_base.domain import EntityBase, ValidationError, BusinessRuleViolation
from datetime import datetime


class Order(EntityBase):
    """
    Order Entity.

    Represents an order with items, total, and status.

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
            raise BusinessRuleViolation("Order has already been paid")

        self.status = "paid"
        self.paid_at = datetime.now()

    def add_item(self, item: dict, price: float) -> None:
        """Add item to order."""
        if self.paid_at is not None:
            raise BusinessRuleViolation("Cannot modify a paid order")

        self.items.append(item)
        self.total += price

    def __str__(self) -> str:
        return f"Order {self.id} ({self.status}) - ${self.total:.2f}"
```

**Key Points**:
- Inherits from `EntityBase`
- `validate()` checks invariants
- Business methods (`mark_as_paid`, `add_item`)
- Appropriate exceptions (`ValidationError` vs `BusinessRuleViolation`)

---

## 2. How to Create a ValueObject

**Problem**: I need an immutable object that represents a value (has no identity).

**Solution**:

```python
from forge_base.domain import ValueObjectBase, ValidationError
import re


class EmailAddress(ValueObjectBase):
    """
    Value object for email address.

    Immutable value representing a validated email.
    """

    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.validate()
        self._freeze()  # Makes it immutable

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
    """Value object for monetary values."""

    def __init__(self, amount: float, currency: str = "BRL"):
        super().__init__()
        self.amount = amount
        self.currency = currency
        self.validate()
        self._freeze()

    def validate(self) -> None:
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")

        if self.currency not in ["USD", "EUR", "BRL"]:
            raise ValidationError(f"Unsupported currency: {self.currency}")

    def add(self, other: 'Money') -> 'Money':
        """Add two monetary values."""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
```

**Key Points**:
- Inherits from `ValueObjectBase`
- `_freeze()` ensures immutability
- Equality based on value, not identity
- Hashable (can be used in sets/dicts)

---

## 3. How to Create a UseCase

**Problem**: I need to implement an application use case.

**Solution**:

```python
from forge_base.application import UseCaseBase, DTOBase


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
    """Output from order creation."""

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
        1. Validate that customer exists
        2. Calculate order total
        3. Create order entity
        4. Persist order
        5. Send confirmation notification
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
        """Execute order creation."""
        # 1. Validate input
        input_dto.validate()

        # 2. Validate that customer exists
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
        pass

    def _after_execute(self) -> None:
        """Hook after execution."""
        pass

    def _on_error(self, error: Exception) -> None:
        """Hook on error."""
        pass
```

**Key Points**:
- Inherits from `UseCaseBase`
- Explicit Input/Output DTOs
- Dependencies injected via constructor
- Clear orchestration (numbered steps)
- Hooks for observability

---

## 4. How to Create a Port

**Problem**: I need to define an external communication contract.

**Solution**:

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
    """Port for payment processing."""

    @abstractmethod
    def charge(
        self,
        amount: float,
        currency: str,
        payment_method: str,
        customer_id: str
    ) -> dict:
        """
        Process a payment.

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
        """Process a refund."""
        pass
```

**Key Points**:
- Inherits from `ABC`
- `@abstractmethod` methods
- Docstring explaining the contract
- Focus on **what**, not **how**
- Clear type hints

---

## 5. How to Create an Adapter

**Problem**: I need to implement a port with specific technology.

**Solution**:

```python
import smtplib
from email.mime.text import MIMEText


class EmailNotificationAdapter(NotificationServicePort):
    """
    Email implementation of NotificationServicePort.

    Uses SMTP to send notifications via email.
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
        """Send notification via email."""
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

    Prints notifications to stdout instead of sending them.
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

**Key Points**:
- Implements the Port
- Receives configuration via constructor
- Implementation details encapsulated
- Multiple adapters for the same port

---

## 6. How to Add Observability

**Problem**: I need logs, metrics, and tracing in my UseCase.

**Solution**:

```python
from forge_base.observability import LogService, TrackMetrics
from forge_base.application.decorators import track_metrics


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
        # Structured logging
        self.logger.info(
            "Creating order",
            customer_id=input_dto.customer_id,
            items_count=len(input_dto.items)
        )

        try:
            # ... logic ...

            # Custom metrics
            self.metrics.increment("orders.placed", tags={"customer": input_dto.customer_id})
            self.metrics.gauge("order.total", total, tags={"customer": input_dto.customer_id})

            self.logger.info(
                "Order created successfully",
                order_id=order.id,
                total=order.total
            )

            return PlaceOrderOutput(...)

        except Exception as e:
            self.logger.error(
                "Failed to create order",
                error=str(e),
                customer_id=input_dto.customer_id
            )
            self.metrics.increment("orders.errors")
            raise
```

**With Context Manager for Performance:**

```python
def execute(self, input_dto):
    with self.metrics.measure("place_order.total"):
        # ... logic ...

        with self.metrics.measure("place_order.validate_customer"):
            customer = self.customer_repository.find_by_id(...)

        with self.metrics.measure("place_order.create_order"):
            order = Order(...)

        with self.metrics.measure("place_order.persist"):
            self.order_repository.save(order)

    return output
```

**Key Points**:
- Logger and metrics injected
- `@track_metrics` decorator for auto-instrumentation
- Structured logs (key-value pairs)
- Context managers for durations
- Error tracking

---

## 7. How to Write Cognitive Tests

See the [Testing Guide](testing-guide.md) for complete documentation on cognitive tests.

---

## 8. How to Integrate with ForgeProcess

**Problem**: I need to synchronize YAML specs with Python code.

**Solution**:

### Step 1: Create YAML Spec

```yaml
# specs/place_order.yaml
version: "1.0"
usecase:
  name: PlaceOrder
  description: Create a new customer order

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

### Step 2: Generate Code

```python
from forge_base.integration import YAMLSync

sync = YAMLSync()

# Parse YAML
spec = sync.parse_yaml("specs/place_order.yaml")

# Generate skeleton code
code = sync.generate_code(spec)

# Write to file
with open("src/application/place_order_usecase.py", "w") as f:
    f.write(code)
```

### Step 3: Validate Consistency

```python
# Detect drift
drift = sync.detect_drift(PlaceOrderUseCase, spec)

if drift:
    print("Drift detected:")
    for issue in drift:
        print(f"  - {issue}")
else:
    print("Code matches the YAML spec")
```

---

## 9. How to Create a Custom Repository

**Problem**: I need to implement a repository for a specific technology (MongoDB, Redis, etc.).

**Solution**:

```python
from forge_base.infrastructure.repository import RepositoryBase
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
        """Clean up connection."""
        self.client.close()


# Usage
repository = MongoDBRepository(
    connection_string="mongodb://localhost:27017",
    database="my_app",
    collection="orders",
    entity_type=Order
)
```

**Key Points**:
- Implements `RepositoryBase[T]`
- Generic type for entity
- Complete CRUD methods
- Cleanup resources (close)

---

## 10. How to Add Custom Validations

**Problem**: I need reusable validations in the domain.

**Solution**:

```python
# src/domain/validators.py
from forge_base.domain import ValidationError


class DomainValidators:
    """Reusable domain validators."""

    @staticmethod
    def not_empty(value: str, field_name: str = "Field") -> None:
        """Validate that string is not empty."""
        if not value or not value.strip():
            raise ValidationError(f"{field_name} cannot be empty")

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str = "Field") -> None:
        """Validate minimum length."""
        if len(value) < min_len:
            raise ValidationError(
                f"{field_name} must have at least {min_len} characters"
            )

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "Field") -> None:
        """Validate maximum length."""
        if len(value) > max_len:
            raise ValidationError(
                f"{field_name} must have at most {max_len} characters"
            )

    @staticmethod
    def in_range(value: float, min_val: float, max_val: float, field_name: str = "Field") -> None:
        """Validate that value is within range."""
        if not (min_val <= value <= max_val):
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}"
            )

    @staticmethod
    def positive(value: float, field_name: str = "Field") -> None:
        """Validate that value is positive."""
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

**Key Points**:
- Centralized and reusable validators
- Consistent error messages
- Easy to test in isolation
- Composition in entities

---

## 11. How to Use Dependency Injection

**Problem**: I need to connect dependencies without coupling.

**Solution**:

```python
# main.py with DI Container
from forge_base.infrastructure.configuration import ConfigLoader


def setup_dependencies(config: dict) -> dict:
    """Set up dependencies from configuration."""

    # Logger
    logger = LogService(
        name="my-app",
        level=config.get("log_level", "INFO")
    )

    # Metrics
    metrics = TrackMetrics()

    # Repositories
    order_repository = JSONRepository(
        file_path=config.get("orders_file", "data/orders.json"),
        entity_type=Order,
        logger=logger
    )

    customer_repository = JSONRepository(
        file_path=config.get("customers_file", "data/customers.json"),
        entity_type=Customer,
        logger=logger
    )

    # Use cases
    place_order_usecase = PlaceOrderUseCase(
        order_repository=order_repository,
        customer_repository=customer_repository,
        logger=logger,
        metrics=metrics
    )

    return {
        "logger": logger,
        "metrics": metrics,
        "order_repository": order_repository,
        "customer_repository": customer_repository,
        "place_order_usecase": place_order_usecase
    }


def main():
    # Load config
    config = ConfigLoader.load("config.yaml")

    # Set up DI
    deps = setup_dependencies(config)

    # Use the use case
    usecase = deps["place_order_usecase"]

    # Execute
    output = usecase.execute(PlaceOrderInput(...))
    print(f"Order created: {output.order_id}")


if __name__ == "__main__":
    main()
```

**Key Points**:
- Centralizes wiring in one place
- Configuration-driven
- Easy to swap implementations

---

## 12. How to Add a New Adapter

**Problem**: I need to add a new type of adapter (e.g., gRPC, GraphQL).

**Solution**:

```python
# src/adapters/grpc/grpc_adapter.py
import grpc
from concurrent import futures
from forge_base.adapters import AdapterBase


class GRPCAdapter(AdapterBase):
    """
    gRPC Adapter to expose UseCases via gRPC.

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
        return "forge_base.adapters.grpc"

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

**Key Points**:
- Inherits from `AdapterBase`
- Implements `name()` and `module()`
- Encapsulates specific technology (gRPC)
- Registers UseCases dynamically

---

## Next Steps

Explore more:
- **[Quick Start](quick-start.md)** -- Complete tutorial
- **[Testing Guide](testing-guide.md)** -- Detailed cognitive tests
- **[ADRs](../adr/)** -- Architectural decisions
- **[Examples](../../examples/)** -- Complete runnable examples

---

**Happy Forging!**

*"Each recipe is a story of transforming thought into structure."*
