from c_parser.visitor import *

class SegmentList:
    def __init__(self):
        self.segments = []

    def add_segment(self, segment):
        self.segments.append(segment)

    def to_dict(self):
        return [s.to_dict() for s in self.segments]

    @staticmethod
    def _is_final(segment):
        return any(w.type_ == type.target for w in segment.waypoints)