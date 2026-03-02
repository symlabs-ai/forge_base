import pytest

from forge_base.pulse.field_names import PulseFieldNames


@pytest.mark.pulse
class TestPulseFieldNames:
    def test_llm_fields_exist(self):
        assert hasattr(PulseFieldNames, "LLM_MODEL")
        assert hasattr(PulseFieldNames, "LLM_PROVIDER")
        assert hasattr(PulseFieldNames, "LLM_TOKENS_IN")
        assert hasattr(PulseFieldNames, "LLM_TOKENS_OUT")
        assert hasattr(PulseFieldNames, "LLM_LATENCY_MS")

    def test_http_fields_exist(self):
        assert hasattr(PulseFieldNames, "HTTP_METHOD")
        assert hasattr(PulseFieldNames, "HTTP_URL")
        assert hasattr(PulseFieldNames, "HTTP_STATUS_CODE")
        assert hasattr(PulseFieldNames, "HTTP_LATENCY_MS")

    def test_db_fields_exist(self):
        assert hasattr(PulseFieldNames, "DB_SYSTEM")
        assert hasattr(PulseFieldNames, "DB_OPERATION")
        assert hasattr(PulseFieldNames, "DB_TABLE")
        assert hasattr(PulseFieldNames, "DB_LATENCY_MS")

    def test_exec_fields_exist(self):
        assert hasattr(PulseFieldNames, "EXEC_USE_CASE")
        assert hasattr(PulseFieldNames, "EXEC_CORRELATION_ID")
        assert hasattr(PulseFieldNames, "EXEC_DURATION_MS")
        assert hasattr(PulseFieldNames, "EXEC_STATUS")
        assert hasattr(PulseFieldNames, "EXEC_ERROR_TYPE")

    def test_dot_namespace_convention(self):
        fields = [
            v for k, v in vars(PulseFieldNames).items()
            if not k.startswith("_") and isinstance(v, str)
        ]
        for f in fields:
            assert "." in f, f"Field {f!r} must use dot-namespace convention"

    def test_no_duplicate_values(self):
        fields = [
            v for k, v in vars(PulseFieldNames).items()
            if not k.startswith("_") and isinstance(v, str)
        ]
        assert len(fields) == len(set(fields)), "Duplicate field values found"
