#  Copyright 2023 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

"""
Utilities for processing setting values.
"""

# Standard Library
import re

from typing import Sequence


def compile_patterns(patterns: Sequence[str | re.Pattern]) -> list[re.Pattern]:
    """
    Compile a list of patterns if necessary.

    :param patterns:
    :return:
    """
    return [p if isinstance(p, re.Pattern) else re.compile(p) for p in patterns]
