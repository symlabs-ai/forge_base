from types import MappingProxyType
from unittest.mock import patch

import pytest

from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.exceptions import PulseConfigError
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.policy import SamplingPolicy


def _ctx(value_track: str = "legacy", tenant: str = "") -> ExecutionContext:
    extra = {"tenant": tenant} if tenant else {}
    return ExecutionContext(
        correlation_id="test",
        level=MonitoringLevel.BASIC,
        use_case_name="TestUC",
        value_track=value_track,
        extra=MappingProxyType(extra),
    )


@pytest.mark.pulse
class TestSamplingPolicyValidation:
    def test_defaults_valid(self):
        policy = SamplingPolicy()
        assert policy.default_rate == 1.0
        assert policy.by_value_track == {}
        assert policy.by_tenant == {}

    def test_rate_below_zero_raises(self):
        with pytest.raises(PulseConfigError, match="default_rate"):
            SamplingPolicy(default_rate=-0.1)

    def test_rate_above_one_raises(self):
        with pytest.raises(PulseConfigError, match="default_rate"):
            SamplingPolicy(default_rate=1.1)

    def test_by_value_track_invalid_rate(self):
        with pytest.raises(PulseConfigError, match="by_value_track"):
            SamplingPolicy(by_value_track={"rev": 2.0})

    def test_by_tenant_invalid_rate(self):
        with pytest.raises(PulseConfigError, match="by_tenant"):
            SamplingPolicy(by_tenant={"acme": -0.5})

    def test_zero_rate_valid(self):
        policy = SamplingPolicy(default_rate=0.0)
        assert policy.default_rate == 0.0

    def test_one_rate_valid(self):
        policy = SamplingPolicy(default_rate=1.0)
        assert policy.default_rate == 1.0

    def test_frozen(self):
        policy = SamplingPolicy()
        with pytest.raises(AttributeError):
            policy.default_rate = 0.5  # type: ignore[misc]

    def test_by_value_track_immutable(self):
        policy = SamplingPolicy(by_value_track={"revenue": 0.5})
        assert isinstance(policy.by_value_track, MappingProxyType)
        with pytest.raises(TypeError):
            policy.by_value_track["new"] = 0.1  # type: ignore[index]

    def test_by_tenant_immutable(self):
        policy = SamplingPolicy(by_tenant={"acme": 0.8})
        assert isinstance(policy.by_tenant, MappingProxyType)
        with pytest.raises(TypeError):
            policy.by_tenant["new"] = 0.1  # type: ignore[index]

    def test_original_dict_not_shared(self):
        original = {"revenue": 0.5}
        policy = SamplingPolicy(by_value_track=original)
        original["revenue"] = 1.0
        assert policy.by_value_track["revenue"] == 0.5


@pytest.mark.pulse
class TestSamplingPolicyBehavior:
    def test_rate_one_always_samples(self):
        policy = SamplingPolicy(default_rate=1.0)
        ctx = _ctx()
        assert all(policy.should_sample(ctx) for _ in range(100))

    def test_rate_zero_never_samples(self):
        policy = SamplingPolicy(default_rate=0.0)
        ctx = _ctx()
        assert not any(policy.should_sample(ctx) for _ in range(100))

    def test_by_value_track_override(self):
        policy = SamplingPolicy(default_rate=1.0, by_value_track={"revenue": 0.0})
        ctx = _ctx(value_track="revenue")
        assert not any(policy.should_sample(ctx) for _ in range(100))

    def test_by_tenant_override(self):
        policy = SamplingPolicy(default_rate=1.0, by_tenant={"acme": 0.0})
        ctx = _ctx(tenant="acme")
        assert not any(policy.should_sample(ctx) for _ in range(100))

    def test_tenant_takes_precedence_over_value_track(self):
        policy = SamplingPolicy(
            default_rate=0.0,
            by_value_track={"revenue": 0.0},
            by_tenant={"acme": 1.0},
        )
        ctx = _ctx(value_track="revenue", tenant="acme")
        assert all(policy.should_sample(ctx) for _ in range(100))

    def test_tenant_not_found_falls_through(self):
        policy = SamplingPolicy(
            default_rate=0.0,
            by_value_track={"revenue": 1.0},
            by_tenant={"acme": 0.0},
        )
        ctx = _ctx(value_track="revenue", tenant="other")
        assert all(policy.should_sample(ctx) for _ in range(100))

    def test_no_tenant_in_extra_falls_through(self):
        policy = SamplingPolicy(
            default_rate=0.0,
            by_value_track={"revenue": 1.0},
            by_tenant={"acme": 0.0},
        )
        ctx = _ctx(value_track="revenue")
        assert all(policy.should_sample(ctx) for _ in range(100))

    def test_value_track_not_found_falls_to_default(self):
        policy = SamplingPolicy(
            default_rate=1.0,
            by_value_track={"revenue": 0.0},
        )
        ctx = _ctx(value_track="growth")
        assert all(policy.should_sample(ctx) for _ in range(100))

    @patch("forge_base.pulse.policy.random.random", return_value=0.49)
    def test_should_sample_uses_random(self, mock_random):
        policy = SamplingPolicy(default_rate=0.5)
        ctx = _ctx()
        assert policy.should_sample(ctx) is True
        mock_random.assert_called_once()
