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
Content extraction using `BoilerPy3 <https://pypi.org/project/boilerpy3/>`__.
"""

# Standard Library
import re

# 3rd Party Library
from scrapy.settings import Settings
from scrapy.utils.misc import load_object

# 1st Party Library
from scrachy.content import BaseContentExtractor


class BoilerpipeExtractor(BaseContentExtractor):
    def __init__(self, settings: Settings):
        """
        A :class:`ContentExtractor` that uses
        `BoilerPy3 <https://pypi.org/project/boilerpy3/>`__ to process the
        HTML.

        The ``SCRACHY_BOILERPY_EXTRACTOR`` must be set to a valid extractor.

        :param settings: The settings to use for initialization.
        """
        super().__init__(settings)

        self.extractor = load_object(settings.get("SCRACHY_BOILERPY_EXTRACTOR"))()

    def get_content(self, html: str) -> str:
        content = self.extractor.get_content(html)

        return self.cleanup(content)

    @staticmethod
    def cleanup(text: str) -> str:
        """
        This applies a few simple rules to clean up the text extracted from an
        html document.

            1. Split on line breaks.
            2. Strip whitespace from the beginning and ending of each line.
            3. Replace all continuous sequences of whitespace characters with a
               single space.
            4. Remove any empty lines.

        :param text: The content to clean up.
        :return: The text after applying these rules.
        """
        lines = text.splitlines()
        lines = [s.strip() for s in lines]
        lines = [re.sub(r"\s+", " ", s) for s in lines]
        lines = [s for s in lines if s]

        return "\n".join(lines)
