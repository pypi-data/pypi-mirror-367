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

"""Database utilities."""

# Standard Library
from typing import Any

# 3rd Party Library
from scrapy.settings import BaseSettings
from sqlalchemy import URL


def construct_url(settings: BaseSettings) -> URL:
    def get(name: str) -> Any:
        return settings.get(f"SCRACHY_DB_{name}")

    driver = get("DRIVER")
    driver = f"+{driver}" if driver else ""
    drivername = f"{get('DIALECT')}{driver}"

    return URL.create(
        drivername=drivername,
        username=get("USERNAME"),
        password=get("PASSWORD"),
        host=get("HOST"),
        port=get("PORT"),
        database=get("DATABASE"),
    )
