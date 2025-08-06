import pytest
from typing import List
from pgsql_parser.models import TokenType, Token
from pgsql_parser.sql_parser import AdvancedStatementAnalyzer, Statement


@pytest.fixture
def create_tokens():
    """Fixture to create a list of mock Token objects."""

    def _create_tokens_list(token_specs: List[tuple]):
        tokens = []
        pos = 0
        for token_type, value in token_specs:
            tokens.append(Token(token_type, value, pos))
            pos += len(value) if isinstance(value, str) else 1
        return tokens

    return _create_tokens_list


def test_simple_select_statement_parsing(create_tokens):
    """Test parsing a simple SELECT statement without subqueries."""
    token_specs = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.PUNCTUATION, ","),
        (TokenType.IDENTIFIER, "name"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.IDENTIFIER, "users"),
    ]
    tokens = create_tokens(token_specs)
    parser = AdvancedStatementAnalyzer(tokens)

    # The parser should simply append the tokens to the AST for a simple statement
    expected_ast = [
        Token(TokenType.KEYWORD, "SELECT", 0),
        Token(TokenType.IDENTIFIER, "id", 6),
        Token(TokenType.PUNCTUATION, ",", 8),
        Token(TokenType.IDENTIFIER, "name", 9),
        Token(TokenType.KEYWORD, "FROM", 13),
        Token(TokenType.IDENTIFIER, "users", 17),
    ]

    actual_ast_values = [(t.token_type, t.value) for t in parser.statement.ast]
    expected_ast_values = [(t.token_type, t.value) for t in expected_ast]
    assert actual_ast_values == expected_ast_values


def test_select_with_enclosed_expression(create_tokens):
    """Test parsing a statement with parentheses but not a subquery."""
    token_specs = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.NUMERIC_LITERAL, "1"),
        (TokenType.OPERATOR, "+"),
        (TokenType.NUMERIC_LITERAL, "2"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.KEYWORD, "AS"),
        (TokenType.IDENTIFIER, "result"),
    ]
    tokens = create_tokens(token_specs)
    parser = AdvancedStatementAnalyzer(tokens)

    # The parser should simply add the tokens to the AST
    expected_ast_values = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.NUMERIC_LITERAL, "1"),
        (TokenType.OPERATOR, "+"),
        (TokenType.NUMERIC_LITERAL, "2"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.KEYWORD, "AS"),
        (TokenType.IDENTIFIER, "result"),
    ]

    actual_ast_values = [(t.token_type, t.value) for t in parser.statement.ast]
    assert actual_ast_values == expected_ast_values


def test_simple_subquery_parsing(create_tokens):
    """Test parsing a statement with a simple subquery."""
    main_query_tokens = create_tokens(
        [
            (TokenType.KEYWORD, "SELECT"),
            (TokenType.IDENTIFIER, "name"),
            (TokenType.KEYWORD, "FROM"),
            (TokenType.OPEN_PAREN, "("),
        ]
    )
    subquery_tokens = create_tokens(
        [
            (TokenType.KEYWORD, "SELECT"),
            (TokenType.IDENTIFIER, "id"),
            (TokenType.IDENTIFIER, "name"),
            (TokenType.KEYWORD, "FROM"),
            (TokenType.IDENTIFIER, "users"),
        ]
    )
    closing_tokens = create_tokens(
        [
            (TokenType.CLOSE_PAREN, ")"),
            (TokenType.IDENTIFIER, "sub"),
        ]
    )

    all_tokens = main_query_tokens + subquery_tokens + closing_tokens

    # Manually adjust positions for subquery tokens for consistency
    # This is a bit brittle, but necessary for the mock tokens.
    start_pos = all_tokens[-2].start_position + 1
    closing_tokens[0].start_position = start_pos
    closing_tokens[1].start_position = start_pos + 1

    parser = AdvancedStatementAnalyzer(all_tokens)
    # The AST should contain the outer tokens and a nested Statement object for the subquery
    assert parser.statement.ast[0].token_type == TokenType.KEYWORD
    assert parser.statement.ast[0].value == "SELECT"
    assert parser.statement.ast[1].token_type == TokenType.IDENTIFIER
    assert parser.statement.ast[1].value == "name"
    assert parser.statement.ast[2].token_type == TokenType.KEYWORD
    assert parser.statement.ast[2].value == "FROM"
    assert parser.statement.ast[3].token_type == TokenType.OPEN_PAREN
    assert isinstance(parser.statement.ast[4], Statement)
    assert parser.statement.ast[5].token_type == TokenType.CLOSE_PAREN
    assert parser.statement.ast[6].token_type == TokenType.IDENTIFIER
    assert parser.statement.ast[6].value == "sub"

    # Verify the contents of the nested statement
    subquery_ast = parser.statement.ast[4].ast
    subquery_ast_values = [(t.token_type, t.value) for t in subquery_ast]
    expected_subquery_values = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "id"),
        (TokenType.IDENTIFIER, "name"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.IDENTIFIER, "users"),
    ]
    assert subquery_ast_values == expected_subquery_values


def test_nested_subquery_parsing(create_tokens):
    """Test parsing a query with a nested subquery."""
    token_specs = [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "a"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "b"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.OPEN_PAREN, "("),
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "c"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.IDENTIFIER, "t3"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.IDENTIFIER, "s2"),
        (TokenType.CLOSE_PAREN, ")"),
        (TokenType.IDENTIFIER, "s1"),
    ]
    tokens = create_tokens(token_specs)

    # Manually adjust positions to make the tokens consistent
    pos = 0
    for tok in tokens:
        tok.start_position = pos
        pos += 1

    parser = AdvancedStatementAnalyzer(tokens)

    # Outer query AST
    assert parser.statement.ast[0].value == "SELECT"
    assert (
        isinstance(parser.statement.ast[3], Token)
        and parser.statement.ast[3].value == "("
    )
    assert isinstance(parser.statement.ast[4], Statement)

    # First nested subquery AST
    subquery1 = parser.statement.ast[4]
    assert subquery1.ast[0].value == "SELECT"
    assert subquery1.ast[3].value == "("
    assert isinstance(subquery1.ast[4], Statement)

    # Second nested subquery AST
    subquery2 = subquery1.ast[4]
    assert [(t.token_type, t.value) for t in subquery2.ast] == [
        (TokenType.KEYWORD, "SELECT"),
        (TokenType.IDENTIFIER, "c"),
        (TokenType.KEYWORD, "FROM"),
        (TokenType.IDENTIFIER, "t3"),
    ]
