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

"""The default settings for configuring:class:`~scrachy.middleware.filter.CachedResponseFilter`."""

# 1st Party Library
from scrachy.settings.defaults.storage import PatternLike

SCRACHY_CACHED_RESPONSE_FILTER_EXCLUSIONS: list[PatternLike] = []
"""Do not filter requests whose ``url`` matches any of these patterns."""
