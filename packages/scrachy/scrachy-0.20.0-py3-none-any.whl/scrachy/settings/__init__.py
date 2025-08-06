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

"""Anything related to the settings for this project."""

# Standard Library
from types import ModuleType
from typing import Any, Iterable, Optional, Tuple

# 3rd Party Library
from scrapy.utils.project import get_project_settings

PROJECT_SETTINGS = get_project_settings()


def iter_default_settings(
    settings_module: Optional[ModuleType] = None,
) -> Iterable[Tuple[str, Any]]:
    """
    Similar to :func:`scrapy.middleware.iter_default_settings`, but accepts
    the module import path to use.

    :param settings_module: The module where the middleware are located.
    :return: An iterator of (name, value) tuples.
    """
    if settings_module is None:
        return []

    for name in dir(settings_module):
        if name.isupper():
            yield name, getattr(settings_module, name)
