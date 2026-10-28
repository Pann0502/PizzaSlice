# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from pycparser import c_parser, c_ast
from collections import Counter


def get_ast(text):
    parser = c_parser.CParser()
    return parser.parse(text, filename="<none>")


class NondetCallCounter(c_ast.NodeVisitor):
    def __init__(self):
        self.nondet_calls = Counter()

    def visit_FuncCall(self, node):  # noqa: N802 Override function in super class
        if "__VERIFIER_nondet" in node.name.name:
            line = node.coord.line
            self.nondet_calls[line] += 1
        super().generic_visit(node)

    def max_nondet_calls(self):
        return max(self.nondet_calls.values(), default=0)


def analyze_program(source):
    result = {}
    ast = get_ast(source)
    ndcc = NondetCallCounter()
    ndcc.visit(ast)
    result["max_nondet_calls_per_line"] = ndcc.max_nondet_calls()
    return result
