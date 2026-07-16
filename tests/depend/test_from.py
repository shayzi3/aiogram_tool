import pytest

from aiogram_tool.tools.depend.depend import From, Depends
from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.types.exceptions import CallableError
from aiogram_tool.types import _MISSING


async def depend() -> int:
     return 1


def test_depend() -> None:
     from_object = From(depend=depend)
     
     assert from_object.depend == depend
     assert from_object.scope == _MISSING
     
     
def test_non_callable_depend() -> None:
     with pytest.raises(CallableError):
          From(depend="Non-callable")
          

def test_depend_with_scope() -> None:
     from_object = From(
          depend=depend,
          scope=Scope.REQUEST
     )
     assert from_object.scope == Scope.REQUEST
     

def test_depend_factory() -> None:
     dep = Depends(depend)
     
     assert isinstance(dep, From)
     assert dep.depend == depend
     

def test_depend_factory_with_scope() -> None:
     dep = Depends(
          depend, scope=Scope.TRANSIENT
     )
     assert dep.scope == Scope.TRANSIENT
     