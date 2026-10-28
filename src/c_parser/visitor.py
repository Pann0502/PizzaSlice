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
        self.segmentlists = segmentlists   # finished lists, one per target
        self.active = [SegmentList()]      # active paths, one per control-flow branch

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
        
        # Skip empty function definitions like reach_error{}
        # pycparser Compound node has 'block_items' attribute for the list of statements
        block_items = getattr(node.body, 'block_items', None)
        if block_items is None or len(block_items) == 0:
            print(f"  Skipping empty function body")
            return
        
        # Only add function_enter for non-empty functions
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        self.add(Waypoint(type.function_enter, loc, action.follow))
        self.generic_visit(node)

    def visit_Assignment(self, node):
        print(f"Assignment at line {node.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        # Extract the right-hand side expression as the constraint
        constraint = expr_to_string(node.rvalue)
        print(f"  Constraint: {constraint}")
        self.add(Waypoint(type.assumption, loc, action.follow, constraint=constraint))
        self.generic_visit(node)

    def visit_FuncCall(self, node):
        name = getattr(node.name, "name", None)
        print(f"Function call: {name} at line {node.coord.line}")

        if name == "reach_error":
            loc = Location(node.coord.file, node.coord.line, node.coord.column)
            target = Segment(Waypoint(type.target, loc, action.follow))

            # Finalize every active path with the target and clear active
            for sl in self.active:
                finished = SegmentList()
                finished.segments = list(sl.segments) + [target]
                self.segmentlists.append(finished)

            # Remove finalized paths so they aren't finalized again by return
            self.active = []

        self.generic_visit(node)

    def visit_If(self, node):
        print(f"If statement at line {node.coord.line}")

        # Extract the condition expression string (e.g., "x > 10")
        cond_expr = expr_to_string(node.cond)
        print(f"  Condition: {cond_expr}")

        # Add branching waypoint to record the decision point
        loc = Location(node.coord.file, node.coord.line, node.coord.column)

        # Fork: duplicate every active path for each branch
        saved = self.active
        active_if_true = [sl.copy() for sl in saved]

        # Add branching waypoint with the condition expression to the if-true paths
        branching_true = Waypoint(type.branching, loc, action.follow, constraint=cond_expr)
        for sl in active_if_true:
            sl.add_segment(Segment(branching_true))

        if node.iffalse:
            # Both branches exist: fork into two separate sets of paths
            active_if_false = [sl.copy() for sl in saved]

            # Add branching waypoint with negated condition to the if-false paths
            branching_false = Waypoint(type.branching, loc, action.follow, constraint=f"(!{cond_expr})")
            for sl in active_if_false:
                sl.add_segment(Segment(branching_false))

            # Visit the 'if-true' branch
            self.active = active_if_true
            if node.iftrue:
                self.visit(node.iftrue)
            # Save the result of if-true branch (may be cleared by reach_error)
            if_true_result = self.active

            # Visit the 'if-false' (else) branch
            self.active = active_if_false
            self.visit(node.iffalse)
            # Save the result of if-false branch
            if_false_result = self.active

            # Combine both sets of paths — no merging, each stays separate
            self.active = if_true_result + if_false_result
        else:
            # No else branch: if-true paths may have been finalized,
            # but the false branch just continues with the original saved paths
            self.active = active_if_true
            if node.iftrue:
                self.visit(node.iftrue)

            # After if-true, combine with saved (false branch = no new waypoints)
            # Use self.active directly because reach_error may have cleared it
            self.active = self.active + saved

    def visit_For(self, node):
        print(f"For loop at line {node.coord.line}")

        # Extract the condition expression string
        cond_expr = expr_to_string(node.cond)
        print(f"  Condition: {cond_expr}")

        # Add branching waypoint to record the loop decision point
        loc = Location(node.coord.file, node.coord.line, node.coord.column)

        # Fork: duplicate every active path for each branch
        saved = self.active
        active_body = [sl.copy() for sl in saved]

        # Add branching waypoint with the condition expression to the loop body paths
        branching_true = Waypoint(type.branching, loc, action.follow, constraint=cond_expr)
        for sl in active_body:
            sl.add_segment(Segment(branching_true))

        self.active = active_body
        if node.stmt:
            self.visit(node.stmt)

        # Paths that went through the body stay separate from paths that skipped it
        self.active = active_body + saved

    def visit_While(self, node):
        print(f"While loop at line {node.coord.line}")

        # Extract the condition expression string
        cond_expr = expr_to_string(node.cond)
        print(f"  Condition: {cond_expr}")

        # Add branching waypoint to record the loop decision point
        loc = Location(node.coord.file, node.coord.line, node.coord.column)

        # Fork: duplicate every active path for each branch
        saved = self.active
        active_body = [sl.copy() for sl in saved]

        # Add branching waypoint with the condition expression to the loop body paths
        branching_true = Waypoint(type.branching, loc, action.follow, constraint=cond_expr)
        for sl in active_body:
            sl.add_segment(Segment(branching_true))

        self.active = active_body
        if node.stmt:
            self.visit(node.stmt)

        # Paths that went through the body stay separate from paths that skipped it
        self.active = active_body + saved

    def visit_Decl(self, node):
        print(f"Declaration: {node.name} at line {node.coord.line}")
        # Handle declarations with initializers, especially __VERIFIER_nondet_* calls
        if node.init:
            init_expr = expr_to_string(node.init)
            print(f"  Initializer: {init_expr}")
            loc = Location(node.coord.file, node.coord.line, node.coord.column)
            # Create an assumption waypoint for the declaration
            self.add(Waypoint(type.assumption, loc, action.follow, constraint=init_expr))
        self.generic_visit(node)

    def visit_DeclList(self, node):
        print(f"Declaration list at line {getattr(node, 'coord', type('Coord', (), {'line': 0})())}")
        for decl in node.decls:
            self.visit(decl)

    def visit_Return(self, node):
        print(f"Return statement at line {node.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        return_wp = Waypoint(type.function_return, loc, action.follow)
        return_seg = Segment(return_wp)

        # Finalize every active path with the return
        for sl in self.active:
            finished = SegmentList()
            finished.segments = list(sl.segments) + [return_seg]
            self.segmentlists.append(finished)

        # Clear active paths after finalizing
        self.active = []
        self.generic_visit(node)