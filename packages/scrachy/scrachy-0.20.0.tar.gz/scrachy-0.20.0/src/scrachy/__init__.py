#  Copyright 2020 Reid Swanson.
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
#   along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

"""Scrachy provides several middleware and utility classes to improve the functionality of scrapy."""

# Standard Library
import pathlib

__version__ = "0.20.0"

PROJECT_ROOT = pathlib.Path(__file__).parent.parent
