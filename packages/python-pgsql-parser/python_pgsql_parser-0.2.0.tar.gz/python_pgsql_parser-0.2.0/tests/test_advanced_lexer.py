import pytest
from pgsql_parser.sql_lexer import AdvancedSQLLexer
from pgsql_parser import (
    TokenType,
    Token,
)  # Replace your_module_name with the actual module name


def get_token_tuples(tokens):
    """Helper function to convert a list of Token objects to a list of (token_type, value) tuples."""
    return [(t.token_type, t.value) for t in tokens]


def test_select_statement():
    sql = "SELECT id, name FROM users WHERE id = 1;"
    lexer = AdvancedSQLLexer(sql)
    tokens = lexer.tokens

    expected_tokens = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "name"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "users"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "WHERE"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPERATOR, "="),
        (TokenType.HIDDEN, " "),
        (TokenType.NUMERIC_LITERAL, "1"),
        (TokenType.STATEMENT_SEP, ";"),
    ]

    actual_token_tuples = get_token_tuples(tokens)
    assert actual_token_tuples == expected_tokens


def test_insert_statement():
    sql = "INSERT INTO my_table (col1, col2) VALUES ('value1', 123);"
    lexer = AdvancedSQLLexer(sql)
    tokens = lexer.tokens

    expected_tokens = [
        (TokenType.KEYWORD, "INSERT"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "INTO"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "my_table"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.IDENTIFIER, "col1"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "col2"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "VALUES"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.STRING_LITERAL, "value1"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.HIDDEN, " "),
        (TokenType.NUMERIC_LITERAL, "123"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.STATEMENT_SEP, ";"),
    ]

    actual_token_tuples = get_token_tuples(tokens)
    assert actual_token_tuples == expected_tokens


def test_quoted_identifiers_and_escaped_strings():
    sql = (
        'SELECT "my""quoted""id" FROM "public"."my-table" WHERE name = \'O\'\'Malley\';'
    )
    lexer = AdvancedSQLLexer(sql)
    tokens = lexer.tokens

    expected_tokens = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.QUOTED_IDENTIFIER, 'my"quoted"id'),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.QUOTED_IDENTIFIER, "public"),
        (TokenType.IDENTIFIER_SEP, "."),
        (TokenType.QUOTED_IDENTIFIER, "my-table"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "WHERE"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "name"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPERATOR, "="),
        (TokenType.HIDDEN, " "),
        (TokenType.STRING_LITERAL, "O'Malley"),
        (TokenType.STATEMENT_SEP, ";"),
    ]

    actual_token_tuples = get_token_tuples(tokens)
    assert actual_token_tuples == expected_tokens


def test_line_comments():
    sql = "SELECT id FROM users; -- This is a comment\nSELECT name FROM users;"
    lexer = AdvancedSQLLexer(sql)
    tokens = lexer.tokens

    expected_tokens = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "users"),
        (TokenType.STATEMENT_SEP, ";"),
        (TokenType.HIDDEN, " "),
        (TokenType.COMMENT, "-- This is a comment\n"),
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "name"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "users"),
        (TokenType.STATEMENT_SEP, ";"),
    ]

    actual_token_tuples = get_token_tuples(tokens)
    assert actual_token_tuples == expected_tokens


def test_complex_query():
    sql = """
    WITH regional_sales AS (
        SELECT region, SUM(amount) AS total_sales
        FROM orders
        GROUP BY region
    )
    SELECT region, total_sales
    FROM regional_sales
    WHERE total_sales > 10000;
    """
    lexer = AdvancedSQLLexer(sql)
    tokens = lexer.tokens
    for token in tokens:
        print(token.token_type, f"[{token.value}]")
    expected_tokens = [
        (TokenType.KEYWORD, "WITH"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "regional_sales"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "AS"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.HIDDEN, "\n        "),
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "region"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "SUM"),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.IDENTIFIER, "amount"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "AS"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "total_sales"),
        (TokenType.HIDDEN, "\n        "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "orders"),
        (TokenType.HIDDEN, "\n        "),
        (TokenType.KEYWORD, "GROUP"),
        (TokenType.HIDDEN, " "),
        (TokenType.KEYWORD, "BY"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "region"),
        (TokenType.HIDDEN, "\n    "),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.HIDDEN, "\n    "),
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "region"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "total_sales"),
        (TokenType.HIDDEN, "\n    "),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "regional_sales"),
        (TokenType.HIDDEN, "\n    "),
        (TokenType.KEYWORD, "WHERE"),
        (TokenType.HIDDEN, " "),
        (TokenType.IDENTIFIER, "total_sales"),
        (TokenType.HIDDEN, " "),
        (TokenType.OPERATOR, ">"),
        (TokenType.HIDDEN, " "),
        (TokenType.NUMERIC_LITERAL, "10000"),
        (TokenType.STATEMENT_SEP, ";"),
    ]

    actual_token_tuples = get_token_tuples(tokens)
    assert actual_token_tuples == expected_tokens


def test_get_statements():
    sql = "SELECT * FROM t1; SELECT * FROM t2 WHERE id = 2;"
    lexer = AdvancedSQLLexer(sql)
    statements = lexer.get_statements()
    for token in lexer.tokens:
        print(token.token_type, token.value)

    # The get_statements method should return a list of lists of non-hidden/comment tokens
    expected_statements = [
        [
            (TokenType.KEYWORD, "SELECT"),
            (TokenType.IDENTIFIER, "*"),
            (TokenType.KEYWORD, "FROM"),
            (TokenType.IDENTIFIER, "t1"),
        ],
        [
            (TokenType.KEYWORD, "SELECT"),
            (TokenType.IDENTIFIER, "*"),
            (TokenType.KEYWORD, "FROM"),
            (TokenType.IDENTIFIER, "t2"),
            (TokenType.KEYWORD, "WHERE"),
            (TokenType.IDENTIFIER, "id"),
            (TokenType.OPERATOR, "="),
            (TokenType.NUMERIC_LITERAL, "2"),
        ],
    ]

    actual_statements_tuples = [get_token_tuples(s) for s in statements]
    for stmt in actual_statements_tuples:
        for item in stmt:
            print(item)

    assert actual_statements_tuples == expected_statements
