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

# Future Library
from __future__ import annotations

# Standard Library
import dataclasses
import datetime
import logging
import pathlib

from dataclasses import dataclass
from typing import Any, NamedTuple, Optional

# 3rd Party Library
import arrow
import pytest
import yaml

from scrapy.settings import Settings, iter_default_settings

# 1st Party Library
from scrachy.db.models import Response
from scrachy.settings.defaults import filter as filter_settings
from scrachy.settings.defaults import fingerprinter as fingerprinter_settings
from scrachy.settings.defaults import policy as policy_settings
from scrachy.settings.defaults import storage as storage_settings

log = logging.getLogger(__name__)


class TimestampPair(NamedTuple):
    scrape_timestamp: datetime.datetime
    current_timestamp: datetime.datetime


@dataclass(kw_only=True)
class ResponseConfig(yaml.YAMLObject):
    yaml_tag = "!ResponseConfig"
    yaml_loader = yaml.SafeLoader

    scrape_timestamp: datetime.datetime
    fingerprint: str
    url: str
    method: str
    request_body: Optional[bytes] = None
    body: bytes
    meta: Optional[dict[str, Any]] = None
    status: Optional[int] = None
    headers: Optional[str] = None
    extracted_text: Optional[str] = None
    body_length: int
    extracted_text_length: Optional[int] = None

    def to_cached_response(self) -> Response:
        """
        Convert the dataclass to a cached ``Response``.
        """
        kwargs = {f.name: getattr(self, f.name) for f in dataclasses.fields(self)}
        kwargs["fingerprint"] = bytes.fromhex(kwargs["fingerprint"])
        kwargs["scrape_timestamp"] = arrow.get(
            kwargs["scrape_timestamp"].replace(tzinfo=datetime.timezone.utc)
        )

        return Response(**kwargs)


@dataclass(kw_only=True)
class SettingsConfig(yaml.YAMLObject):
    yaml_tag = "!SettingsConfig"
    yaml_loader = yaml.SafeLoader

    settings: dict[str, Any]

    def to_settings(self):
        settings = Settings(dict(iter_default_settings()))
        settings.setmodule(filter_settings)
        settings.setmodule(fingerprinter_settings)
        settings.setmodule(policy_settings)
        settings.setmodule(storage_settings)
        settings.update(self.settings)

        return settings


@pytest.fixture(scope="module")
def example_urls() -> list[str]:
    return [
        "http://www.example.com",
        "https://www.example.com/page1",
        "ftp://www.example.com/page2.html",
        "http://wwwwexample.com",
        "http://w3.example.com",
        "https://anything.edu",
        "http://anything.edu",
        "https://anything.edu",
        "ftp://anything.edu/page1",
        "https://www.anything.edu/page1",
        "foo://test.com",
        "http://test.comhttps://test.com/page1",
    ]


@pytest.fixture(scope="module")
def response_configs() -> list[ResponseConfig]:
    path = pathlib.Path(__file__).with_name("responses.yaml")
    with path.open("r") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def cached_responses(response_configs: list[ResponseConfig]) -> list[Response]:
    return [r.to_cached_response() for r in response_configs]


@pytest.fixture(scope="module")
def settings_choices() -> dict[str, Settings]:
    path = pathlib.Path(__file__).with_name("settings.yaml")
    with path.open("r") as fh:
        settings = yaml.safe_load(fh)

    return (
        {name: config.to_settings() for name, config in settings.items()}
        if settings
        else {}
    )
