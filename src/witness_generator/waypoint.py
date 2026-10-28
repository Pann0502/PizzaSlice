from enum import Enum
from witness_generator.location import Location

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

    def __init__(self, type_, loc, action_=action.follow, constraint=None, thread_id=None):
        self.type_ = type_
        self.loc = loc.getLocation()
        self.action = action_
        self.constraint = constraint
        self.thread_id = thread_id

        match self.type_:
            case type.assumption:            # `type` is now the enum class
                self.fmt = "c_expression"
            case type.branching:
                self.fmt = "c_expression"
            case type.function_return:       # was function_enter
                self.fmt = "ext_c_expression"
            case _:
                self.fmt = None

    def to_dict(self):
        wp = {
            "type": self.type_.value,        # string, not the enum member
            "location": self.loc,
            "action": self.action.value,     # was `action`, i.e. the class itself
        }
        if self.constraint is not None:
            wp["constraint"] = {"value": self.constraint}
            if self.fmt:
                wp["constraint"]["format"] = self.fmt
        if self.thread_id is not None:
            wp["thread_id"] = self.thread_id
        return {"waypoint": wp}

    getWaypoint = to_dict                    # keeps old calls working
