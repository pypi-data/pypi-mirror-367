from enum import Enum


class LogLevel(str, Enum):
    trace: str = "trace"
    debug: str = "debug"
    info: str = "info"
    warning: str = "warning"
    error: str = "error"
    critical: str = "critical"

    @classmethod
    def _missing_(cls, value):
        return cls(value.lower())


class LogCategory(str, Enum):
    request: str = "request"
    response: str = "response"
    service: str = "service"
    outbound: str = "outbound"
    excel: str = "excel"
    access: str = "access"
    query: str = "query"

    @classmethod
    def _missing_(cls, value):
        return cls(value.lower())
