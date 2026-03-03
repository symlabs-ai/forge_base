class PulseFieldNames:
    # LLM fields
    LLM_MODEL = "llm.model"
    LLM_PROVIDER = "llm.provider"
    LLM_TOKENS_IN = "llm.tokens_in"
    LLM_TOKENS_OUT = "llm.tokens_out"
    LLM_LATENCY_MS = "llm.latency_ms"

    # HTTP fields
    HTTP_METHOD = "http.method"
    HTTP_URL = "http.url"
    HTTP_STATUS_CODE = "http.status_code"
    HTTP_LATENCY_MS = "http.latency_ms"

    # DB fields
    DB_SYSTEM = "db.system"
    DB_OPERATION = "db.operation"
    DB_TABLE = "db.table"
    DB_LATENCY_MS = "db.latency_ms"

    # Execution fields
    EXEC_USE_CASE = "exec.use_case"
    EXEC_CORRELATION_ID = "exec.correlation_id"
    EXEC_DURATION_MS = "exec.duration_ms"
    EXEC_STATUS = "exec.status"
    EXEC_ERROR_TYPE = "exec.error_type"
    EXEC_TRACK_TYPE = "exec.track_type"
    EXEC_SUPPORTS = "exec.supports"

    # Pulse execution metrics (Fase 1)
    PULSE_EXEC_COUNT = "pulse.execution.count"
    PULSE_EXEC_DURATION_MS = "pulse.execution.duration_ms"
    PULSE_EXEC_ERRORS = "pulse.execution.errors"
    PULSE_EXEC_SUCCESS = "pulse.execution.success"
