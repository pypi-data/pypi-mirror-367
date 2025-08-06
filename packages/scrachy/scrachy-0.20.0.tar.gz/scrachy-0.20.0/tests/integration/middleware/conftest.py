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
import pathlib

from typing import Any, Optional, Protocol

# 3rd Party Library
import pytest

from scrapy import Spider
from scrapy.http.response import Response
from scrapy.settings import Settings, iter_default_settings

# 1st Party Library
from scrachy.settings.defaults import filter as filter_defaults
from scrachy.settings.defaults import selenium as selenium_defaults
from scrachy.settings.defaults.selenium import WebDriverName
from scrachy.settings.defaults.storage import PatternLike


class MockSpider(Spider):
    name = "mock_spider"
    allowed_domains = ["scrapethissite.com"]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass


class SettingsFactory(Protocol):
    def __call__(
        self,
        driver_name: Optional[WebDriverName] = None,
        options: Optional[list[str]] = None,
        extensions: Optional[list[str]] = None,
    ) -> Settings: ...


@pytest.fixture
def extensions(request: pytest.FixtureRequest) -> list[str]:
    if not request.param:
        return []

    driver_name = request.node.funcargs["driver"]
    basedir = pathlib.Path(__file__).parent / "selenium" / "extensions"

    if driver_name == "Chrome":
        return [str(f) for f in basedir.glob("*.crx")]
    elif driver_name == "Firefox":
        return [str(f) for f in basedir.glob("*.xpi")]

    raise ValueError(f"Unsupported driver: {driver_name}")


@pytest.fixture
def settings_factory() -> SettingsFactory:
    settings = Settings(dict(iter_default_settings()))
    settings.setmodule(selenium_defaults)
    settings.setmodule(filter_defaults)

    def wrapper(
        driver_name: Optional[WebDriverName] = None,
        options: Optional[list[str]] = None,
        extensions: Optional[list[str]] = None,
        exclusions: Optional[list[PatternLike]] = None,
    ) -> Settings:
        s = settings.copy()
        s["CONCURRENT_REQUESTS"] = 1

        if driver_name:
            s["SCRACHY_SELENIUM_WEB_DRIVER"] = driver_name

        if options:
            s["SCRACHY_SELENIUM_WEB_DRIVER_OPTIONS"] = options

        if extensions:
            s["SCRACHY_SELENIUM_WEB_DRIVER_EXTENSIONS"] = extensions

        s["SCRACHY_CACHED_RESPONSE_FILTER_EXCLUSIONS"] = exclusions or []

        return s

    return wrapper
