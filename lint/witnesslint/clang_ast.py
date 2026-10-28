# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2025 Levente Bajczi <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import clang.cindex
from dataclasses import dataclass
from collections import defaultdict
from typing import Optional
from itertools import chain


@dataclass
class NodeInfo:
    node_type: str
    startline: int
    startcol: int
    endline: int
    endcol: int
    rparenline: int = None
    rparencol: int = None


class ProgramNodes:
    def __init__(self):
        self.start = defaultdict(lambda: defaultdict(list))
        self.rparen = defaultdict(lambda: defaultdict(list))

    def add_node(self, node_info: NodeInfo):
        self.start[node_info.startline][node_info.startcol].append(node_info)
        if node_info.rparenline:
            self.rparen[node_info.rparenline][node_info.rparencol].append(node_info)

    def by_start_of_statement(self, line: int, col: Optional[int]):
        col_to_stmts = self.start[line]
        if not col:
            return list(chain(col_to_stmts.values()))
        return col_to_stmts[col]

    def by_rparen_of_statement(self, line: int, col: Optional[int]):
        col_to_stmts = self.rparen[line]
        if not col:
            return list(chain(col_to_stmts.values()))
        return col_to_stmts[col]


def get_close_paren_location(cursor):
    """Returns the location of the closing ')' in a function call."""
    tu = cursor.translation_unit
    tokens = list(tu.get_tokens(extent=cursor.extent))
    line = None
    for tok in tokens:
        if tok.spelling == ")":
            line = {"line": tok.location.line, "column": tok.location.column}
    return line


def extract_stmt_locations(cursor, results):
    loc = cursor.extent
    if loc.start.file:
        start_line, start_col = loc.start.line, loc.start.column
        end_line, end_col = loc.end.line, loc.end.column
        node_info = NodeInfo(
            node_type=str(cursor.kind).split(".")[-1],
            startline=start_line,
            startcol=start_col,
            endline=end_line,
            endcol=end_col,
        )

        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            paren_loc = get_close_paren_location(cursor)
            if paren_loc:
                node_info.rparenline = paren_loc["line"]
                node_info.rparencol = paren_loc["column"]

        results.add_node(node_info)

    for child in cursor.get_children():
        extract_stmt_locations(child, results)


def get_stmt_locations_from_source(source_file):
    index = clang.cindex.Index.create()
    tu = index.parse(source_file, args=["-std=c11"])

    results = ProgramNodes()
    extract_stmt_locations(tu.cursor, results)
    return results
