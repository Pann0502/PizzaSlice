# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import gzip
import logging
from hashlib import sha256
from typing import Optional

import yaml

from witnesslint.constants import WitnessType, WITNESS_FAULTY
from witnesslint.utils import file_is_zipped, _exit, NoDatesSafeLoader


class YAMLWitness:
    def __init__(self, witness_file: str, expected_witness_type: WitnessType):
        zipped = file_is_zipped(witness_file)
        # We assume the witness file is large enough to load into memory
        self.witness_file = witness_file
        if zipped:
            witness_contents = gzip.open(witness_file).read()
        else:
            witness_contents = open(witness_file, "rb").read()

        # Since NoDatesSafeLoader is a subclass of SafeLoader, it is safe to use
        self.witness_entries = yaml.load(  # noqa: S506
            witness_contents, Loader=NoDatesSafeLoader
        )
        self._check_not_empty()

        self.witness_type: Optional[WitnessType] = None
        self.witness_type_match: Optional[bool] = None
        self._determine_witness_type()

        if expected_witness_type is not None:
            self.witness_type_match = self.witness_type == expected_witness_type
            if not self.witness_type_match:
                logging.error(
                    "Witness type mismatch, expected witness type %s but found %s",
                    expected_witness_type,
                    self.witness_type,
                )

        # Statistics about the witnesses
        # Length of a binary string is the size of it in bytes
        self.size_in_bytes = len(witness_contents)
        self.lines_of_code = witness_contents.decode("utf-8").count("\n")
        self.amount_invariants = None
        self.amount_segments = None
        self.amount_waypoints = None
        self.witness_hash = sha256(open(witness_file, "rb").read()).hexdigest()
        self.specifications = list(
            {x["metadata"]["task"]["specification"] for x in self.witness_entries}
        )
        if self.witness_type == WitnessType.CORRECTNESS:
            self.amount_invariants = sum(
                len(x["content"]) for x in self.witness_entries
            )
        else:
            self.amount_segments = sum(len(x["content"]) for x in self.witness_entries)
            self.amount_waypoints = sum(
                len(segment["segment"])
                for x in self.witness_entries
                for segment in x["content"]
            )
        return

    def _determine_witness_type(self):
        self.witness_type = None
        for e in self.witness_entries:
            if not isinstance(e, dict) or "content" not in e.keys():
                _exit(WITNESS_FAULTY)

            if (
                "entry_type" in e.keys()
                and e["entry_type"] in ["invariant_set", "ghost_instrumentation"]
                and self.witness_type != WitnessType.VIOLATION
            ):
                self.witness_type = WitnessType.CORRECTNESS
            elif (
                "entry_type" in e.keys()
                and e["entry_type"] == "violation_sequence"
                and self.witness_type != WitnessType.CORRECTNESS
            ):
                self.witness_type = WitnessType.VIOLATION
            else:
                logging.critical(
                    "It could not be determined if the given YAML "
                    "witness is a correctness or violation witness."
                    "Due to an unknown 'entry_type'."
                )
                _exit(WITNESS_FAULTY)
            if e["entry_type"] in ["invariant_set", "violation_sequence"]:
                for c in e["content"]:
                    if not isinstance(c, dict):
                        logging.critical(
                            "Entries in the YAML witness are not dictionaries."
                        )
                        _exit(WITNESS_FAULTY)
                    if (
                        "invariant" in c.keys()
                        or "contract" in c.keys()
                        and self.witness_type != WitnessType.VIOLATION
                    ):
                        self.witness_type = WitnessType.CORRECTNESS
                    elif (
                        "segment" in c.keys()
                        and self.witness_type != WitnessType.CORRECTNESS
                    ):
                        self.witness_type = WitnessType.VIOLATION
                    else:
                        logging.critical(
                            "It could not be determined if the given YAML "
                            "witness is a correctness or violation witness."
                            "Due to {} not having any known keyword.".format(c.keys())
                        )
                        _exit(WITNESS_FAULTY)

        if self.witness_type is None:
            logging.critical(
                "It could not be determined if the given YAML "
                "witness is a correctness or violation witness."
                "Due to the witness being empty."
            )
            _exit(WITNESS_FAULTY)

        return self.witness_type

    def _check_not_empty(self):
        if self.witness_entries is None or len(self.witness_entries) == 0:
            logging.critical("Witness is empty.")
            _exit(WITNESS_FAULTY)
        return

    def print_witness_statistics(self):
        info = "Overview of checked witness:\n"
        info += "Witness File: {}\n".format(self.witness_file)
        info += "Witness Type: {}\n".format(self.witness_type.output_str())
        info += "Witness Type-Match: {}\n".format(self.witness_type_match)
        info += "Number of entries: {}\n".format(len(self.witness_entries))
        info += "Witness Lines of Code: {}\n".format(self.lines_of_code)
        info += "Witness Size in Bytes: {}\n".format(self.size_in_bytes)
        info += "Amount of Invariants: {}\n".format(self.amount_invariants)
        info += "Amount of Segments: {}\n".format(self.amount_segments)
        info += "Amount of Waypoints: {}\n".format(self.amount_waypoints)
        info += "Specification: {}\n".format(" && ".join(self.specifications))
        info += "Witness Hash: {}\n".format(self.witness_hash)
        print(info)
