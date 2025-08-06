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
"""
Additional ``Request`` and ``Response`` classes for working with Selenium
and the ``AlchemyCacheStorage`` backend.

Note: Naming this module ``http`` causes a circular import error, so I've appended
an underscore to avoid conflicts.
"""

# Future Library
from __future__ import annotations

# Standard Library
import logging

from typing import Any, Callable, Optional

# 3rd Party Library
from scrapy.http.request import Request
from scrapy.http.response import Response
from selenium.webdriver.remote.webdriver import WebDriver

log = logging.getLogger(__name__)


DEFAULT_WAIT_TIMEOUT = 30
DEFAULT_POLL_FREQUENCY = 1
DEFAULT_MAX_RETRIES = 10


WaitCondition = Callable[[WebDriver], Any]


ScriptExecutor = Callable[
    [WebDriver, Request], Optional[Response | list[Response] | dict[str, Response]]
]


class SeleniumRequest(Request):
    """
    A subclass of :class:`scrapy.http.Request` that provides extra information for downloading pages using
    Selenium.

    Based off the code from `Scrapy-Selenium <https://github.com/clemfromspace/scrapy-selenium>`_
    """

    def __init__(
        self,
        wait_timeout: float = DEFAULT_WAIT_TIMEOUT,
        wait_until: Optional[WaitCondition] = None,
        poll_frequency: float = DEFAULT_POLL_FREQUENCY,
        screenshot: bool = False,
        script_executor: Optional[ScriptExecutor] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        *args,
        **kwargs,
    ):
        """
        A new ``SeleniumRequest``.

        :param wait_timeout: The number of seconds to wait before accessing the data.
        :param wait_until: One of the "selenium.webdriver.support.expected_conditions". The response
                           will be returned until the given condition is fulfilled.
        :param poll_frequency: The sleep interval between calls
        :param screenshot: If ``True``, a screenshot of the page will be taken and the data of the screenshot
                           will be returned in the response "meta" attribute.
        :param script_executor: A function that takes a webdriver and a response as its parameters and optionally
                                returns a list of new response objects as a side effect of its actions (e.g.,
                                executing arbitrary javascript code on the page). Any returned responses will
                                be returned in the ``request.meta`` attribute with the key ``script_result``.
                                Note that the returned responses will not be further processed by any other
                                middleware.
        :param max_retries: The maximum number of times a request will be retried (sent back to
                            scrapy to be rescheduled) if a TimeoutException is raised because the
                            wait_until conditions are not satisfied while downloading the source.

        """
        super().__init__(*args, **kwargs)

        self.wait_timeout = wait_timeout
        self.wait_until = wait_until
        self.poll_frequency = poll_frequency
        self.screenshot = screenshot
        self.script_executor = script_executor
        self.retries = 0
        self.max_retries = max_retries
