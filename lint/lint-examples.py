#!/usr/bin/env python3

"""
This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses

SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
"""

import argparse
import os
import subprocess  # noqa: S404
import sys
from pathlib import Path
from typing import Tuple, List


def witnesslinter_path() -> Path:
    return Path(__file__).absolute().parent / "witnesslinter.py"


def examples_dir() -> Path:
    return Path(__file__).absolute().parent / "examples"


def pase_args():
    parser = argparse.ArgumentParser(
        description="Lint all examples with witnesslinter."
    )

    parser.add_argument(
        "--examples-dir",
        type=Path,
        help="Directory containing the examples to lint.",
        default=examples_dir(),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output.",
        default=False,
    )

    return parser.parse_args()


def run_lint(
    witness_pattern: str, label: str, examples_dir: Path, debug: bool = False
) -> List[Tuple[Path, Path]]:
    print(f"Linting {label}{os.linesep}")
    amount_found = 0
    linting_failed = []

    # find all .c and .i files
    for file in examples_dir.glob("*"):
        if file.suffix not in [".c", ".i"]:
            continue

        # match witnesses with same basename prefix
        base = file.with_suffix("")  # strip extension
        for witness in examples_dir.glob(f"{base.name}{witness_pattern}"):
            print(
                " " * 5
                + "Linting witness {:<60} for source {:<30}".format(
                    witness.name, file.name
                )
            )

            amount_found += 1
            command = [str(witnesslinter_path()), str(file), "--witness", str(witness)]
            output = None
            try:
                output = subprocess.run(  # noqa: S603
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                if debug:
                    if output is not None:
                        print(output.stdout.decode())
                        print(output.stderr.decode())
                    print(" ".join(command))
                    raise e

                linting_failed.append((file, witness))

    total_amount_files = 0
    for witness_file in examples_dir.glob(f"{witness_pattern}"):
        for program in [p for p in examples_dir.glob("*") if p.suffix in [".c", ".i"]]:
            if witness_file.name.startswith(program.with_suffix("").name):
                total_amount_files += 1

    if amount_found != total_amount_files:
        print(
            f"Not enough witnesses ending with {witness_pattern} found. "
            f"Expected {total_amount_files}, found {amount_found}."
        )
        sys.exit(1)

    print(os.linesep)

    return linting_failed


def main(examples_dir: Path, debug: bool = False) -> None:
    linting_failed = []

    # GraphML examples
    linting_failed += run_lint("*.graphml", "GraphML examples", examples_dir, debug)

    # Witness examples 2.0
    linting_failed += run_lint(
        "*.witness-2.0.yml", "witness examples version 2.0", examples_dir, debug
    )

    # Witness examples 2.1
    linting_failed += run_lint(
        "*.witness-2.1.yml", "witness examples version 2.1", examples_dir, debug
    )

    for file, witness in linting_failed:
        print(f"Linting failed for {witness} with source {file}")

    if len(linting_failed) == 0:
        print("All examples linted successfully.")

    sys.exit(0 if len(linting_failed) == 0 else 1)


if __name__ == "__main__":
    arguments = pase_args()
    try:
        main(Path(arguments.examples_dir), arguments.debug)
    except Exception as e:
        if arguments.debug:
            raise e
        print(type(e).__name__, ":", e)
        sys.exit(1)
