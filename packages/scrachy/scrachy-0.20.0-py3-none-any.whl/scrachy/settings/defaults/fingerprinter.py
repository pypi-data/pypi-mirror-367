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
The default settings for configuring
:class:`~scrachy.utils.request.DynamicHashRequestFingerprinter`.
"""

# Standard Library
from typing import Type

# 1st Party Library
from scrachy.utils.hash import Hasher

SCRACHY_REQUEST_FINGERPRINTER_HASHER_CLASS: str | Type[Hasher] = "hashlib.sha1"
"""
The hash algorithm to use for fingerprinting the :class:`scrapy.http.Request`.
It can either be specified as an import path to a class implementing the
:class:`~scrachy.utils.hash.Hasher` protocol or a ``Hasher`` class directly.
"""
