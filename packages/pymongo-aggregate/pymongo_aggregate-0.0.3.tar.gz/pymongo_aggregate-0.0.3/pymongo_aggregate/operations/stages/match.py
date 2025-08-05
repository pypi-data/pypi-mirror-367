from re import Pattern

from pymongo_aggregate.operations.operators.op_operation import OpOperation
from pymongo_aggregate.operations.stages.stage_operation import StageOperation


class Match(StageOperation[dict[str, int | str | Pattern | OpOperation]]):

    """$match (aggregation)

    Filters documents based on a specified queries predicate. Matched documents are passed to the
    next pipeline stages.
    """

    operator = "$match"
