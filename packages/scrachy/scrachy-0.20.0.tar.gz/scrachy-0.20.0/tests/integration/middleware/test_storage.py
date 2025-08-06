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
#

# Standard Library
import logging
import time

from pathlib import Path
from typing import Optional, Protocol

# 3rd Party Library
import pytest

from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.settings import Settings
from scrapy.utils.python import to_bytes
from sqlalchemy import delete
from w3lib.http import headers_raw_to_dict

# 1st Party Library
from scrachy.db.models import Response, ScrapeHistory
from scrachy.middleware.httpcache import AlchemyCacheStorage
from scrachy.settings.defaults.storage import RetrievalMethod
from tests.utils import is_postgresql_setup

log = logging.getLogger("test_storage")


DATABASE_DIALECTS = ["sqlite", "postgresql"] if is_postgresql_setup() else ["sqlite"]


class SettingsFactory(Protocol):
    def __call__(
        self, hasher: Optional[str], extractor: Optional[str], method: RetrievalMethod
    ) -> Settings: ...


@pytest.fixture
def headers(request: pytest.FixtureRequest) -> Optional[str]:
    if request.param:  # noqa
        return """
            Host: code.tutsplus.com
            User-Agent: Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
            Accept-Language: en-us,en;q=0.5
            Accept-Encoding: gzip,deflate
            Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
            Keep-Alive: 300
            Connection: keep-alive
            Cookie: PHPSESSID=r2t5uvjq435r4q7ib3vtdjq120
            Pragma: no-cache
            Cache-Control: no-cache
        """

    return None


@pytest.fixture
def request_body(request: pytest.FixtureRequest) -> Optional[str]:
    if request.param:  # noqa
        return """
            POST /test HTTP/1.1
            Host: foo.example
            Content-Type: application/x-www-form-urlencoded
            Content-Length: 27
            field1=value1&field2=value2
        """

    return None


@pytest.fixture
def response_body(request: pytest.FixtureRequest) -> Optional[str]:
    if request.param == "page_1":
        return '<!-- http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm -->\n<HTML>\n<HEAD>\n  <TITLE>Your Title Here</TITLE>\n</HEAD>\n<BODY BGCOLOR="FFFFFF">\n<CENTER><IMG SRC="clouds.jpg" ALIGN="BOTTOM"></CENTER>\n<HR>\n<a href="http://somegreatsite.com">Link Name</a>\nis a link to another nifty site\n<H1>This is a Header</H1>\n<H2>This is a Medium Header</H2>\nSend me mail at <a href="mailto:support@yourcompany.com">support@yourcompany.com</a>.\n<P> This is a new paragraph!</P>\n<P><B>This is a new paragraph!</B>\n  <BR> <B><I>This is a new sentence without a paragraph break, in bold italics.</I></B>\n</P>\n<HR>\n</BODY>\n</HTML>'


@pytest.fixture
def extracted_text(request: pytest.FixtureRequest) -> Optional[str]:
    if request.param == ("page_1", "html.parser"):  # noqa
        return "Your Title Here\nLink Name\nis a link to another nifty site\nThis is a Header\nThis is a Medium Header\nSend me mail at\nsupport@yourcompany.com\n.\nThis is a new paragraph!\nThis is a new paragraph!\nThis is a new sentence without a paragraph break, in bold italics."
    elif request.param == ("page_1", "ArticleExtractor"):  # noqa
        return "Link Name is a link to another nifty site\nThis is a Header\nThis is a Medium Header\nSend me mail at support@yourcompany.com .\nThis is a new paragraph!\nThis is a new paragraph!\nThis is a new sentence without a paragraph break, in bold italics."

    return None


