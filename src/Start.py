import sys
import os

from c_parser.cParser import get_ast, analyze_program
from c_parser.visitor import NodeVisitor, PrintAll
from witness_generator import *

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python Start.py <c_file>")
        sys.exit(1)

    c_file = sys.argv[1]

    with open(c_file, "r", encoding="utf-8-sig") as f:
        source = f.read()

    ast = analyze_program(source)
    print(f"Parsed AST for: {c_file}")
    visitor = NodeVisitor()
    visitor.visit(ast)
