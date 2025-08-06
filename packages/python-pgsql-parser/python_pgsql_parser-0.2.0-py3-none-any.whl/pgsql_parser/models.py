from typing import Optional, List, Tuple, Dict
from enum import Enum


class Column:
    __slots__ = (
        "table_name",
        "name",
        "data_type",
        "char_length",
        "numeric_precision",
        "numeric_scale",
        "nullable",
        "default_value",
        "is_primary",
        "primary_key_position",
        "foreign_key_ref",
        "constraints",
        "expr",
        "alias",
    )

    def __init__(
        self,
        table_name,
        name: str,
        data_type: Optional[str] = None,
        nullable: bool = True,
        default_value: Optional[str] = None,
        is_primary: bool = False,
    ):
        self.table_name = (table_name,)
        self.name = name
        self.data_type: Optional[str] = data_type
        self.nullable: bool = nullable
        self.default_value: Optional[str] = default_value
        self.is_primary: bool = is_primary
        self.char_length: Optional[int] = None
        self.numeric_precision: Optional[int] = None
        self.numeric_scale: Optional[int] = None
        self.expr = None
        self.alias = None
        self.primary_key_position: Optional[int] = None
        self.foreign_key_ref: Optional[Tuple[str, str, str]] = None
        self.constraints: List[Dict] = []  # For column-level constraints

    def uval(self):
        return self.value.upper() if self.value else ""

    def __repr__(self):
        return (
            f"Column(table_name={self.table_name}, name={self.name!r}, type={self.data_type!r}, "
            f"nullable={self.nullable})"
        )


class PrimaryKey:
    __slots__ = ("name", "table_name", "columns")

    def __init__(self, name: Optional[str], table_name: str, columns: List[str]):
        self.name = name
        self.columns = columns
        self.table_name = table_name

    def __repr__(self):
        return f"PrimaryKey(name={self.name!r}, table_name={self.table_name}, columns={self.columns})"


class ForeignKey:
    __slots__ = (
        "name",
        "table_name",
        "columns",
        "ref_table",
        "ref_columns",
        "ref_schema",
        "ref_database",
        "is_composite_key",
    )

    def __init__(
        self,
        name: Optional[str],
        table_name: str,
        columns: List[str],
        ref_table: str,
        ref_columns: List[str],
        ref_schema: str = None,
        is_composite_key=False,
        ref_database: str = None,
    ):
        self.name = name
        self.table_name = table_name
        self.columns = columns
        self.ref_table = ref_table
        self.ref_columns = ref_columns
        self.is_composite_key = is_composite_key
        self.ref_schema = ref_schema
        self.ref_database = ref_database

    def __repr__(self):
        return (
            f"ForeignKey(name={self.name!r}, table_name={self.table_name}, columns={self.columns}, "
            f"ref_table={self.ref_table!r}, ref_columns={self.ref_columns})"
        )


class Constraint:
    __slots__ = ("name", "ctype", "expression", "columns")

    def __init__(
        self,
        name: str,
        ctype: str,
        expression: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ):
        self.name = name
        self.ctype = ctype  # 'CHECK', 'UNIQUE', 'NOT NULL', etc.
        self.expression = expression
        self.columns = columns or []

    def __repr__(self):
        return f"Constraint({self.ctype}, name={self.name!r}, cols={self.columns})"


class Index:
    __slots__ = ("name", "table", "columns", "is_unique", "method")

    def __init__(
        self,
        name: str,
        table: str,
        columns: List[str],
        is_unique: bool = False,
        method: Optional[str] = None,
    ):
        self.name = name
        self.table = table
        self.columns = columns
        self.is_unique = is_unique
        self.method = method

    def __repr__(self):
        return f"Index(name={self.name!r}, table={self.table}, columns={self.columns})"


class Table:
    __slots__ = (
        "database",
        "schema",
        "name",
        "table_type",
        "columns",
        "primary_key",
        "foreign_keys",
        "constraints",
        "is_view",
        "view_definition",
        "is_materialized",
    )

    def __init__(
        self,
        name: str,
        schema: Optional[str] = None,
        database: Optional[str] = None,
        table_type: str = "TABLE",
    ):
        self.database = database
        self.schema = schema
        self.name = name
        self.table_type = table_type
        self.primary_key = None
        self.columns: Dict[str, Column] = {}
        self.foreign_keys: List[ForeignKey] = []
        self.constraints: List[Constraint] = []
        self.is_view = False
        self.view_definition: Optional[str] = None
        self.is_materialized = False

    def add_column(self, column: Column):
        print("Adding column (281)", column)
        if isinstance(column, ForeignKey):
            self.foreign_keys.append(column)
        elif isinstance(column, PrimaryKey):
            self.primary_key = column
        else:
            self.columns[column.name] = column
        print("Added column (288)", self.columns)

    def get_qualified_name(self) -> str:
        parts = []
        if self.database:
            parts.append(self.database)
        if self.schema:
            parts.append(self.schema)
        parts.append(self.name)
        return ".".join(parts)

    def __repr__(self):
        return (
            f"Table(name={self.get_qualified_name()}, type={self.table_type}, "
            f"columns={len(self.columns)}, pkey={self.primary_key!r})"
        )


class TokenType(Enum):
    HIDDEN = 0
    KEYWORD = 1
    IDENTIFIER = 2
    QUOTED_IDENTIFIER = 3
    STRING_LITERAL = 4
    NUMERIC_LITERAL = 5
    OPERATOR = 6
    PUNCTUATION = 7
    COMMENT = 8
    BLOCK_CONTROL = 9
    OPEN_PAREN = 10
    CLOSE_PAREN = 11
    STATEMENT_SEP = 12
    IDENTIFIER_SEP = 13
    VOID = 999
    STATEMENT = 1000


class Token:
    __slots__ = (
        "token_type",
        "value",
        "start_position",
        "end_position",
        "line_number",
        "line_postion",
        "before_token",
        "after_token",
    )

    def __init__(self, token_type: TokenType, value: str, start_position: int):
        self.token_type = token_type
        self.value = value
        self.start_position = start_position
        self.end_position = None
        self.line_number = 0
        self.line_postion = 1
        self.before_token: Any = None
        self.after_token: Any = None

    def __repr__(self):
        return (
            f"Token({self.token_type.name}, '{self.value}', pos={self.start_position})"
        )

    def uval(self):
        return self.value.upper()


VOID_TOKEN = Token(TokenType.VOID, "", -1)


class Statement:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []
        self.token_type = TokenType.STATEMENT

    def get_statement_ast(self):
        return self.ast

    @property
    def value(self):
        return " ".join(tok.value for tok in self.ast)

    def __repr__(self):
        return self.value
