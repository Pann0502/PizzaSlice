# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

CREATIONTIME_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$"

SV_COMP_SPECIFICATIONS = [
    "CHECK( init(main()), LTL(G ! call(reach_error())) )",
    "CHECK( init(main()), LTL(G valid-free) )",
    "CHECK( init(main()), LTL(G valid-deref) )",
    "CHECK( init(main()), LTL(G valid-memtrack) )",
    "CHECK( init(main()), LTL(G valid-memcleanup) )",
    "CHECK( init(main()), LTL(G ! overflow) )",
    "CHECK( init(main()), LTL(G ! data-race) )",
    "CHECK( init(main()), LTL(F end) )",
]

WITNESS_VALID = 0
WITNESS_FAULTY = 1
NO_WITNESS = 5
NO_PROGRAM = 6
INTERNAL_ERROR = 7

IGNORE_FAULTY_WITNESS = False


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IgnoreFaultyWitness(metaclass=Singleton):
    def __init__(self, value=False):
        self.__value = value

    @property
    def value(self):
        return self.__value


class WitnessFormat(Enum):
    YAML = 1
    GRAPHML = 2

    def __str__(self):
        return str(self.name)


class WitnessType(Enum):
    CORRECTNESS = 1
    VIOLATION = 2

    def output_str(self) -> str:
        if self == WitnessType.CORRECTNESS:
            return "correctness_witness"
        if self == WitnessType.VIOLATION:
            return "violation_witness"

        raise AssertionError("Unknown witness type")

    def __str__(self):
        return str(self.name)
