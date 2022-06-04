from lark import Lark, Transformer, Tree, v_args
from enum import Enum, auto
from typing import Any, List, Union
from dataclasses import dataclass

from .symbols import (
    _Symbol
)


class JoinType(Enum):
    Inner = auto()
    LeftOuter = auto()
    RightOuter = auto()
    FullOuter = auto()
    Cross = auto()


class ColumnModifier(Enum):
    PrimaryKey = auto()
    NotNull = auto()
    Nil = auto()  # no modifier - likely not needed


class DataType(Enum):
    """
    Enums for system datatypes
     NOTE: This represents data-types as understood by the parser. Which
     maybe different from VM's notion of datatypes
    """
    Integer = auto()
    Text = auto()
    Real = auto()
    Blob = auto()


class CreateStmnt(_Symbol):
    def __init__(self, table_name: Tree = None, column_def_list: Tree = None):
        self.table_name = table_name
        self.columns = column_def_list
        self.validate()

    def validate(self):
        """
        Ensure one and only one primary key
        """
        pkey_count = len([col for col in self.columns if col.is_primary_key])
        if pkey_count != 1:
            raise ValueError(f"Expected 1 primary key received {pkey_count}")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.__class__.__name__}({self.__dict__})'


class ColumnDef(_Symbol):

    def __init__(self, column_name: Tree = None, datatype: Tree = None, column_modifier=ColumnModifier.Nil):
        self.column_name = column_name
        self.datatype = datatype
        self.is_primary_key = column_modifier == ColumnModifier.PrimaryKey
        self.is_nullable = column_modifier == ColumnModifier.NotNull or column_modifier == ColumnModifier.PrimaryKey

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.prettystr()


class SelectStmnt:
    pass


@dataclass
class SelectClause:
    selectables: List[Any]


class FromClause:
    pass


class WhereClause:
    pass


class InsertStmnt:
    pass


# simple classes - i.e. don't need custom methods

@dataclass
class Program(_Symbol):
    statements: list


@dataclass
class TableName(_Symbol):
    table_name: Any


@dataclass
class ColumnName(_Symbol):
    column_name: Any


@v_args(tree=True)
class ToAst2(Transformer):
    """
    Convert parse tree to AST.
    Handles rules with optionals at tail
    and optionals in body.

    NOTE: another decision point here
    is where I wrap every rule in a dummy symbol class.
    - I could wrap each class, and a parent node can unwrap a child.
    - however, for boolean like fields, e.g. column_def__is_primary_key, it might be better
      to return an enum
    """
    # helpers

    def rules_to_kwargs(self, args) -> dict:
        # todo:nuke
        kwargs = {arg.data: arg for arg in args}
        return kwargs

    # simple classes

    def program(self, arg):
        breakpoint()
        pass

    def create_stmnt(self, arg):
        return CreateStmnt(arg.children[0], arg.children[1])

    def table_name(self, arg: Tree):
        assert len(arg.children) == 1
        val = TableName(arg.children[0])
        # breakpoint()
        return val

    def column_def_list(self, arg):
        return arg.children

    def column_name(self, arg):
        assert len(arg.children) == 1
        val = ColumnName(arg.children[0])
        # breakpoint()
        return val

    def datatype(self, arg):
        """
        Convert datatype text to arg
        """
        datatype = arg.children[0].lower()
        if datatype == "integer":
            return DataType.Integer
        elif datatype == "real":
            return DataType.Real
        elif datatype == "text":
            return DataType.Text
        elif datatype == "blob":
            return DataType.Blob
        else:
            raise ValueError(f"Unrecognized datatype [{datatype}]")

    def primary_key(self, arg):
        # this rule doesn't have any children nodes
        assert len(arg.children) == 0, f"Expected 0 children; received {len(arg.children)}"
        return ColumnModifier.PrimaryKey

    def not_null(self, arg):
        # this rule doesn't have any children nodes
        assert len(arg.children) == 0
        return ColumnModifier.NotNull
        # breakpoint()

    # custom logic classes

    def column_def(self, tree):
        """
        ?column_def       : column_name datatype primary_key? not_null?

        check with if, else conds
        """
        args = tree.children
        column_name = args[0]
        datatype = args[1]
        # any remaining args are column modifiers
        modifier = ColumnModifier.Nil
        if len(args) >= 3:
            # the logic here is that if the primary key modifier is used
            # not null is redudanct; and the parser ensures/requires primary
            # key mod must be specified before not null
            # todo: this more cleanly, e.g. primary key implies not null, uniqueness
            # modifiers could be a flag enum, which can be or'ed
            modifier = args[2]
        val = ColumnDef(column_name, datatype, modifier)
        return val


