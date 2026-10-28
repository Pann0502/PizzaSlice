from pycparser import c_parser, c_ast


def get_ast(text):
    """Parse C source code text and return the AST."""
    parser = c_parser.CParser()
    return parser.parse(text, filename="<none>")


def analyze_program(source):
    """Analyze a C program by parsing it into an AST."""
    ast = get_ast(source)
    return ast