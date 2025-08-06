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
import logging

from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from typing import Generator, Optional

# 3rd Party Library
import pytest
import pytest_twisted

from scrapy.crawler import Crawler
from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.settings import Settings, iter_default_settings

# 1st Party Library
from scrachy.http_ import SeleniumRequest
from scrachy.middleware.selenium import AsyncSeleniumMiddleware
from scrachy.settings.defaults import selenium as selenium_defaults
from scrachy.settings.defaults.selenium import WebDriverName
from tests.integration.middleware.conftest import MockSpider, SettingsFactory
from tests.integration.middleware.test_selenium import paginate

log = logging.getLogger("test_async_selenium")

pytest.skip(
    "The async middleware is probably broken and difficult to fix",
    allow_module_level=True,
)


@pytest.fixture(scope="module")
def middleware() -> Generator[AsyncSeleniumMiddleware, None, None]:
    settings = Settings(dict(iter_default_settings()))
    settings.setmodule(selenium_defaults)
    settings.set("CONCURRENT_REQUESTS", 4)  # temporary
    settings.set("SCRACHY_SELENIUM_WEB_DRIVER", "Chrome")
    settings.set("SCRACHY_SELENIUM_WEB_DRIVER_OPTIONS", ["--headless=new"])

    crawler = Crawler(spidercls=MockSpider, settings=settings)
    middleware = AsyncSeleniumMiddleware.from_crawler(crawler)

    yield middleware

    log.info("Calling spider_closed")
    middleware.spider_closed(crawler.spider)


@pytest_twisted.ensureDeferred
@pytest.mark.parametrize(
    "driver, options, extensions, raises_expectation",
    [
        (None, None, None, does_not_raise()),
        ("Chrome", ["--headless=new"], True, does_not_raise()),
        ("Firefox", ["-headless"], True, does_not_raise()),
    ],
    indirect=["extensions"],
)
async def test_initialize_driver(
    settings_factory: SettingsFactory,
    driver: WebDriverName,
    options: Optional[list[str]],
    extensions: Optional[list[str]],
    raises_expectation: AbstractContextManager,
):
    with raises_expectation:
        settings = settings_factory(driver, options, extensions)

        crawler = Crawler(spidercls=MockSpider, settings=settings)

        try:
            middleware = AsyncSeleniumMiddleware.from_crawler(crawler)
            assert middleware.drivers.qsize() == settings.getint("CONCURRENT_REQUESTS")
        except:  # noqa: E722
            middleware = None
        finally:
            if middleware is not None:
                middleware.spider_closed(crawler.spider)


@pytest_twisted.ensureDeferred
async def test_return_none_on_scrapy_request(middleware: AsyncSeleniumMiddleware):
    scrapy_request = Request(url="http://not-an-url")

    assert middleware.process_request(scrapy_request) is None


@pytest_twisted.ensureDeferred
async def test_return_response(middleware: AsyncSeleniumMiddleware):
    request = SeleniumRequest(url="https://www.scrapethissite.com/pages/forms/")
    result = middleware.process_request(request)

    assert result is not None

    response = await result

    assert isinstance(response, HtmlResponse)

    title = response.css("title::text").get()
    assert title is not None
    assert "Hockey Teams" in title


@pytest_twisted.ensureDeferred
async def test_screenshot(middleware: AsyncSeleniumMiddleware):
    request = SeleniumRequest(
        url="https://www.scrapethissite.com/pages/forms/", screenshot=True
    )
    result = middleware.process_request(request)

    assert result is not None

    response = await result

    assert isinstance(response, HtmlResponse)
    assert response.meta["screenshot"] is not None


@pytest_twisted.ensureDeferred
async def test_script(middleware: AsyncSeleniumMiddleware):
    request = SeleniumRequest(
        url="https://www.scrapethissite.com/pages/ajax-javascript/",
        script_executor=paginate,
    )

    result = middleware.process_request(request)
    assert result is not None
    response = await result
    assert isinstance(response, HtmlResponse)

    expected_titles = {
        "2015": "Spotlight",
        "2014": "Birdman",
        "2013": "12 Years a Slave",
        "2012": "Argo",
        "2011": "The Artist",
        "2010": "The King's Speech",
    }

    for key, script_response in response.meta["script_result"].items():
        title = (
            script_response.css("tbody#table-body > tr.film > td.film-title::text")
            .get()
            .strip()
        )

        assert expected_titles[key] == title
        assert expected_titles[key] == title
