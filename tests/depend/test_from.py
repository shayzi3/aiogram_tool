import pytest

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.enums import Scope


async def depend() -> int:
     return 1


def test_depend() -> None:
     from_object = From(depend=depend)
     
     assert from_object.depend == depend
     assert from_object.scope == None
     
     
def test_non_callable_depend() -> None:
     with pytest.raises(ValueError):
          From(depend="Non-callable")
          

def test_depend_with_scope() -> None:
     from_object = From(
          depend=depend,
          scope=Scope.REQUEST
     )
     assert from_object.scope == Scope.REQUEST
     