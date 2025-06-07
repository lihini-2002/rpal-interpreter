import pytest
from src.lexer import Token, TokenType
from src.parser import Parser

def test_parser_token_matching():
    # Simulated token stream: let x = 42;
    tokens = [
        Token(TokenType.KEYWORD, 'let', 1, 0),
        Token(TokenType.IDENTIFIER, 'x', 1, 4),
        Token(TokenType.OPERATOR, '=', 1, 6),
        Token(TokenType.INTEGER, 42, 1, 8),
        Token(TokenType.PUNCTUATION, ';', 1, 10),
        Token(TokenType.EOF, 'EOF', 1, 11),
    ]

    parser = Parser(tokens)

    # Assertions to ensure match works
    token = parser.match(TokenType.KEYWORD, 'let')
    assert token.value == 'let'

    token = parser.match(TokenType.IDENTIFIER)
    assert token.value == 'x'

    token = parser.match(TokenType.OPERATOR, '=')
    assert token.value == '='

    token = parser.match(TokenType.INTEGER)
    assert token.value == 42

    token = parser.match(TokenType.PUNCTUATION, ';')
    assert token.value == ';'

    token = parser.match(TokenType.EOF)
    assert token.value == 'EOF'
