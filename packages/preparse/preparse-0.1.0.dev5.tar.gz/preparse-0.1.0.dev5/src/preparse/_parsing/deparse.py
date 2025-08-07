from typing import *

from preparse._parsing.Item import *

if TYPE_CHECKING:
    from preparse.core.PreParser import PreParser
__all__ = ["deparse"]


def deparse(items: list[Item]) -> list[str]:
    ans: str = list()
    item: Item
    for item in items:
        ans += deparse_item(item)
    return ans


def deparse_item(item: Item) -> list[str]:
    if item.isspecial():
        return ["--"]
    if item.ispositional():
        return [item.value]
    if item.isgroup():
        if item.value is None:
            return ["-" + item.key]
        if item.remainder:
            return ["-" + item.key + item.value]
        else:
            return ["-" + item.key, item.value]
    else:
        if item.value is None:
            return [item.key]
        if item.remainder:
            return [item.key + "=" + item.value]
        else:
            return [item.key, item.value]
