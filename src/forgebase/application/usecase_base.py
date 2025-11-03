"""
Base class for all use cases in ForgeBase.

Use cases orchestrate application logic, coordinating between domain entities
and infrastructure through ports. They represent the entry points for
application functionality.

Author: Jorge, The Forge
Created: 2025-11-03
"""

from abc import ABC, abstractmethod
from typing import Any


class UseCaseBase(ABC):
    """
    Abstract base class for all use cases (ValueTracks).

    Use cases implement application logic by orchestrating domain entities
    and communicating with external systems through ports. They remain
    framework-independent and testable.

    Design Decisions:
        - Lifecycle hooks (_before_execute, _after_execute, _on_error) enable
          cross-cutting concerns like logging, metrics, transactions
        - Abstract execute() enforces consistent interface
        - No return type specified - use cases return domain-appropriate types

    :Example:

        class CreateUserUseCase(UseCaseBase):
            def __init__(self, user_repository: UserRepositoryPort):
                self.user_repository = user_repository

            def execute(self, input_dto: CreateUserDTO) -> UserDTO:
                # Validate input
                input_dto.validate()

                # Create domain entity
                user = User(None, input_dto.email, input_dto.name)
                user.validate()

                # Persist
                self.user_repository.save(user)

                return UserDTO.from_entity(user)

    .. note::
        Override lifecycle hooks for cross-cutting concerns.

    .. seealso::
        :class:`PortBase` - For external communication contracts
    """

    def _before_execute(self) -> None:
        """
        Hook called before execute().

        Override this for pre-execution logic like:
        - Starting transactions
        - Beginning metric collection
        - Logging execution start

        :Example:

            def _before_execute(self) -> None:
                self.logger.info("Starting use case execution")
                self.metrics.start_timer("usecase_duration")
        """
        pass

    def _after_execute(self) -> None:
        """
        Hook called after successful execute().

        Override this for post-execution logic like:
        - Committing transactions
        - Recording metrics
        - Logging success

        :Example:

            def _after_execute(self) -> None:
                self.metrics.stop_timer("usecase_duration")
                self.logger.info("Use case completed successfully")
        """
        pass

    def _on_error(self, error: Exception) -> None:
        """
        Hook called when execute() raises an exception.

        Override this for error handling like:
        - Rolling back transactions
        - Logging errors
        - Recording failure metrics

        :param error: The exception that was raised
        :type error: Exception

        :Example:

            def _on_error(self, error: Exception) -> None:
                self.logger.error(f"Use case failed: {error}")
                self.metrics.increment("usecase_errors")
        """
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the use case logic.

        This method must be implemented by all use case subclasses.
        It contains the core application logic, orchestrating domain
        entities and ports.

        :param args: Positional arguments (typically DTOs)
        :param kwargs: Keyword arguments
        :return: Use case result (typically a DTO)
        :rtype: Any

        :Example:

            def execute(self, input_dto: CreateOrderDTO) -> OrderDTO:
                # 1. Validate input
                input_dto.validate()

                # 2. Load domain entities
                customer = self.customer_repo.find_by_id(input_dto.customer_id)
                if not customer:
                    raise EntityNotFoundError("Customer not found")

                # 3. Execute domain logic
                order = Order.create(customer, input_dto.items)
                order.validate()

                # 4. Persist
                self.order_repo.save(order)

                # 5. Return result
                return OrderDTO.from_entity(order)
        """
        pass
