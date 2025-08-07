from typing import *

from preparse._parsing.Item import *
from preparse.core.enums import *
from preparse.core.warnings import *

if TYPE_CHECKING:
    from preparse.core.PreParser import PreParser

__all__ = ["digest"]


def digest(*, items: list[Item], parser: "PreParser") -> list[Item]:
    items = list(digest_order(items=items, order=parser.order))
    items = list(digest_group(items=items, group=parser.group))
    return items


def digest_group(*, items: list[Item], group: Group) -> list[Item]:
    if group == Group.MINIMIZE:
        return digest_group_minimize(items)
    if group == Group.MAXIMIZE:
        return digest_group_maximize(items)
    return items


def digest_group_minimize(items: list[Item]) -> list[Item]:
    ans: list[Item] = list()
    item: Item
    for item in items:
        ans += digest_group_minimize_split(item)
    return ans


def digest_group_minimize_split(item: Item) -> list[Item]:
    if not item.isgroup():
        return [item]
    ans: list[Item] = list()
    x: str
    for x in item.key:
        if x == "-":
            ans[-1].key += "-"
        else:
            ans.append(Item(key=x))
    item.key = ans[-1].key
    ans[-1] = item
    return ans


def digest_group_maximize(items: list[Item]) -> list[Item]:
    ans: list[Item] = [items.pop(0)]
    item: Item
    for item in items:
        if item.isgroup() and ans[-1].isgroup() and ans[-1].value is None:
            item.key = ans[-1].key + item.key
            ans[-1] = item
        else:
            ans.append(item)
    return ans


def digest_order(*, items: list[Item], order: Order) -> list[Item]:
    if order == Order.PERMUTE:
        items.sort(key=digest_order_key)
    return items


def digest_order_key(item: Item):
    if item.isoption():
        return 0
    if item.isspecial():
        return 1
    return 2
