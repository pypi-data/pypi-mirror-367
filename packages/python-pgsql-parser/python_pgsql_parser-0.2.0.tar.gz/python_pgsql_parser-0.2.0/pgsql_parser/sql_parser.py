from typing import List, Dict
from collections import OrderedDict
from .models import Token, TokenType, VOID_TOKEN, Statement
from .parser_base import ParserBase
from .sql_lexer import AdvancedSQLLexer
from .models import (
    Statement,
    TokenType,
    Token,
    VOID_TOKEN,
    Table,
    Column,
    PrimaryKey,
    ForeignKey,
    Constraint,
    Index,
)


class AdvancedStatementAnalyzer(ParserBase):
    def __init__(self, stmt_tokens: List[Token]):
        super().__init__(stmt_tokens)
        self.statement = Statement(stmt_tokens)
        self._parse()

    def _parse(self):
        while self.current_pos < self.num_of_tokens:
            current_token = self.tokens[self.current_pos]
            if current_token.token_type == TokenType.OPEN_PAREN:
                toks = self._read_enclosure()
                if (
                    len(toks) > 2
                    and toks[1].token_type == TokenType.KEYWORD
                    and toks[1].value.upper() == "SELECT"
                ):
                    _parser = AdvancedStatementAnalyzer(toks[1:-1])
                    substmt = _parser.statement
                    self.statement.ast.append(toks[0])
                    self.statement.ast.append(substmt)
                    self.statement.ast.append(toks[-1])
                else:
                    self.statement.ast.extend(toks)
            else:
                self.statement.ast.append(self._consume_one())


