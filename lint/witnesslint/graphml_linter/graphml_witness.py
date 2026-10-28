# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

"""
This module contains a class for representing witnesses for a linter.
"""

import gzip
import hashlib
import re

from witnesslint.utils import file_is_zipped

DATA = "data"
DEFAULT = "default"
KEY = "key"
NODE = "node"
EDGE = "edge"
GRAPH = "graph"
GRAPHML = "graphml"

WITNESS_TYPE = "witness-type"
SOURCECODELANG = "sourcecodelang"
PRODUCER = "producer"
SPECIFICATION = "specification"
PROGRAMFILE = "programfile"
PROGRAMHASH = "programhash"
ARCHITECTURE = "architecture"
CREATIONTIME = "creationtime"
ENTRY = "entry"
SINK = "sink"
VIOLATION = "violation"
INVARIANT = "invariant"
INVARIANT_SCOPE = "invariant.scope"
CYCLEHEAD = "cyclehead"
ASSUMPTION = "assumption"
ASSUMPTION_SCOPE = "assumption.scope"
ASSUMPTION_RESULTFUNCTION = "assumption.resultfunction"
CONTROL = "control"
STARTLINE = "startline"
ENDLINE = "endline"
STARTOFFSET = "startoffset"
ENDOFFSET = "endoffset"
ENTERLOOPHEAD = "enterLoopHead"
ENTERFUNCTION = "enterFunction"
RETURNFROMFUNCTION = "returnFromFunction"
THREADID = "threadId"
CREATETHREAD = "createThread"

COMMON_KEYS = {
    WITNESS_TYPE: GRAPH,
    SOURCECODELANG: GRAPH,
    PRODUCER: GRAPH,
    SPECIFICATION: GRAPH,
    PROGRAMFILE: GRAPH,
    PROGRAMHASH: GRAPH,
    ARCHITECTURE: GRAPH,
    CREATIONTIME: GRAPH,
    ENTRY: NODE,
    SINK: NODE,
    VIOLATION: NODE,
    INVARIANT: NODE,
    INVARIANT_SCOPE: NODE,
    CYCLEHEAD: NODE,
    ASSUMPTION: EDGE,
    ASSUMPTION_SCOPE: EDGE,
    ASSUMPTION_RESULTFUNCTION: EDGE,
    CONTROL: EDGE,
    STARTLINE: EDGE,
    ENDLINE: EDGE,
    STARTOFFSET: EDGE,
    ENDOFFSET: EDGE,
    ENTERLOOPHEAD: EDGE,
    ENTERFUNCTION: EDGE,
    RETURNFROMFUNCTION: EDGE,
    THREADID: EDGE,
    CREATETHREAD: EDGE,
}

TERMINATION_PROPERTY_PATTERN = (
    r"CHECK[(]\s*init[(]\s*\w+[(][)]\s*[)]\s*,\s*LTL[(]\s*F\s+end\s*[)]\s*[)]"
)


class GraphMLWitness:
    def __init__(self, witness_file):
        self.witness_file_path = witness_file
        zipped = file_is_zipped(witness_file)
        if zipped:
            self.witness_file = gzip.open(witness_file)
        else:
            self.witness_file = open(witness_file, "rb")
        self.witness_type = None
        self.witness_type_match = "Unknown"
        self.sourcecodelang = None
        self.producer = None
        self.specifications = set()
        self.programfile = None
        self.programhash = None
        self.architecture = None
        self.creationtime = None
        self.entry_node = None
        self.cyclehead = None
        self.node_ids = set()
        self.sink_nodes = set()
        self.defined_keys = {}
        self.used_keys = set()
        self.threads = {}
        self.transition_sources = set()
        self.transitions = {}
        self.lines_of_code = None
        self.size_in_bytes = None
        self.amount_nodes = None
        self.amount_edges = None
        self.amount_invariants = None
        self.witness_hash = None

    def is_termination_witness(self):
        if self.cyclehead is not None:
            return True
        termination_pattern = re.compile(TERMINATION_PROPERTY_PATTERN)
        for spec in self.specifications:
            if re.match(termination_pattern, spec):
                return True
        return False

    def witness_statistics(self):
        witness_contents = self.witness_file.read()
        self.witness_file.seek(0)  # Reset file pointer to beginning of file
        self.size_in_bytes = len(witness_contents)
        witness_contents_utf8 = witness_contents.decode("utf-8")
        self.lines_of_code = witness_contents_utf8.count("\n")
        self.amount_nodes = witness_contents_utf8.count("<node")
        self.amount_edges = witness_contents_utf8.count("<edge")
        self.amount_invariants = witness_contents_utf8.count('<data key="invariant"')
        self.witness_hash = hashlib.sha256(
            open(self.witness_file_path, mode="rb").read()
        ).hexdigest()
        return

    def show_witness_data(self):
        info = "Overview of checked witness:\n"
        info += "Witness File: {}\n".format(self.witness_file.name)
        info += "Witness Type: {}\n".format(self.witness_type)
        info += "Witness Type-Match: {}\n".format(self.witness_type_match)
        info += "Producer: {}\n".format(self.producer)
        info += "Creation Time: {}\n".format(self.creationtime)
        info += "Architecture: {}\n".format(self.architecture)
        info += "Program File: {}\n".format(self.programfile)
        info += "Program Hash: {}\n".format(self.programhash)
        info += "Source-Code Language: {}\n".format(self.sourcecodelang)
        info += "Witness Lines of Code: {}\n".format(self.lines_of_code)
        info += "Witness Size in Bytes: {}\n".format(self.size_in_bytes)
        info += "Amount of Nodes: {}\n".format(self.amount_nodes)
        info += "Amount of Edges: {}\n".format(self.amount_edges)
        info += "Amount of Invariants: {}\n".format(self.amount_invariants)
        info += "Specification: {}\n".format(" && ".join(self.specifications))
        info += "Witness Hash: {}\n".format(self.witness_hash)
        print(info)
