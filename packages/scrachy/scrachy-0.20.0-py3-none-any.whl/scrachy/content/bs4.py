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

"""Content extraction using `Beautiful Soup <https://www.crummy.com/software/BeautifulSoup/>`__."""

# Standard Library
import re

# 3rd Party Library
import bs4

from scrapy.settings import Settings

# 1st Party Library
from scrachy.content import BaseContentExtractor

DOM_BLACKLIST: set[str] = {
    "[document]",
    "noscript",
    "header",
    "html",
    "meta",
    "head",
    "input",
}


class BeautifulSoupExtractor(BaseContentExtractor):
    def __init__(self, settings: Settings):
        """
        A :class:`ContentExtractor` that uses
        `Beautiful Soup <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_
        to process the HTML.

        The ``SCRACHY_CONTENT_BS4_PARSER`` setting must be set to a valid
        parser name.

        :param settings: The Scrapy ``Settings``.
        """
        super().__init__(settings)

        self.parser_name = settings.get("SCRACHY_CONTENT_BS4_PARSER")

    def get_content(self, html: str) -> str:
        """
        Extracts the textual content from the html using a simple algorithm
        described
        `here <https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/>`_.
        In short, it ignores blocks that are unlikely to contain meaningful
        content, e.g., script blocks, and then strips the tags from the remaining
        document.

        :param html: The html content as text.
        :return: Return the extracted text.

        :param html:
        :return:
        """
        dom = bs4.BeautifulSoup(html, self.parser_name)

        # Remove script and style nodes from the DOM
        for node in dom(["script", "style"]):
            node.extract()

        # Find the remaining text nodes
        text_nodes = dom.find_all(string=True)

        # Only include nodes that aren't blacklisted
        valid_nodes = [
            t for t in text_nodes if t.parent and t.parent.name not in DOM_BLACKLIST
        ]

        # Get the text from the nodes
        valid_nodes = [t.text.strip() for t in valid_nodes]

        # Normalize spaces
        valid_nodes = [re.sub(r"\s+", " ", t) for t in valid_nodes]

        # Remove blank lines
        valid_nodes = [t for t in valid_nodes if t]

        return "\n".join([t for t in valid_nodes])
