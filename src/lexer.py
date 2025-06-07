import re
from enum import Enum


# === Token Types ===
class TokenType(Enum):
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    INTEGER = 'INTEGER'
    STRING = 'STRING'
    OPERATOR = 'OPERATOR'
    PUNCTUATION = 'PUNCTUATION'
    EOF = 'EOF'


# === Token Object ===
class Token:
    def __init__(self, type_, value, line=None, column=None):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        if self.type == TokenType.EOF:
            return f"<{self.type.name} → {self.value!r}>"
        location = f" @ {self.line}:{self.column}"
        return f"<{self.type.name}{location} → {self.value!r}>"

# === Token Patterns ===
token_specification = [
    ('WHITESPACE',   r'[ \t]+'),
    ('COMMENT',      r'//.*'),
    ('NEWLINE',      r'\n'),
    ('KEYWORD',      r'\b(let|in|where|fn|rec|aug|or|not|gr|ge|ls|le|eq|ne|true|false|nil|dummy|within|and|isstring|isint|istuple|isfunction|isdummy|istruthvalue|order|null)\b'),
    ('IDENTIFIER',   r'[A-Za-z_][A-Za-z0-9_]*'),
    ('INTEGER',      r'\d+'),
    ('STRING',       r"'([^'\\]|\\[tn\\']|'''')*'"),
    ('OPERATOR',     r'[+\-*/<>&.@/:=~|$!#%^_\[\]{}"‘?\';]+'),
    ('PUNCTUATION',  r'[(),;]'),
]


# === Lexer Class ===
class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.line = 1

    def tokenize(self):
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        get_token = re.compile(tok_regex).match
        pos = 0
        while pos < len(self.source):
            mo = get_token(self.source, pos)
            if mo is None:
                raise SyntaxError(f"Illegal character at line {self.line}: {self.source[pos]!r}")
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - self.source.rfind('\n', 0, mo.start())

            if kind == 'NEWLINE':
                self.line += 1
            elif kind in ('WHITESPACE', 'COMMENT'):
                pass  # Skip
            elif kind == 'KEYWORD':
                self.tokens.append(Token(TokenType.KEYWORD, value, self.line, column))
            elif kind == 'IDENTIFIER':
                self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line, column))
            elif kind == 'INTEGER':
                self.tokens.append(Token(TokenType.INTEGER, int(value), self.line, column))
            elif kind == 'STRING':
                self.tokens.append(Token(TokenType.STRING, value, self.line, column))
            elif kind == 'OPERATOR':
                self.tokens.append(Token(TokenType.OPERATOR, value, self.line, column))
            elif kind == 'PUNCTUATION':
                self.tokens.append(Token(TokenType.PUNCTUATION, value, self.line, column))

            pos = mo.end()

        self.tokens.append(Token(TokenType.EOF, 'EOF', self.line, pos))
        return self.tokens
