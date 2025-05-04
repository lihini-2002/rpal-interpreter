import argparse
from src.lexer import Lexer
from src.parser import Parser
from src.rpal_ast import print_ast
from src.standerdizer import standardize
from src.control_generator import generate_control, control_structures
from src.cse_machine import evaluate

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Input RPAL program file")
    parser.add_argument("-ast", action="store_true", help="Print original AST only")
    parser.add_argument("-st", action="store_true", help="Print standardized AST only")
    args = parser.parse_args()

    # Step 1: Read the source code
    with open(args.filename, "r") as file:
        source_code = file.read()

    # Step 2: Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Step 3: Syntax Analysis
    parser = Parser(tokens)
    ast_root = parser.parse()

    # Step 4: If -ast → print raw AST and exit
    if args.ast:
        print("Original AST:")
        print_ast(ast_root)
        return

    print("==== RAW AST BEFORE STANDARDIZATION ====")
    print_ast(ast_root)

    # Step 5: Standardize
    standardized_ast = standardize(ast_root)

    # If -st → print standardized AST and exit
    if args.st:
        print("Standardized AST:")
        print_ast(standardized_ast)
        return

    # Step 6: Generate Control Structure
    control = generate_control(standardized_ast)
    print("Main Control:")
    print(control)
    print("\nLambda Bodies (Control Structures):")
    for i, c in control_structures:
        print(f"delta {i} → {c}")

    # Step 7: Evaluate with CSE Machine
    result = evaluate(control, control_structures)

    # Step 8: Print final result
    print(result)

if __name__ == "__main__":
    main()
