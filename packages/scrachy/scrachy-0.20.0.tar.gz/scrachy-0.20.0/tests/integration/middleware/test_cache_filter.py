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

# Standard Library
import datetime
import logging
import re

from collections.abc import Iterable
from contextlib import contextmanager
from contextlib import nullcontext as does_not_raise

# 3rd Party Library
import arrow
import pytest

from integration.middleware.conftest import MockSpider
from rwskit.sqlalchemy.engine import SyncAlchemyEngine
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest
from scrapy.http.request import Request
from scrapy.settings import Settings, iter_default_settings
from sqlalchemy import delete

# 1st Party Library
from scrachy.db.models import Response
from scrachy.db.repositories import SyncResponseRepository
from scrachy.middleware.filter import CachedResponseFilter
from scrachy.settings.defaults.storage import PatternLike

log = logging.getLogger("test_cache_filter")


CACHED_URLS = [
    "https://www.google.com/page1",
    "https://www.google.com/page2",
    "https://university.edu",
    "https://university.edu/page1",
    "https://example.org",
]

UN_CACHED_URLS = [
    "https://www.google.com/page5",
    "https://college.edu",
    "https://college.edu/page1",
    "https://example.org/page_1",
]


@pytest.fixture
def settings(request: pytest.FixtureRequest) -> Iterable[Settings]:
    exclusions = request.getfixturevalue("exclusions")

    settings = Settings(dict(iter_default_settings()))
    settings.set("SCRACHY_CACHED_RESPONSE_FILTER_EXCLUSIONS", exclusions)
    settings.set("SCRACHY_DB_DIALECT", "sqlite")
    settings.set("SCRACHY_DB_DATABASE", ":memory:")

    # See: https://stackoverflow.com/a/78053441
    settings.delete("TWISTED_REACTOR")

    yield settings


@pytest.fixture
def crawler(request: pytest.FixtureRequest) -> Crawler:
    settings: Settings = request.getfixturevalue("settings")

    crawler = Crawler(MockSpider, settings=settings)

    crawler._apply_settings()

    return crawler


@contextmanager
def populate_cache(engine: SyncAlchemyEngine, crawler: Crawler):
    urls = CACHED_URLS

    assert crawler.request_fingerprinter is not None

    fingerprints = [
        crawler.request_fingerprinter.fingerprint(Request(url)) for url in urls
    ]
    scrape_timestamps = [
        arrow.get(datetime.datetime(2023, 1, 1, 12, i)) for i in range(len(urls))
    ]

    with engine.session_scope() as session:
        repo = SyncResponseRepository(engine)

        for fingerprint, scrape_timestamp, url in zip(
            fingerprints, scrape_timestamps, urls
        ):
            repo.insert(
                Response(
                    fingerprint=fingerprint,
                    scrape_timestamp=scrape_timestamp,
                    url=url,
                    method=True,
                    body=b"",
                    body_length=0,
                ),
                session=session,
            )

        session.flush()

        yield

        session.execute(delete(Response))


@pytest.mark.parametrize(
    "exclusions, raise_expectations",
    [
        (
            [r"google\.com", r"\.edu$"],
            [
                does_not_raise(),
                does_not_raise(),
                does_not_raise(),
                pytest.raises(IgnoreRequest),
                pytest.raises(IgnoreRequest),
                does_not_raise(),
                does_not_raise(),
                does_not_raise(),
                does_not_raise(),
            ],
        ),
        (
            [re.compile(r"\.edu$")],
            [
                pytest.raises(IgnoreRequest),
                pytest.raises(IgnoreRequest),
                does_not_raise(),
                pytest.raises(IgnoreRequest),
                pytest.raises(IgnoreRequest),
                does_not_raise(),
                does_not_raise(),
                does_not_raise(),
                does_not_raise(),
            ],
        ),
    ],
)
def test_cache_filter(
    crawler: Crawler,
    exclusions: list[PatternLike],
    raise_expectations: list,
):
    cache_filter = CachedResponseFilter(crawler)
    spider = crawler.spider

    # TODO Rethink how the fixtures work.
    # This is probably failing because 'populate_cache' and the 'cache_filter'
    # are using different engines and therefore databases.
    with populate_cache(cache_filter._engine, crawler):
        # It's not (easily) possible to test if an item should be skipped due to
        # being stale. That path of code is fairly straight forward and the
        # expiration manager is tested, so it should be correct.
        for url, raise_expectation in zip(
            CACHED_URLS + UN_CACHED_URLS, raise_expectations
        ):
            with raise_expectation:
                cache_filter.process_request(Request(url=url), spider)

        dont_cache = {"dont_cache": True}
        dont_filter = {"dont_filter": True}
        cachable_url = "https://example.org"

        assert (
            cache_filter.process_request(
                Request(url=cachable_url, meta=dont_cache), spider
            )
            is None
        )
        assert (
            cache_filter.process_request(
                Request(url=cachable_url, meta=dont_filter), spider
            )
            is None
        )
