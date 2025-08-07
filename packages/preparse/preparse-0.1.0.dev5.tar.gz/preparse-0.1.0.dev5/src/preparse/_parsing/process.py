import sys
from typing import *

from preparse._parsing.deparse import *
from preparse._parsing.digest import *
from preparse._parsing.Item import *
from preparse._parsing.parse import *

if TYPE_CHECKING:
    from preparse.core.PreParser import PreParser

__all__ = ["process"]


def process(
    *,
    args: Optional[Iterable] = None,
    parser: "PreParser",
) -> list[str]:
    "This method parses args."
    if args is None:
        args = sys.argv[1:]
    args = [str(a) for a in args]
    parser = parser.copy()
    items: list[Item] = list(parse(args=args, parser=parser))
    items: list[Item] = list(digest(items=items, parser=parser))
    ans: list[str] = list(deparse(items=items))
    return ans
