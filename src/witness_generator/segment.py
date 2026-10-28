class Segment:
    """Group waypoints into one segment.

    Rules (the schema/linter enforces these, this helper doesn't):
    - the order of waypoints inside one segment doesn't matter
    - a normal segment has exactly one follow waypoint (plus any avoids)
    - the final segment holds the target waypoint(s) and must be last
    - no-data-race: the final segment needs exactly two targets
    """

    def __init__(self, *waypoints):
        self.waypoints = list(waypoints)

    def to_dict(self):
        return {"segment": [w.to_dict() for w in self.waypoints]}