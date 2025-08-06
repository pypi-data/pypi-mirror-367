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

"""Benchmarks for testing the efficiency of the ``DynamicHashRequestFingerprinter` and the throughput of the Selenium middleware."""

# Standard Library
import argparse
import logging
import pickle
import pprint
import time
import warnings

from collections import defaultdict
from typing import Any, Optional, Type

# 3rd Party Library
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.settings import Settings, iter_default_settings
from scrapy.spiders import Spider
from scrapy.utils.log import configure_logging
from scrapy.utils.request import RequestFingerprinter
from tabulate import tabulate
from twisted.internet import defer, reactor

# 1st Party Library
from scrachy.http_ import SeleniumRequest
from scrachy.settings.defaults import selenium as selenium_defaults
from scrachy.settings.defaults.selenium import WebDriverName
from scrachy.utils.request import DynamicHashRequestFingerprinter

logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger("benchmark")


class BenchmarkSpider(Spider):
    name = "benchmark"
    start_urls = ["https://books.toscrape.com/"]

    def __init__(self, request_class: Type[Request | SeleniumRequest], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request_class = request_class

    def parse(self, response: Response, **kwargs: Any) -> Any:
        links = response.css("a::attr(href)").getall()

        for link in links:
            url = response.urljoin(link)

            if "books.toscrape.com" in url:
                yield self.request_class(url=url, callback=self.parse)


def get_settings(
    concurrent_requests: int = 4,
    driver_name: WebDriverName = "Chrome",
    driver_options: Optional[list[str]] = None,
    driver_extensions: Optional[list[str]] = None,
    middleware: Optional[str] = None,
    fingerprinter_class: str = "scrapy.utils.request.RequestFingerprinter",
    implementation: str = "2.7",
    hasher: str = "hashlib.sha1",
) -> Settings:
    settings = Settings(dict(iter_default_settings()))
    settings.setmodule(selenium_defaults)

    settings["LOG_LEVEL"] = logging.INFO
    settings["DOWNLOAD_DELAY"] = 0
    settings["REQUEST_FINGERPRINTER_CLASS"] = fingerprinter_class
    settings["REQUEST_FINGERPRINTER_IMPLEMENTATION"] = implementation
    settings["CONCURRENT_REQUESTS"] = concurrent_requests
    settings["SCRACHY_FINGERPRINTER_HASHER_CLASS"] = hasher
    settings["SCRACHY_SELENIUM_WEB_DRIVER"] = driver_name
    settings["SCRACHY_SELENIUM_WEB_DRIVER_OPTIONS"] = driver_options or [
        "--headless=new"
    ]
    settings["SCRACHY_SELENIUM_WEB_DRIVER_EXTENSIONS"] = driver_extensions or []

    if middleware == "Selenium":
        settings["DOWNLOADER_MIDDLEWARES"] = {
            "scrachy.middleware.selenium.SeleniumMiddleware": 800
        }
    elif middleware == "AsyncSelenium":
        settings["DOWNLOADER_MIDDLEWARES"] = {
            "scrachy.middleware.selenium.AsyncSeleniumMiddleware": 800
        }

    return settings


def save_requests(args: argparse.Namespace):
    log.info(f"Reading urls from '{args.url_file}'")
    with open(args.url_file, "r") as fh:
        requests = [Request(url=url) for url in fh]

    log.info(f"Writing requests to '{args.request_file}'")
    with open(args.request_file, "wb") as fh:
        pickle.dump(requests, fh)
    log.info("Done writing requests")


def make_fingerprinter(
    settings: Settings,
) -> RequestFingerprinter | DynamicHashRequestFingerprinter:
    if settings.get("REQUEST_FINGERPRINTER_CLASS").startswith("scrapy"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            crawler = Crawler(BenchmarkSpider, settings=settings)
            return RequestFingerprinter(crawler)

    return DynamicHashRequestFingerprinter(settings)


def run_fingerprinter(
    settings: Settings, requests: list[Request]
) -> tuple[str, str, str, dict[str, list[str]], float]:
    fingerprinter = make_fingerprinter(settings)

    fingerprints = defaultdict(list)

    total_time = 0
    for i, request in enumerate(requests):
        start = time.time()
        fingerprint = fingerprinter.fingerprint(request)
        total_time += time.time() - start

        fingerprints[fingerprint].append(request.url)

    collisions: dict[str, list[str]] = {}
    for fingerprint, urls in fingerprints.items():
        if len(urls) > 1:
            collisions[fingerprint.hex()] = urls

    return (
        fingerprinter.__class__.__name__,
        settings.get("REQUEST_FINGERPRINTER_IMPLEMENTATION"),
        settings.get("SCRACHY_FINGERPRINTER_HASHER_CLASS"),
        collisions,
        total_time,
    )


def fingerprinter(args: argparse.Namespace):
    """
    5 million URL only requests using an AMD 3900X.

    ============= ============== ========= ========== ========
    Fingerprinter Implementation Hasher    Collisions Time (s)
    ============= ============== ========= ========== ========
    Scrapy        2.6            sha1      0          238.0
    Scrapy        2.6            sha1      0          231.8
    Scrachy         -            sha1      0          204.4
    Scrachy         -            xxh32     0            4.3
    Scrachy         -            xxh64     0            4.0
    Scrachy         -            xxh3_64   0           12.6
    Scrachy         -            xxh3_128  0            4.1
    Scrachy         -            spooky32  0           12.7
    Scrachy         -            spooky64  0            4.3
    Scrachy         -            spooky128 0           13.4
    ============= ============== ========= ========== ========

    :param args:
    :return:
    """
    if args.url_file and args.request_file:
        save_requests(args)
        return

    log.info("Start reading requests")
    if args.url_file:
        with open(args.url_file, "r") as fh:
            requests: list[Request] = [Request(url=url) for url in fh]
    elif args.request_file:
        with open(args.request_file, "rb") as fh:
            requests: list[Request] = pickle.load(fh)
    else:
        raise ValueError(
            "The requests must be specified either from a 'url_file' or 'request_file'"
        )
    log.info("Done reading requests")

    results: list[tuple] = []
    collisions: dict[tuple[str, str, str], dict[str, list[str]]] = {}
    scrapy_fingerprinter = "scrapy.utils.request.RequestFingerprinter"
    scrachy_fingerprinter = "scrachy.utils.request.DynamicHashRequestFingerprinter"

    experiments = [
        (scrapy_fingerprinter, "2.6", "hashlib.sha1"),
        (scrapy_fingerprinter, "2.7", "hashlib.sha1"),
        (scrachy_fingerprinter, "2.7s", "hashlib.sha1"),
        (scrachy_fingerprinter, "2.7s", "xxhash.xxh32"),
        (scrachy_fingerprinter, "2.7s", "xxhash.xxh64"),
        (scrachy_fingerprinter, "2.7s", "xxhash.xxh3_64"),
        (scrachy_fingerprinter, "2.7s", "xxhash.xxh3_128"),
        (scrachy_fingerprinter, "2.7s", "spooky_hash.hash32"),
        (scrachy_fingerprinter, "2.7s", "spooky_hash.hash64"),
        (scrachy_fingerprinter, "2.7s", "spooky_hash.hash128_long"),
    ]

    for cls, impl, hasher in experiments:
        log.info(f"Starting experiment: {cls} - {impl} - {hasher}")
        tmp_result = run_fingerprinter(
            get_settings(fingerprinter_class=cls, implementation=impl, hasher=hasher),
            requests,
        )
        collisions[tmp_result[:3]] = tmp_result[3]
        results.append((tmp_result[:3]) + (len(tmp_result[3]),) + (tmp_result[-1],))

    print(
        tabulate(
            results,
            headers=[
                "Fingerprinter Class",
                "Implementation",
                "Hasher",
                "Collisions",
                "Time (s)",
            ],
        )
    )
    print()

    print("Collisions:")
    pprint.pprint(collisions)


@defer.inlineCallbacks
def selenium(args: argparse.Namespace):
    """
    Compare the performance of the standard scrapy downloader against the
    :class:`SeleniumMiddleware` and :class:`AsyncSeleniumMiddleware`.

    The ``https://books.toscrape.com/`` site is crawled 3 times using each
    method using the number of concurrent requests specified on the command
    line.

    Example results are given below. The absolute numbers will depend on
    several factors (e.g., your internet connection and responsiveness of the
    server), but it should give a rough idea of the relative throughput for
    each method.

    The Scrapy downloader is by far the fastest way to download pages.
    The ``SeleniumMiddleware`` is bottle-necked by a single instance
    of a WebDriver and does not benefit at all from increased concurrency.
    The ``AsyncSeleniumMiddleware`` is still considerably slower than
    the default downloader, but can benefit from concurrent downloads.

    =============== =========== ======== ===========
    Method          Concurrency Requests Elapsed (s)
    =============== =========== ======== ===========
    Scrapy          2           1195     54
    Selenium        2           1195     233
    Async Selenium  2           1195     205
    Scrapy          4           1195     38
    Selenium        4           1195     233
    Async Selenium  4           1195     164
    Scrapy          8           1195     28
    Selenium        8           1195     239
    Async Selenium  8           1195     111
    Scrapy          16          1195     27
    Selenium        16          1195     235
    Async Selenium  16          1195     85
    ================================================

    :param args:
    :return:
    """
    log.info("Starting reactor")

    rows = []

    concurrent_requests = args.concurrent_requests

    log.info("Starting vanilla scrapy crawl")
    crawler, runner = setup_runner(
        "Scrapy", get_settings(concurrent_requests=concurrent_requests)
    )
    yield runner.crawl(crawler, request_class=Request)
    update_selenium_results("Scrapy", crawler, rows)

    log.info("Starting Selenium crawl")
    crawler, runner = setup_runner(
        "Selenium",
        get_settings(middleware="Selenium", concurrent_requests=concurrent_requests),
    )
    yield runner.crawl(crawler, request_class=SeleniumRequest)
    update_selenium_results("Selenium", crawler, rows)

    log.info("Starting AsyncSelenium crawl")
    crawler, runner = setup_runner(
        "AsyncSelenium",
        get_settings(
            middleware="AsyncSelenium", concurrent_requests=concurrent_requests
        ),
    )
    yield runner.crawl(crawler, request_class=SeleniumRequest)
    update_selenium_results("Async Selenium", crawler, rows)

    print(tabulate(rows, headers=["Method", "Concurrency", "Requests", "Elapsed (s)"]))

    reactor.stop()  # type: ignore


def setup_runner(name: str, settings: Settings) -> tuple[Crawler, CrawlerRunner]:
    runner = CrawlerRunner(settings=settings)
    crawler = runner.create_crawler(BenchmarkSpider)

    return crawler, runner


def update_selenium_results(name: str, crawler: Crawler, rows: list[list[Any]]):
    stats = crawler.stats
    if stats is None:
        raise ValueError("The scrapy stats are undefined")

    rows.append([
        name,
        crawler.settings.getint("CONCURRENT_REQUESTS"),
        stats.get_value("downloader/request_count"),
        stats.get_value("elapsed_time_seconds"),
    ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(dest="subparser")

    selenium_parser = subparsers.add_parser(
        "selenium",
        help=(
            "Run a simple spider over https://books.toscrape.com/ and compare "
            "the processing speed of the default scrapy downloader versus the "
            "two selenium middleware downloaders."
        ),
    )
    selenium_parser.add_argument(
        "-c",
        "--concurrent-requests",
        type=int,
        default=4,
        help="The number of current requests.",
    )
    selenium_parser.set_defaults(func=selenium)

    finger_parser = subparsers.add_parser(
        "fingerprinter",
        help=(
            "If either -u or -r is set exclusively, then this will benchmark "
            "the scrapy fingerprinter against the "
            "DynamicHashRequestFingerprinter using several different hash "
            "algorithms. xxhash and spooky hash must be installed. If both "
            "-u and -r are specified then the urls from -u will be used to "
            "create Responses that will be pickled to the file specified by "
            "-u. If the number of urls is large it is recommended to pickle "
            "them first."
        ),
    )
    finger_parser.add_argument(
        "-u", "--url-file", help="A file containing a newline delimited list of urls."
    )
    finger_parser.add_argument(
        "-r", "--request-file", help="A file containing a list of pickled Requests."
    )
    finger_parser.set_defaults(func=fingerprinter)

    configure_logging(get_settings())

    opts = parser.parse_args()
    opts.func(opts)

    if opts.subparser == "selenium":
        reactor.run()  # type: ignore
        reactor.run()  # type: ignore
