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
import logging

from contextlib import contextmanager
from typing import Any, Generator, Optional

# 3rd Party Library
from psycopg import Connection
from rwskit.sqlalchemy.config import DatabaseConnectionConfig
from sqlalchemy import Engine

# 1st Party Library
from scrachy.db.base import ScrachyBase

log = logging.getLogger(__name__)


@contextmanager
def sync_engine_manager(
    dialect: str, postgresql: Optional[Connection] = None
) -> Generator[Engine, Any, None]:
    if dialect == "postgresql" and postgresql is not None:
        info = postgresql.info
        config = DatabaseConnectionConfig(
            drivername="postgresql+psycopg",
            username=info.user,
            host=info.host,
            port=info.port,
            database=info.dbname,
        )
        engine = config.create_sync_engine()
    elif dialect == "sqlite":
        # In memory sqlite database tables only persist within the same
        # database connection used to create them. Using a 'StaticPool'
        # ensures the same connection is always reused and
        # 'check_same_thread=False' allows the same connection to be reused
        # across threads (if necessary)
        config = DatabaseConnectionConfig(
            drivername="sqlite",
            database=":memory:",
            poolclass_name="StaticPool",
            pool_size=None,
            max_overflow=None,
        )

        engine = config.create_sync_engine()
    else:
        raise ValueError(f"Unsupported dialect: {dialect}")

    ScrachyBase.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        # Catching exceptions here will hide any errors and potentially even
        # assertion failures
        ScrachyBase.metadata.drop_all(bind=engine)
        engine.dispose()
