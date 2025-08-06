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
String utilities.
"""

# Python Modules
import re

# 3rd Party Modules

# Project Modules


def camel_to_snake(s: str) -> str:
    """
    Convert a string ``s`` in CamelCase to snake_case.

    :param s:
    :return:
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
