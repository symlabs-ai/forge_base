import re
from typing import Any

SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"auth[_-]?(token|key|secret|header|cookie|code|hash)", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
    re.compile(r"ssn", re.IGNORECASE),
    re.compile(r"credit[_-]?card", re.IGNORECASE),
)

_REDACTED = "[REDACTED]"


def _is_sensitive(key: str) -> bool:
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(key):
            return True
    return False


def redact_keys(data: dict[str, Any]) -> dict[str, Any]:
    return {k: (_REDACTED if _is_sensitive(k) else v) for k, v in data.items()}
