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

    def parse_Ew(self):
        self.parse_T()

        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'where':
            self.match(TokenType.KEYWORD, 'where')
            self.parse_Dr()
            build_tree('where', 2, self.stack)

    def parse_T(self):
        self.parse_Ta()
        count = 1

        while self.peek().type == TokenType.PUNCTUATION and self.peek().value == ',':
            self.match(TokenType.PUNCTUATION, ',')
            self.parse_Ta()
            count += 1

        if count > 1:
            build_tree('tau', count, self.stack)

    def parse_Ta(self):
        self.parse_Tc()

        while self.peek().type == TokenType.KEYWORD and self.peek().value == 'aug':
            self.match(TokenType.KEYWORD, 'aug')
            self.parse_Tc()
            build_tree('aug', 2, self.stack)

    def parse_Tc(self):
        self.parse_B()

        if self.peek().type == TokenType.OPERATOR and self.peek().value == '->':
            self.match(TokenType.OPERATOR, '->')
            self.parse_Tc()
            self.match(TokenType.OPERATOR, '|')
            self.parse_Tc()
            build_tree('->', 3, self.stack)

    def parse_B(self):
        self.parse_Bt()

        while self.peek().type == TokenType.KEYWORD and self.peek().value == 'or':
            self.match(TokenType.KEYWORD, 'or')
            self.parse_Bt()
            build_tree('or', 2, self.stack)

    def parse_Bt(self):
        self.parse_Bs()

        while self.peek().type == TokenType.OPERATOR and self.peek().value == '&':
            self.match(TokenType.OPERATOR, '&')
            self.parse_Bs()
            build_tree('&', 2, self.stack)

    def parse_Bs(self):
        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'not':
            self.match(TokenType.KEYWORD, 'not')
            self.parse_Bp()
            build_tree('not', 1, self.stack)
        else:
            self.parse_Bp()
