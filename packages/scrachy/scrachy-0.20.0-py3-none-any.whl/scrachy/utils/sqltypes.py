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

"""Custom SqlAlchemy types."""

# Standard Library
from typing import Any

# 3rd Party Library
from sqlalchemy import JSON, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.type_api import TypeEngine


class ConditionalJson(TypeDecorator):
    """Uses JSONB if the dialect is postgresql otherwise uses JSON"""

    # The common base type
    impl = JSON

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())

        if dialect.name in ("sqlite", "mysql", "mssql"):
            return dialect.type_descriptor(JSON())

        raise ValueError("The dialect must at least support the JSON data type.")
