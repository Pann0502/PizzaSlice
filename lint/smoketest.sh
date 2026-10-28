#!/bin/bash

# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

set -e

SCRIPTDIR=$(dirname "$0")

echo "Starting smoke test fof WitnessLint...."

echo "Running WitnessLint on examples from the repository..."

$SCRIPTDIR/lint-examples.py --examples-dir $SCRIPTDIR/examples

echo "Finished running WitnessLint on examples"

echo "WitnessLint smoke test completed successfully."