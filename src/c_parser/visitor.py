from pycparser.c_ast import NodeVisitor


class NodeVisitor(NodeVisitor):
    """
    A base visitor class for walking and inspecting a pycparser AST.

    Subclass this class and define visit_<NodeType> methods to handle
    specific AST node types (e.g., visit_FuncDef, visit_FuncCall, visit_If).

    To continue traversing child nodes after processing a node, call
    self.generic_visit(node) within the visitor method.
    """

    def __init__(self):
        self.assignments = []

    def visit_FuncDef(self, node):
        """Visit a function definition node."""
        print(f"Function: {node.decl.name} at line {node.decl.coord.line}")
        self.generic_visit(node)

    def visit_Assignment(self, node):
        # Handle assignment statements
        print(f"Assignment at line {node.coord.line}")
        self.generic_visit(node)

    def visit_FuncCall(self, node):  # noqa: N802
        """Visit a function call node."""
        print(f"Function call: {node.name.name} at line {node.coord.line}")
        self.generic_visit(node)

    def visit_If(self, node):
        """Visit an if statement node."""
        print(f"If statement at line {node.coord.line}")
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit a for loop node."""
        print(f"For loop at line {node.coord.line}")
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit a while loop node."""
        print(f"While loop at line {node.coord.line}")
        self.generic_visit(node)

    def visit_Return(self, node):
        """Visit a return statement node."""
        print(f"Return statement at line {node.coord.line}")
        self.generic_visit(node)

class PrintAll(NodeVisitor):
    def generic_visit(self, node):
        print(type(node).__name__)
        super().generic_visit(node)