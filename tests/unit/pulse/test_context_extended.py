from types import MappingProxyType

import pytest

from forge_base.pulse.context import _EMPTY_TAGS, ExecutionContext
from forge_base.pulse.level import MonitoringLevel


@pytest.mark.pulse
class TestExecutionContextNewFields:
    def test_default_value_track(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.value_track == "legacy"

    def test_default_subtrack(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.subtrack == ""

    def test_default_feature(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.feature == ""

    def test_default_mapping_source(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.mapping_source == "legacy"

    def test_build_with_new_fields(self):
        ctx = ExecutionContext.build(
            level=MonitoringLevel.BASIC,
            use_case_name="CreateInvoice",
            value_track="billing",
            subtrack="invoices",
            feature="create_invoice",
            mapping_source="heuristic",
        )
        assert ctx.value_track == "billing"
        assert ctx.subtrack == "invoices"
        assert ctx.feature == "create_invoice"
        assert ctx.mapping_source == "heuristic"

    def test_frozen_new_fields(self):
        ctx = ExecutionContext(correlation_id="abc")
        with pytest.raises(AttributeError):
            ctx.value_track = "new"  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.subtrack = "new"  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.feature = "new"  # type: ignore[misc]
        with pytest.raises(AttributeError):
            ctx.mapping_source = "new"  # type: ignore[misc]

    def test_backward_compat_no_new_fields(self):
        ctx = ExecutionContext(correlation_id="abc", level=MonitoringLevel.BASIC)
        assert ctx.correlation_id == "abc"
        assert ctx.level == MonitoringLevel.BASIC
        assert ctx.value_track == "legacy"


@pytest.mark.pulse
class TestExecutionContextTags:
    def test_default_tags_empty(self):
        ctx = ExecutionContext(correlation_id="abc")
        assert ctx.tags == _EMPTY_TAGS
        assert len(ctx.tags) == 0

    def test_build_with_tags(self):
        ctx = ExecutionContext.build(
            level=MonitoringLevel.BASIC,
            tags={"tier": "premium", "region": "us"},
        )
        assert ctx.tags["tier"] == "premium"
        assert ctx.tags["region"] == "us"
        assert isinstance(ctx.tags, MappingProxyType)

    def test_build_tags_none(self):
        ctx = ExecutionContext.build(level=MonitoringLevel.BASIC, tags=None)
        assert ctx.tags == _EMPTY_TAGS

    def test_tags_immutable(self):
        ctx = ExecutionContext.build(
            level=MonitoringLevel.BASIC,
            tags={"key": "val"},
        )
        with pytest.raises(TypeError):
            ctx.tags["key"] = "new"  # type: ignore[index]
