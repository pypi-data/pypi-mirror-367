##############################################################################
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

##############################################################################
#
#   In addition to the terms listed above you must also follow the terms
#   set by the 3-Clause BSD license. See the BSD_LICENSE.md file or online
#   at <https://opensource.org/licenses/BSD-3-Clause>.
#
##############################################################################

"""Classes for managing Http Cache Storage."""

# Standard Library
import logging
import re

from typing import Any, Optional, cast

# 3rd Party Library
from arrow import Arrow
from rwskit.sqlalchemy.engine import SyncAlchemyEngine
from scrapy.http.headers import Headers
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.http.response.text import TextResponse
from scrapy.responsetypes import responsetypes
from scrapy.settings import Settings
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object
from scrapy.utils.python import to_bytes, to_unicode
from scrapy.utils.request import RequestFingerprinterProtocol
from sqlalchemy import Engine
from w3lib.http import headers_dict_to_raw, headers_raw_to_dict

# 1st Party Library
from scrachy.addons import try_import
from scrachy.content import ContentExtractor
from scrachy.db.engine import initialize_engine
from scrachy.db.models import Response as CachedResponse
from scrachy.db.models import ScrapeHistory
from scrachy.db.repositories import SyncResponseRepository, SyncScrapeHistoryRepository
from scrachy.exceptions import InvalidSettingError
from scrachy.settings import iter_default_settings
from scrachy.settings.defaults import filter as default_filter_settings
from scrachy.settings.defaults import fingerprinter as default_fingerprinter_settings
from scrachy.settings.defaults import storage as default_storage_settings
from scrachy.settings.defaults.storage import RetrievalMethod
from scrachy.settings.prefixed import PrefixedSettings
from scrachy.utils.datetime import now_tzaware
from scrachy.utils.imports import get_import_path
from scrachy.utils.request import DynamicHashRequestFingerprinter, ExpirationManager
from scrachy.utils.settings import compile_patterns

log = logging.getLogger(__name__)


class BlacklistPolicy:
    """
    A wrapper around another cache control policy, but you can also blacklist
    urls (exclude from caching) via pattern matching using the
    :code:`SCRACHY_POLICY_EXCLUDE_URL_PATTERNS` setting. The patterns must
    either be strings that can be compiled with :meth:`re.compile` or
    :class:`re.Pattern` objects.
    """

    def __init__(self, settings: Settings):
        super().__init__()

        self.base_policy = load_object(settings.get("SCRACHY_POLICY_BASE_CLASS"))(
            settings
        )
        self.exclude_patterns = compile_patterns(
            settings.getlist("SCRACHY_POLICY_EXCLUDE_URL_PATTERNS")
        )

    def should_cache_request(self, request: Request) -> bool:
        if self.is_excluded(request.url):
            log.debug(f"Request url is excluded from the cache: {request.url}")
            return False

        return self.base_policy.should_cache_request(request)

    def should_cache_response(self, response: Response, request: Request) -> bool:
        if self.is_excluded(response.url):
            log.debug(f"Response url is excluded from the cache: {response.url}")
            return False

        return self.base_policy.should_cache_response(response, request)

    def is_cached_response_fresh(self, response: Response, request: Request) -> bool:
        if self.is_excluded(response.url):
            log.debug(
                f"Response url is excluded from the cache and should never be fresh: {response.url}"
            )
            return False

        return self.base_policy.is_cached_response_fresh(response, request)

    def is_excluded(self, url: str) -> bool:
        return any([p.match(url) for p in self.exclude_patterns])


