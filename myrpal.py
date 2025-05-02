import argparse
from src.lexer import Lexer
from src.parser import Parser
from src.rpal_ast import print_ast

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input RPAL program file")
    parser.add_argument("-ast", action="store_true", help="Print AST only")
    args = parser.parse_args()

    # Step 1: Read the source code from the input file
    with open(args.filename, "r") as file:
        source_code = file.read()

    # Step 2: Run the lexer to tokenize the source code
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Step 3: Run the parser to build the AST
    parser = Parser(tokens)
    ast_root = parser.parse()

    # Step 4: If `-ast` switch is given, print the tree and exit
    if args.ast:
        print_ast(ast_root)

if __name__ == "__main__":
    main()
