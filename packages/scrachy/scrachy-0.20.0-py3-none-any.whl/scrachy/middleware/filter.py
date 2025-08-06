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
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.
"""Middleware for filtering (or ignoring) responses if they are fresh in the cache."""

# Standard Library
import logging

from typing import Optional

# 3rd Party Library
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest
from scrapy.http.request import Request
from scrapy.spiders import Spider

# 1st Party Library
from scrachy.db.engine import initialize_engine
from scrachy.db.repositories import SyncResponseRepository
from scrachy.utils.datetime import now_tzaware
from scrachy.utils.request import ExpirationManager
from scrachy.utils.settings import compile_patterns

log = logging.getLogger(__name__)


class CachedResponseFilter:
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(crawler)

    def __init__(self, crawler: Crawler):
        """
        Sometimes you scrape the same domains multiple times looking for
        new content. However, when crawling them you might encounter pages that
        you have already scraped. If your extraction rules have not changed
        since the last crawl it may not be worth reprocessing those pages.

        This middleware will look to see if a response corresponding to this
        request is already in the cache and is not stale. If the response
        is not in the cache ``process_request`` will return immediately.
        Otherwise, it will use the following rules to determine whether
        the request should be filtered.

        * You can specify a set of patterns to match against the
          request url. Any pattern that matches part of the url will not be
          filtered regardless of whether it is in the cache or
          not. This might be useful after changing parsing rules
          for a set of pages. These are specified using the
          ``SCRACHY_CACHED_RESPONSE_FILTER_EXCLUSIONS`` setting, which takes a
          list of ``re.Patterns`` or strings which can be compiled to regular
          expressions.
        * Setting the request meta key, ``dont_filter`` to ``True``, will
          not be processed by this middleware.
        * Any page that is already excluded from caching via the ``dont_cache``
          request meta key will also never be filtered.

        Any other request that has a fresh response in the cache will be
        filtered.

        :param crawler: The current crawler.
        """
        settings = crawler.spider.settings if crawler.spider else crawler.settings
        self._exclude_patterns = compile_patterns(
            settings.get("SCRACHY_CACHED_RESPONSE_FILTER_EXCLUSIONS")
        )
        self._expiration_manager = ExpirationManager(settings)

        if crawler.request_fingerprinter is None:
            raise ValueError("The request fingerprinter is not set.")
        else:
            self._fingerprinter = crawler.request_fingerprinter

        self._engine = initialize_engine(settings)
        self._response_repository = SyncResponseRepository(self._engine)

    # noinspection PyUnusedLocal
    def process_request(self, request: Request, spider: Optional[Spider]):
        """

        :param request: The Scrapy request.
        :param spider: The Scrapy Spider issuing the request.

        :raises IgnoreRequest: If the item is already cached, and it does
                not meet the requirement to be excluded.
        """
        # If dont_cache or dont_skip is set then don't skip the item.
        if request.meta.get("dont_cache") or request.meta.get("dont_filter"):
            return

        url = request.url
        fingerprint = self._fingerprinter.fingerprint(request)

        # Otherwise check to see if the request is already in the cache and
        # skip further processing if it is.
        scrape_timestamp = self._response_repository.find_timestamp_by_fingerprint(
            fingerprint
        )

        # If the item is not in the cache, then don't filter it
        if scrape_timestamp is None:
            return

        current_timestamp = now_tzaware()

        # If the item in the cache is stale, don't filter it.
        if self._expiration_manager.is_stale(url, scrape_timestamp, current_timestamp):
            return

        # If the url is in the exclusion list then don't filter the request
        # even if it is already in the cache.
        for pattern in self._exclude_patterns:
            if pattern.search(url):
                return

        # Otherwise ignore the cached request
        raise IgnoreRequest()