class ToAst3(Transformer):
    """
    Convert parse tree to AST.
    Handles rules with optionals at tail
    and optionals in body.

    NOTE: another decision point here
    is where I wrap every rule in a dummy symbol class.
    - I could wrap each class, and a parent node can unwrap a child.
    - however, for boolean like fields, e.g. column_def__is_primary_key, it might be better
      to return an enum

    NOTE: If a grammar symbol has a leading "?", the corresponding class won't be visited
    """
    # helpers

    # simple classes - top level statements

    def program(self, args):
        return Program(args)

    def create_stmnt(self, args):
        return CreateStmnt(args[0], args[1])

    def select_stmnt(self, args):
        # TODO: remove all rules from comments; and make grammar.py the authoritative source of rule def
        """select_clause from_clause? group_by_clause? having_clause? order_by_clause? limit_clause?"""



    def insert_stmnt(self, args):
        pass

    # simple classes - select stmnt components

    def select_clause(self, args):
        return SelectClause(args)

    def from_clause(self, args):
        pass

    def where_clause(self, args):
        pass

    def group_by_clause(self, args):
        pass

    def having_clause(self, args):
        pass

    def order_by_clause(self, args):
        pass

    def limit_clause(self, args):
        pass

    def condition(self, args):
        pass

    def primary(self, args):
        return args[0]

    # simple classes - insert stmnt components

    # simple classes - create stmnt components

    def table_name(self, args: list):
        assert len(args) == 1
        val = TableName(args[0])
        # breakpoint()
        return val

    def column_def_list(self, args):
        return args

    def column_name(self, args):
        assert len(args) == 1
        val = ColumnName(args[0])
        # breakpoint()
        return val

    def datatype(self, args):
        """
        Convert datatype text to arg
        """
        datatype = args[0].lower()
        if datatype == "integer":
            return DataType.Integer
        elif datatype == "real":
            return DataType.Real
        elif datatype == "text":
            return DataType.Text
        elif datatype == "blob":
            return DataType.Blob
        else:
            raise ValueError(f"Unrecognized datatype [{datatype}]")

    def primary_key(self, arg):
        # this rule doesn't have any children nodes
        #assert len(arg.children) == 0, f"Expected 0 children; received {len(arg.children)}"
        return ColumnModifier.PrimaryKey

    def not_null(self, arg):
        # this rule doesn't have any children nodes
        #assert len(arg.children) == 0
        return ColumnModifier.NotNull
        # breakpoint()

    # custom logic classes

    def column_def(self, args):
        """
        ?column_def       : column_name datatype primary_key? not_null?

        check with if, else conds
        """
        column_name = args[0]
        datatype = args[1]
        # any remaining args are column modifiers
        modifier = ColumnModifier.Nil
        if len(args) >= 3:
            # the logic here is that if the primary key modifier is used
            # not null is redudanct; and the parser ensures/requires primary
            # key mod must be specified before not null
            # todo: this more cleanly, e.g. primary key implies not null, uniqueness
            # modifiers could be a flag enum, which can be or'ed
            modifier = args[2]
        val = ColumnDef(column_name, datatype, modifier)
        return val