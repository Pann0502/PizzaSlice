class Location:


    def __init__(self, file, line, column=None, function=None):
        self.file = file
        self.line = line
        self.column = column
        self.function = function

    def getLocation(self):
        """Build a `location` element.

            file_name and line are required. column is optional: if omitted,
            it defaults to the first syntactically matching column for the
            waypoint type. function is only for human readability.
            Columns are 1-based and a tab counts as 1 character.
            """
        loc = {"file_name": self.file, "line": self.line}
        if self.column is not None:
            loc["column"] = self.column
        if self.function is not None:
            loc["function"] = self.function
        return loc