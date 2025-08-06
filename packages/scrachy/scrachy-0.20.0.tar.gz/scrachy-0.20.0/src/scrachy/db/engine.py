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

"""
Utilities to initialize and work with the SqlAlchemy engine.
"""

# Standard Library
import logging

from typing import Optional

# 3rd Party Library
from rwskit.sqlalchemy.engine import SyncAlchemyEngine
from scrapy.settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.sql.ddl import CreateSchema

# 1st Party Library
from scrachy.db.base import ScrachyBase
from scrachy.utils.db import construct_url

log = logging.getLogger(__name__)


# Singleton engine for the project. However, it is the responsibility
# of the AlchemyCacheStorage to initialize it on construction.
engine: Optional[SyncAlchemyEngine] = None


def initialize_engine(settings: BaseSettings):
    global engine

    if engine is not None:
        log.debug("The engine is already initialized.")
        return engine  # The engine is already setup

    schema = settings.get("SCRACHY_DB_SCHEMA")
    connect_args = settings.getdict("SCRACHY_DB_CONNECT_ARGS", {})

    # Create the engine
    execution_options = {"schema_translate_map": {None: schema}} if schema else {}
    url = construct_url(settings)

    log.debug(f"Constructing engine from url: {url}")
    sa_engine = create_engine(
        url,
        connect_args=connect_args,
        execution_options=execution_options,
        pool_pre_ping=True,
    )

    log.debug(
        f"Engine initialized from parameters: "
        f"{sa_engine.url.render_as_string(hide_password=True)}."
    )

    # Create the schema if necessary
    if schema is not None:
        with sa_engine.connect() as connection:
            connection.execute(CreateSchema(schema, if_not_exists=True))
            connection.commit()

    # Create the tables if necessary
    ScrachyBase.metadata.create_all(sa_engine)

    engine = SyncAlchemyEngine(sa_engine, ScrachyBase)

    return engine


# def reset_engine():
#     global engine
#     global session_factory

#     if engine is not None:
#         engine.dispose()

#     if session_factory is not None:
#         session_factory.close_all()

#     engine = None
#     session_factory = None


# @contextmanager
# def session_scope():
#     if session_factory is None:
#         raise ValueError("You must initialize the engine first.")

#     session = session_factory()

#     # noinspection PyBroadException
#     try:
#         yield session
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         raise e
#     finally:
#         session.close()
