"""A ``Settings`` class that assumes all setting names start with a given ``prefix``."""

# Standard Library
from typing import Any, Mapping, Optional, Union

# 3rd Party Library
from scrapy.settings import Settings, _SettingsKeyT

_SettingsInputT = Union[Mapping[_SettingsKeyT, Any], str, None]


class PrefixedSettings(Settings):
    """A ``Settings`` class that assumes all setting names start with a given ``prefix``."""

    def __init__(
        self,
        prefix: str,
        values: _SettingsInputT = None,
        priority: int | str = "project",
    ):
        super().__init__(values, priority)

        self._prefix = prefix

    def full_key(self, name: _SettingsKeyT) -> _SettingsKeyT:
        """Get the full key for the setting, including the prefix, from the given ``name``.

        If the ``name`` is a string, the full key is constructed from the
        following pattern ``{prefix}_{name}``. Otherwise, the ``name`` is
        returned as is.

        Parameters
        ----------
        name : _SettingsKeyT
            The (unprefixed) name of the setting.

        Returns
        -------
        _SettingsKeyT
            The full name of the setting (or unaltered key if it is not a string.)
        """
        if isinstance(name, str):
            return f"{self._prefix}_{name}"

        return name

    def get(self, name: _SettingsKeyT, default: Any = None) -> Any:
        return super().get(self.full_key(name), default)

    def getbool(self, name: _SettingsKeyT, default: bool = False) -> bool:
        return super().getbool(self.full_key(name), default)

    def getint(self, name: _SettingsKeyT, default: int = 0) -> int:
        return super().getint(self.full_key(name), default)

    def getfloat(self, name: _SettingsKeyT, default: float = 0) -> float:
        return super().getfloat(self.full_key(name), default)

    def getlist(
        self, name: _SettingsKeyT, default: Optional[list[Any]] = None
    ) -> list[Any]:
        return super().getlist(self.full_key(name), default)

    def getdict(
        self, name: _SettingsKeyT, default: Optional[dict[Any, Any]] = None
    ) -> dict[Any, Any]:
        return super().getdict(self.full_key(name), default)

    def getdictorlist(
        self,
        name: _SettingsKeyT,
        default: dict[Any, Any] | list[Any] | tuple[Any] | None = None,
    ) -> dict[Any, Any] | list[Any]:
        return super().getdictorlist(self.full_key(name), default)
        return super().getdictorlist(self.full_key(name), default)
