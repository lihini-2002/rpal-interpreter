import argparse
from src.lexer import Lexer
from src.parser import Parser
from src.standerizer.ast import AST
from src.standerizer.node import Node
from src.standerizer import ast_factory
from src.lcrs_to_nary_convertor import lcrs_to_nary
from src.rpal_ast import print_ast
from src.nary_to_lcrs_convertor import nary_to_lcrs
from src.CSEM.csemachine import CSEMachine
from src.CSEM.cse_factory import CSEMachineFactory

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
        print_ast(ast_root)
        return

    # Step 5: Convert LCRS AST to n-ary tree
    nary_root = lcrs_to_nary(ast_root)

    # Wrap in AST object
    ast_obj = AST(nary_root)

    # Step 6: Standardize
    ast_obj.standardize()

    # If -st → print standardized AST and exit
    if args.st:
        print("Standardized AST:")
        ast_obj.print_ast()
        return

    # Step 7: Convert n-ary tree back to LCRS(Now the standardized AST is in the lcrs format.Now an ADTNode object)
    st_lcrs_root = nary_to_lcrs(ast_obj.root)
    
    cse_machine_factory = CSEMachineFactory()
    cse_machine = cse_machine_factory.get_cse_machine(ast_obj)
        
    # Default action: print the final output
    print("Output of the above program is:")
    print(cse_machine.get_answer())


if __name__ == "__main__":
    main()
