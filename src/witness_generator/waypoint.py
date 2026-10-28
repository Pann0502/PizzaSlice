from enum import Enum
from location import *

class type(Enum):
    assumption = "assumption"
    branching = "branching"
    target = "target"
    function_enter = "function_enter"
    function_return = "function_return"

class action(Enum):
    follow = "follow"
    avoid = "avoid"
    cycle = "cycle"

class Waypoint:
    """Build one waypoint.

       type_:      assumption | branching | target | function_enter | function_return
       action:     follow | avoid | cycle
                   (a `target` waypoint must be `follow` and have no constraint)
       constraint: expression string, or for branching "true"/"false"
                   (for switch: an integer constant or "default")
       fmt:        c_expression | ext_c_expression
                   - assumption: c_expression
                   - function_return: ext_c_expression
                   - branching: omit the format entirely
                   - target, function_enter: no constraint at all
       thread_id:  optional, for multi-threaded programs (0 = main thread)
       """

    def __init__(self,type:type, loc:Location, action:action="follow", constraint=None, thread_id=None):
        self.type = type
        self.loc = loc.getLocation()
        self.action = action
        self.constraint = constraint

        self.thread_id = thread_id

        match self.type:
            case type.assumption:
                self.fmt = "c_expression"
            case type.function_enter:
                self.fmt = "ext_c_expression"
            case _:
                self.fmt = None



    def getWaypoint(self):
        wp = {"type": self.type, "location": self.loc, "action": action}
        if self.constraint is not None:
            wp["constraint"] = {"value": self.constraint}
            if self.fmt:  # branching has no format, so only add it when given
                wp["constraint"]["format"] = self.fmt
        if self.thread_id is not None:
            wp["thread_id"] = self.thread_id
        # Each list item in a segment is wrapped in a "waypoint" key.
        return {"waypoint": wp}