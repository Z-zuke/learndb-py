from __future__ import annotations
import logging
import os
import sys
import dataclasses
from dataclasses import dataclass

from lark import Lark, logger, ast_utils, Transformer
from lark.exceptions import UnexpectedInput  # root of all lark exceptions
from typing import Any, List

logger.setLevel(logging.DEBUG)

this_module = sys.modules[__name__]

WHITESPACE = ' '


class _Ast(ast_utils.Ast):
    """
    The root of AST hierarchy
    """
    # NOTE: classes with preceding "_" will be skipped

    def is_virtual(self) -> bool:
        """
        Helper method to determine whether symbol/parsed
        rules' class is virtual, i.e. won't be materialized.
        Classes whose names begins with "_" are virtual.
        :return:
        """
        classname = self.__class__.__name__
        return classname.startswith("_")

    def get_prettychild(self, child, child_depth) -> list:
        """
        Get pretty printed child; calls different method depending on whether
        child is derived from _Ast, Lark.Tree, or Lark.Token.

        :param child:
        :param child_depth:
        :return:
        """
        if hasattr(child, "prettyprint"):
            # part of Ast hierarchy
            val = child.prettyprint(depth=child_depth)
        elif hasattr(child, "pretty"):
            # part of autogenerated hierarchy
            preceding = WHITESPACE * child_depth
            formatted = f"{preceding}{child.pretty(preceding)}"
            val = [formatted]
        else:
            # token
            preceding = WHITESPACE * child_depth
            formatted = f"{preceding}{str(child)}"
            val = [formatted]
        return val

    def prettyprint(self, depth=0) -> list:
        """
        return a pretty printed string
        :return:
        """
        children = dataclasses.asdict(self)
        lines = []

        child_depth = depth if self.is_virtual() else depth + 1
        preceding = WHITESPACE * depth
        if not self.is_virtual():
            classname = self.__class__.__name__
            lines.append(f'{preceding}{classname}:{os.linesep}')

        for key, value in children.items():
            child = getattr(self, key)
            if isinstance(child, list):
                for element in child:
                    lines.extend(self.get_prettychild(element, child_depth))
            else:
                # scalar
                lines.extend(self.get_prettychild(child, child_depth))

        return lines


@dataclass
class Program(_Ast, ast_utils.AsList):
    statements: List[_Stmnt]


# is this even needed
class _Stmnt(_Ast):
    pass


@dataclass
class SelectStmnt(_Ast):
    select_clause: _Selectables
    from_clause: FromClause = None
    group_by_clause: Any = None
    having_clause: Any = None
    order_by_clause: Any = None
    limit_clause: Any = None


@dataclass
class _Selectables(_Ast,  ast_utils.AsList):
    selections: List[Selectable]


@dataclass
class Selectable(_Ast):
    item: Any


@dataclass
class FromClause(_Ast):
    source: Any
    # where clauses is nested in from, i.e. in a select
    # a where clause without a from clause is invalid
    where_clause: Any = None


# Not sure how
@dataclass
class SourceX(_Ast):
    source: Any
    #join_modifier: Any = None
    #other_source: Any = None
    #join_condition: Any = None


# NOTES about lark
# NOTE: terminal we want to capture must be named

import importlib.util
spec = importlib.util.spec_from_file_location("grammar", "/Users/spand/universe/learndb-py/lang_parser/grammar.py")
grammar_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grammar_mod)
grammar = grammar_mod.GRAMMAR



class ToAst(Transformer):
    pass
    # todo: this should convert literals to datatype


def driver():
    parser = Lark(grammar, parser='earley', start="program", debug=True)  # , ambiguity='explicit')
    # text = "select cola from foo;"
    text = "select cola from foo f join bar b on f.x <> b.w;"
    text = "select cola, colb from foo where cola <> colb and colx > coly;"
    text = "select cola, colb from foo join bar on where cola <> colb and colx > coly;"
    text = "select cola, colb from foo left outer join bar on where cola <> colb and colx > coly having foo > 4;    "
    text = """select cola, colb from foo left outer join bar b on x = 1 
    cross join jar j on jb = xw where cola <> colb and colx > coly;
    drop table foo;"""
    text = "select cola, colb from foo f left join bar r on fx = ry;"
    text = "select cola, colb from foo f left join bar r on (select macdcd from fodo where x = 1);"
    text = "select cola, colb from foo f left join bar r on (select max(fig) from fodo where x = 1);"

    text = "select cola, colb from foo f left join bar r on r.x = y.b;"
    text = "select cola, colb from foo f left outer join bar r on f.b = r.y right join car c on c.x = f.b;"
    text = "select cola, colb from foo f left join bar r on (select max(fig, farce) from fodo where x = 1);"
    text = "select cola, colb from foo f where car = 'hello world' "
    text = "delete from table_foo where car_name <> 'marmar'"
    #text = "drop table foo"
    text = "update table_name set column_name = 32"
    text = "update table_name set column_name = 'value' where foo = 'bar'"
    text = "insert into table_name (col_a, col_b) values (11, 92)"
    text  = "insert into table_name (col_a, col_b) values ('val_a', 'val_b')"
    text = "insert into table_name (col_a, col_b) values (11, 92)"
    # parse tree
    print(parser.parse(text).pretty())
    #return

    # Ast
    tree = parser.parse(text)
    transformer = ast_utils.create_transformer(this_module, ToAst())
    tree = transformer.transform(tree)
    pretty = tree.prettyprint()
    pretty = os.linesep.join(pretty)
    print(pretty)
    #print(tree.children[0].select_clause.children[0].Selections)
    return tree


#driver0()
driver()
