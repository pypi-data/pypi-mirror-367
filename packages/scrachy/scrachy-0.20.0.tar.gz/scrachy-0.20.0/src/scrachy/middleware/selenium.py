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

"""Middleware for processing requests with Selenium."""

# Future Library
from __future__ import annotations

# Standard Library
import atexit

# Python Modules
import logging
import math
import os
import pickle
import queue
import signal
import subprocess
import sys
import time

from struct import pack, unpack
from subprocess import CalledProcessError
from sys import executable
from typing import Any, Optional, cast

try:
    # 3rd Party Library
    import psutil
except ImportError:
    psutil = None


# 3rd Party Library
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest
from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.settings import Settings
from selenium.common import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ProcessProtocol
from twisted.python import failure

# 1st Party Library
from scrachy import PROJECT_ROOT
from scrachy.cli.webdriver_server import DEFAULT_BUFFER_SIZE, Message
from scrachy.http_ import SeleniumRequest
from scrachy.settings.defaults.selenium import WebDriverName
from scrachy.utils.selenium import ShutdownRequest, initialize_driver
from scrachy.utils.selenium import process_request as process_request_helper

log = logging.getLogger(__name__)


class SeleniumMiddleware:
    """
    A downloader middleware that uses a Selenium WebDriver to download
    the content and return an ``HtmlResponse`` if the incoming ``Response``
    is an instance of :class:`~scrachy.http_.SeleniumRequest`. Otherwise,
    it returns ``None`` to let another downloader process it.
    """

    webdriver_import_base = "selenium.webdriver"

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = settings
        self._driver: Optional[WebDriver] = self._initialize_driver()

        self.register_cleanup()

    # region Properties
    def get(self, name: str, default_value: Any = None) -> Any:
        return self.settings.get(f"SCRACHY_SELENIUM_{name}", default_value)

    @property
    def driver_name(self) -> WebDriverName:
        return self.get("WEB_DRIVER")

    @property
    def driver_options(self) -> list[str]:
        return self.get("WEB_DRIVER_OPTIONS")

    @property
    def driver_extensions(self) -> list[str]:
        return self.get("WEB_DRIVER_EXTENSIONS")

    @property
    def driver_preferences(self) -> dict[str, Any]:
        return self.get("WEB_DRIVER_PREFERENCES")

    @property
    def driver_page_load_timeout(self) -> float:
        return self.get("PAGE_LOAD_TIMEOUT")

    @property
    def driver_implicit_wait(self) -> Optional[float]:
        return self.get("IMPLICIT_WAIT")

    @property
    def driver_verify_proxy(self) -> bool:
        return self.get("VERIFY_PROXY", False)

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise ValueError("The instance is no longer valid.")

        return self._driver

    # endregion Properties

    # region API
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> SeleniumMiddleware:
        middleware = cls(crawler.settings)

        # See: https://docs.scrapy.org/en/latest/topics/signals.html
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(
        self, request: Request, spider: Optional[Spider] = None
    ) -> Optional[HtmlResponse | Request]:
        request = cast(SeleniumRequest, request)

        try:
            return process_request_helper(self.driver, request)
        except IgnoreRequest as e:
            raise e
        except WebDriverException as e:
            request.retries += 1
            if request.retries > request.max_retries:
                log.error(
                    f"The request for {request.url} reached the maximum number of retries and "
                    f"could not be processed."
                )
                raise IgnoreRequest()

            log.warning(
                f"A WebDriverException occurred '{e}'. "
                f"Retrying ({request.retries} out of {request.max_retries})."
            )

            request.dont_filter = True

            # Try to reinitialize the driver
            log.info("Restarting the WebDriver.")
            self.spider_closed()
            self._driver = self._initialize_driver()

            # Sleep longer and longer each time we time out
            sleep_time = request.wait_timeout * request.retries

            log.debug(f"Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)

            return request
        except Exception as e:
            # Sometimes the client will hang when we catch this exception.
            # I suspect it is because the shutdown/clean up code is done
            # asynchronously. So, while the driver is still being cleaned up
            # we have already initialized the new driver and changed its
            # reference.
            # I am not sure how to solve this problem correctly. For now it
            # seems like adding a short delay between cleaning up
            # (i.e., 'spider_closed') and reinitializing might be a
            # semi-workable solution. A more robust solution, that would
            # require a major refactor and introduce significant complexity
            # (and additional surface for bugs) could be running the
            # driver in a subprocess.
            log.error(f"'{type(e)}': processing request: {e}")
            self.spider_closed()

            # Sleep for 5 seconds before reinitializing the driver.
            time.sleep(5.0)

            # Reinitialize the driver.
            self._driver = self._initialize_driver()

            raise e

    def register_cleanup(self):
        atexit.register(self.cleanup)

        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        original_exception_hook = sys.excepthook

        def custom_excepthook(exc_type, exc_value, traceback):
            log.error(f"Uncaught exception: {exc_type} {exc_value}")
            self.cleanup()
            original_exception_hook(exc_type, exc_value, traceback)

        sys.excepthook = custom_excepthook

    def cleanup(self):
        """Quit the driver and try to clean up stray processes."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception as e:
                log.warning(
                    "Failed to quit the selenium driver. Will try to kill it.",
                    exc_info=e,
                )
            finally:
                # Standard Library
                import platform

                self._driver = None
                # Sometimes there are still processes left behind even when
                # `driver.quit()` is called. I have a hunch it is related to
                # scrapy's use of twisted, but am not sure. For Chrome and
                # Firefox we can use some clues and hacks to determine the
                # parent WebDriver process and kill it manually, which should
                # kill all the other left over processes.
                if platform.system() == "Windows":
                    return

                # Although I wound up doing something different the idea was
                # inspired by the following post: https://stackoverflow.com/a/38509696
                if psutil is None:
                    self._cleanup_processes_native()
                else:
                    self._cleanup_processes_psutil()

    def spider_closed(self, spider: Optional[Spider] = None):
        """
        Close the webdriver when the spider is closed.

        :param spider:
        :return:
        """
        self.cleanup()

    def _handle_signal(self, signum, frame):
        log.info(f"Received signal {signum}.")
        self.cleanup()

    @classmethod
    def _cleanup_processes_psutil(cls):
        if psutil is None:
            log.warning("psutil is not available.")
            return

        log.debug("Cleaning up processes using psutil commands.")
        for process in psutil.process_iter():
            try:
                is_zombie = process.status() == psutil.STATUS_ZOMBIE
                cmdline = " ".join(process.cmdline()).lower()

                cls._kill_driver_process(process.pid, cmdline, is_zombie)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                log.info(
                    "Unable to kill process because it no longer exists or we don't have access."
                )

    @classmethod
    def _cleanup_processes_native(cls):
        log.debug("Cleaning up processes using native Linux commands.")
        ps_cmd = ["ps", "aux"]

        try:
            result = subprocess.run(ps_cmd, capture_output=True, text=True, check=True)
            processes = result.stdout.splitlines()
        except CalledProcessError as e:
            log.error(f"Failed to retrieve process list: {e}")
        else:
            for process in processes[1:]:  # The first line is the header
                columns = process.split()
                pid = int(columns[1])
                is_zombie = "Z" in columns[7]
                cmdline = " ".join(columns[10:]).lower()

                cls._kill_driver_process(pid, cmdline, is_zombie)

    @classmethod
    def _kill_driver_process(cls, pid: int, cmdline: str, is_zombie: bool):
        try:
            if "chrom" in cmdline and "--class=selenium" in cmdline:
                # You can add a custom WM_CLASS to chrome using the --class flag.
                # If the user uses the class name 'selenium' we can detect the root
                # process and kill it here.
                log.warning(f"Force terminating Chrome webdriver with pid: {pid}")
                os.kill(pid, signal.SIGKILL)
            elif "firefox" in cmdline and "--marionette" in cmdline:
                # The root Firefox WebDriver appears to have the --marionette flag
                # associated with it. If it is still running kill it.
                log.warning(f"Force terminating Firefox webdriver with pid: {pid}")
                os.kill(pid, signal.SIGKILL)

            # Check for zombie process based on `ps` output state column
            if is_zombie:
                log.warning(f"Found and terminating a zombie process with pid: {pid}")
                os.kill(pid, signal.SIGKILL)
        except OSError:
            log.info(f"Unable to kill process with pid: {pid}")

    # endregion API
    def _initialize_driver(self) -> WebDriver:
        return initialize_driver(
            self.driver_name,
            self.driver_options,
            self.driver_extensions,
            self.driver_preferences,
            self.driver_page_load_timeout,
            self.driver_implicit_wait,
            self.driver_verify_proxy,
        )


class AsyncSeleniumMiddleware:
    """
    A downloader middleware that creates a pool of Selenium WebDrivers
    and sends any incoming
    :class:`SeleniumRequests <~scrachy.http_.SeleniumRequest>` to an
    available driver to be processed.
    """

    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = settings

        concurrent_requests: int = settings.getint("CONCURRENT_REQUESTS")
        log_file: str = settings.get("SCRACHY_SELENIUM_LOG_FILE")

        # Create a pool of drivers to increase the throughput. Since there
        # isn't actually any parallelism involved I don't think I have to
        # be all that careful with synchronization (e.g., locks).
        self.drivers = queue.Queue(maxsize=concurrent_requests)
        for driver in [WebDriverProtocol(i) for i in range(concurrent_requests)]:
            self.drivers.put(driver)

            args = [executable, "-m", "scrachy.cli.webdriver_server"]
            args += ["-d", self.driver_name]
            args += [f'-o "{o}"' for o in self.driver_options]
            args += [f'-e "{e}"' for e in self.driver_extensions]

            if log_file:
                args += [f'-f "{log_file}"']

            # noinspection PyUnresolvedReferences
            reactor.spawnProcess(  # type: ignore
                driver,
                executable,
                args,
                path=PROJECT_ROOT,
                env=os.environ,
            )

    # region Properties
    def get(self, name: str) -> Any:
        return self.settings.get(f"SCRACHY_SELENIUM_{name}")

    @property
    def driver_name(self) -> WebDriverName:
        return self.get("WEB_DRIVER")

    @property
    def driver_options(self) -> list[str]:
        return self.get("WEB_DRIVER_OPTIONS")

    @property
    def driver_extensions(self) -> list[str]:
        return self.get("WEB_DRIVER_EXTENSIONS")

    # endregion Properties

    # region API
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> AsyncSeleniumMiddleware:
        middleware = cls(crawler.settings)

        # See: https://docs.scrapy.org/en/latest/topics/signals.html
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(
        self, request: Request, spider: Optional[Spider] = None
    ) -> Optional[Deferred[HtmlResponse | Request]]:
        if not isinstance(request, SeleniumRequest):
            # Let some other downloader handle this request
            return None

        driver = self.drivers.get()

        try:
            d = driver.process_request(request)
        except Exception as e:
            log.error(f"Error processing request: {e}")
            driver.shutdown()
            raise e

        def enqueue_driver(r: HtmlResponse | Request) -> HtmlResponse | Request:
            self.drivers.put(driver)
            return r

        d.addCallback(enqueue_driver)

        return d

    def spider_closed(self, spider: Optional[Spider] = None):
        # Closing stdin should shut down the server
        while not self.drivers.empty():
            driver = self.drivers.get(block=False)
            driver.shutdown()

        # Uncommenting the following lines will allow any final messages
        # sent to stderr from the server just before exiting.
        # import time
        # from twisted.internet.threads import deferToThread
        # yield deferToThread(lambda: time.sleep(0.5))

    # endregion API


class WebDriverProtocol(ProcessProtocol):
    # The number of bytes in the response message.
    response_header_size = 4

    def __init__(self, id_: int, process_buffer_size: int = DEFAULT_BUFFER_SIZE):
        # An identifier for this process
        self.id = id_

        # The size of the read buffer on the spawned process. We need to send
        # at lest this many bytes in order for the server's read buffer
        # to flush. Otherwise, the server will hang until it gets more data.
        self.process_buffer_size = process_buffer_size

        # Buffer to accumulate incoming messages
        self.buffer = b""

        # The deferred object we will eventually return
        self.deferred_response: Optional[Deferred[HtmlResponse]] = None

        # This gets set once the shutdown message is sent and will be used
        # to prevent any further communication with the protocol.
        self.is_shutdown = False

    # region Interface Methods
    def connectionMade(self):
        if self.transport is None:
            log.debug("Unable to make connection.")
        else:
            log.debug(f"Connection made to: {self.id} with pid: {self.transport.pid}")

    def outReceived(self, data: bytes):
        self.buffer += data
        self._extract_message()

    def errReceived(self, data: bytes):
        log.error(f"Driver process error: {data.decode()}")

    def inConnectionLost(self):
        log.debug("Lost stdin")

    def outConnectionLost(self):
        log.debug("Lost stdout")

    def errConnectionLost(self):
        log.debug("Lost stderr")

    def processExited(self, reason: failure.Failure):
        # reason.value.exitCode is taken directly from the twisted documentation
        # https://docs.twisted.org/en/stable/core/howto/process.html#verbose-example
        log.info(f"Child process exited with exit code: {reason.value.exitCode}")  # type: ignore

    def processEnded(self, reason: failure.Failure):
        # reason.value.exitCode is taken directly from the twisted documentation
        # https://docs.twisted.org/en/stable/core/howto/process.html#verbose-example
        log.info(f"Child process ended: {reason.value.exitCode}")  # type: ignore

    # endregion Interface Methods

    def process_request(self, request: SeleniumRequest) -> Deferred[HtmlResponse]:
        if self.is_shutdown:
            raise ValueError(
                "You cannot process requests after the server has been shut down."
            )

        # The original request has references to all sorts of unnecessary
        # and impossible to pickle objects. Just send over what we need.
        self._send_message(
            SeleniumRequest(
                url=request.url,
                wait_timeout=request.wait_timeout,
                wait_until=request.wait_until,
                screenshot=request.screenshot,
                script_executor=request.script_executor,
            )
        )

        # We'll store the response here when it is ready.
        self.deferred_response = Deferred()

        return self.deferred_response

    def shutdown(self):
        self._send_message(ShutdownRequest())

        if self.transport is not None:
            self.transport.closeStdin()

        self.is_shutdown = True

    def _send_message(self, message: Message):
        message_data = pickle.dumps(message)

        # The number of bytes to encode the pickled data
        data_length = len(message_data)

        # The total number of bytes sent in the message (including the header
        # and padding)
        msg_length = self._get_message_length(data_length + 8)

        # The number of bytes to pad the message by. The sum of the header,
        # message, and padding should be an exact multiple of the process
        # buffer size. This is the difference between the total message length
        # and the data length and excluding the header.
        pad_length = (msg_length - data_length) - 8

        data_field = pack("!I", data_length)
        msg_field = pack("!I", msg_length)

        if self.transport is not None:
            self.transport.writeSequence([
                data_field,
                msg_field,
                message_data,
                b" " * pad_length,
            ])

    def _get_message_length(self, request_length: int) -> int:
        return self.process_buffer_size * math.ceil(
            request_length / self.process_buffer_size
        )

    def _extract_message(self):
        while len(self.buffer) >= self.response_header_size:
            msg_length = unpack("!I", self.buffer[:4])[0]
            if len(self.buffer) >= msg_length + 4:
                # Get the data from the buffer
                data = self.buffer[4 : 4 + msg_length]

                # Remove the processed data from the buffer
                self.buffer = self.buffer[4 + msg_length :]

                # Try to decode the message
                try:
                    obj = pickle.loads(data)
                except pickle.PickleError as e:
                    if self.deferred_response is not None:
                        self.deferred_response.errback(e)
                    else:
                        log.error(
                            "There was a pickle error but the deferred response was "
                            "not ready."
                        )
                    continue

                if self.deferred_response is None:
                    log.error("Deferred response is not ready!")
                    continue

                if not isinstance(obj, HtmlResponse):
                    log.error(
                        f"The message was not an HtmlResponse. Got '{type(obj)}' "
                        "instead."
                    )
                    self.deferred_response.errback(obj)
                    continue

                self.deferred_response.callback(obj)
            else:
                break  # The message is not complete
