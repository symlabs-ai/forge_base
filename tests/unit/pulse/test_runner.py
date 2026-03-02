from typing import Any

import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.collector import NoOpCollector, PulseCollector
from forge_base.pulse.context import ExecutionContext, _current_context, get_context
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.meta import pulse_meta
from forge_base.pulse.runner import UseCaseRunner


class _EchoUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


class _ContextCapture(UseCaseBase[str, str]):
    captured: ExecutionContext | None = None

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        self.__class__.captured = get_context()
        return input_dto


class _FailUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        raise ValueError("boom")


class _SpyCollector:
    def __init__(self) -> None:
        self.started: list[ExecutionContext] = []
        self.succeeded: list[tuple[ExecutionContext, Any]] = []
        self.errors: list[tuple[ExecutionContext, Exception]] = []
        self.finished: list[ExecutionContext] = []

    def on_start(self, context: ExecutionContext) -> None:
        self.started.append(context)

    def on_success(self, context: ExecutionContext, result: Any) -> None:
        self.succeeded.append((context, result))

    def on_error(self, context: ExecutionContext, error: Exception) -> None:
        self.errors.append((context, error))

    def on_finish(self, context: ExecutionContext) -> None:
        self.finished.append(context)


@pytest.mark.pulse
class TestUseCaseRunner:
    def setup_method(self):
        self._token = _current_context.set(None)

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_off_passthrough(self):
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF)
        assert runner.run("hello") == "hello"

    def test_off_no_context_set(self):
        uc = _ContextCapture()
        _ContextCapture.captured = None
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF)
        runner.run("hello")
        assert _ContextCapture.captured is None

    def test_basic_with_spy_collector(self):
        spy = _SpyCollector()
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=spy)
        result = runner.run("hello")
        assert result == "hello"
        assert len(spy.started) == 1
        assert len(spy.succeeded) == 1
        assert spy.succeeded[0][1] == "hello"
        assert len(spy.finished) == 1
        assert len(spy.errors) == 0

    def test_context_visible_during_execute(self):
        uc = _ContextCapture()
        _ContextCapture.captured = None
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("hello")
        assert _ContextCapture.captured is not None
        assert _ContextCapture.captured.level == MonitoringLevel.BASIC
        assert _ContextCapture.captured.use_case_name == "_ContextCapture"

    def test_ctx_overrides(self):
        uc = _ContextCapture()
        _ContextCapture.captured = None
        runner = UseCaseRunner(uc, level=MonitoringLevel.STANDARD)
        runner.run("hello", correlation_id="custom-42")
        assert _ContextCapture.captured is not None
        assert _ContextCapture.captured.correlation_id == "custom-42"

    def test_error_handling(self):
        spy = _SpyCollector()
        uc = _FailUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC, collector=spy)
        with pytest.raises(ValueError, match="boom"):
            runner.run("hello")
        assert len(spy.errors) == 1
        assert len(spy.finished) == 1
        assert len(spy.succeeded) == 0

    def test_context_cleanup_after_run(self):
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("hello")
        assert get_context() is None

    def test_context_cleanup_after_error(self):
        uc = _FailUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        with pytest.raises(ValueError):
            runner.run("hello")
        assert get_context() is None

    def test_default_collector_is_noop(self):
        uc = _EchoUseCase()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        assert isinstance(runner._collector, NoOpCollector)

    def test_spy_satisfies_collector_protocol(self):
        spy = _SpyCollector()
        assert isinstance(spy, PulseCollector)


@pulse_meta(subtrack="checkout", feature="pay", value_track="revenue")
class _DecoratedCapture(UseCaseBase[str, str]):
    captured: ExecutionContext | None = None

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        self.__class__.captured = get_context()
        return input_dto


@pulse_meta()
class _EmptyDecoratedCapture(UseCaseBase[str, str]):
    captured: ExecutionContext | None = None

    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        self.__class__.captured = get_context()
        return input_dto


@pytest.mark.pulse
class TestUseCaseRunnerWithDecorator:
    def setup_method(self):
        self._token = _current_context.set(None)
        _DecoratedCapture.captured = None
        _EmptyDecoratedCapture.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_decorator_overrides_subtrack(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.subtrack == "checkout"

    def test_decorator_overrides_feature(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.feature == "pay"

    def test_decorator_overrides_value_track(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.value_track == "revenue"

    def test_mapping_source_decorator(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.mapping_source == "decorator"

    def test_empty_decorator_keeps_heuristic(self):
        uc = _EmptyDecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _EmptyDecoratedCapture.captured
        assert ctx is not None
        assert ctx.mapping_source == "heuristic"

    def test_ctx_overrides_win_over_decorator(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x", value_track="custom", subtrack="override")
        ctx = _DecoratedCapture.captured
        assert ctx is not None
        assert ctx.value_track == "custom"
        assert ctx.subtrack == "override"

    def test_off_level_does_not_read_decorator(self):
        uc = _DecoratedCapture()
        runner = UseCaseRunner(uc, level=MonitoringLevel.OFF)
        assert runner._inferred == {}

    def test_undecorated_usecase_unaffected(self):
        uc = _ContextCapture()
        _ContextCapture.captured = None
        runner = UseCaseRunner(uc, level=MonitoringLevel.BASIC)
        runner.run("x")
        ctx = _ContextCapture.captured
        assert ctx is not None
        assert ctx.mapping_source == "heuristic"
        assert ctx.value_track == "legacy"
