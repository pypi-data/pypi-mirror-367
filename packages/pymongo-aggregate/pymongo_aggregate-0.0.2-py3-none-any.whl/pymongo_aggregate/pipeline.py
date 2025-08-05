from re import Pattern
from typing import Self, Literal, Any

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.operations.stages.match import Match
from pymongo_aggregate.operations.stages.project import Project
from pymongo_aggregate.operations.stages.stage_operation import StageOperation
from pymongo_aggregate.operations.stages.unwind import Unwind


class PipelineBuilder:

    def __init__(self):
        self._stages: list[StageOperation] = []
        self._pipeline: list[StageOperation] = []

    @property
    def pipeline(self) -> list[StageOperation]:
        return self._pipeline

    def match(self, content: dict[str, int | str | Pattern | OpOperation]) -> Self:
        self._stages.append(Match(content))
        return self

    def project(self, content: dict[str, str | Literal[1, 0] | OpOperation[Any]]) -> Self:
        self._stages.append(Project(content))
        return self

    def unwind(self, path: str,
               include_array_index: str | None = None,
               preserve_null_and_empty_arrays: bool | None = None) -> Self:
        self._stages.append(Unwind(path, include_array_index, preserve_null_and_empty_arrays))
        return self

    def build(self) -> Self:
        while len(self._stages) > 0:
            self._pipeline.append(self._stages.pop())
        return self
