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
# Python Modules
import datetime
import logging
import os
import pathlib

from typing import Any, Optional, TypeVar

# 3rd Party Library
# 3rd Party Modules
from dateutil import parser as date_parser
from dotenv import load_dotenv
from scrapy.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# 1st Party Library
# Project Modules
from scrachy.utils.db import construct_url

load_dotenv()

log = logging.getLogger(__name__)


T = TypeVar("T")

TEST_DATABASE_NAME = "scrachy_test"


def load_postgresql_settings() -> Settings:
    sslrootcert: Optional[str] = os.getenv("TEST_SCRACHY_DB_SSL_ROOT_CERT")
    sslcert: Optional[str] = os.getenv("TEST_SCRACHY_DB_SSL_CERT")
    sslkey: Optional[str] = os.getenv("TEST_SCRACHY_DB_SSL_KEY")
    sslmode: Optional[str] = os.getenv("TEST_SCRACHY_DB_SSL_MODE")

    connect_args = {
        "sslrootcert": sslrootcert,
        "sslcert": sslcert,
        "sslkey": sslkey,
        "sslmode": sslmode,
    }
    connect_args = {k: v for k, v in connect_args.items() if v}

    settings = Settings({
        "SCRACHY_DB_DIALECT": "postgresql",
        "SCRACHY_DB_DRIVER": "psycopg",
        "SCRACHY_DB_HOST": os.getenv("TEST_SCRACHY_DB_HOST", "localhost"),
        "SCRACHY_DB_PORT": int(os.getenv("TEST_SCRACHY_DB_PORT", "5432")),
        "SCRACHY_DB_DATABASE": os.getenv("TEST_SCRACHY_DB_DATABASE", "scrachy_test"),
        "SCRACHY_DB_USERNAME": os.getenv("TEST_SCRACHY_DB_USERNAME", "scrachy"),
        "SCRACHY_DB_PASSWORD": os.getenv("TEST_SCRACHY_DB_PASSWORD"),
        "SCRACHY_DB_CONNECT_ARGS": connect_args,
    })

    return settings


def is_postgresql_setup() -> bool:
    """
    Check to see if it is possible to connect to the ``scrachy_test``
    database using the user ``scrachy``.

    :return:
    """
    try:
        settings = load_postgresql_settings()
    except Exception as e:
        log.error(
            f"There was a problem configuring the test database settings: {str(e)}"
        )
        return False

    url = construct_url(settings)
    engine = create_engine(url, connect_args=settings["SCRACHY_DB_CONNECT_ARGS"])

    try:
        with engine.connect():
            can_connect = True
    except OperationalError as e:
        log.warning(f"Unable to connect to the postgresql test database: {str(e)}")
        can_connect = False
    finally:
        if engine is not None:
            engine.dispose()

    return can_connect


def update_database_settings(
    original_settings: Settings | list[Settings], dialect: str, basedir: pathlib.Path
):
    if isinstance(original_settings, Settings):
        original_settings = [original_settings]

    for current_settings in original_settings:
        current_settings["SCRACHY_DB_DIALECT"] = dialect

        if dialect in ("sqlite", "other"):
            db_dir = basedir
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / f"{TEST_DATABASE_NAME}.sqlite3"
            db_path.unlink(missing_ok=True)

            current_settings.set("SCRACHY_DB_DIALECT", "sqlite")
            current_settings.set("SCRACHY_DB_HOST", None)
            current_settings.set("SCRACHY_DB_PORT", None)
            current_settings.set("SCRACHY_DB_USERNAME", None)
            current_settings.set("SCRACHY_DB_PASSWORD", None)
            current_settings.set("SCRACHY_DB_DATABASE", str(db_path))
            current_settings.set("SCRACHY_DB_SCHEMA", None)
            current_settings.set("SCRACHY_DB_CONNECT_ARGS", {})
        elif dialect == "postgresql":
            current_settings.update(load_postgresql_settings())


def parse_date(obj: Any) -> datetime.datetime:
    if isinstance(obj, str):
        return date_parser.parse(obj)

    if isinstance(obj, datetime.datetime):
        return obj

    raise ValueError(f"Can't parse: {str(obj)}")
