# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import yaml
from jsonschema.exceptions import ValidationError, SchemaError
from jsonschema import Draft202012Validator, RefResolver

from witnesslint import logger as logging
from witnesslint.constants import (
    WitnessType,
    WITNESS_FAULTY,
    INTERNAL_ERROR,
)
from witnesslint.linter import Linter
from witnesslint.utils import _exit
from witnesslint.yaml_linter.constants import (
    common_schema_path,
    correctness_witness_2_0_schema_path,
    violation_witness_2_0_schema_path,
    correctness_witness_2_1_schema_path,
    violation_witness_2_1_schema_path,
)
from witnesslint.clang_ast import get_stmt_locations_from_source


class YAMLWitnessLinter(Linter):
    def __init__(self, witness, program, options, version):
        self.witness = witness
        if options.strictChecking:
            try:
                self.ast_nodes = get_stmt_locations_from_source(program)
            except Exception as e:
                logging.warning(
                    "Clang threw an exception while parsing AST nodes.\n{}".format(e)
                )
                self.ast_nodes = None
        if program is not None:
            self.program_contents = open(program, "r").read()
        else:
            self.program_contents = None
        self.options = options
        self.version = version

    @staticmethod
    def _correctness_schema_for_version(version: str):
        if version == "2.0":
            return correctness_witness_2_0_schema_path()

        if version == "2.1":
            return correctness_witness_2_1_schema_path()

        raise ValueError(f"No known schema for {version}")

    @staticmethod
    def _violation_schema_for_version(version: str):
        if version == "2.0":
            return violation_witness_2_0_schema_path()

        if version == "2.1":
            return violation_witness_2_1_schema_path()

        raise ValueError(f"No known schema for {version}")

    def _build_json_schema_validator(self, schema_path):
        # Load main schema
        main_schema = yaml.safe_load(open(schema_path, "r"))

        # Load all common schemas and register them by $id
        common_schemas = {}
        for file in common_schema_path().glob("*.yml"):
            schema = yaml.safe_load(open(file, "r"))
            schema_id = schema.get("$id")
            if not schema_id:
                raise ValueError(f"Schema {file} has no $id defined.")
            common_schemas[schema_id] = schema

        resolver = RefResolver.from_schema(main_schema, store=common_schemas)

        return Draft202012Validator(schema=main_schema, resolver=resolver)

    def matches_schema(self):
        try:
            if self.witness.witness_type == WitnessType.CORRECTNESS:
                schema_path = YAMLWitnessLinter._correctness_schema_for_version(
                    self.version
                )
            elif self.witness.witness_type == WitnessType.VIOLATION:
                schema_path = YAMLWitnessLinter._violation_schema_for_version(
                    self.version
                )
            else:
                logging.critical("Witness type could not be determined.")
                _exit(INTERNAL_ERROR)

            validator = self._build_json_schema_validator(schema_path)
            validator.validate(self.witness.witness_entries)
        except ValidationError as e:
            logging.critical("Witness does not match the schema.\n{}".format(e))
            _exit(WITNESS_FAULTY)
        except SchemaError as e:
            logging.critical(
                "Error in the schema for correctness witnesses.\n{}".format(e)
            )
            _exit(INTERNAL_ERROR)
        return

    def invariants_at_feasible_locations(self):
        if self.witness.witness_type != WitnessType.CORRECTNESS:
            return

        if self.program_contents is None:
            return

        program_lines = self.program_contents.split("\n")
        witness_faulty = False

        for e in self.witness.witness_entries:
            if e["entry_type"] != "invariant_set":
                continue

            for c in e["content"]:
                # Skip contracts
                if "invariant" not in c.keys():
                    continue

                entry = c["invariant"]
                line_number = entry["location"]["line"]
                if "column" in entry["location"]:
                    column = entry["location"]["column"]
                else:
                    column = None

                # Invariants and columns start being indexed at 1
                if 0 <= line_number <= len(program_lines):
                    line = program_lines[line_number - 1]
                    line = line.replace("\t", " " * 8)
                    if column is not None and not (0 <= column <= len(line)):
                        witness_faulty = True

                    if witness_faulty:
                        logging.critical(
                            # We make use of implicit concatenation
                            # in order to not exceed the 82 character limit
                            (
                                "Invariant at line {} column {} "
                                "is not at a feasible location."
                            ).format(line_number, column)
                        )
                        _exit(WITNESS_FAULTY)

        return

    def waypoints_at_feasible_locations(self):
        if self.witness.witness_type != WitnessType.VIOLATION:
            return

        program_lines = self.program_contents.split("\n")
        witness_faulty = False

        for entry in self.witness.witness_entries:
            for segment in entry["content"]:
                for waypoint in segment["segment"]:
                    waypoint = waypoint["waypoint"]
                    # lines start being indexed at 1
                    # in the witness, but we need them 0 indexed
                    line_number = waypoint["location"]["line"]

                    if "column" in waypoint["location"]:
                        column = waypoint["location"]["column"]
                    else:
                        column = None

                    if 0 < line_number <= len(program_lines):
                        line = program_lines[line_number - 1]
                        line = line.replace("\t", " " * 8)
                        # Waypoints and columns start being indexed at 1
                        if column is not None and not (0 < column <= len(line)):
                            witness_faulty = True
                    else:
                        witness_faulty = True

                    if witness_faulty:
                        print(self.program_contents)
                        logging.critical(
                            # We make use of implicit concatenation
                            # in order to not exceed the 82 character limit
                            (
                                "Waypoint at line {} column {} "
                                "is not at a feasible location."
                                "The program only has {} lines, "
                                "and line {} only has {} columns."
                            ).format(
                                line_number,
                                column,
                                len(program_lines),
                                line_number,
                                len(program_lines[line_number]),
                            )
                        )
                        _exit(WITNESS_FAULTY)

                    if self.options.strictChecking and self.ast_nodes:
                        # Waypoints point to the beginning of a proper AST construct
                        witness_faulty = True
                        wp_type = waypoint["type"]
                        if wp_type in ["assumption", "branching"]:
                            if self.ast_nodes.by_start_of_statement(
                                line_number, column
                            ):
                                witness_faulty = False
                                break
                        elif (
                            wp_type == "function_return" or wp_type == "function_enter"
                        ):
                            if self.ast_nodes.by_rparen_of_statement(
                                line_number, column
                            ):
                                witness_faulty = False
                                break
                        else:
                            logging.critical(
                                ("Unknown waypoint type {}.").format(wp_type)
                            )
                            _exit(WITNESS_FAULTY)

                        if witness_faulty:
                            logging.critical(
                                (
                                    "Waypoint at line {} column {} "
                                    "does not point to a feasible AST node."
                                ).format(line_number, column)
                            )
                            _exit(WITNESS_FAULTY)

        return

    def matches_file_name_schema(self):
        if not self.witness.witness_file.endswith(
            ".yml"
        ) and not self.witness.witness_file.endswith(".yml.gz"):
            logging.critical("Witness file name does not match the schema.")
            _exit(WITNESS_FAULTY)
        return

    def lint(self):
        self.matches_file_name_schema()
        self.matches_schema()
        if self.program_contents is not None:
            self.invariants_at_feasible_locations()
            self.waypoints_at_feasible_locations()
        self.witness.print_witness_statistics()
