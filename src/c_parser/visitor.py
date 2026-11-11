from pycparser.c_ast import NodeVisitor, UnaryOp, BinaryOp, Constant, ID, FuncCall, Decl, DeclList

from witness_generator.waypoint import Waypoint, type, action
from witness_generator.location import Location
from witness_generator.segmentList import SegmentList
from witness_generator.segment import Segment


def expr_to_string(node):
    """Convert a pycparser expression node back to a C expression string."""
    if node is None:
        return "1"
    if isinstance(node, Constant):
        return node.value
    if isinstance(node, ID):
        return node.name
    if isinstance(node, UnaryOp):
        operand = expr_to_string(node.expr)
        return f"{node.op} {operand}"
    if isinstance(node, BinaryOp):
        left = expr_to_string(node.left)
        right = expr_to_string(node.right)
        return f"({left} {node.op} {right})"
    if isinstance(node, FuncCall):
        name = expr_to_string(node.name)
        if node.args:
            args = ", ".join(expr_to_string(arg) for arg in node.args.exprs)
            return f"{name}({args})"
        return f"{name}()"
    return str(node)


class NodeVisitor(NodeVisitor):
    def __init__(self, segmentlists: list[SegmentList]):
        self.assignments = []
        self.segmentlists = segmentlists   # finished lists: only paths that reach the target
        self.active = [SegmentList()]      # active paths, one per control-flow branch

    def has_target(self):
        return len(self.segmentlists) > 0

    def add(self, waypoint):
        segment = Segment(waypoint)
        for sl in self.active:
            sl.add_segment(segment)

    def printSegmentList(self):
        for i, segmentlist in enumerate(self.segmentlists):
            print(f"--- SegmentList {i} ---")
            for segment in segmentlist.segments:
                for waypoint in segment.waypoints:
                    print(f"Waypoint: {waypoint.getWaypoint()}")

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        print(f"Function: {func_name} at line {node.decl.coord.line}")

        block_items = getattr(node.body, 'block_items', None)
        if block_items is None or len(block_items) == 0:
            print("  Skipping empty function body")
            return

        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        self.add(Waypoint(type.function_enter, loc, action.follow))
        self.generic_visit(node)

    def visit_Assignment(self, node):
        print(f"Assignment at line {node.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        constraint = f"{expr_to_string(node.lvalue)} == {expr_to_string(node.rvalue)}"
        print(f"  Constraint: {constraint}")
        self.add(Waypoint(type.assumption, loc, action.follow, constraint=constraint))
        self.generic_visit(node)

    def visit_FuncCall(self, node):
        name = getattr(node.name, "name", None)
        print(f"Function call: {name} at line {node.coord.line}")

        if name == "reach_error":
            loc = Location(node.coord.file, node.coord.line, node.coord.column)
            target = Segment(Waypoint(type.target, loc, action.follow))

            # Finish every active path with the target
            for sl in self.active:
                finished = SegmentList()
                finished.segments = list(sl.segments) + [target]
                self.segmentlists.append(finished)

            self.active = []

        self.generic_visit(node)

    def visit_If(self, node):
        print(f"If statement at line {node.coord.line}")
        cond_expr = expr_to_string(node.cond)
        print(f"  Condition: {cond_expr}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)

        saved = self.active
        active_true = [sl.copy() for sl in saved]
        active_false = [sl.copy() for sl in saved]

        wp_true = Waypoint(type.branching, loc, action.follow, constraint="true")
        wp_false = Waypoint(type.branching, loc, action.follow, constraint="false")
        for sl in active_true:
            sl.add_segment(Segment(wp_true))
        for sl in active_false:
            sl.add_segment(Segment(wp_false))

        self.active = active_true
        if node.iftrue:
            self.visit(node.iftrue)
        true_result = self.active

        self.active = active_false
        if node.iffalse:
            self.visit(node.iffalse)
        false_result = self.active

        self.active = true_result + false_result

    def _visit_loop(self, node, label):
        print(f"{label} at line {node.coord.line}")
        cond_expr = expr_to_string(node.cond)
        print(f"  Condition: {cond_expr}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)

        saved = self.active
        active_body = [sl.copy() for sl in saved]
        active_skip = [sl.copy() for sl in saved]

        wp_true = Waypoint(type.branching, loc, action.follow, constraint="true")
        wp_false = Waypoint(type.branching, loc, action.follow, constraint="false")
        for sl in active_body:
            sl.add_segment(Segment(wp_true))
        for sl in active_skip:
            sl.add_segment(Segment(wp_false))

        self.active = active_body
        if node.stmt:
            self.visit(node.stmt)

        self.active = self.active + active_skip

    def visit_For(self, node):
        self._visit_loop(node, "For loop")

    def visit_While(self, node):
        self._visit_loop(node, "While loop")

    def visit_Decl(self, node):
        print(f"Declaration: {node.name} at line {node.coord.line}")
        if node.init:
            init_expr = expr_to_string(node.init)
            print(f"  Initializer: {init_expr}")
            loc = Location(node.coord.file, node.coord.line, node.coord.column)
            self.add(Waypoint(type.assumption, loc, action.follow,
                              constraint=f"{node.name} == {init_expr}"))
        self.generic_visit(node)

    def visit_DeclList(self, node):
        for decl in node.decls:
            self.visit(decl)

    def visit_Return(self, node):
        print(f"Return statement at line {node.coord.line}")
        # Paths that return never reached the target, so they are thrown away
        self.active = []
        self.generic_visit(node)