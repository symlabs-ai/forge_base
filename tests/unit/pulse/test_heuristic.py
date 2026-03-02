import pytest

from forge_base.application.usecase_base import UseCaseBase
from forge_base.pulse.heuristic import _extract_domain, _extract_feature, infer_context


class _DummyUseCase(UseCaseBase[str, str]):
    def _before_execute(self) -> None:
        pass

    def _after_execute(self) -> None:
        pass

    def _on_error(self, error: Exception) -> None:
        pass

    def execute(self, input_dto: str) -> str:
        return input_dto


@pytest.mark.pulse
class TestInferContext:
    def test_returns_class_name(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        assert result["use_case_name"] == "_DummyUseCase"

    def test_returns_heuristic_mapping_source(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        assert result["mapping_source"] == "heuristic"

    def test_returns_legacy_value_track(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        assert result["value_track"] == "legacy"

    def test_returns_feature_from_module(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        assert result["feature"] == "test_heuristic"

    def test_returns_subtrack_from_module(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        # subtrack is the domain segment (skips last segment = feature, skips infra)
        assert isinstance(result["subtrack"], str)
        assert result["subtrack"] != ""
        # Should NOT be the feature (last segment)
        assert result["subtrack"] != result["feature"]

    def test_all_keys_present(self):
        uc = _DummyUseCase()
        result = infer_context(uc)
        expected_keys = {"use_case_name", "feature", "value_track", "subtrack", "mapping_source"}
        assert set(result.keys()) == expected_keys


@pytest.mark.pulse
class TestExtractFeature:
    def test_simple_module(self):
        assert _extract_feature("app.billing.usecases.create_invoice") == "create_invoice"

    def test_single_segment(self):
        assert _extract_feature("create_invoice") == "create_invoice"

    def test_empty_module(self):
        assert _extract_feature("") == ""


@pytest.mark.pulse
class TestExtractDomain:
    def test_skips_feature_and_usecases(self):
        # Last segment (feature) is skipped, then "usecases" is infra → returns "billing"
        assert _extract_domain("app.billing.usecases.create_invoice") == "billing"

    def test_skips_feature_and_application(self):
        # Last segment (feature) is skipped, then "application" is infra → returns "billing"
        assert _extract_domain("app.billing.application.create") == "billing"

    def test_skips_infra_only_segments(self):
        # Last segment skipped → walks ["app", "billing"] reversed → "billing"
        assert _extract_domain("app.billing.usecases") == "billing"

    def test_single_segment(self):
        # Single segment: parts[:-1] is empty → fallback to parts[0]
        assert _extract_domain("billing") == "billing"

    def test_empty_module(self):
        assert _extract_domain("") == ""

    def test_all_infra_returns_first(self):
        # Last skipped → reversed(["usecases", "application"]) → all infra → fallback parts[0]
        assert _extract_domain("usecases.application.services") == "usecases"

    def test_deep_module_path(self):
        assert _extract_domain("myapp.payments.billing.usecases.charge") == "billing"
