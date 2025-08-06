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

"""
The basic data types and classes required to define the SqlAlchemy models.
"""

# Future Library
from __future__ import annotations

# Standard Library
import logging

from typing import Annotated, Any, ClassVar

# 3rd Party Library
from arrow import Arrow
from rwskit.sqlalchemy.base import BaseModel, default_metadata
from sqlalchemy import BigInteger, LargeBinary, MetaData, SmallInteger
from sqlalchemy_utils.types import ArrowType

# 1st Party Library
from scrachy.settings import PROJECT_SETTINGS
from scrachy.utils.sqltypes import ConditionalJson

log = logging.getLogger(__name__)


schema = PROJECT_SETTINGS.get("SCRACHY_DB_SCHEMA")
schema_prefix = f"{schema}." if schema else ""

bigint = Annotated[int, 64]
binary = Annotated[bytes, None]
smallint = Annotated[int, 16]
timestamp = Annotated[Arrow, None]
conditional_json = Annotated[dict[str, Any], None]


BaseModel.registry.update_type_annotation_map({
    bigint: BigInteger,
    binary: LargeBinary,
    conditional_json: ConditionalJson,
    smallint: SmallInteger,
    timestamp: ArrowType,
})


class ScrachyBase(BaseModel):
    __abstract__ = True

    metadata: ClassVar[MetaData] = default_metadata()
