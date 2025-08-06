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
# Loosely based on: https://hackernoon.com/building-a-to-do-list-app-with-python-data-access-layer-with-sqlalchemy

"""
The Data Access Layer.
"""

# Standard Library
import logging

from typing import Any, Callable, Optional, TypeVar

# 3rd Party Library
from arrow import Arrow
from rwskit.sqlalchemy.engine import AsyncAlchemyEngine, SyncAlchemyEngine
from rwskit.sqlalchemy.repository import AsyncRepository, SyncRepository
from sqlalchemy import Select, select
from sqlalchemy.dialects.postgresql.dml import Insert as PostgresInsert
from sqlalchemy.dialects.sqlite.dml import Insert as SqliteInsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, load_only, selectinload

# 1st Party Library
from scrachy.db.base import ScrachyBase
from scrachy.db.models import Response, ScrapeHistory
from scrachy.settings.defaults.storage import RetrievalMethod

BaseT = TypeVar("BaseT", bound=ScrachyBase)

InsertFunction = Callable[[Any], SqliteInsert | PostgresInsert]


log = logging.getLogger(__name__)


class ResponseRepository:
    def _find_minimal_stmt(self, fingerprint: bytes) -> Select:
        return (
            select(Response)
            .options(load_only(Response.body))
            .where(Response.fingerprint == fingerprint)
        )

    def _find_standard_stmt(self, fingerprint: bytes) -> Select:
        return (
            select(Response)
            .options(
                load_only(
                    Response.body, Response.meta, Response.headers, Response.status
                )
            )
            .where(Response.fingerprint == fingerprint)
        )

    def _find_full_stmt(self, fingerprint: bytes) -> Select:
        return (
            select(Response)
            .options(selectinload(Response.scrape_history))
            .where(
                Response.fingerprint == fingerprint,
            )
        )


class SyncResponseRepository(SyncRepository[Response], ResponseRepository):
    def __init__(self, engine: SyncAlchemyEngine):
        super().__init__(engine, Response)

    def find_timestamp_by_fingerprint(
        self, fingerprint: bytes, session: Optional[Session] = None
    ) -> Optional[Arrow]:
        stmt = select(Response.scrape_timestamp).where(
            Response.fingerprint == fingerprint
        )

        with self.get_or_create_session(session) as local_session:
            return local_session.scalars(stmt).first()

    def find_by_fingerprint(
        self,
        fingerprint: bytes,
        retrieval_method: RetrievalMethod = "full",
        session: Optional[Session] = None,
    ) -> Optional[Response]:
        if retrieval_method == "minimal":
            stmt = self._find_minimal_stmt(fingerprint)
        elif retrieval_method == "standard":
            stmt = self._find_standard_stmt(fingerprint)
        elif retrieval_method == "full":
            stmt = self._find_full_stmt(fingerprint)
        else:
            raise ValueError(f"Unknown retrieval method: {retrieval_method}")

        with self.get_or_create_session(session) as local_session:
            return self._find(stmt, local_session)

    def _find(self, stmt: Select, session: Session) -> Optional[Response]:
        return session.scalars(stmt).one_or_none()


class AsyncResponseRepository(AsyncRepository[Response], ResponseRepository):
    def __init__(self, engine: AsyncAlchemyEngine):
        super().__init__(engine, Response)

    async def find_timestamp_by_fingerprint(
        self, fingerprint: bytes, session: Optional[AsyncSession] = None
    ) -> Optional[Arrow]:
        stmt = select(Response.scrape_timestamp).where(
            Response.fingerprint == fingerprint
        )

        async with self.get_or_create_session(session) as local_session:
            future_result = await local_session.scalars(stmt)
            return future_result.first()

    async def find_by_fingerprint(
        self,
        fingerprint: bytes,
        retrieval_method: RetrievalMethod = "full",
        session: Optional[AsyncSession] = None,
    ) -> Optional[Response]:
        if retrieval_method == "minimal":
            stmt = self._find_minimal_stmt(fingerprint)
        elif retrieval_method == "standard":
            stmt = self._find_standard_stmt(fingerprint)
        elif retrieval_method == "full":
            stmt = self._find_full_stmt(fingerprint)
        else:
            raise ValueError(f"Unknown retrieval method: {retrieval_method}")

        async with self.get_or_create_session(session) as local_session:
            return await self._find(stmt, local_session)

    async def _find(self, stmt: Select, session: AsyncSession) -> Optional[Response]:
        future_result = await session.scalars(stmt)
        return future_result.one_or_none()


class SyncScrapeHistoryRepository(SyncRepository[ScrapeHistory]):
    def __init__(self, engine: SyncAlchemyEngine):
        super().__init__(engine, ScrapeHistory)


class AsyncScrapeHistoryRepository(AsyncRepository[ScrapeHistory]):
    def __init__(self, engine: AsyncAlchemyEngine):
        super().__init__(engine, ScrapeHistory)
