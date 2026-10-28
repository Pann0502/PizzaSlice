# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path


def _base_dir() -> Path:
    return Path(__file__).absolute().parent.joinpath("../../", "schemas")


def correctness_witness_2_0_schema_path() -> Path:
    return _base_dir().joinpath("archive", "v2.0", "correctness-witness-2.0-schema.yml")


def correctness_witness_2_1_schema_path() -> Path:
    return _base_dir().joinpath("correctness-witness-schema.yml")


def violation_witness_2_0_schema_path() -> Path:
    return _base_dir().joinpath("archive", "v2.0", "violation-witness-2.0-schema.yml")


def violation_witness_2_1_schema_path() -> Path:
    return _base_dir().joinpath("violation-witness-schema.yml")


def common_schema_path() -> Path:
    return _base_dir().joinpath("common")
