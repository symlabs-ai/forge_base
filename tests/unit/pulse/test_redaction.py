import pytest

from forge_base.pulse.redaction import _is_sensitive, redact_keys


@pytest.mark.pulse
class TestRedaction:
    def test_sensitive_keys_redacted(self):
        data = {"password": "s3cret", "user": "alice"}
        result = redact_keys(data)
        assert result["password"] == "[REDACTED]"
        assert result["user"] == "alice"

    def test_normal_keys_preserved(self):
        data = {"name": "bob", "count": 42}
        result = redact_keys(data)
        assert result == data

    def test_case_insensitive(self):
        data = {"PASSWORD": "x", "Api_Key": "y", "TOKEN": "z"}
        result = redact_keys(data)
        assert all(v == "[REDACTED]" for v in result.values())

    def test_compound_keys(self):
        data = {"db_password_hash": "h", "api-key-v2": "k", "user_token_exp": "t"}
        result = redact_keys(data)
        assert result["db_password_hash"] == "[REDACTED]"
        assert result["api-key-v2"] == "[REDACTED]"
        assert result["user_token_exp"] == "[REDACTED]"

    def test_empty_dict(self):
        assert redact_keys({}) == {}

    def test_is_sensitive_positive(self):
        assert _is_sensitive("password")
        assert _is_sensitive("api_key")
        assert _is_sensitive("secret_value")
        assert _is_sensitive("auth_token")
        assert _is_sensitive("auth_key")
        assert _is_sensitive("auth-secret")
        assert _is_sensitive("auth_header")
        assert _is_sensitive("auth_cookie")

    def test_is_sensitive_negative(self):
        assert not _is_sensitive("username")
        assert not _is_sensitive("count")
        assert not _is_sensitive("host")

    def test_auth_pattern_no_false_positives(self):
        assert not _is_sensitive("author")
        assert not _is_sensitive("authority")
        assert not _is_sensitive("auth_method")
        assert not _is_sensitive("authorization_type")
