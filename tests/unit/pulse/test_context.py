import uuid

import pytest

from forge_base.pulse.context import (
    ExecutionContext,
    _current_context,
    get_context,
    set_context,
)
from forge_base.pulse.level import MonitoringLevel


@pytest.mark.pulse
class TestExecutionContext:
    def test_defaults(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.correlation_id == "abc"
        assert ctx.level == MonitoringLevel.OFF
        assert ctx.use_case_name == ""
        assert dict(ctx.extra) == {}

    def test_frozen(self):
        ctx = ExecutionContext(correlation_id="abc")
        with pytest.raises(AttributeError):
            ctx.correlation_id = "xyz"  # type: ignore[misc]

    def test_extra_is_immutable(self):
        ctx = ExecutionContext.build(extra={"key": "value"})
        with pytest.raises(TypeError):
            ctx.extra["new_key"] = "mutated"  # type: ignore[index]

    def test_build_generates_correlation_id(self):
        ctx = ExecutionContext.build()
        uuid.UUID(ctx.correlation_id)  # valid UUID

    def test_build_uses_given_correlation_id(self):
        ctx = ExecutionContext.build(correlation_id="custom-123")
        assert ctx.correlation_id == "custom-123"

    def test_build_redacts_sensitive_extra(self):
        ctx = ExecutionContext.build(extra={"password": "s3cret", "name": "alice"})
        assert ctx.extra["password"] == "[REDACTED]"
        assert ctx.extra["name"] == "alice"

    def test_build_with_kwargs(self):
        ctx = ExecutionContext.build(level=MonitoringLevel.BASIC, use_case_name="Test")
        assert ctx.level == MonitoringLevel.BASIC
        assert ctx.use_case_name == "Test"


@pytest.mark.pulse
class TestContextVar:
    def setup_method(self):
        self._token = _current_context.set(None)

    def teardown_method(self):
        _current_context.reset(self._token)

    def test_default_is_none(self):
        assert get_context() is None

    def test_set_and_get(self):
        ctx = ExecutionContext(correlation_id="abc")
        set_context(ctx)
        assert get_context() is ctx

    def test_reset(self):
        ctx = ExecutionContext(correlation_id="abc")
        token = set_context(ctx)
        assert get_context() is ctx
        _current_context.reset(token)
        assert get_context() is None
