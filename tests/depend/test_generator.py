from typing import Annotated
from contextlib import asynccontextmanager, contextmanager

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.utils.resolver import DependResolver


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
          with self.bool_attr("sync"):
               yield "sync"

     @asynccontextmanager
     async def async_generator_with_context(self):
          with self.bool_attr("async_ctx"):
               yield "async_ctx"

     @contextmanager
     def sync_generator_with_context(self):
          with self.bool_attr("sync_ctx"):
               yield "sync_ctx"
               

generators = Generators()
     
     
async def handler_async(
     data: Annotated[str, From(generators.async_generator)]
):
     assert data == "async"

async def handler_sync(
     data: Annotated[str, From(generators.sync_generator)]
):
     assert data == "sync"
     
async def handler_async_ctx(
     data: Annotated[str, From(generators.async_generator_with_context)]
):
     assert data == "async_ctx"
     
async def handler_sync_ctx(
     data: Annotated[str, From(generators.sync_generator_with_context)]
):
     assert data == "sync_ctx"
     
     
async def test_handler_async(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_async
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_async(**inject)
     await depend_resolver.stack.aclose()
     assert generators.async_ == False
     
async def test_handler_sync(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_sync
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_sync(**inject)
     await depend_resolver.stack.aclose()
     assert generators.sync == False
     
async def test_handler_async_ctx(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_async_ctx
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_async_ctx(**inject)
     await depend_resolver.stack.aclose()
     assert generators.async_ctx == False
     
async def test_handler_sync_ctx(
     depend_resolver: DependResolver
) -> None:
     depend_resolver.handler_callback = handler_sync_ctx
     
     inject = await depend_resolver.resolve_callback_depends()
     await handler_sync_ctx(**inject)
     await depend_resolver.stack.aclose()
     assert generators.sync_ctx == False
     
