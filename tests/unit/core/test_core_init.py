"""
Unit tests for ForgeBase Core Initialization.

Tests the bootstrap sequence, dependency injection, and lifecycle management.

:author: ForgeBase Development Team
:since: 2025-11-03
"""

import unittest
from unittest.mock import MagicMock, patch

from forge_base.application.usecase_base import UseCaseBase
from forge_base.core_init import DependencyContainer, ForgeBaseCore


class TestDependencyContainer(unittest.TestCase):
    """Test cases for DependencyContainer."""

    def setUp(self):
        """Set up test fixtures."""
        self.container = DependencyContainer()

    def test_register_and_get_singleton(self):
        """Test registering and retrieving a singleton service."""
        service = MagicMock()
        self.container.register('test_service', service, singleton=True)

        retrieved = self.container.get('test_service')
        self.assertIs(retrieved, service)

    def test_register_and_get_non_singleton(self):
        """Test registering and retrieving a non-singleton service."""
        service = MagicMock()
        self.container.register('test_service', service, singleton=False)

        retrieved = self.container.get('test_service')
        self.assertIs(retrieved, service)

    def test_get_nonexistent_service_raises_error(self):
        """Test that getting nonexistent service raises KeyError."""
        with self.assertRaises(KeyError) as context:
            self.container.get('nonexistent')

        self.assertIn('not found', str(context.exception))

    def test_has_service(self):
        """Test checking if service exists."""
        service = MagicMock()
        self.container.register('test_service', service)

        self.assertTrue(self.container.has('test_service'))
        self.assertFalse(self.container.has('nonexistent'))

    def test_clear_services(self):
        """Test clearing all services."""
        self.container.register('service1', MagicMock())
        self.container.register('service2', MagicMock(), singleton=False)

        self.container.clear()

        self.assertFalse(self.container.has('service1'))
        self.assertFalse(self.container.has('service2'))


class MockUseCase(UseCaseBase):
    """Mock UseCase for testing."""

    def execute(self, **kwargs):  # noqa: ARG002
        """Execute mock usecase."""
        return "mock_result"

    def _before_execute(self) -> None:
        """Hook before execution."""
        pass

    def _after_execute(self) -> None:
        """Hook after execution."""
        pass

    def _on_error(self, error: Exception) -> None:
        """Hook on error."""
        pass


class TestForgeBaseCore(unittest.TestCase):
    """Test cases for ForgeBaseCore."""

    def setUp(self):
        """Set up test fixtures."""
        self.core = ForgeBaseCore()

    def tearDown(self):
        """Clean up after tests."""
        if self.core._initialized:
            self.core.shutdown()

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_bootstrap_success(self, mock_atexit, mock_signal):
        """Test successful bootstrap sequence."""
        self.core.bootstrap()

        self.assertTrue(self.core._initialized)
        self.assertTrue(self.core.container.has('config'))
        self.assertTrue(self.core.container.has('logger'))
        self.assertTrue(self.core.container.has('metrics'))
        self.assertTrue(self.core.container.has('tracer'))

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_bootstrap_twice_raises_error(self, mock_atexit, mock_signal):
        """Test that bootstrapping twice raises RuntimeError."""
        self.core.bootstrap()

        with self.assertRaises(RuntimeError) as context:
            self.core.bootstrap()

        self.assertIn('already initialized', str(context.exception))

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_register_and_get_usecase(self, mock_atexit, mock_signal):
        """Test registering and retrieving a UseCase."""
        self.core.bootstrap()

        usecase = MockUseCase()
        self.core.register_usecase('test_usecase', usecase)

        retrieved = self.core.get_usecase('test_usecase')
        self.assertIs(retrieved, usecase)

    def test_get_nonexistent_usecase_raises_error(self):
        """Test that getting nonexistent UseCase raises KeyError."""
        with self.assertRaises(KeyError) as context:
            self.core.get_usecase('nonexistent')

        self.assertIn('not found', str(context.exception))

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_list_usecases(self, mock_atexit, mock_signal):
        """Test listing all registered UseCases."""
        self.core.bootstrap()

        usecase1 = MockUseCase()
        usecase2 = MockUseCase()

        self.core.register_usecase('usecase1', usecase1)
        self.core.register_usecase('usecase2', usecase2)

        usecases = self.core.list_usecases()

        self.assertEqual(len(usecases), 2)
        self.assertIn('usecase1', usecases)
        self.assertIn('usecase2', usecases)

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_register_and_get_adapter(self, mock_atexit, mock_signal):
        """Test registering and retrieving an adapter."""
        self.core.bootstrap()

        adapter = MagicMock()
        self.core.register_adapter('test_adapter', adapter)

        retrieved = self.core.get_adapter('test_adapter')
        self.assertIs(retrieved, adapter)

    def test_get_nonexistent_adapter_raises_error(self):
        """Test that getting nonexistent adapter raises KeyError."""
        with self.assertRaises(KeyError) as context:
            self.core.get_adapter('nonexistent')

        self.assertIn('not found', str(context.exception))

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_health_check_before_bootstrap(self, mock_atexit, mock_signal):
        """Test health check before bootstrap shows missing components."""
        health = self.core.health_check()

        self.assertFalse(health['healthy'])
        self.assertEqual(health['components']['config']['status'], 'missing')
        self.assertEqual(health['components']['logging']['status'], 'missing')

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_health_check_after_bootstrap(self, mock_atexit, mock_signal):
        """Test health check after bootstrap shows healthy system."""
        self.core.bootstrap()

        health = self.core.health_check()

        self.assertTrue(health['healthy'])
        self.assertEqual(health['components']['config']['status'], 'ok')
        self.assertEqual(health['components']['logging']['status'], 'ok')
        self.assertEqual(health['components']['metrics']['status'], 'ok')
        self.assertEqual(health['components']['tracer']['status'], 'ok')

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_info_returns_system_information(self, mock_atexit, mock_signal):
        """Test that info() returns comprehensive system information."""
        self.core.bootstrap()

        usecase = MockUseCase()
        self.core.register_usecase('test_usecase', usecase)

        adapter = MagicMock()
        self.core.register_adapter('test_adapter', adapter)

        info = self.core.info()

        self.assertTrue(info['initialized'])
        self.assertEqual(info['usecases']['count'], 1)
        self.assertIn('test_usecase', info['usecases']['names'])
        self.assertEqual(info['adapters']['count'], 1)
        self.assertIn('test_adapter', info['adapters']['names'])
        self.assertIn('logger', info['services']['registered'])

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_shutdown_handlers(self, mock_atexit, mock_signal):
        """Test custom shutdown handlers are executed."""
        self.core.bootstrap()

        handler_called = []

        def custom_handler():
            handler_called.append(True)

        self.core.add_shutdown_handler(custom_handler)
        self.core.shutdown()

        self.assertTrue(handler_called)

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_shutdown_stops_adapters(self, mock_atexit, mock_signal):
        """Test that shutdown stops registered adapters."""
        self.core.bootstrap()

        adapter = MagicMock()
        adapter.stop = MagicMock()

        self.core.register_adapter('test_adapter', adapter)
        self.core.shutdown()

        adapter.stop.assert_called_once()

    @patch('forge_base.core_init.signal')
    @patch('forge_base.core_init.atexit')
    def test_shutdown_when_not_initialized(self, mock_atexit, mock_signal):
        """Test that shutdown without initialization is safe."""
        # Should not raise any errors
        self.core.shutdown()

        self.assertFalse(self.core._initialized)


if __name__ == '__main__':
    unittest.main()
