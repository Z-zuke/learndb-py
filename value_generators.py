"""
Contains classes corresponding to value generators.

ValueGenerators are used in to evaluate select clauses. They are objects
that track the formal parameters passed to the select clause. Then
when iterating over a recordset, the valueGenerator takes a record, and returns a single output value
"""
from dataclasses import dataclass
from typing import Any, Dict, List, NewType, Union
from functions import FunctionDefinition


@dataclass
class ColumnRefSelectableAtom:
    """
    Represents a selectable, that is a column ref, as opposed to a literal.
    A note on name, a selectable is any component of a select clause, e.g.
    select 1, upper(name) from people

    Here, `upper(name)` is a selectable, and `name` is a ColumnRefSelectableAtom, and 1 is a LiteralSelectableAtom.
    """
    name: Any


@dataclass
class LiteralSelectableAtom:
    """
    Represents a literal selectable
    """
    value: Any


SelectableAtom = NewType("SelectableAtom", Union[ColumnRefSelectableAtom, LiteralSelectableAtom])


class ValueExtractorFromRecord:
    """
    This is a simplified form of ValueGeneratorFromRecord of, which
    extracts a single column value, i.e. without any transformation
    """
    def __init__(self, pos_arg: SelectableAtom):
        self.pos_arg = pos_arg

    def get_value(self, record) -> Any:
        # as a perf improvement, for static values, we can do the check once, and store the static value
        if isinstance(self.pos_arg, LiteralSelectableAtom):
            return self.pos_arg.value
        else:
            return record.get(self.pos_arg.value)


class ValueGeneratorFromRecord:
    """
    Generate value from a single record.

    This is used in a select clause, e.g.

    select cola from foo

    or

    select upper(cola) from foo

    """

    def __init__(self, pos_args: List[SelectableAtom],
                 named_args: Dict[str, SelectableAtom], func: FunctionDefinition):
        """
        pos_args: List of SelectableAtoms which represents either: 1) static values, 2) column identifiers
        named_args: Dict of ^
        func: should this be a FunctionDefinition or None
            - if this None, then this means that this is a simple
        """
        self.pos_args = pos_args
        self.named_args = named_args
        self.func = func

    def get_value(self, record) -> Any:
        """
        This is invoked when iterating over a recordset with each record
        """
        # evaluate pos_args, i.e. convert SelectableAtom to a value that can be passed to a function
        evaluated_pos_args = []
        for arg in self.pos_args:
            if isinstance(arg, LiteralSelectableAtom):
                # evaluate any literals, by unboxing from `LiteralSelectableAtom`
                evaluated_pos_args.append(arg.value)
            else:
                # evaluate any column references, i.e. replace with value in record
                evaluated_pos_args.append(record.get(arg.name))

        evaluated_named_args = {}
        for arg_name, arg_val in self.named_args.items():
            if isinstance(arg_val, LiteralSelectableAtom):
                evaluated_named_args[arg_name] = arg_val.value
            else:
                evaluated_named_args[arg_name] = record.get(arg_val.name)

        # apply a function on arguments to
        return self.func.apply(evaluated_pos_args, evaluated_named_args)


class ValueGeneratorFromRecordGroup:

    def __init__(self):
        pass