class ColumnDefParser(ParserBase):
    def __init__(self, col_def: List[Token]):
        super().__init__(col_def)
        self.col_name = None
        self.col_type = None
        self.nullable = True
        self.default_value = None
        self.is_primary = False
        self.fk_ref = None
        self.max_char_length = None
        self.precision = 0
        self.scale = 0
        self.primary_key = None
        self.foreign_key = None
        self.constraint = None
        self.foreign_key_ref = None
        self._parse()

    def _parse(self):
        first_tok = self._peek()
        second_tok = self._look_ahead()
        if self._is_keyword(first_tok, "PRIMARY") and self._is_keyword(
            second_tok, "KEY"
        ):
            self._parse_primary_key()
        elif self._is_keyword(first_tok, "FOREIGN") and self._is_keyword(
            second_tok, "KEY"
        ):
            self._parse_foreign_key()
        elif self._is_keyword(first_tok, "CONSTRAINT"):
            self._parse_constraint()
        else:
            self._parse_column_def()

    def _parse_column_def(self):
        while self.current_pos < self.num_of_tokens:
            tok = self._consume_one()
            if self.col_name is None:
                self.col_name = tok.value
            elif self.col_type is None:
                self.col_type = tok.value.upper()
            elif tok.token_type == TokenType.OPEN_PAREN:
                self._parse_precision_scale()
                self._consume_one()  # consume close_paren
            elif self._is_keyword(tok, "NOT") and self._is_keyword(
                self._peek(), "NULL"
            ):
                self.nullable = False
                self._consume_one()  # consume null
            elif self._is_keyword(tok, "NULL"):
                self.nullable = True
            elif self._is_keyword(tok, "PRIMARY") and self._is_keyword(
                self._peek(), "KEY"
            ):
                self.nullable = False
                self.is_primary = True
                self._consume_one()  # consume key
                self.primary_key = PrimaryKey(None, None, [self.col_name])
            elif self._is_keyword(tok, "DEFAULT"):
                self._parse_column_default()  # consume key
            elif self._is_keyword(tok, "COLLATE"):
                self._parse_column_collate()  # consume key
            elif self._is_keyword(tok, "REFERENCES"):
                self._parse_fk_refrence()
            elif self._is_keyword(tok, "UNIQUE"):
                self.constraint = Constraint(None, "UNIQUE", None, [self.col_name])
            elif self._is_keyword(tok, "CHECK"):
                expr = self._consume_enclosure()
                self.constraint = Constraint(None, "CHECK", expr, [self.col_name])

    def _parse_fk_refrence(self):
        dbname = None
        schema = None
        ref_table = self._consume_one().value
        if self._peek().token_type == TokenType.IDENTIFIER_SEP:
            self._consume_one()
            schema = ref_table
            ref_table = self._consume_one().value
        if self._peek().token_type == TokenType.IDENTIFIER_SEP:
            self._consume_one()
            dbname = schema
            schema = ref_table
            ref_table = self._consume_one().value

        ref_columns = self._consume_enclosured_elements()
        print(ref_columns)
        if self.foreign_key is None:
            self.foreign_key = ForeignKey(
                None,
                None,
                columns=[self.col_name],
                ref_table=ref_table,
                ref_schema=schema,
                ref_database=dbname,
                ref_columns=ref_columns,
            )
        else:
            self.foreign_key.ref_table = ref_table
            self.foreign_key.ref_schema = schema
            self.foreign_key.ref_database = dbname
            self.foreign_key.ref_columns = ref_columns
        self.foreign_key.is_composite_key = len(ref_columns) > 1

    def _parse_column_default(self):
        tok = self._consume_one()
        if tok.token_type in [TokenType.STRING_LITERAL, TokenType.NUMERIC_LITERAL]:
            self.default_value = tok.value
        else:
            val = ""
            if self._peek().token_type == TokenType.OPEN_PAREN:
                val = self._consume_enclosure()
            self.default_value = f"SERVER_SIDE_FUNCTION:{tok.value}{val}"

    def _parse_column_collate(self):
        self._consume_one()
        if self._peek().token_type == TokenType.IDENTIFIER_SEP:
            self._consume_one()
            self._consume_one()

    def _parse_precision_scale(self):
        length_precision = self._consume_one().value
        scale = None
        if (
            self._peek().token_type == TokenType.PUNCTUATION
            and self._peek().value == ","
        ):
            self._consume_one()
            scale = self._consume_one().value
        if scale is not None:
            self.precision = int(length_precision)
            self.scale = scale
        else:
            self.max_char_length = int(length_precision)

    def _parse_primary_key(self, name: str = None):
        self._consume_one()  # Primary
        self._consume_one()  # Key
        columns = self._consume_enclosured_elements()
        self.primary_key = PrimaryKey(name, None, columns)
        pass

    def _parse_foreign_key(self, name: str = None):
        self._consume_one()  # foreign
        self._consume_one()  # Key
        columns = self._consume_enclosured_elements()
        self.foreign_key = ForeignKey(name, None, columns, None, None)
        self._consume_one()  # references

        self._parse_fk_refrence()

        pass

    def _parse_constraint(self):
        self._consume_one()
        cst_name = self._consume_one().value
        if self._is_keyword(self._peek(), "PRIMARY") and self._is_keyword(
            self._look_ahead(), "KEY"
        ):
            self._parse_primary_key(cst_name)
        elif self._is_keyword(self._peek(), "FOREIGN") and self._is_keyword(
            self._look_ahead(), "KEY"
        ):
            self._parse_foreign_key(cst_name)
        elif self._is_keyword(self._peek(), "UNIQUE"):
            self._consume_one()
            while (
                self._peek().token_type == TokenType.KEYWORD
                and self._peek().value.upper() in ["NULLS", "NOT", "DISTINCT"]
            ):
                self._consume_one()
            columns = self._consume_enclosured_elements()
            self.constraint = Constraint(cst_name, "UNIQUE", None, columns)
        elif self._is_keyword(self._peek(), "CHECK"):
            self._consume_one()
            expr = self._consume_one()
            self.constraint = Constraint(cst_name, "CHECK", expr, None)
        else:
            while self.current_pos < self.nums_of_tokes:
                self._consume_one()


