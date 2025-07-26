"""
Lexical analyzer for RPAL language that converts source code into a sequence of tokens.
Implements token recognition using regular expressions and handles basic lexical elements
like keywords, identifiers, literals, operators, and punctuation.
"""

import re
from enum import Enum


# === Token Types ===
class TokenType(Enum):
    """Enumeration of all possible token types in the RPAL language."""
    KEYWORD = 'KEYWORD'      # Reserved words like 'let', 'in', 'where', etc.
    IDENTIFIER = 'IDENTIFIER'  # Variable and function names
    INTEGER = 'INTEGER'      # Numeric literals
    STRING = 'STRING'        # String literals enclosed in single quotes
    OPERATOR = 'OPERATOR'    # Special characters and operators
    PUNCTUATION = 'PUNCTUATION'  # Delimiters like parentheses and commas
    EOF = 'EOF'             # End of file marker


# === Token Object ===
class Token:
    """Represents a lexical token with its type, value, and position in source code."""
    
    def __init__(self, type_, value, line=None, column=None):
        self.type = type_      # TokenType enum value
        self.value = value     # Actual token value
        self.line = line       # Line number in source
        self.column = column   # Column position in line

    def __repr__(self):
        """String representation of the token with type, value, and position."""
        if self.type == TokenType.EOF:
            return f"<{self.type.name} → {self.value!r}>"
        location = f" @ {self.line}:{self.column}"
        return f"<{self.type.name}{location} → {self.value!r}>"

# === Token Patterns ===
token_specification = [
    ('WHITESPACE',   r'[ \t]+'),                    # Spaces and tabs
    ('COMMENT',      r'//.*'),                      # Single-line comments
    ('NEWLINE',      r'\n'),                        # Line breaks
    ('KEYWORD',      r'\b(let|in|where|fn|rec|aug|or|not|gr|ge|ls|le|eq|ne|true|false|nil|dummy|within|and|isstring|isint|istuple|isfunction|isdummy|istruthvalue|order|null)\b'),  # RPAL keywords
    ('IDENTIFIER',   r'[A-Za-z_][A-Za-z0-9_]*'),    # Variable/function names
    ('INTEGER',      r'\d+'),                       # Whole numbers
    ('STRING',       r"'([^'\\]|\\[tn\\']|'''')*'"), # String literals with escape sequences
    ('OPERATOR',     r'[+\-*/<>&.@/:=~|$!#%^_\[\]{}"‘?\';]+'),  # Operators and special characters
    ('PUNCTUATION',  r'[(),;]'),                    # Delimiters
]


# === Lexer Class ===
class Lexer:
    """Converts source code into a sequence of tokens using regular expression matching."""
    
    def __init__(self, source_code):
        self.source = source_code    # Input source code
        self.tokens = []             # List of recognized tokens
        self.line = 1                # Current line number

    def tokenize(self):
        """
        Tokenizes the source code into a sequence of tokens.
        
        Returns:
            list[Token]: List of tokens representing the source code
            
        Raises:
            SyntaxError: If an illegal character is encountered
        """
        # Compile all token patterns into a single regex
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        get_token = re.compile(tok_regex).match
        pos = 0

        while pos < len(self.source):
            mo = get_token(self.source, pos)
            if mo is None:
                raise SyntaxError(f"Illegal character at line {self.line}: {self.source[pos]!r}")
            
            # Extract token information
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - self.source.rfind('\n', 0, mo.start())

            # Process different token types
            if kind == 'NEWLINE':
                self.line += 1
            elif kind in ('WHITESPACE', 'COMMENT'):
                pass  # Skip whitespace and comments
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

        # Add EOF token at the end
        self.tokens.append(Token(TokenType.EOF, 'EOF', self.line, pos))
        return self.tokens
