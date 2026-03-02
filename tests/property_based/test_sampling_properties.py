from types import MappingProxyType

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from forge_base.pulse.context import ExecutionContext
from forge_base.pulse.level import MonitoringLevel
from forge_base.pulse.policy import SamplingPolicy

SAMPLES = 10_000
TOLERANCE = 0.05


def _ctx(value_track: str = "legacy", tenant: str = "") -> ExecutionContext:
    extra = {"tenant": tenant} if tenant else {}
    return ExecutionContext(
        correlation_id="test",
        level=MonitoringLevel.BASIC,
        use_case_name="TestUC",
        value_track=value_track,
        extra=MappingProxyType(extra),
    )


@pytest.mark.property
@pytest.mark.pulse
class TestSamplingProperties:
    @given(rate=st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=20, deadline=None)
    def test_default_rate_converges(self, rate: float):
        policy = SamplingPolicy(default_rate=rate)
        ctx = _ctx()
        sampled = sum(1 for _ in range(SAMPLES) if policy.should_sample(ctx))
        actual_rate = sampled / SAMPLES
        assert abs(actual_rate - rate) < TOLERANCE, (
            f"Expected ~{rate:.2f}, got {actual_rate:.2f}"
        )

    @given(
        default=st.floats(min_value=0.0, max_value=1.0),
        override=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=None)
    def test_value_track_rate_overrides_default(self, default: float, override: float):
        policy = SamplingPolicy(
            default_rate=default,
            by_value_track={"revenue": override},
        )
        ctx = _ctx(value_track="revenue")
        sampled = sum(1 for _ in range(SAMPLES) if policy.should_sample(ctx))
        actual_rate = sampled / SAMPLES
        assert abs(actual_rate - override) < TOLERANCE, (
            f"Expected ~{override:.2f} (override), got {actual_rate:.2f}"
        )

    @given(
        default=st.floats(min_value=0.0, max_value=1.0),
        vt_rate=st.floats(min_value=0.0, max_value=1.0),
        tenant_rate=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=20, deadline=None)
    def test_tenant_rate_takes_precedence(
        self, default: float, vt_rate: float, tenant_rate: float
    ):
        policy = SamplingPolicy(
            default_rate=default,
            by_value_track={"revenue": vt_rate},
            by_tenant={"acme": tenant_rate},
        )
        ctx = _ctx(value_track="revenue", tenant="acme")
        sampled = sum(1 for _ in range(SAMPLES) if policy.should_sample(ctx))
        actual_rate = sampled / SAMPLES
        assert abs(actual_rate - tenant_rate) < TOLERANCE, (
            f"Expected ~{tenant_rate:.2f} (tenant), got {actual_rate:.2f}"
        )
