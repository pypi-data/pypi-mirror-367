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

"""The addons provided by Scrachy."""

# Future Library
from __future__ import annotations

# Standard Library
import importlib
import logging

from types import ModuleType
from typing import Optional

# 3rd Party Library
from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings

# 1st Party Library
from scrachy.settings.defaults import filter as cache_filter
from scrachy.settings.defaults import fingerprinter, storage
from scrachy.utils.imports import get_import_path
from scrachy.utils.request import DEFAULT_SCRACHY_FINGERPRINTER_VERSION

log = logging.getLogger(__name__)


def try_import(module_name: str, addon_name):
    """
    Try importing a module by name and raise a
    :class:`scrapy.exceptions.NotConfigured` error if it can't be found.

    :param module_name: The full path to the module.
    :param addon_name: The name of the addon.
    """
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise NotConfigured(
            f"The {addon_name} addon requires the module: {module_name}"
        )


class ScrachyAddon:
    """
    The base class for all Scrachy addons.
    """

    def __init__(self, settings_module: Optional[ModuleType] = None):
        self.settings_module = settings_module

    def update_settings(self, settings: Settings):
        if self.settings_module is not None:
            settings.setmodule(self.settings_module, "addon")


class BlacklistPolicyAddon(ScrachyAddon):
    def __int__(self):
        super().__init__()


class DynamicHashRequestFingerprinterAddon(ScrachyAddon):
    def __init__(self):
        super().__init__(fingerprinter)

    def update_settings(self, settings: Settings):
        super().update_settings(settings)

        fp = get_import_path(settings.get("REQUEST_FINGERPRINTER_CLASS"))

        if fp.startswith("scrachy"):
            settings["REQUEST_FINGERPRINTER_IMPLEMENTATION"] = (
                DEFAULT_SCRACHY_FINGERPRINTER_VERSION
            )


class AlchemyCacheStorageAddon(ScrachyAddon):
    def __init__(self):
        super().__init__(storage)

    def update_settings(self, settings: Settings):
        def check_import(m: str):
            try_import(m, self.__class__.__name__)

        check_import("bs4")
        check_import("w3lib")
        check_import("sqlalchemy")

        super().update_settings(settings)


class CachedResponseFilterAddon(ScrachyAddon):
    def __init__(self):
        super().__init__(cache_filter)
        super().__init__(cache_filter)
