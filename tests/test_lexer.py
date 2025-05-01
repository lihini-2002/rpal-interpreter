import pytest
from src.lexer import Lexer, TokenType

def get_token_types(code):
    """Helper to return a list of token types from code."""
    return [token.type for token in Lexer(code).tokenize()]

def test_let_expression():
    code = "let X = 42 in X"
    tokens = Lexer(code).tokenize()

    assert tokens[0].type == TokenType.KEYWORD and tokens[0].value == "let"
    assert tokens[1].type == TokenType.IDENTIFIER and tokens[1].value == "X"
    assert tokens[2].type == TokenType.OPERATOR and tokens[2].value == "="
    assert tokens[3].type == TokenType.INTEGER and tokens[3].value == 42
    assert tokens[4].type == TokenType.KEYWORD and tokens[4].value == "in"
    assert tokens[5].type == TokenType.IDENTIFIER and tokens[5].value == "X"
    assert tokens[-1].type == TokenType.EOF

def test_string_literal():
    code = "'hello'"
    tokens = Lexer(code).tokenize()
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "hello"
    assert tokens[-1].type == TokenType.EOF

def test_skips_whitespace_and_comments():
    code = "let X = 10 // this is a comment\n in X"
    token_types = get_token_types(code)
    assert token_types == [
        TokenType.KEYWORD,    # let
        TokenType.IDENTIFIER, # X
        TokenType.OPERATOR,   # =
        TokenType.INTEGER,    # 10
        TokenType.KEYWORD,    # in
        TokenType.IDENTIFIER, # X
        TokenType.EOF
    ]

def test_raises_on_illegal_character():
    with pytest.raises(SyntaxError):
        Lexer("let X = `42").tokenize()  # '@' is not a valid token

def test_function_call_with_punctuation():
    code = "Print(X, 'hello')"
    tokens = Lexer(code).tokenize()

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[1].type == TokenType.PUNCTUATION and tokens[1].value == "("
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[3].type == TokenType.PUNCTUATION and tokens[3].value == ","
    assert tokens[4].type == TokenType.STRING and tokens[4].value == "hello"
    assert tokens[5].type == TokenType.PUNCTUATION and tokens[5].value == ")"
    assert tokens[-1].type == TokenType.EOF
