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

"""Utilities for managing dynamic imports."""

# Standard Library
import inspect

from typing import Any


def get_import_path(obj: Any) -> str:
    """
    Get the import path to the given object. If the ``obj`` is a string then
    we assume it is already an import path and return the value unchanged.

    :param obj:
    :return:
    """

    if isinstance(obj, str):
        return obj

    obj_module = inspect.getmodule(obj)

    if obj_module is None:
        return f"{obj.__name__}"
    else:
        return f"{obj_module.__name__}.{obj.__name__}"
