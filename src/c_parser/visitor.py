from pycparser.c_ast import NodeVisitor

from witness_generator.waypoint import Waypoint, type, action
from witness_generator.location import Location
from witness_generator.astConverterToSegment import SegmentList
from witness_generator.segment import Segment


class NodeVisitor(NodeVisitor):
    def __init__(self, segmentlists: list[SegmentList]):
        self.assignments = []
        self.segmentlists = segmentlists   # finished lists, one per target
        self.running = SegmentList()       # everything seen so far

    def add(self, waypoint):
        self.running.add_segment(segment=Segment(waypoint))

    def printSegmentList(self):
        for i, segmentlist in enumerate(self.segmentlists):
            print(f"--- SegmentList {i} ---")
            for segment in segmentlist.segments:
                for waypoint in segment.waypoints:
                    print(f"Waypoint: {waypoint.getWaypoint()}")

    def visit_FuncDef(self, node):
        print(f"Function: {node.decl.name} at line {node.decl.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        self.add(Waypoint(type.function_enter, loc, action.follow))
        self.generic_visit(node)

    def visit_Assignment(self, node):
        print(f"Assignment at line {node.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        self.add(Waypoint(type.assumption, loc, action.follow))
        self.generic_visit(node)

    def visit_FuncCall(self, node):
        name = getattr(node.name, "name", None)
        print(f"Function call: {name} at line {node.coord.line}")

        if name == "reach_error":
            loc = Location(node.coord.file, node.coord.line, node.coord.column)
            target = Segment(Waypoint(type.target, loc, action.follow))

            finished = SegmentList()
            finished.segments = self.running.segments + [target]  # copy, target last
            self.segmentlists.append(finished)

        self.generic_visit(node)

    def visit_If(self, node):
        print(f"If statement at line {node.coord.line}")
        self.generic_visit(node)

    def visit_For(self, node):
        print(f"For loop at line {node.coord.line}")
        self.generic_visit(node)

    def visit_While(self, node):
        print(f"While loop at line {node.coord.line}")
        self.generic_visit(node)

    def visit_Return(self, node):
        print(f"Return statement at line {node.coord.line}")
        loc = Location(node.coord.file, node.coord.line, node.coord.column)
        self.add(Waypoint(type.function_return, loc, action.follow))
        self.generic_visit(node)