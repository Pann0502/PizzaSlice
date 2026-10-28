# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import gzip
import sys

import yaml
from lxml.etree import XMLSyntaxError, ParserError, parse

from witnesslint import logger as logging
from witnesslint.constants import (
    WITNESS_FAULTY,
    WITNESS_VALID,
    WitnessFormat,
    IgnoreFaultyWitness,
)


def file_is_zipped(witness_file):
    with gzip.open(witness_file) as unzipped_witness:
        try:
            unzipped_witness.read(1)
            zipped = True
        except OSError:
            zipped = False
    return zipped


def determine_witness_type(witness_file: str) -> WitnessFormat:
    if file_is_zipped(witness_file):
        file_handle = gzip.open(witness_file, mode="r")
    else:
        file_handle = open(witness_file, mode="r")
    try:
        parse(file_handle)
        return WitnessFormat.GRAPHML
    except (ParserError, XMLSyntaxError):
        try:
            file_handle.seek(0)
            yaml.safe_load(file_handle)
            return WitnessFormat.YAML
        except yaml.YAMLError:
            logging.critical("Witness is neither a YAML nor a GraphML file.")
            _exit(WITNESS_FAULTY)


class NoDatesSafeLoader(yaml.SafeLoader):
    @classmethod
    def remove_implicit_resolver(cls, tag_to_remove):
        """
        Remove implicit resolvers for a particular tag

        Takes care not to modify resolvers in super classes.

        We want to load datetimes as strings, not dates, because we
        go on to serialise as json which doesn't have the advanced types
        of yaml, and leads to incompatibilities down the track.
        """
        if "yaml_implicit_resolvers" not in cls.__dict__:
            cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()

        for first_letter, mappings in cls.yaml_implicit_resolvers.items():
            cls.yaml_implicit_resolvers[first_letter] = [
                (tag, regexp) for tag, regexp in mappings if tag != tag_to_remove
            ]


NoDatesSafeLoader.remove_implicit_resolver("tag:yaml.org,2002:timestamp")


def _exit(exit_code=None):
    """
    There is an explicit check in BenchExec which
    requires WitnessLint to finish with "witnesslint finished".
    If this is not done the verdict from BenchExec is considered an Exception.
    """
    if exit_code is None:
        if logging.critical.counter or logging.error.counter or logging.warning.counter:
            exit_code = WITNESS_FAULTY
        else:
            exit_code = WITNESS_VALID

    if exit_code == WITNESS_FAULTY and IgnoreFaultyWitness().value:
        print(
            (
                "Ignoring exit code {} which corresponds to a "
                "faulty witness and exiting with exit code 0."
            ).format(exit_code)
        )
        exit_code = 0

    print("\nwitnesslint finished with exit code {}".format(exit_code))
    sys.exit(exit_code)
