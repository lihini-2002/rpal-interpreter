"""
Recursive descent parser for RPAL language that implements the grammar rules
to build an Abstract Syntax Tree (AST). The parser processes tokens according to
the RPAL grammar and constructs a tree representation of the program structure.
"""

from src.rpal_ast import ASTNode, build_tree
from src.lexer import Token, TokenType  

class Parser:
    """Implements a recursive descent parser for RPAL language."""
    
    def __init__(self, tokens):
        self.tokens = tokens      # List of tokens to parse
        self.pos = 0             # Current position in token stream
        self.stack = []          # Stack for building AST nodes

    def peek(self):
        """Look at the current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def match(self, expected_type, expected_value=None):
        """
        Match and consume the current token if it matches expected type and value.
        Raises SyntaxError if token doesn't match or end of input is reached.
        """
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
        """
        Parse an expression (E) according to grammar rules:
        E -> let D in E | fn Vb+ . E | Ew
        """
        token = self.peek()

        if token.type == TokenType.KEYWORD and token.value == 'let':
            # Handle let expression: let D in E
            self.match(TokenType.KEYWORD, 'let')
            self.parse_D()
            self.match(TokenType.KEYWORD, 'in')
            self.parse_E()
            build_tree('let', 2, self.stack)

        elif token.type == TokenType.KEYWORD and token.value == 'fn':
            # Handle function definition: fn Vb+ . E
            self.match(TokenType.KEYWORD, 'fn')

            count = 0
            while self.peek().type in {TokenType.IDENTIFIER, TokenType.PUNCTUATION}:
                if self.peek().value == '(' or self.peek().value == ')':
                    break
                self.parse_Vb()
                count += 1

            self.match(TokenType.OPERATOR, '.')
            self.parse_E()
            build_tree('lambda', count + 1, self.stack)

        else:
            self.parse_Ew()

    def parse_Ew(self):
        """
        Parse where expression: Ew -> T [where Dr]
        """
        self.parse_T()

        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'where':
            self.match(TokenType.KEYWORD, 'where')
            self.parse_Dr()
            build_tree('where', 2, self.stack)

    def parse_T(self):
        """
        Parse tuple expression: T -> Ta (, Ta)*
        """
        self.parse_Ta()
        count = 1

        while self.peek().type == TokenType.PUNCTUATION and self.peek().value == ',':
            self.match(TokenType.PUNCTUATION, ',')
            self.parse_Ta()
            count += 1

        if count > 1:
            build_tree('tau', count, self.stack)

    def parse_Ta(self):
        """
        Parse augmented tuple: Ta -> Tc (aug Tc)*
        """
        self.parse_Tc()

        while self.peek().type == TokenType.KEYWORD and self.peek().value == 'aug':
            self.match(TokenType.KEYWORD, 'aug')
            self.parse_Tc()
            build_tree('aug', 2, self.stack)

    def parse_Tc(self):
        """
        Parse conditional expression: Tc -> B (-> Tc | Tc)*
        """
        self.parse_B()

        if self.peek().type == TokenType.OPERATOR and self.peek().value == '->':
            self.match(TokenType.OPERATOR, '->')
            self.parse_Tc()
            self.match(TokenType.OPERATOR, '|')
            self.parse_Tc()
            build_tree('->', 3, self.stack)

    def parse_B(self):
        """
        Parse boolean expression: B -> Bt (or Bt)*
        """
        self.parse_Bt()

        while self.peek().type == TokenType.KEYWORD and self.peek().value == 'or':
            self.match(TokenType.KEYWORD, 'or')
            self.parse_Bt()
            build_tree('or', 2, self.stack)

    def parse_Bt(self):
        """
        Parse boolean term: Bt -> Bs (& Bs)*
        """
        self.parse_Bs()

        while self.peek().type == TokenType.OPERATOR and self.peek().value == '&':
            self.match(TokenType.OPERATOR, '&')
            self.parse_Bs()
            build_tree('&', 2, self.stack)

    def parse_Bs(self):
        """
        Parse boolean secondary: Bs -> not Bp | Bp
        """
        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'not':
            self.match(TokenType.KEYWORD, 'not')
            self.parse_Bp()
            build_tree('not', 1, self.stack)
        else:
            self.parse_Bp()

    def parse_Bp(self):
        """
        Parse boolean primary: Bp -> A (relop A)?
        """
        self.parse_A()

        token = self.peek()
        if token is None:
            return

        # Map relational operators to AST labels
        relational_ops = {
            'gr': 'gr', '>': 'gr',
            'ge': 'ge', '>=': 'ge',
            'ls': 'ls', '<': 'ls',
            'le': 'le', '<=': 'le',
            'eq': 'eq',
            'ne': 'ne'
        }

        if token.value in relational_ops:
            op_token = self.match(token.type, token.value)
            self.parse_A()
            build_tree(relational_ops[op_token.value], 2, self.stack)

    def parse_A(self):
        """
        Parse arithmetic expression: A -> [+-]? At ((+|-) At)*
        """
        token = self.peek()

        # Handle unary operators
        if token.type == TokenType.OPERATOR and token.value in {'+', '-'}:
            op = self.match(TokenType.OPERATOR).value
            self.parse_At()
            if op == '-':
                build_tree('neg', 1, self.stack)
        else:
            self.parse_At()

            # Handle binary operators
            while self.peek().type == TokenType.OPERATOR and self.peek().value in {'+', '-'}:
                op = self.match(TokenType.OPERATOR).value
                self.parse_At()
                build_tree(op, 2, self.stack)

    def parse_At(self):
        """
        Parse arithmetic term: At -> Af ((*|/) Af)*
        """
        self.parse_Af()

        while self.peek().type == TokenType.OPERATOR and self.peek().value in {'*', '/'}:
            op = self.match(TokenType.OPERATOR).value
            self.parse_Af()
            build_tree(op, 2, self.stack)

    def parse_Af(self):
        """
        Parse arithmetic factor: Af -> Ap (** Af)?
        """
        self.parse_Ap()

        if self.peek().type == TokenType.OPERATOR and self.peek().value == '**':
            self.match(TokenType.OPERATOR, '**')
            self.parse_Af()
            build_tree('**', 2, self.stack)

    def parse_Ap(self):
        """
        Parse arithmetic primary: Ap -> R (@ <id> R)*
        """
        self.parse_R()

        while self.peek().type == TokenType.OPERATOR and self.peek().value == '@':
            self.match(TokenType.OPERATOR, '@')
            id_token = self.match(TokenType.IDENTIFIER)
            self.stack.append(ASTNode(f"<ID:{id_token.value}>"))
            self.parse_R()
            build_tree('@', 3, self.stack)
    
    def parse_R(self):
        """
        Parse R-expression: R -> Rn+
        """
        self.parse_Rn()

        while self.is_start_of_Rn():
            self.parse_Rn()
            build_tree('gamma', 2, self.stack)

    def is_start_of_Rn(self):
        """Check if current token can start an Rn expression."""
        token = self.peek()
        if token is None:
            return False

        return (
            token.type in {TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.STRING} or
            (token.type == TokenType.KEYWORD and token.value in {'true', 'false', 'nil', 'dummy'}) or
            (token.type == TokenType.PUNCTUATION and token.value == '(')
        )

    def parse_Rn(self):
        """
        Parse Rn-expression: Rn -> (E) | <id> | <integer> | <string> | true | false | nil | dummy
        """
        token = self.peek()

        if token.type == TokenType.PUNCTUATION and token.value == '(':
            # Handle parenthesized expression
            self.match(TokenType.PUNCTUATION, '(')
            self.parse_E()
            self.match(TokenType.PUNCTUATION, ')')

        elif token.type == TokenType.IDENTIFIER:
            # Handle identifier
            token = self.match(TokenType.IDENTIFIER)
            self.stack.append(ASTNode(f"<ID:{token.value}>"))

        elif token.type == TokenType.INTEGER:
            # Handle integer literal
            token = self.match(TokenType.INTEGER)
            self.stack.append(ASTNode(f"<INT:{token.value}>"))

        elif token.type == TokenType.STRING:
            # Handle string literal
            token = self.match(TokenType.STRING)
            self.stack.append(ASTNode(f"<STR:{token.value}>"))

        elif token.type == TokenType.KEYWORD and token.value in {'true', 'false', 'nil', 'dummy'}:
            # Handle boolean and special literals
            token = self.match(TokenType.KEYWORD)
            label = f"<{token.value}>" if token.value == "nil" else token.value
            self.stack.append(ASTNode(label))

        else:
            raise SyntaxError(f"Unexpected token in Rn: {token}")

    def parse_D(self):
        """
        Parse definition: D -> Da (within D)?
        """
        self.parse_Da()

        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'within':
            self.match(TokenType.KEYWORD, 'within')
            self.parse_D()
            build_tree('within', 2, self.stack)

    def parse_Da(self):
        """
        Parse and definition: Da -> Dr (and Dr)*
        """
        self.parse_Dr()
        count = 1

        while self.peek().type == TokenType.KEYWORD and self.peek().value == 'and':
            self.match(TokenType.KEYWORD, 'and')
            self.parse_Dr()
            count += 1

        if count > 1:
            build_tree('and', count, self.stack)

    def parse_Dr(self):
        """
        Parse recursive definition: Dr -> rec Db | Db
        """
        if self.peek().type == TokenType.KEYWORD and self.peek().value == 'rec':
            self.match(TokenType.KEYWORD, 'rec')
            self.parse_Db()
            build_tree('rec', 1, self.stack)
        else:
            self.parse_Db()

    def parse_Db(self):
        """
        Parse basic definition: Db -> (D) | Vl = E | <id> Vb+ = E
        """
        if self.peek().type == TokenType.PUNCTUATION and self.peek().value == '(':
            # Handle parenthesized definition
            self.match(TokenType.PUNCTUATION, '(')
            self.parse_D()
            self.match(TokenType.PUNCTUATION, ')')

        elif (
            self.peek().type == TokenType.IDENTIFIER and
            self.lookahead_is_vb_sequence()
        ):
            # Handle function definition
            id_token = self.match(TokenType.IDENTIFIER)
            self.stack.append(ASTNode(f"<ID:{id_token.value}>"))

            count = 1
            while self.is_start_of_Vb():
                self.parse_Vb()
                count += 1

            self.match(TokenType.OPERATOR, '=')
            self.parse_E()
            build_tree('function_form', count + 1, self.stack)

        else:
            # Handle simple definition
            self.parse_Vl()
            self.match(TokenType.OPERATOR, '=')
            self.parse_E()
            build_tree('=', 2, self.stack)

    def is_start_of_Vb(self):
        """Check if current token can start a Vb (variable binding)."""
        token = self.peek()
        return (
            token.type == TokenType.IDENTIFIER or
            (token.type == TokenType.PUNCTUATION and token.value == '(')
        )

    def lookahead_is_vb_sequence(self):
        """Check if next token is part of a variable binding sequence."""
        if self.pos + 1 >= len(self.tokens):
            return False

        next_token = self.tokens[self.pos + 1]
        return (
            next_token.type == TokenType.IDENTIFIER or
            (next_token.type == TokenType.PUNCTUATION and next_token.value == '(')
        )

    def parse_Vb(self):
        """
        Parse variable binding: Vb -> <id> | (<Vl>)
        """
        if self.peek().type == TokenType.PUNCTUATION and self.peek().value == '(':
            self.match(TokenType.PUNCTUATION, '(')

            if self.peek().type == TokenType.PUNCTUATION and self.peek().value == ')':
                self.match(TokenType.PUNCTUATION, ')')
                self.stack.append(ASTNode('()'))  # Empty binding
            else:
                self.parse_Vl()
                self.match(TokenType.PUNCTUATION, ')')

        else:
            id_token = self.match(TokenType.IDENTIFIER)
            self.stack.append(ASTNode(f"<ID:{id_token.value}>"))

    def parse_Vl(self):
        """
        Parse variable list: Vl -> <id> (, <id>)*
        """
        id_token = self.match(TokenType.IDENTIFIER)
        self.stack.append(ASTNode(f"<ID:{id_token.value}>"))
        count = 1

        while self.peek().type == TokenType.PUNCTUATION and self.peek().value == ',':
            self.match(TokenType.PUNCTUATION, ',')
            id_token = self.match(TokenType.IDENTIFIER)
            self.stack.append(ASTNode(f"<ID:{id_token.value}>"))
            count += 1

        if count > 1:
            build_tree(',', count, self.stack)

    def parse(self):
        """
        Parse the entire token stream into an AST.
        
        Returns:
            ASTNode: Root of the constructed abstract syntax tree
            
        Raises:
            SyntaxError: If the input doesn't match the grammar
        """
        self.parse_E()
        if self.pos < len(self.tokens) - 1:
            raise SyntaxError("Unexpected tokens after end of expression")
        return self.stack.pop()
