import re
from typing import List
from .models import Token, TokenType


_sql_keywords = [
    # Data types
    "INT",
    "INTEGER",
    "SMALLINT",
    "BIGINT",
    "SERIAL",
    "BIGSERIAL",
    "VARCHAR",
    "CHARACTER",
    "VARYING",
    "CHAR",
    "TEXT",
    "BOOLEAN",
    "NUMERIC",
    "DECIMAL",
    "REAL",
    "FLOAT",
    "DOUBLE",
    "PRECISION",
    "COLLATE",
    "DATE",
    "TIME",
    "TIMESTAMP",
    "INTERVAL",
    "JSON",
    "JSONB",
    "UUID",
    "CROSS",
    "BYTEA",
    # DDL commands
    "CREATE",
    "DROP",
    "ALTER",
    "TABLE",
    "COLUMN",
    "CONSTRAINT",
    "INDEX",
    "SEQUENCE",
    "VIEW",
    "TRIGGER",
    "FUNCTION",
    "SCHEMA",
    "DOMAIN",
    "TYPE",
    "EXTENSION",
    "DATABASE",
    "SERVER",
    "FOREIGN",
    "DATA",
    "WRAPPER",
    "ROLE",
    "USER",
    "GROUP",
    # Constraints
    "PRIMARY",
    "KEY",
    "FOREIGN",
    "REFERENCES",
    "UNIQUE",
    "CHECK",
    "DEFAULT",
    "NOT",
    "NULL",
    "CONSTRAINT",
    # DML commands
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE",
    "FROM",
    "WHERE",
    "INTO",
    "VALUES",
    "SET",
    "ORDER",
    "BY",
    "GROUP",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "RETURNING",
    # Joins
    "JOIN",
    "INNER",
    "LEFT",
    "RIGHT",
    "FULL",
    "OUTER",
    "ON",
    "USING",
    # Conditionals
    "AND",
    "OR",
    "BETWEEN",
    "IN",
    "LIKE",
    "ILIKE",
    "IS",
    "EXISTS",
    "ONLY",
    # Functions
    "COUNT",
    "SUM",
    "AVG",
    "MIN",
    "MAX",
    "DISTINCT",
    # Control
    "BEGIN",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    # Other
    "AS",
    "ASC",
    "DESC",
    "WITH",
    "WITHOUT",
    "TIME",
    "ZONE",
    "IF",
    "EXISTS",
    "CASCADE",
    "RESTRICT",
    "ADD",
    "RENAME",
    "TO",
    "COLUMN",
    # PostgreSQL specific
    "TEMPORARY",
    "TEMP",
    "VIEW",
    "MATERIALIZED",
    "UNLOGGED",
    "INDEX",
    "CONCURRENTLY",
    "USING",
    "UNIQUE",
    "CLUSTER",
    "WITH",
]


