import pytest

from forge_base.pulse.budget import BudgetPolicy
from forge_base.pulse.exceptions import PulseConfigError


@pytest.mark.pulse
class TestBudgetPolicyValidation:
    def test_defaults_ok(self):
        bp = BudgetPolicy()
        assert bp.max_spans_per_execution == 64
        assert bp.max_events_per_execution == 128

    def test_max_spans_zero_invalid(self):
        with pytest.raises(PulseConfigError, match="max_spans_per_execution"):
            BudgetPolicy(max_spans_per_execution=0)

    def test_negative_spans_invalid(self):
        with pytest.raises(PulseConfigError, match="max_spans_per_execution"):
            BudgetPolicy(max_spans_per_execution=-1)

    def test_bool_spans_invalid(self):
        with pytest.raises(PulseConfigError, match="max_spans_per_execution"):
            BudgetPolicy(max_spans_per_execution=True)  # type: ignore[arg-type]

    def test_float_spans_invalid(self):
        with pytest.raises(PulseConfigError, match="max_spans_per_execution"):
            BudgetPolicy(max_spans_per_execution=3.5)  # type: ignore[arg-type]

    def test_frozen(self):
        bp = BudgetPolicy()
        with pytest.raises(AttributeError):
            bp.max_spans_per_execution = 10  # type: ignore[misc]

    def test_max_events_zero_invalid(self):
        with pytest.raises(PulseConfigError, match="max_events_per_execution"):
            BudgetPolicy(max_events_per_execution=0)

    def test_negative_events_invalid(self):
        with pytest.raises(PulseConfigError, match="max_events_per_execution"):
            BudgetPolicy(max_events_per_execution=-5)


@pytest.mark.pulse
class TestBudgetPolicyDefaults:
    def test_default_spans(self):
        assert BudgetPolicy().max_spans_per_execution == 64

    def test_default_events(self):
        assert BudgetPolicy().max_events_per_execution == 128
