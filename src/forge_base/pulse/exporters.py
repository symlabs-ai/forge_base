from __future__ import annotations

import json
from typing import IO, Any

from forge_base.pulse.context import ExecutionContext


class JsonLinesExporter:
    __slots__ = ("_stream",)

    def __init__(self, stream: IO[str]) -> None:
        self._stream = stream

    def export(self, context: ExecutionContext, data: dict[str, Any]) -> None:
        line = json.dumps(data, default=str, separators=(",", ":"))
        self._stream.write(line + "\n")


class InMemoryExporter:
    __slots__ = ("_records",)

    def __init__(self) -> None:
        self._records: list[tuple[ExecutionContext, dict[str, Any]]] = []

    def export(self, context: ExecutionContext, data: dict[str, Any]) -> None:
        self._records.append((context, data))

    @property
    def records(self) -> list[tuple[ExecutionContext, dict[str, Any]]]:
        return list(self._records)
