from typing import Any

import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.context import ExecutionContext, _current_context, get_context
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.policy import SamplingPolicy
from forge_base.pulse.runner import UseCaseRunner


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
@pytest.mark.integration
class TestRunnerWithPolicy:
    def setup_method(self):
        self._token = _current_context.set(None)
        _ContextCapture.captured = None

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_rate_zero_skips_collector(self):
        spy = _SpyCollector()
        policy = SamplingPolicy(default_rate=0.0)
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=spy, policy=policy
        )
        runner.run("hello")
        assert len(spy.started) == 0
        assert len(spy.succeeded) == 0
        assert len(spy.finished) == 0

    def test_rate_one_uses_collector(self):
        spy = _SpyCollector()
        policy = SamplingPolicy(default_rate=1.0)
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=spy, policy=policy
        )
        runner.run("hello")
        assert len(spy.started) == 1
        assert len(spy.succeeded) == 1
        assert len(spy.finished) == 1

    def test_no_policy_full_sampling(self):
        spy = _SpyCollector()
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, collector=spy, policy=None
        )
        runner.run("hello")
        assert len(spy.started) == 1
        assert len(spy.succeeded) == 1

    def test_context_set_even_when_not_sampled(self):
        policy = SamplingPolicy(default_rate=0.0)
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, policy=policy
        )
        runner.run("hello")
        assert _ContextCapture.captured is not None
        assert _ContextCapture.captured.use_case_name == "_ContextCapture"

    def test_context_cleaned_after_not_sampled(self):
        policy = SamplingPolicy(default_rate=0.0)
        uc = _ContextCapture()
        runner = UseCaseRunner(
            uc, level=MonitoringLevel.BASIC, policy=policy
        )
        runner.run("hello")
        assert get_context() is None