class AdvancedSQLLexer:

    def __init__(self, sql: str):
        # Set for quick keyword lookups (case-insensitive)
        self.keyword_set = {kw.lower() for kw in _sql_keywords}
        self.sql = sql.strip()
        self.current_pos = 0
        self.line_pos = 1
        self.line_num = 1
        self.text_length = len(self.sql)
        self.tokens = []
        self.current_token = None
        self._parse()

    def _look_ahead(self, ahead: int = 1):
        pos = self.current_pos + ahead
        if pos >= self.text_length:
            return None
        return self.sql[pos]

    def _match(self, text: str, ignorecase: bool = True):
        tlen = len(text)
        end_idx = self.current_pos + tlen
        tgt_text = self.sql[self.current_pos : end_idx]
        if ignorecase is True:
            return tgt_text.upper() == text.upper()
        return tgt_text == text

    def _read_line_comment(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        c = self.sql[self.current_pos]
        buf = []
        while self.current_pos < self.text_length and c != "\n":
            c = self.sql[self.current_pos]
            buf.append(c)
            self.current_pos += 1
            self.line_pos += 1

        end_pos = self.current_pos + 1
        self.line_num += 1
        self.line_pos = 1
        val = "".join(buf)
        self._add_token(
            TokenType.COMMENT,
            val,
            start_pos,
            end_pos,
            start_line_number,
            start_line_pos,
        )

    def _add_token(
        self,
        token_type: TokenType,
        val: str,
        start_pos: int,
        end_pos: int,
        line_num: int,
        line_pos: int,
    ):
        htoken = Token(token_type, val, start_pos)
        htoken.line_postion = line_pos
        htoken.line_number = line_num
        htoken.end_position = end_pos
        if self.current_token is not None:
            self.current_token.after_token = htoken
        self.current_token = htoken
        self.tokens.append(htoken)

    def comsume(self, num: int = 1):
        buf = []
        for x in range(num):
            pos = self.current_pos + x
            if pos < self.text_length:
                c = self.sql[pos]
                buf.append(c)
                self.current_pos += 1
                self.line_pos += 1
                if c == "\n":
                    self.line_pos = 1
                    self.line_num += 1
        return "".join(buf)

    def _read_string_literal(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        self.comsume()
        buf = []
        while self.current_pos < self.text_length:
            c = self.sql[self.current_pos]
            if c == "'" and self._look_ahead() == "'":
                buf.append(self.comsume())
                self.comsume()
            elif c == "'":
                self.comsume()
                self._add_token(
                    TokenType.STRING_LITERAL,
                    "".join(buf),
                    start_pos,
                    self.current_pos,
                    start_line_number,
                    start_line_pos,
                )
                break
            else:
                buf.append(self.comsume())

    def _read_quoted_identifier(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        self.comsume()
        buf = []
        while self.current_pos < self.text_length:
            c = self.sql[self.current_pos]
            if c == '"' and self._look_ahead() == '"':
                buf.append(self.comsume())
                self.comsume()
            elif c == '"':
                self.comsume()
                self._add_token(
                    TokenType.QUOTED_IDENTIFIER,
                    "".join(buf),
                    start_pos,
                    self.current_pos,
                    start_line_number,
                    start_line_pos,
                )
                break
            else:
                buf.append(self.comsume())

    def _read_identifier(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        c = self.sql[self.current_pos]
        self.current_pos += 1
        self.line_pos += 1
        buf = [c]
        while self.current_pos < self.text_length:
            c = self.sql[self.current_pos]
            if not re.match(r"^[A-Za-z0-9_$]$", c):
                tt = TokenType.IDENTIFIER
                val = "".join(buf)
                if val.lower() in self.keyword_set:
                    tt = TokenType.KEYWORD
                self._add_token(
                    tt,
                    val,
                    start_pos,
                    self.current_pos,
                    start_line_number,
                    start_line_pos,
                )
                break
            else:
                buf.append(self.comsume())

    def _read_numeric_literal(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        c = self.sql[self.current_pos]
        self.current_pos += 1
        self.line_pos += 1
        buf = [c]
        while self.current_pos < self.text_length:
            c = self.sql[self.current_pos]
            if not re.match(r"^[0-9.]$", c):
                self._add_token(
                    TokenType.NUMERIC_LITERAL,
                    "".join(buf),
                    start_pos,
                    self.current_pos,
                    start_line_number,
                    start_line_pos,
                )
                break
            else:
                buf.append(self.comsume())

    def _read_space(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        buf = []
        buf.append(self.comsume())
        while self.current_pos < self.text_length:
            c = self.sql[self.current_pos]
            if c not in [" ", "\r", "\n", "\b"]:
                self._add_token(
                    TokenType.HIDDEN,
                    "".join(buf),
                    start_pos,
                    self.current_pos,
                    start_line_number,
                    start_line_pos,
                )
                break
            else:
                buf.append(self.comsume())

    def read_single_char_token(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        current_char = self.comsume()
        token_type = TokenType.OPERATOR
        if current_char in ["*" "/", "+", "-", "%"]:
            token_type = TokenType.OPERATOR
        elif current_char == "(":
            token_type = TokenType.OPEN_PAREN
        elif current_char == ")":
            token_type = TokenType.CLOSE_PAREN
        elif current_char == ";":
            token_type = TokenType.STATEMENT_SEP
        elif current_char == ",":
            token_type = TokenType.PUNCTUATION
        elif current_char == ".":
            token_type = TokenType.IDENTIFIER_SEP

        self._add_token(
            token_type,
            current_char,
            start_pos,
            start_pos,
            start_line_number,
            start_line_pos,
        )

    def read_single_or_double_char_operator(self):
        start_pos = self.current_pos
        start_line_pos = self.line_pos
        start_line_number = self.line_num
        current_char = self.comsume()
        token_type = TokenType.OPERATOR
        ahead = self._look_ahead()
        val = current_char
        if current_char == "<" and ahead in ["=", ">"]:
            val = current_char + self.comsume()
        elif current_char == ">" and ahead == "=":
            val = current_char + self.comsume()
        elif current_char == "~" and ahead == "*":
            val = current_char + self.comsume()
        elif current_char == "!" and ahead == "=":
            val = current_char + self.comsume()

        self._add_token(
            token_type,
            val,
            start_pos,
            start_pos,
            start_line_number,
            start_line_pos,
        )

    def _parse(self):
        while self.current_pos < self.text_length:
            current_char = self.sql[self.current_pos]
            if current_char == "-":
                if self._look_ahead() == "-":
                    self._read_line_comment()
                else:
                    self.read_single_char_token()
            elif current_char == "'":
                self._read_string_literal()
            elif current_char == '"':
                self._read_quoted_identifier()
            elif current_char == "*":
                self.read_single_char_token()
            elif current_char in [
                "/",
                "+",
                "-",
                "%",
                ";",
                ",",
                ".",
                "=",
                "(",
                ")",
            ]:
                self.read_single_char_token()
            elif current_char in ["<", ">", "~", "!"]:
                self.read_single_or_double_char_operator()
            elif current_char in [" ", "\r", "\n", "\b"]:
                self._read_space()
            elif re.match(r"^[A-Za-z]$", current_char):
                self._read_identifier()
            elif re.match(r"^[0-9]$", current_char):
                self._read_numeric_literal()
            else:
                self.comsume()

    def get_statements(self) -> List[Token]:
        stmts = []
        stmt = []
        for token in self.tokens:
            if token.token_type == TokenType.STATEMENT_SEP and stmt:
                print(token, token.line_number)
                stmts.append(stmt)
                stmt = []
            elif token.token_type not in [TokenType.HIDDEN, TokenType.COMMENT]:
                stmt.append(token)
        if stmt:
            stmts.append(stmt)

        for stmt in stmts:
            ptoken = None
            for token in stmt:
                if (
                    token.token_type == TokenType.OPERATOR
                    and token.value == "*"
                    and ptoken is not None
                ):
                    if ptoken.token_type in [
                        TokenType.IDENTIFIER_SEP,
                        TokenType.KEYWORD,
                        TokenType.PUNCTUATION,
                    ]:
                        token.token_type = TokenType.IDENTIFIER
                ptoken = token
        return stmts
