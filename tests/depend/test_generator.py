import pytest

from typing import Annotated
from contextlib import asynccontextmanager, contextmanager

from aiogram_tool.tools.depend.depend import Depends
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.types.exceptions import ContextManagerError


class Generators:
     
     def __init__(self):
          self.sync = None
          self.async_ = None
          self.sync_ctx = None
          self.async_ctx = None
     
     @contextmanager
     def bool_attr(self, attr: str):
          setattr(self, attr, True)
          yield
          setattr(self, attr, False)

     async def async_generator(self):
          with self.bool_attr("async_"):
               yield "async"

     def sync_generator(self):
          yield "sync"

     @asynccontextmanager
     async def async_generator_with_context(self):
          with self.bool_attr("async_ctx"):
               yield "async_ctx"

     @contextmanager
     def sync_generator_with_context(self):
          yield "sync_ctx"
               

generators = Generators()
     
     
async def test_handler_async(
     depend_resolver: DependResolver
) -> None:
     async def handler_async(
          data: Annotated[str, Depends(generators.async_generator)]
     ):
          assert data == "async"
          
     depend_resolver.handler_callback = handler_async
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_async(**inject)
     await depend_resolver.stack.stack.aclose()
     assert generators.async_ == False
     
async def test_handler_sync(
     depend_resolver: DependResolver
) -> None:
     async def handler_sync(
          data: Annotated[str, Depends(generators.sync_generator)]
     ):
          assert data == "sync"
          
     depend_resolver.handler_callback = handler_sync
     with pytest.raises(ContextManagerError):
          await depend_resolver.resolve_callback_depends()
     
async def test_handler_async_ctx(
     depend_resolver: DependResolver
) -> None:
     async def handler_async_ctx(
          data: Annotated[str, Depends(generators.async_generator_with_context)]
     ):
          assert data == "async_ctx"
          
     depend_resolver.handler_callback = handler_async_ctx
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_async_ctx(**inject)
     await depend_resolver.stack.stack.aclose()
     assert generators.async_ctx == False
     
async def test_handler_sync_ctx(
     depend_resolver: DependResolver
) -> None:
     async def handler_sync_ctx(
          data: Annotated[str, Depends(generators.sync_generator_with_context)]
     ):
          assert data == "sync_ctx"
          
     depend_resolver.handler_callback = handler_sync_ctx
     with pytest.raises(ContextManagerError):
          await depend_resolver.resolve_callback_depends()
     