class AdvancedDDLStatementParser(ParserBase):
    def __init__(self, statement: Statement, parsed_tables: Dict[str, Table]):
        self.table = None
        self.statement = statement
        super().__init__(self.statement.ast)
        self.parsed_tables = parsed_tables
        self.current_table = None
        self._parse()

    def _parse(self):
        first_token_value = self._peek().value.upper()
        second_token_value = self._look_ahead(1).value.upper()
        if first_token_value == "CREATE" and second_token_value in [
            "TABLE",
            "TEMPORARY",
            "TEMP",
            "UNLOGGED",
            "MATERIALIZED",
            "VIEW",
        ]:
            self._parse_create_table_statement()
        elif first_token_value == "ALTER" and second_token_value == "TABLE":
            self._parse_alter_table_statement()
        elif first_token_value == "CREATE" and second_token_value == "INDEX":
            self._parse_create_index_statement()

    def _is_keyword(self, tok: Token, expected_val):
        return tok.token_type == TokenType.KEYWORD and tok.uval() == expected_val

    def _parse_full_qualify_table_name(self):
        dbname = None
        dbschema = None
        table_name = None
        tok_cnt = 1
        if self._look_ahead(1).value == ".":
            if self._look_ahead(3).value == ".":
                dbname = self._peek().value
                dbschema = self._look_ahead(2).value
                table_name = self._look_ahead(4).value
                tok_cnt = 5
            else:
                dbschema = self._peek().value
                table_name = self._look_ahead(3).value
                tok_cnt = 3
        else:
            table_name = self._peek().value
        self._consume(tok_cnt)
        self.current_table = Table(table_name, dbschema, dbname)
        return (dbname, dbschema, table_name)

    def _parse_create_table_statement(self):
        while self.current_pos < self.num_of_tokens:
            curent_token = self._consume_one()
            print(curent_token.value)
            if self._is_keyword(curent_token, "TABLE"):
                break
        if self._is_keyword(self._look_ahead(), "IF"):
            self._consume(3)
        self._parse_full_qualify_table_name()
        if self._peek().token_type == TokenType.OPEN_PAREN:
            self._parse_create_table_columns()

        elif self._is_keyword(self._peek(), "AS"):
            pass

    def _parse_create_table_columns(self):
        self._consume_one()  # pop open Paren
        stack = 0
        columns_def = []
        col_buf = []
        while self.current_pos < self.num_of_tokens:
            tok = self._consume_one()
            if tok.token_type == TokenType.OPEN_PAREN:
                col_buf.append(tok)
                stack += 1
            elif tok.token_type == TokenType.CLOSE_PAREN:
                if stack == 0:
                    self.current_pos -= 1
                    columns_def.append(col_buf)
                    col_buf = []
                    break
                else:
                    stack -= 1
                    col_buf.append(tok)
            elif (
                tok.token_type == TokenType.PUNCTUATION
                and tok.value == ","
                and stack == 0
            ):
                columns_def.append(col_buf)
                col_buf = []
            else:
                col_buf.append(tok)

        for col_def in columns_def:
            self._parse_col_def(col_def)

    def _parse_col_def(self, col_def):
        col_parser = ColumnDefParser(col_def)
        if col_parser.col_name is not None:
            self.current_table.columns[col_parser.col_name] = Column(
                self.current_table.name,
                col_parser.col_name,
                col_parser.col_type,
                nullable=col_parser.nullable,
                default_value=col_parser.default_value,
                is_primary=col_parser.is_primary,
            )
        if col_parser.primary_key is not None:
            col_parser.primary_key.table_name = self.current_table.name
            self.current_table.primary_key = col_parser.primary_key
            for col in col_parser.primary_key.columns:
                self.current_table.columns[col].is_primary = True
                self.current_table.columns[col].nullable = False
        if col_parser.foreign_key is not None:
            self.current_table.foreign_keys.append(col_parser.foreign_key)
        if col_parser.constraint is not None:
            self.current_table.constraints.append(col_parser.constraint)

    def _parse_alter_table_statement(self):
        self._consume(2)
        if self._is_keyword(self._peek(), "IF"):
            self._consume(2)
        if self._is_keyword(self._peek(), "ONLY"):
            self._consume_one()
        table_name = self._consume_one()
        if self._peek().token_type == TokenType.IDENTIFIER_SEP:
            table_name = self._consume_one()
            if self._peek().token_type == TokenType.IDENTIFIER_SEP:
                table_name = self._consume_one()

        self.current_table = self.parsed_tables.get(table_name.value)
        if self.current_table is None:
            print(
                f"warning table {table_name.value} not found {self.parsed_tables.keys()}"
            )
            return

        if self._is_keyword(self._peek(), "ADD"):
            self._consume_one()
        col_def = None
        if self._is_keyword(self._peek(), "CONSTRAINT"):
            col_def = self.tokens[self.current_pos :]
        elif self._is_keyword(self._peek(), "COLUMN"):
            if self._is_keyword(self._peek(), "IF"):
                self._consume(3)
            col_def = self.tokens[self.current_pos + 1 :]

        elif self._is_keyword(self._peek(), "IF"):
            self._consume(3)
            col_def = self.tokens[self.current_pos + 1 :]

        if col_def:
            self._parse_col_def(col_def)

    def _parse_create_index_statement(self):
        pass


