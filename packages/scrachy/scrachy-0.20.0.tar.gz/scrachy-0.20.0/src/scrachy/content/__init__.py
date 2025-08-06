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

"""Classes and utilities for extracting textual content from the HTML body."""

# Standard Library
from typing import Protocol

# 3rd Party Library
from scrapy.settings import Settings


class ContentExtractor(Protocol):
    def get_content(self, html: str) -> str:
        """Get the desired textual content from the HTML.

        Parameters
        ----------
        html : str
            The textual HTML to process.

        Returns
        -------
        str
            The desired content (e.g., text with tags removed).
        """
        ...


class BaseContentExtractor(ContentExtractor):
    def __init__(self, settings: Settings):
        """A content extractor base class that keeps track of the project middleware.

        Parameters
        ----------
        settings : Settings
            The Scrapy ``Settings``.
        """
        super().__init__()

        self.settings = settings
