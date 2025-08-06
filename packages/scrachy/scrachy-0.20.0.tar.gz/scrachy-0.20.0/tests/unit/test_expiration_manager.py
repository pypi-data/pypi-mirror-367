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

# 3rd Party Library
import arrow
import pytest

from scrapy.settings import Settings

# 1st Party Library
from scrachy.middleware.httpcache import ExpirationManager
from tests.utils import parse_date

log = logging.getLogger("test_expiration_manager")


@pytest.fixture
def settings(
    settings_choices: dict[str, Settings], request: pytest.FixtureRequest
) -> Settings:
    return settings_choices[request.param]  # noqa


@pytest.fixture
def scrape_timestamp(request: pytest.FixtureRequest) -> datetime.datetime:
    return parse_date(request.param).replace(tzinfo=datetime.timezone.utc)  # noqa


@pytest.fixture
def current_timestamp(request: pytest.FixtureRequest) -> datetime.datetime:
    return parse_date(request.param).replace(tzinfo=datetime.timezone.utc)  # noqa


@pytest.mark.parametrize(
    "settings, url, scrape_timestamp, current_timestamp, expected_staleness",
    [
        (
            "defaults",
            "http://www.example.com",
            "2020-01-01T12:00",
            "2025-01-01T12:00",
            False,
        ),
        (
            "defaults",
            "ftp://anything.edu",
            "2020-01-01T12:00",
            "2025-01-01T12:00",
            False,
        ),
        (
            "defaults_with_expiration_secs",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            False,
        ),
        (
            "defaults_with_expiration_secs",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:03",
            True,
        ),
        (
            "defaults_with_activation_secs",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            True,
        ),
        (
            "defaults_with_activation_secs",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:03",
            False,
        ),
        (
            "defaults_with_expiration_schedule",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T13:00",
            False,
        ),
        (
            "defaults_with_expiration_schedule",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-02T13:01",
            True,
        ),
        (
            "defaults_with_activation_pat",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            True,
        ),
        (
            "defaults_with_activation_pat",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            True,
        ),
        (
            "defaults_with_activation_pat",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:03",
            False,
        ),
        (
            "defaults_with_activation_pat",
            "ftp://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            False,
        ),
        (
            "defaults_with_expiration_pat",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            False,
        ),
        (
            "defaults_with_expiration_pat",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            False,
        ),
        (
            "defaults_with_expiration_pat",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:03",
            True,
        ),
        (
            "defaults_with_expiration_pat",
            "ftp://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02",
            False,
        ),
        (
            "defaults_with_expiration_schedule_pat",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T13:01",
            False,
        ),
        (
            "defaults_with_expiration_schedule_pat",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-02T12:01",
            True,
        ),
        (
            "defaults_with_expiration_schedule_pat",
            "ftp://www.example.com",
            "2020-01-01T12:01",
            "2020-01-02T12:01",
            False,
        ),
        (
            "all_expiration_values",
            "http://test.com",
            "2020-01-01T12:01",
            "2020-01-02T12:01:05",
            True,
        ),  # Non matching
        (
            "all_expiration_values",
            "http://test.com",
            "2020-01-01T12:01",
            "2020-01-01T12:01:20",
            False,
        ),  # Non matching
        (
            "all_expiration_values",
            "http://test.com",
            "2020-01-01T12:01",
            "2020-01-01T12:18:00",
            True,
        ),  # Non matching
        # This has been in the cache long enough to be active, but not long enough to exceed expiration_secs,
        # but it should expire due to the default schedule.
        (
            "all_expiration_values",
            "http://test.com",
            "2020-01-29T23:30",
            "2020-01-31T00:00:00",
            True,
        ),  # Non matching
        (
            "all_expiration_values",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:00:40",
            True,
        ),
        (
            "all_expiration_values",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:03:00",
            False,
        ),
        (
            "all_expiration_values",
            "http://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:10:00",
            True,
        ),
        (
            "all_expiration_values",
            "http://www.example.com",
            "2020-01-01T11:55",
            "2020-01-01T12:00:01",
            True,
        ),
        (
            "all_expiration_values",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T12:02:40",
            True,
        ),
        (
            "all_expiration_values",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T13:10:00",
            False,
        ),
        (
            "all_expiration_values",
            "https://www.example.com",
            "2020-01-01T12:01",
            "2020-01-01T14:00:00",
            True,
        ),
        (
            "all_expiration_values",
            "https://www.example.com",
            "2020-01-01T11:50",
            "2020-01-01T12:00:01",
            False,
        ),
        (
            "all_expiration_values",
            "ftp://www.example.com",
            "2020-01-01T11:59",
            "2020-01-01T12:00:01",
            True,
        ),
    ],
    indirect=["settings", "scrape_timestamp", "current_timestamp"],
)
def test_manager(
    settings: Settings,
    url: str,
    scrape_timestamp: datetime.datetime,
    current_timestamp: datetime.datetime,
    expected_staleness: bool,
):
    manager = ExpirationManager(settings)

    log.debug(f"scrape_timetamp: {type(scrape_timestamp)}")

    assert (
        manager.is_stale(url, arrow.get(scrape_timestamp), arrow.get(current_timestamp))
        == expected_staleness
    )
