from typing_extensions import Self, Any
from contextlib import (
     AsyncExitStack, 
     AbstractAsyncContextManager
)

from aiogram_tool.tools.depend.types.enums import Scope



class AsyncExitStackTransaction:
     
     def __init__(self, app_stack: AsyncExitStack) -> None:
          self.app_stack = app_stack
          self.stack = AsyncExitStack()
          
     async def __aenter__(self) -> Self:
          return self
     
     async def __aexit__(self, *args) -> None:
          await self.stack.aclose()
          
     def _get_stack(self, scope: Scope) -> AsyncExitStack:
          return self.app_stack if scope == Scope.SINGLETON else self.stack
     
     async def enter_async_context(
          self,
          context_manager: AbstractAsyncContextManager,
          scope: Scope,
     ) -> Any:
          stack = self._get_stack(scope)
          return await stack.enter_async_context(context_manager)          
     


class AsyncExitStackTransactionManager:
     
     def __init__(self):
          self.stack = AsyncExitStack()
          
     def transaction(self) -> AsyncExitStackTransaction:
          return AsyncExitStackTransaction(self.stack)