class SQLQueryParser(ParserBase):

    def __init__(self, statement: Statement, parsed_tables: Dict[str, Table]):
        self.table = None
        self.statement = statement
        super().__init__(self.statement.ast)
        self.parsed_tables = parsed_tables
        self.current_table = None
        self.cte_queries = None
        self._parse()

    def _parse(self):
        if self._is_keyword(self._peek(), "WITH"):
            self._parse_cte()
        else:
            self._parse_select()

    def _parse_cte_with(self):
        cte_queries = {}
        while (
            not self._is_keyword(self._peek(), "SELECT") and self._peek() != VOID_TOKEN
        ):
            alias = self._consume_one()
            self._consume_one()  # AS
            self._consume_one()  # (
            stmt = self._consume_one()
            self._consume_one()  # )
            if (
                self._peek().token_type == TokenType.PUNCTUATION
                and self._peek().value == ","
            ):
                self._consume_one()
            cte_queries[alias] = stmt
        return cte_queries

    def _parse_cte(self):
        self._consume_one()
        self.cte_queries = self._parse_cte_with()
        self._parse_select()

    def _parse_select(self):
        self._consume_one()  # Select
        self.current_table = Table(self.to_string(), None, None, "QUERY")
        while not self._is_keyword(self._peek(), "FROM") and self._peek() != VOID_TOKEN:
            self._parse_select_element()

    def _parse_select_element(self):
        col_tok = self._consume_one()
        col_tok2 = self._consume_one()
        expr = None
        alias = None
        if self._is_comma(col_tok2):
            alias = col_tok.value
            expr = col_tok.value
        elif self._is_keyword(col_tok2, "AS"):
            alias = self._consume_one()
            expr = col_tok.value
            self._consume_one()  # comma
        elif self._is_possible_column(col_tok2) and self._is_comma(self._peek()):
            alias = col_tok2.value
            expr = col_tok.value
            self._consume_one()  # comma
        else:
            stack = 0
            expr_buf = [col_tok, col_tok2]
            while (
                not self._is_keyword(self._peek(), "FROM")
                and self._peek() != VOID_TOKEN
            ):
                tok = self._consume_one()
                if tok.token_type == TokenType.OPEN_PAREN:
                    stack += 1
                elif tok.token_type == TokenType.CLOSE_PAREN:
                    stack -= 1
                if self._is_comma(tok) and stack == 0:
                    break
                else:
                    expr_buf.append(tok)

            self._consume_one()  # comma
            last_token = expr_buf[-1]
            if self._is_expr_ending(last_token):
                expr = " ".join(t.value for t in expr_buf)
                alias = None
            elif self._is_possible_column(last_token) and self._is_keyword(
                expr_buf[-2], "AS"
            ):
                expr = " ".join(t.value for t in expr_buf[0:-2])
                alias = last_token.value
            elif self._is_possible_column(last_token):
                expr = " ".join(t.value for t in expr_buf[0:-1])
                alias = last_token.value
            else:
                expr = " ".join(t.value for t in expr_buf)
                alias = None

        col = Column("", alias, "VARCHAR", True, None, None)
        col.alias = alias
        col.expr = expr
        self.current_table.add_column(col)


class AdvancedSQLParser:

    def __init__(self, sql_script: str):
        self.lexer = AdvancedSQLLexer(sql_script)
        self.tables = OrderedDict()
        self._parse()

    def _parse(self):
        for ddl_stmt_tokens in self.lexer.get_statements():
            analyzer = AdvancedStatementAnalyzer(ddl_stmt_tokens)
            first_token = analyzer.statement.ast[0]
            if (
                first_token.token_type == TokenType.KEYWORD
                and first_token.value.upper() in ["SELECT", "WITH"]
            ):
                parser = SQLQueryParser(analyzer.statement, self.tables)
            else:
                parser = AdvancedDDLStatementParser(analyzer.statement, self.tables)
            table = parser.current_table
            if table is not None:
                self.tables[table.name] = table

    def get_tables(self) -> Dict[str, Table]:
        return self.tables

    def get_table(self, table_name: str) -> Table | None:
        return self.tables.get(table_name)

    def get_table_list(self) -> List[Table]:
        return [self.tables[t] for t in self.tables]
