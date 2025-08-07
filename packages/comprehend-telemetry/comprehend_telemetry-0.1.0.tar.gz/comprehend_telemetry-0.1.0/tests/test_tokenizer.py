"""Tests for SQL tokenizer."""

from comprehend_telemetry.sql_analyzer import tokenize_sql, Token, TokenType


def test_simple_select():
    sql = "SELECT * FROM users"
    tokens = list(tokenize_sql(sql))

    expected = [
        Token(TokenType.KEYWORD, "SELECT"),
        Token(TokenType.WHITESPACE, " "),
        Token(TokenType.UNKNOWN, "*"),
        Token(TokenType.WHITESPACE, " "),
        Token(TokenType.KEYWORD, "FROM"),
        Token(TokenType.WHITESPACE, " "),
        Token(TokenType.IDENTIFIER, "users")
    ]

    assert tokens == expected


def test_quoted_identifiers():
    sql = 'SELECT "Name", `Email`, [UserId] FROM users'
    tokens = list(tokenize_sql(sql))

    # Check that quoted identifiers are properly tokenized
    token_values = [t.value for t in tokens if t.type != TokenType.WHITESPACE]
    assert token_values == ['SELECT', '"', 'Name', '"', ',', '`', 'Email', '`', ',', '[', 'UserId', ']', 'FROM', 'users']


def test_string_literals():
    sql = "INSERT INTO logs VALUES ('info', 'message')"
    tokens = list(tokenize_sql(sql))

    string_tokens = [t for t in tokens if t.type == TokenType.STRING]
    assert len(string_tokens) == 2
    assert string_tokens[0].value == "'info'"
    assert string_tokens[1].value == "'message'"


def test_comments():
    sql = """
    -- Single line comment
    SELECT * FROM users /* Multi
    line comment */
    """
    tokens = list(tokenize_sql(sql))

    comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
    assert len(comment_tokens) == 2
    assert comment_tokens[0].value == "-- Single line comment"
    assert "Multi" in comment_tokens[1].value and "line comment" in comment_tokens[1].value


def test_operators_and_punctuation():
    sql = "SELECT id WHERE id >= 10 AND id <= 20;"
    tokens = list(tokenize_sql(sql))

    operator_tokens = [t for t in tokens if t.type == TokenType.OPERATOR]
    punct_tokens = [t for t in tokens if t.type == TokenType.PUNCT]

    assert len(operator_tokens) == 2
    assert operator_tokens[0].value == ">="
    assert operator_tokens[1].value == "<="

    assert len(punct_tokens) == 1
    assert punct_tokens[0].value == ";"


def test_keyword_classification():
    sql = "SELECT user_name FROM users WHERE active = true"
    tokens = list(tokenize_sql(sql))

    keyword_tokens = [t for t in tokens if t.type == TokenType.KEYWORD]
    identifier_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER]

    keyword_values = [t.value for t in keyword_tokens]
    identifier_values = [t.value for t in identifier_tokens]

    assert "SELECT" in keyword_values
    assert "FROM" in keyword_values
    assert "WHERE" in keyword_values

    assert "user_name" in identifier_values
    assert "users" in identifier_values
    assert "active" in identifier_values
    assert "true" in identifier_values