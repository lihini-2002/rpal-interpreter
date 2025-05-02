from src.rpal_ast import ASTNode, build_tree
from src.lexer import Token, TokenType  

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.stack = []

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type, expected_value=None):
        token = self.peek()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if token.type == expected_type and (expected_value is None or token.value == expected_value):
            self.pos += 1
            return token
        else:
            expected = f"{expected_type.name}"
            if expected_value:
                expected += f" with value '{expected_value}'"
            raise SyntaxError(
                f"Unexpected token {token.value!r} at line {token.line}, column {token.column}. Expected {expected}."
            )
        
    def parse_E(self):
        token = self.peek()

        if token.type == TokenType.KEYWORD and token.value == 'let':
            self.match(TokenType.KEYWORD, 'let')
            self.parse_D()
            self.match(TokenType.KEYWORD, 'in')
            self.parse_E()
            build_tree('let', 2, self.stack)

        elif token.type == TokenType.KEYWORD and token.value == 'fn':
            self.match(TokenType.KEYWORD, 'fn')

            count = 0
            while self.peek().type in {TokenType.IDENTIFIER, TokenType.PUNCTUATION}:
                if self.peek().value == '(' or self.peek().value == ')':
                    break
                self.parse_Vb()
                count += 1

            self.match(TokenType.OPERATOR, '.')  # the dot in `fn ... . E`
            self.parse_E()
            build_tree('lambda', count + 1, self.stack)

        else:
            self.parse_Ew()

    def parse_D(self):
        raise NotImplementedError("parse_D not yet implemented")

    def parse_Vb(self):
        raise NotImplementedError("parse_Vb not yet implemented")

    def parse_Ew(self):
        raise NotImplementedError("parse_Ew not yet implemented")