@pytest.fixture
def settings_factory(settings_choices: dict[str, Settings], tmp_path: Path):
    def wrapper(
        hasher: Optional[str],
        extractor: Optional[str],
        retrieval_method: RetrievalMethod = "full",
    ) -> Settings:
        settings = settings_choices["defaults"].copy()

        db_path = tmp_path / "test_storage.db"
        db_path.unlink(missing_ok=True)

        settings.set("SCRACHY_DB_DIALECT", "sqlite")
        settings.set("SCRACHY_DB_DATABASE", str(db_path))

        if hasher is not None:
            finger_class = "scrachy.utils.request.DynamicHashRequestFingerprinter"
            settings.set("REQUEST_FINGERPRINTER_CLASS", finger_class)
            settings.set("SCRACHY_REQUEST_FINGERPRINTER_HASHER_CLASS", hasher)

        if extractor is not None:
            if extractor in ("html.parser", "lxml", "html5lib"):
                settings.set(
                    "SCRACHY_CONTENT_EXTRACTOR",
                    "scrachy.content.bs4.BeautifulSoupExtractor",
                )
                settings.set("SCRACHY_CONTENT_BS4_PARSER", extractor)
            elif extractor in ("DefaultExtractor", "ArticleExtractor"):
                settings.set(
                    "SCRACHY_CONTENT_EXTRACTOR",
                    "scrachy.content.boilerpipe.BoilerpipeExtractor",
                )
                settings.set(
                    "SCRACHY_BOILERPY_EXTRACTOR", f"boilerpy3.extractors.{extractor}"
                )

        settings.set("SCRACHY_CACHE_RESPONSE_RETRIEVAL_METHOD", retrieval_method)
        settings.set("HTTPCACHE_EXPIRATION_SECS", 0.5)

        # See: https://stackoverflow.com/a/78053441
        settings.delete("TWISTED_REACTOR")

        return settings

    return wrapper


class MockSpider(Spider):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


@pytest.mark.parametrize(
    "url, hasher, extractor, method, headers, request_body, response_body, extracted_text, wait",
    [
        (
            "https://www.example.com",
            None,
            None,
            "minimal",
            False,
            False,
            "page_1",
            None,
            0.0,
        ),
        (
            "https://www.example.com",
            None,
            "html.parser",
            "full",
            False,
            False,
            "page_1",
            ("page_1", "html.parser"),
            0.0,
        ),
        (
            "https://www.example.com",
            None,
            "ArticleExtractor",
            "full",
            False,
            False,
            "page_1",
            ("page_1", "ArticleExtractor"),
            0.0,
        ),
        (
            "https://www.example.com",
            "hashlib.md5",
            "ArticleExtractor",
            "full",
            True,
            True,
            "page_1",
            ("page_1", "ArticleExtractor"),
            1.0,
        ),
    ],
    indirect=["headers", "request_body", "response_body", "extracted_text"],
)
def test_storage(
    settings_factory: SettingsFactory,
    url: str,
    hasher: str,
    extractor: str,
    method: RetrievalMethod,
    headers: Optional[str],
    request_body: Optional[str],
    response_body: str,
    extracted_text: Optional[str],
    wait: float,
):
    settings = settings_factory(hasher, extractor, method)
    crawler = Crawler(MockSpider, settings)
    crawler._apply_settings()
    spider = MockSpider.from_crawler(crawler, name="mock_spider")

    storage = AlchemyCacheStorage(settings)
    storage.open_spider(spider)

    # The database is persistent across calls, so we need to clear it each
    # time.
    with storage.engine.session_scope() as session:
        session.execute(delete(Response))
        session.execute(delete(ScrapeHistory))

    request = Request(
        url=url,
        body=request_body,
        headers=headers_raw_to_dict(to_bytes(headers)) if headers else None,
        method="POST" if request_body else "GET",
    )

    response = HtmlResponse(url=url, body=response_body, encoding="utf-8", status=200)

    storage.store_response(spider, request, response)

    time.sleep(wait)

    act_response = storage.retrieve_response(spider, request)

    log.debug(f"wait: {wait} method: {method} act_response: {act_response}")
    if wait > 0.5:
        assert act_response is None
    else:
        assert act_response is not None
        assert act_response.url == request.url == response.url
        assert act_response.text == response.text
        assert act_response.meta.get("extracted_text") == extracted_text

    storage.close_spider(spider)
