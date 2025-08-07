import dataclasses
import functools
from typing import *

from preparse.core.enums import *
from preparse.core.warnings import *

__all__ = ["Item"]


@dataclasses.dataclass
class Item:
    key: Optional[str] = None
    remainder: bool | str = False
    value: Optional[str] = None

    def ishungry(self: Self) -> bool:
        return self.remainder and (self.value is None)

    def isoption(self: Self) -> bool:
        return self.key is not None

    def islong(self: Self) -> bool:
        return self.isoption() and self.key.startswith("-")

    def isgroup(self: Self) -> bool:
        return self.isoption() and not self.key.startswith("-")

    def isspecial(self: Self) -> bool:
        return self.key is None and self.value is None

    def ispositional(self: Self) -> bool:
        return self.key is None and self.value is not None
