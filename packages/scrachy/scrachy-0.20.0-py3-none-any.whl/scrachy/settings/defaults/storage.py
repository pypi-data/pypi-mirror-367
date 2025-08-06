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

"""The default settings for configuring :class:`~scrachy.middleware.httpcache.AlchemyCacheStorage`."""

# Standard Library
import re

from typing import Any, Literal, Optional, Type

# 3rd Party Library
from boilerpy3.extractors import Extractor
from cron_converter import Cron

# 1st Party Library
from scrachy.content import ContentExtractor

BeautifulSoupParser = Literal["html.parser", "lxml", "lxml-xml", "html5lib"]
RetrievalMethod = Literal["minimal", "standard", "full"]
PatternLike = str | re.Pattern
Schedulable = str | Cron

# Expiration ##################################################################
SCRACHY_CACHE_ACTIVATION_SECS: float = 0
"""
Consider any page that is in the cache stale (do not retrieve it) if it has
not been in the cache for at least this many seconds. This might be used
for sites that initially post unreliable or partial data then update it
with better data after some period of time but then rarely change it again.
"""

SCRACHY_CACHE_ACTIVATION_SECS_PATTERNS: list[tuple[PatternLike, float]] = []
"""
A list of tuples consisting of a pattern and a delay time in seconds. The
pattern should either be a :class:`re.Pattern` or a string that can be
compiled to one. Any url that matches this pattern will use the value in
the second element of the tuple as its activation delay.

See: :const:`SCRACHY_CACHE_ACTIVATION_SECS`.
"""

SCRACHY_CACHE_EXPIRATION_SECS_PATTERNS: list[tuple[PatternLike, float]] = []
"""
Similar to :const:`SCRACHY_CACHE_ACTIVATION_SECS_PATTERNS`, but overrides
``HTTPCACHE_EXPIRATION_SECS`` for matching urls.
"""

SCRACHY_CACHE_EXPIRATION_SCHEDULE: Optional[Schedulable] = None
"""
Expire all responses that do not match a
:const:`schedule pattern <SCRACHY_CACHE_EXPIRATION_SCHEDULE_PATTERNS>` in the
cache  according to this schedule.
"""

SCRACHY_CACHE_EXPIRATION_SCHEDULE_PATTERNS: Optional[
    list[tuple[PatternLike, Schedulable]]
] = []
"""
Expire any response who's URL matches the given pattern according to the
corresponding schedule.
"""

# Encoding ####################################################################
SCRACHY_CACHE_DEFAULT_ENCODING: str = "utf-8"
"""
Sometimes it is not possible to determine the encoding of a page because it was
not set properly at the source. But this also seems to happen for compressed
pages which have an encoding based on the compression algorithm (e.g., gzip).
However, Scrapy will raise an exception when constructing a
:class:`scrapy.http.TextResponse` if it can't determine the encoding.
To avoid these issues you can specify a default encoding to use when Scrapy
fails to automatically identify a compatible one.
"""

# Retrieval ###################################################################
SCRACHY_CACHE_RESPONSE_RETRIEVAL_METHOD: RetrievalMethod = "standard"
"""
The cache stores quite a bit of information about each response. Not all of this
information is useful for a given scraping task or might only be used for post
scraping analysis. To help avoid loading unnecessary information you can select
one of three retrieval methods that vary in the amount of data they retrieve.
All three methods return some subclass of
:class:`~scrapy.http.TextResponse` object,  but may have ``null`` values for
some of the properties.
"""

# Database Settings ###########################################################
SCRACHY_DB_DIALECT: str = "sqlite"
"""
This specifies the database dialect to use and must be supported by
`SQLAlchemy <https://docs.sqlalchemy.org/en/20/dialects/>`_
"""

SCRACHY_DB_DRIVER: Optional[str] = None
"""
This specifies the name of the driver used to connect to the database. It must
be a name recognized by
`SQLAlchemy <https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases>`_
or ``None`` to use the default driver. Note, the selected driver (including the
default) must be installed separately prior to using it.
"""

SCRACHY_DB_HOST: Optional[str] = None
"""
The hostname (or ip address) where the database server is running. This should
be ``None`` for sqlite databases. For other databases, the hostname is assumed
to be ``localhost`` if this setting is ``None``.
"""

SCRACHY_DB_PORT: Optional[int] = None
"""
The port number the database server is listening on. This should be ``None``
for sqlite databases. For other databases, the default port for the database
server is used when this setting is ``None``.
"""

SCRACHY_DB_DATABASE: Optional[str] = None
"""
For sqlite this is the path to the database file and it will be created if it
does not already exist. For other dialects this is the name of the database
where the cached items will be stored. The database must exist prior to running
any crawlers, but the backend will create all necessary tables. This requires
that the database user have sufficient privileges to do so. If the value is
``None`` for the sqlite dialect, an in memory database will be used (which is
probably not what you want). For all other dialects ``None`` is not permitted.
"""

SCRACHY_DB_SCHEMA: Optional[str] = None
"""
This will set the schema for databases that support them (e.g., PostgreSQL).
"""

SCRACHY_DB_USERNAME: Optional[str] = None
"""
The username used to connect to the database.
"""

SCRACHY_DB_PASSWORD: Optional[str] = None
"""
The password (if any) used to connect to the database. It is not recommended to
store this directly in the settings file. Instead, it should be loaded
dynamically, e.g., using environment variables or ``python-dotenv``.
"""

SCRACHY_DB_CONNECT_ARGS: dict[str, Any] = dict()
"""
Any other arguments that should be passed to :func:`sqla.create_engine`. For
example, you could use the following ``dict`` to connect to postgresql using
ssl:

.. code-block::

    {
        sslrootcert: "path.to.rootcert",
        sslcert: "path.to.clientcert",
        sslkey: "path.to.clientkey",
        sslmode: "verify-full"
    }
"""

# History #####################################################################
SCRACHY_CACHE_SAVE_HISTORY: bool = False
"""
Whether or not to store the full scrape history for each page (identified by
its fingerprint).
"""

# Content Extraction Settings #################################################
SCRACHY_CONTENT_EXTRACTOR: Optional[str | Type[ContentExtractor]] = None
"""
A class implementing the :class:`~scrachy.content.ContentExtractor` protocol
or an import path to a class implementing it. Scrachy provides two
implementations.

    * :class:`scrachy.content.bs4.BeautifulSoupExtractor`
    * :class:`scrachy.content.boilerpipe.BoilerpipeExtractor`
"""

SCRACHY_CONTENT_BS4_PARSER: Optional[BeautifulSoupParser] = "html.parser"
"""
The
`parser <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser>`_
to use for constructing the DOM. It can be one of the following: [html.parser,
lxml, lxml-xml, html5lib]. By default, it will use ``html.parser``, but lxml
or html5lib are probably preferred.
"""

SCRACHY_BOILERPY_EXTRACTOR: Optional[str | Type[Extractor]] = (
    "boilerpy3.extractors.DefaultExtractor"
)
"""
A boilerpy ``Extractor`` class or the import path to one of the classes. See:
`the usage section <https://github.com/jmriebold/BoilerPy3#extractors>`_ of
the boilerpy3 documentation.
"""

# Simhash is no longer supported

# Simhash is no longer supported
