##############################################################################
#  Copyright 2020 Reid Swanson and the Scrapy developers.
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

"""Hashing utilities."""

# Standard Library
from typing import Optional, Protocol, Sequence

# 3rd Party Library
from scrapy.utils.python import to_bytes


class Hasher(Protocol):
    """
    An object that can hash byte strings.
    """

    def update(self, b: bytes): ...

    def digest(self) -> bytes: ...


def hash_text(
    hash_fn: Hasher, text: Optional[str | Sequence[str | None]] = None
) -> bytes:
    """
    Hash a string, or list of strings, using the given ``hash_fn``. If any
    string is ``None``, it will return the hash value of an empty string.

    :param text: The string to hash.
    :param hash_fn: A hash function object that adheres to the hashlib API.
           Namely, it must have an ``update`` function and a ``digest``
           function.
    :return: The hash digest as an array of bytes.

    """
    if text is None or isinstance(text, str):
        text = [text]
    elif not isinstance(text, Sequence):
        raise ValueError(
            "If the input is not None, it must either be a string or sequence of "
            f"strings, but got: '{type(text)}'"
        )

    for t in text:
        hash_fn.update(to_bytes(t or b""))

    return hash_fn.digest()


# endregion Utility Methods
