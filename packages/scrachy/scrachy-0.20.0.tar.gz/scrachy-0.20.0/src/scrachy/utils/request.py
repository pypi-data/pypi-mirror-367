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
An enhanced ``RequestFingerprinter``.
"""

# Future Library
from __future__ import annotations

# Standard Library
import datetime
import re

from typing import Iterable, Optional, Tuple, TypeVar, Union
from weakref import WeakKeyDictionary

# 3rd Party Library
import msgspec

from arrow import Arrow
from cron_converter import Cron
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.settings import BaseSettings, Settings
from scrapy.utils.misc import load_object
from scrapy.utils.python import to_bytes
from w3lib.url import canonicalize_url

# 1st Party Library
from scrachy.settings.defaults.storage import PatternLike, Schedulable
from scrachy.utils.datetime import now_tzaware

ExpirationType = TypeVar("ExpirationType")

DEFAULT_HASHER_CLASS = "hashlib.sha1"
DEFAULT_SCRACHY_FINGERPRINTER_VERSION = "scrachy_2.7"

_fingerprint_cache = WeakKeyDictionary()


class DynamicHashRequestFingerprinter:
    """Almost identical to the Scrapy version 2.7 algorithm, but allows you to configure which hash algorithm is used."""

    def __init__(self, settings: Optional[Settings] = None):
        super().__init__()

        if settings is None:
            self.hasher = load_object(DEFAULT_HASHER_CLASS)
        else:
            self.hasher = load_object(
                settings.get(
                    "SCRACHY_REQUEST_FINGERPRINTER_HASHER_CLASS", DEFAULT_HASHER_CLASS
                )
            )

        self.encoder = msgspec.msgpack.Encoder()

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> DynamicHashRequestFingerprinter:
        return cls(crawler.settings)

    def fingerprint(
        self,
        request: Request,
        *,
        include_headers: Optional[Iterable[Union[bytes, str]]] = None,
        keep_fragments: bool = False,
    ) -> bytes:
        """
        Return the request fingerprint.

        The request fingerprint is a hash that uniquely identifies the resource the
        request points to. For example, take the following two urls:

        http://www.example.com/query?id=111&cat=222
        http://www.example.com/query?cat=222&id=111

        Even though those are two different URLs both point to the same resource
        and are equivalent (i.e. they should return the same response).

        Another example are cookies used to store session ids. Suppose the
        following page is only accessible to authenticated users:

        http://www.example.com/members/offers.html

        Lots of sites use a cookie to store the session id, which adds a random
        component to the HTTP Request and thus should be ignored when calculating
        the fingerprint.

        For this reason, request headers are ignored by default when calculating
        the fingerprint. If you want to include specific headers use the
        include_headers argument, which is a list of Request headers to include.

        Also, servers usually ignore fragments in urls when handling requests,
        so they are also ignored by default when calculating the fingerprint.
        If you want to include them, set the keep_fragments argument to True
        (for instance when handling requests with a headless browser).
        """
        processed_include_headers: Optional[Tuple[bytes, ...]] = None
        if include_headers:
            processed_include_headers = tuple(
                to_bytes(h.lower()) for h in sorted(include_headers)
            )

        cache = _fingerprint_cache.setdefault(request, {})
        cache_key = (processed_include_headers, keep_fragments)

        if cache_key not in cache:
            # Unlike json, msgspec should be able to handle bytes
            if processed_include_headers:
                headers = {
                    k: request.headers.values()
                    for k in processed_include_headers
                    if k in request.headers
                }
            else:
                headers: dict[bytes, list[bytes | None]] = {}

            fingerprint_data = {
                "method": to_bytes(request.method),
                "url": to_bytes(
                    canonicalize_url(request.url, keep_fragments=keep_fragments)
                ),
                "body": request.body or b"",
                "headers": headers,
            }
            fingerprint_msgpack = self.encoder.encode(fingerprint_data)
            cache[cache_key] = self.hasher(fingerprint_msgpack).digest()

        return cache[cache_key]


class ExpirationPattern[ExpirationType]:
    def __init__(
        self,
        patterns: list[tuple[PatternLike, ExpirationType]],
        default_value: ExpirationType,
    ):
        self.patterns = self._initialize_patterns(patterns)
        self.default_value = default_value
        self.cache: dict[str, ExpirationType] = dict()

    def __call__(self, url: str) -> ExpirationType:
        if url in self.cache:
            return self.cache[url]

        for pattern, value in self.patterns:
            if pattern.match(url):
                self.cache[url] = value
                return value

        self.cache[url] = self.default_value
        return self.default_value

    @staticmethod
    def _initialize_patterns(
        patterns: list[tuple[PatternLike, ExpirationType]],
    ) -> list[tuple[re.Pattern, ExpirationType]]:
        return [(re.compile(p), v) for p, v in patterns]


class ExpirationManager:
    def __init__(self, settings: Settings | BaseSettings):
        self.activation_matcher = ExpirationPattern(
            settings.getlist("SCRACHY_CACHE_ACTIVATION_SECS_PATTERNS"),
            settings.getfloat("SCRACHY_CACHE_ACTIVATION_SECS", 0.0),
        )

        self.expiration_matcher = ExpirationPattern(
            settings.getlist("SCRACHY_CACHE_EXPIRATION_SECS_PATTERNS"),
            settings.getfloat("HTTPCACHE_EXPIRATION_SECS", 0),
        )

        patterns = [
            (k, self._initialize_schedule(v))
            for k, v in settings.getlist("SCRACHY_CACHE_EXPIRATION_SCHEDULE_PATTERNS")
        ]
        self.schedule_matcher = ExpirationPattern(
            patterns,
            self._initialize_schedule(
                settings.get("SCRACHY_CACHE_EXPIRATION_SCHEDULE")
            ),
        )

    def is_stale(
        self,
        url: str,
        scrape_timestamp: Arrow,
        current_timestamp: Optional[Arrow] = None,
    ) -> bool:
        return not self.is_fresh(url, scrape_timestamp, current_timestamp)

    def is_fresh(
        self,
        url: str,
        scrape_timestamp: Arrow,
        current_timestamp: Optional[Arrow] = None,
    ) -> bool:
        current_timestamp = current_timestamp or now_tzaware()

        secs_in_cache = (current_timestamp - scrape_timestamp).total_seconds()

        if secs_in_cache < self.activation_matcher(url):
            # The item hasn't been in the cache long enough
            return False

        expiration_secs = self.expiration_matcher(url)
        if 0 < expiration_secs < secs_in_cache:
            # The item has been in the cache too long
            return False

        if current_timestamp > self.get_expiration_date(url, scrape_timestamp):
            # The current time is past the expiration date (regardless of
            # how long the item has been in the cache)
            return False

        return True

    def get_expiration_date(self, url: str, timestamp: Arrow) -> datetime.datetime:
        cron: Optional[Cron] = self.schedule_matcher(url)

        if cron is None:
            return datetime.datetime(datetime.MAXYEAR, 12, 31).replace(
                tzinfo=datetime.timezone.utc
            )

        return cron.schedule(timestamp.datetime).next()

    @staticmethod
    def _initialize_schedule(cron: Optional[Schedulable]) -> Optional[Cron]:
        if cron is None:
            return None

        if isinstance(cron, str):
            return Cron(cron)

        if isinstance(cron, Cron):
            return cron

        raise ValueError(f"Unknown scheduler class: {type(cron)}")
