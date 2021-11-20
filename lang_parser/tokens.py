"""
Contains types related to tokens
"""
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """
    types of tokens
    """
    # single-char tokens
    STAR = auto()  # '*'
    LEFT_PAREN = auto()  # '(
    RIGHT_PAREN = auto()  # ')'
    LEFT_BRACKET = auto()  # '['
    RIGHT_BRACKET = auto()  # ']'
    DOT = auto()  # '.'
    EQUAL = auto()  # =
    LESS = auto()  # <
    GREATER = auto()  # >
    COMMA = auto()  # ,
    SEMI_COLON = auto(), # ;

    # 2-char tokens
    LESS_EQUAL = auto()  # <=
    GREATER_EQUAL = auto()  # >=
    NOT_EQUAL = auto()  # represents both: <>, !=

    # misc
    EOF = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # keywords
    FROM = auto()
    OR = auto()
    WHERE = auto()
    ON = auto()
    CREATE = auto()
    AND = auto()
    DELETE = auto()
    DROP = auto()
    TRUNCATE = auto()
    INSERT = auto()
    INTO = auto()
    VALUES = auto()
    JOIN = auto()
    CASE = auto()
    HAVING = auto()
    GROUP = auto()
    ORDER = auto()
    UPDATE = auto()
    BY = auto()
    SELECT = auto()
    NULL = auto()
    TABLE = auto()
    SET = auto()

    INTEGER = auto()
    REAL = auto()
    TEXT = auto()


KEYWORDS = {
    'select',
    'from',
    'where',
    'join',
    'on',
    'group',
    'order',
    'by',
    'having',
    'case',
    'or',
    'and',
    'null',
    'create',
    'delete',
    'drop',
    'truncate',
    'update',
    'insert',
    'into',
    'table',
    'values',
    'set',

    #  datatypes
    'integer',
    'real',  # floating point number
    'text',  # variable length text

}


class Token:
    """
    Represents a token of the source
    """
    def __init__(self, token_type: TokenType, lexeme: str, literal: Any, line: int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        # when object is printed
        body = f'{self.token_type}'
        tail = self.literal or self.lexeme
        if tail:
            body = f'{body}[{tail}]'
        return body

    def __repr__(self) -> str:
        # appears in collections
        return f'Token({self.__str__()})'