class AlchemyCacheStorage:
    """
    This class implements a `scrapy cache storage backend
    <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#writing-your-own-storage-backend>`_
    that uses a relational database to store the cached documents.
    """

    def __init__(self, settings: Settings):
        """
        This class implements a `scrapy cache storage backend
        <https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#writing-your-own-storage-backend>`_
        that uses a relational database to store the cached documents.

        :param settings: The Scrapy project middleware.
        """
        self._settings = PrefixedSettings("SCRACHY", settings)

        log.info(f"Setting up alchemy storage with settings: {settings.copy_to_dict()}")

        self._expiration_manager = ExpirationManager(settings)
        self._content_extractor = self._load_content_extractor(settings)

        # The following are created if necessary and set in the `open_spider` method
        # The callable used to fingerprint requests
        self._fingerprinter: Optional[RequestFingerprinterProtocol] = None

        # The SqlAlchemy engine used to persist the responses. This is
        # either passed in as an existing engine or created from the
        # settings in `open_spider`.
        self._engine: Optional[SyncAlchemyEngine] = None

        # If we create the engine ourselves we should dispose of it when
        # the spider closes. Otherwise, let the creator deal with it.
        # self._dispose_on_close = None

        # A factory for creating sessions.
        # self._session_factory: Optional[sessionmaker] = None

    # region API
    # region Properties
    # Add properties for all valid middleware. At the expense of being verbose
    # this helps avoid typos and validate them (although currently there is
    # very little validation).
    # def get(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
    #     """
    #     Get a ``Scrachy`` setting without having to prefix the name with ``SCRACHY_``.

    #     :return: The value of the setting or ``None`` if it is not set.
    #     """
    #     return self._settings.get(f"SCRACHY_{name}".upper(), default)

    @property
    def fingerprinter(self) -> RequestFingerprinterProtocol:
        """Return the request fingerprinter or raise an exception if it is not available."""
        if self._fingerprinter is None:
            raise ValueError("The fingerprinter has not been initialized.")

        return self._fingerprinter

    @property
    def engine(self) -> SyncAlchemyEngine:
        """Return the alchemy engine or raise an exception if it is not available."""
        if self._engine is None:
            raise ValueError("The engine is not available.")

        return self._engine

    @property
    def is_scrapy_fingerprinter(self) -> bool:
        """
        Returns ``True`` if we're using the scrapy fingerprinter.
        """
        return self.fingerprinter_import_path.startswith("scrapy")

    @property
    def is_scrachy_fingerprinter(self) -> bool:
        """
        Returns ``True`` if we're using the scrachy fingerprinter.
        """
        return self.fingerprinter_import_path.startswith("scrachy")

    @property
    def fingerprinter_import_path(self) -> str:
        """
        Get the import path to our fingerprinter.
        """
        return get_import_path(type(self._fingerprinter))

    @property
    def fingerprinter_implementation(self) -> str:
        """
        Get the implementation string of the fingerprinter in use.
        """
        return self._settings.get("REQUEST_FINGERPRINTER_IMPLEMENTATION")

    @property
    def fingerprinter_hasher_import_path(self) -> Optional[str]:
        if not self.is_scrachy_fingerprinter:
            return None

        hasher = cast(DynamicHashRequestFingerprinter, self._fingerprinter).hasher

        return get_import_path(hasher)

    @property
    def engine_connect_args(self) -> dict[str, Any]:
        # return self.get("DB_CONNECT_ARGS", {})
        return self._settings.getdict("DB_CONNECT_ARGS", {})

    @property
    def dialect(self) -> str:
        """
        The dialect used for connecting to the database server as specified in
        the project middleware. A dialect is always required and should never be
        ``None``. For supported dialects and drivers see the
        `SQLAlchemy website <https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases>`_.

        :return: The dialect name.
        """
        # return self.get("DB_DIALECT")
        return self._settings.get("DB_DIALECT")

    @property
    def driver(self) -> Optional[str]:
        """
        The name of the driver to use with the database or ``None`` to use the
        default driver provided by SqlAlchemy.

        :return: The driver name.
        """
        # return self.get("DB_DRIVER")
        return self._settings.get("DB_DRIVER")

    @property
    def host(self) -> Optional[str]:
        """
        Returns the host name specified in the project middleware.

        :return: The host name.
        """
        # return self.get("DB_HOST")
        return self._settings.get("DB_HOST")

    @property
    def port(self) -> Optional[int]:
        """
        The port used to connect to the database as specified in the project
        middleware. For sqlite this should return ``None``. ``None`` also
        represents the default port for other database dialects. An error
        is raised if the port specified in the middleware can not be cast
        to an integer.

        :return: The port.
        :raises ValueError: If the port is not ``None`` and cannot be cast to
                an int.
        """
        port = self._settings.get("DB_PORT")

        try:
            return port if port is None else int(port)
        except ValueError as e:
            log.error(
                f"If the port is set (not None) it must be an integer but got: {port}"
            )
            raise e

    @property
    def database(self) -> Optional[str]:
        """
        The name of the database to connect to. The only time this should be
        ``None`` is when using an in memory sqlite database (which mostly
        defeats the purpose of a cache storage engine).

        :return: The name of the database.
        """
        return self._settings.get("DB_DATABASE")

    @property
    def schema(self) -> Optional[str]:
        """
        The name of the schema tables will be stored in.

        :return: The name of the database.
        """
        return self._settings.get("DB_SCHEMA")

    @property
    def default_encoding(self) -> str:
        return self._settings.get("CACHE_DEFAULT_ENCODING", "utf-8")

    @property
    def save_history(self) -> bool:
        return self._settings.getbool("CACHE_SAVE_HISTORY")

    @property
    def activation_delay(self) -> float:
        return self._settings.getfloat("CACHE_ACTIVATION_SECS")

    @property
    def bs4_parser(self) -> str:
        """
        The parser to use for parsing HTML with BeautifulSoup.

        :return:
        """
        return self._settings.get("CONTENT_BS4_PARSER")

    @property
    def response_retrieval_method(self) -> RetrievalMethod:
        """
        The name of the response retrieval method.

        This determines how much information to retrieve in the response.

        minimal
            This returns the minimal amount of information and should be the
            fastest because it does not require any joins. However, it will
            return null values for the response status and headers. Use this
            method of you don't need these or the more detailed information.
        standard
            This returns the standard information an :class:`scrapy.http.HtmlResponse`
            does.
        full
            This returns a :class:`scrachy.http.CachedResponse`, which contains
            all the information available for an item in the cache.

        :return: The type of response to retrieve.
        """
        return self._settings.get("CACHE_RESPONSE_RETRIEVAL_METHOD")

    @property
    def expiration_secs(self) -> int:
        """
        The value of the scrapy HTTPCACHE_EXPIRATION_SECS setting.

        :return: The number of seconds before the cached item becomes stale.
                 Stale items will be re-downloaded and processed through the
                 normal pipeline regardless if they are in the cache or not.
        """
        return self._settings.getint("HTTPCACHE_EXPIRATION_SECS", 0)

    # endregion Properties

    # region Scrapy API
    def open_spider(self, spider: Spider, engine: Optional[Engine] = None):
        """
        Connect to the database, validate the middleware and set up the database
        tables if necessary.

        :param spider: The Scrapy spider.
        :param engine: Use this engine instead of creating a new one.
        """
        self._fingerprinter = spider.crawler.request_fingerprinter

        if self._fingerprinter is None:
            raise ValueError("The request fingerprinter has not been initialized")

        self._engine = initialize_engine(spider.settings)

        self.validate_settings()

    def close_spider(self, spider: Optional[Spider] = None):
        """
        Dispose of the SqlAlchemy Engine.

        :param spider: The Scrapy spider
        """

        # self._engine.dispose()

    def retrieve_response(self, spider: Spider, request: Request) -> Optional[Response]:
        """
        Retrieves an item from the cache if it exists, otherwise this returns
        ``None`` to signal downstream processes to continue retrieving the
        page normally. Depending on the value of the
        ``SCRACHY_RESPONSE_RETRIEVAL_METHOD`` setting more or less information
        may be returned in the response.

        :param spider: The Scrapy Spider requesting the data.
        :param request: The request describing what information to retrieve.
        :return: If the page is in the cache then this will return a
                 :class:`~scrapy.http.Response`, otherwise it will
                 return ``None``.
        """
        cached_response: Optional[CachedResponse] = self._read_data(spider, request)

        # We didn't find anything (or the item is expired)
        if cached_response is None:
            return None

        # Create a new Response from the cached items.
        response_retrieval_method = self.response_retrieval_method

        # Always return this info
        response_kwargs = {
            "request": request,
            "url": request.url,
            "body": cached_response.body,
        }

        meta_kwargs = dict()
        if (
            response_retrieval_method == "standard"
            or response_retrieval_method == "full"
        ):
            if cached_response.meta:
                meta_kwargs |= cached_response.meta

            if cached_response.headers:
                raw_headers = headers_raw_to_dict(to_bytes(cached_response.headers))
                response_kwargs["headers"] = Headers(raw_headers)

            response_kwargs["status"] = cached_response.status

        if response_retrieval_method == "full":
            # This will return (almost) all the data Scrachy has about this
            # cached item.
            meta_kwargs |= {
                "scrape_timestamp": cached_response.scrape_timestamp,
                "extracted_text": cached_response.extracted_text,
                "body_length": cached_response.body_length,
                "extracted_text_length": cached_response.extracted_text_length,
                "scrape_history": cached_response.scrape_history,
            }

        return self._make_scrapy_response(response_kwargs, meta_kwargs)

    def store_response(self, spider: Spider, request: Request, response: Response):
        """
        Stores the response in the cache.

        :param spider: The Scrapy Spider issuing the request.
        :param request: The request describing what data is desired.
        :param response: The response to be stored in the cache as created by
               Scrapy's standard downloading process.
        """
        fingerprint: bytes = self.fingerprinter.fingerprint(request)
        timestamp = now_tzaware()
        cached_response = self._make_cached_response(
            fingerprint, timestamp, request, response
        )

        with self.engine.session_scope() as session:
            response_repo = SyncResponseRepository(self.engine)
            response_repo.upsert(cached_response, session=session)

            if self.save_history:
                history_repo = SyncScrapeHistoryRepository(self.engine)
                history_repo.insert(
                    ScrapeHistory(
                        fingerprint=fingerprint,
                        scrape_timestamp=timestamp,
                        body=to_bytes(response.text),
                    ),
                    session=session,
                )

    # endregion Scrapy API

    def validate_settings(self):
        """
        This makes sure that any setting starting with the prefix ``SCRACHY``
        is known to the storage backend.

        It performs some minor validation like checking to make sure the
        port is an integer and a host name is specified unless the dialect is
        sqlite. It is still primarily up to the user to ensure the database
        connection properties are valid for the type of database being used.

        :raises InvalidSettingError: If there are:

                * unknown scrachy middleware.
                * invalid database middleware.
                * an option to a setting that is not valid.
                * the hash algorithm specified in the project middleware used to
                  create the request fingerprint is different from the one
                  already used for this cache region.
        """
        self._validate_unknown_settings()
        self._validate_supported_options()
        self._validate_database_parameters()

    def clear_cache(self):
        with self.engine.session_scope() as session:
            session.query(Response).delete()
            session.query(Request).delete()

    def dump_cache(self) -> list[CachedResponse]:
        """
        Dump the contents of the cache. This is not recommended except for
        debugging.

        :return: A list of SQLAlchemy result objects that contains all
                 the items in the cache.
        """
        return list(SyncResponseRepository(self.engine).find_all_models())

    # endregion Extended API
    # endregion API

    # region Utility Methods
    # region Initialization
    @staticmethod
    def _load_content_extractor(settings: Settings) -> Optional[ContentExtractor]:
        extraction_obj = settings.get("SCRACHY_CONTENT_EXTRACTOR")

        if not extraction_obj:
            return None

        return load_object(extraction_obj)(settings)

    # endregion Initialization

    # region Validation
    def _validate_unknown_settings(self):
        """
        Check that there aren't any unknown scrachy middleware (e.g., typos).

        :raises InvalidSettingError:
        """
        storage_re = re.compile(
            "^SCRACHY_(CACHE|DB|USE_CONTENT|CONTENT|USE_SIMHASH|SIMHASH)"
        )
        storage_keys = set([
            k for k, _ in iter_default_settings(default_storage_settings)
        ])
        finger_keys = set([
            k for k, _ in iter_default_settings(default_fingerprinter_settings)
        ])
        filter_keys = set([
            k for k, _ in iter_default_settings(default_filter_settings)
        ])

        valid_keys = storage_keys | finger_keys | filter_keys

        for key, value in self._settings.items():
            if not isinstance(key, str):
                raise InvalidSettingError(f"Unknown scrachy setting: {key}")

            if storage_re.match(key) and key not in valid_keys:
                raise InvalidSettingError(f"Unknown scrachy setting: {key}")

    def _validate_supported_options(self):
        """
        Make sure the parameters for middleware that take one are valid.

        :raises InvalidSettingError:
        """
        if "lxml" in self.bs4_parser:
            try_import("lxml", "AlchemyCacheStorageAddon")

        if self.bs4_parser == "html5lib":
            try_import("html5lib", "AlchemyCacheStorageAddon")

    def _validate_database_parameters(self):
        """
        Check to make sure the database parameters are valid.

        :raises InvalidSettingError:
        """

        if self.port and not isinstance(self.port, int):
            raise InvalidSettingError(
                f"If the port is specified it must be an integer, but was: {self.port}"
            )

        if self.dialect != "sqlite" and self.database is None:
            raise InvalidSettingError(
                "You must specify a database name for dialects except sqlite."
            )

        if self.dialect == "sqlite" and self.driver == "pysqlcipher":
            raise InvalidSettingError("The pysqlcipher driver is not supported.")

    # region Retrieve Response Utilities
    def _read_data(self, spider: Spider, request: Request) -> Optional[CachedResponse]:
        # In an effort to save storage space in the previous version I stored
        # the diff of the body if there was already an entry. I think this
        # was misguided, because it traded disk space for latency by having
        # to retrieve multiple objects from the database and then apply the
        # diffs to get the actual body. So, in this version I just store
        # everything no matter what. It also adds a lot of additional complexity
        # that is difficult to maintain.
        fingerprint = self._fingerprinter.fingerprint(request)  # type: ignore

        # with self.session_scope() as session:
        with self.engine.session_scope() as session:
            repo = SyncResponseRepository(self.engine)
            scrape_timestamp = repo.find_timestamp_by_fingerprint(fingerprint)

            # A missing timestamp indicates the data is not in the cache.
            if not scrape_timestamp:
                log.debug(
                    f"Did not find the timestamp for '{request.url}' "
                    f"with fingerprint '{fingerprint.hex()}' in the cache."
                )
                return None

            # Don't use the cached data if it is stale.
            # Note the CachePolicy does something different. It only uses
            # info available from the page itself (e.g., the headers) and
            # doesn't know anything about how long (if at all) the data
            # has been in our cache.
            if self._expiration_manager.is_stale(request.url, scrape_timestamp):
                log.debug(
                    f"The response with url '{request.url}' "
                    f"and timestamp '{scrape_timestamp}' is stale"
                )
                return None

            cached_response = repo.find_by_fingerprint(
                fingerprint, self.response_retrieval_method
            )

            session.expunge_all()

        return cached_response

    # endregion Retrieve Response Utilities

    # region Common Utilities
    def _make_cached_response(
        self,
        fingerprint: bytes,
        timestamp: Arrow,
        request: Request,
        response: Response,
    ):
        cached_response = CachedResponse(
            fingerprint=fingerprint,
            scrape_timestamp=timestamp,
            url=request.url,
            body=response.body,
            status=response.status,
            body_length=len(response.body),
        )

        # For some reason this doesn't work as a constructor parameter anymore
        cached_response.request_method = request.method

        if request.body is not None:
            cached_response.request_body = request.body

        if response.request is not None:
            cached_response.meta = request.meta

        if response.headers is not None:
            cached_response.headers = to_unicode(headers_dict_to_raw(response.headers))

        if self._content_extractor is not None and isinstance(response, TextResponse):
            extracted_text = self._content_extractor.get_content(response.text)
            cached_response.extracted_text = extracted_text
            cached_response.extracted_text_length = len(to_bytes(extracted_text))

        return cached_response

    def _make_scrapy_response(
        self, response_kwargs: dict[str, Any], meta_kwargs: dict[str, Any]
    ) -> Response:
        response_cls = responsetypes.from_args(
            headers=response_kwargs.get("headers"),
            url=response_kwargs.get("url"),
            body=response_kwargs.get("body"),
        )

        if issubclass(response_cls, TextResponse):
            response = response_cls(encoding=self.default_encoding, **response_kwargs)
        else:
            response = response_cls(**response_kwargs)

        if response.request is not None:
            log.debug(f"updating meta kwargs: {meta_kwargs}")
            response.meta.update(meta_kwargs)

        return response

    # endregion Common Utilities
    # endregion Utility Methods
    # endregion Utility Methods
