# This file is part of sv-witnesses repository: https://github.com/sosy-lab/sv-witnesses
#
# SPDX-FileCopyrightText: 2023 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod


class Linter(ABC):
    @abstractmethod
    def lint(self):
        raise NotImplementedError(
            f"Unimplemented function in class {self.lint.__name__}"
        )
