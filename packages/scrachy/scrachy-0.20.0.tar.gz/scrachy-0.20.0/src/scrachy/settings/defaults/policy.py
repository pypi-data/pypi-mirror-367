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

"""The default settings for configuring :class:`~scrachy.middleware.httpcache.BlacklistPolicy`."""

# Standard Library
import re

from typing import Callable

SCRACHY_POLICY_BASE_CLASS: str | Callable = "scrapy.extensions.httpcache.DummyPolicy"
"""
The base policy the :class:`~scrachy.middleware.httpcache.BlacklistPolicy`
will wrap around. The policy can be specified as the full import path to
the class or a class object itself. Either way the class constructor must
accept a :class:`~scrapy.settings.Settings` object as its first parameter.
"""

SCRACHY_POLICY_EXCLUDE_URL_PATTERNS: list[str | re.Pattern] = []
"""
A list of regular expression patterns, as compilable strings or
:class:`re.Pattern` objects. Any url matching any of these patterns will be
excluded from being processed by the
:class:`~scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleWare`.
"""
