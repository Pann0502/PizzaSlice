# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

__version__ = "2.1.1"

import argparse
import os
import sys

from witnesslint import logger as logging
from witnesslint.constants import (
    NO_WITNESS,
    NO_PROGRAM,
    WITNESS_FAULTY,
    INTERNAL_ERROR,
    WitnessFormat,
    IgnoreFaultyWitness,
    WitnessType,
)
from witnesslint.graphml_linter.graphml_linter import GraphMLWitnessLinter
from witnesslint.graphml_linter.graphml_witness import GraphMLWitness
from witnesslint.linter import Linter
from witnesslint.utils import _exit, determine_witness_type
from witnesslint.yaml_linter.yaml_linter import YAMLWitnessLinter
from witnesslint.yaml_linter.yaml_witness import YAMLWitness


def witness_file(path):
    try:
        return open(path, "r")
    except FileNotFoundError as e:
        print(e)
        _exit(NO_WITNESS)


def program_file(path):
    try:
        return open(path, "r")
    except FileNotFoundError as e:
        print(e)
        _exit(NO_PROGRAM)


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version="This is version {} of the witness linter.".format(__version__),
    )
    parser.add_argument(
        "--witness",
        required=True,
        help="GraphML file containing a witness. Mandatory argument.",
        type=witness_file,
        metavar="WITNESS",
    )
    parser.add_argument(
        "--loglevel",
        default="warning",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Desired verbosity of logging output. "
        "Only log messages at or above the specified level are displayed.",
        metavar="LOGLEVEL",
    )
    parser.add_argument(
        "program",
        nargs="?",
        default=None,
        help="The program for which the witness was created.",
        type=program_file,
        metavar="PROGRAM",
    )
    parser.add_argument(
        "--strictChecking",
        help="Also check smaller details, like line numbers from startline tags, "
        "or whether values of enterFunction and returnFromFunction are consistent. "
        "This option is better left disabled for big witnesses.",
        action="store_true",
    )
    parser.add_argument(
        "--ignoreSelfLoops",
        help="Produce no warnings when encountering edges that represent a self-loop.",
        action="store_true",
    )
    parser.add_argument(
        "--svcomp",
        help="Run some additional checks specific to SV-COMP.",
        action="store_true",
    )
    parser.add_argument(
        "--excludeRecentChecks",
        type=int,
        nargs="?",
        metavar="RECENCY_LEVEL",
        const=1,
        default=1024,
        help="Allow failing recently introduced checks. "
        "An optional recency level can be given to specify "
        "how recent checks have to be in order to get excluded.",
    )
    parser.add_argument(
        "--expectCorrectnessWitness",
        help="Set the info field 'Witness Type-Match' to 'True' if"
        "the input witness is a correctness witness.",
        action="store_true",
    )
    parser.add_argument(
        "--expectViolationWitness",
        help="Set the info field 'Witness Type-Match' to 'True' if"
        "the input witness is a violation witness.",
        action="store_true",
    )
    parser.add_argument(
        "--expectedWitnessVersion",
        default=None,
        type=str,
        help="Set the info field 'Witness Version-Match' to 'True' if"
        "the input witness has the expected version.",
    )
    parser.add_argument(
        "--ignoreFaultyWitness",
        action="store_true",
        default=False,
        help="Even when a witness has faults exit successfully.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Debug mode.",
    )
    return parser


def create_linter(parsed_args) -> Linter:
    print("Running witnesslint version {}\n".format(__version__))

    # Initialize utils
    logging.init_logging(parsed_args.loglevel)
    IgnoreFaultyWitness(parsed_args.ignoreFaultyWitness)

    program = parsed_args.program
    if program is not None:
        program = program.name

    witness_path = parsed_args.witness.name
    if not os.path.isfile(witness_path):
        _exit(NO_WITNESS)

    witness_version = None
    witness_type: WitnessFormat = determine_witness_type(witness_path)
    linter = None
    if witness_type == WitnessFormat.YAML:
        expected_witness_type = None
        if parsed_args.expectCorrectnessWitness:
            expected_witness_type = WitnessType.CORRECTNESS
        elif parsed_args.expectViolationWitness:
            expected_witness_type = WitnessType.VIOLATION

        witness = YAMLWitness(witness_path, expected_witness_type)

        if "metadata" not in witness.witness_entries[0]:
            logging.critical(
                "The given YAML witness does not contain a metadata field."
            )
            _exit(WITNESS_FAULTY)
        if "format_version" not in witness.witness_entries[0]["metadata"]:
            logging.critical(
                "The given YAML witness does not contain a format_version field."
            )
            _exit(WITNESS_FAULTY)

        witness_versions = list(
            {entry["metadata"]["format_version"] for entry in witness.witness_entries}
        )
        if len(witness_versions) != 1:
            logging.critical(
                "The given YAML witness contains "
                "entries with different format versions."
            )
            _exit(WITNESS_FAULTY)

        witness_version = witness_versions[0]
        linter = YAMLWitnessLinter(witness, program, parsed_args, witness_version)
    elif witness_type == WitnessFormat.GRAPHML:
        witness = GraphMLWitness(witness_path)
        witness_version = "1.0"
        linter = GraphMLWitnessLinter(witness, program, parsed_args)
    else:
        logging.critical("Unknown witness type.")
        _exit(WITNESS_FAULTY)

    print("Witness Version: {}".format(witness_version))
    expected_witness_version = parsed_args.expectedWitnessVersion
    if expected_witness_version is not None:
        print(
            "Witness Version-Match: {}".format(
                witness_version.startswith(expected_witness_version)
            )
        )

    return linter


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(argv)
    try:
        linter = create_linter(parsed_args)
        linter.lint()
        _exit()
    except Exception as e:
        print(type(e).__name__, ":", e)
        if parsed_args.debug:
            raise e
        _exit(INTERNAL_ERROR)
