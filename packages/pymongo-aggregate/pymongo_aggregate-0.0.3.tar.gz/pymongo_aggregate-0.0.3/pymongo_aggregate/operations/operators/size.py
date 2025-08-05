from pymongo_aggregate.operations.operators.op_operation import OpOperation


class Size(OpOperation[dict[str, str]]):

    operator = "$size"
