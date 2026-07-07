from typing import Any, Callable
from contextlib import (
     AsyncExitStack, 
     asynccontextmanager,
     contextmanager,
)

from aiogram_tool.tools.depend.types.enums import Scope



class AsyncExitStackTransaction(AsyncExitStack):
     
     def __init__(self, app_stack: AsyncExitStack) -> None:
          self.app_stack = app_stack
          super().__init__()
          
     async def enter_async_context(
          self, 
          func: Callable, 
          scope: Scope,
          *args, 
          **kwargs
     ) -> Any:
          stack = super()
          if scope == Scope.APP:
               stack = self.app_stack
               
          try:
               return await stack.enter_async_context(func(*args, **kwargs))
          except TypeError:
               return await stack.enter_async_context(
                    asynccontextmanager(func)(*args, **kwargs)
               )
     
     async def enter_context(
          self, 
          func: Callable, 
          scope: Scope,
          *args, 
          **kwargs
     ) -> Any:
          stack = super()
          if scope == Scope.APP:
               stack = self.app_stack
               
          try:
               return stack.enter_context(func(*args, **kwargs))
          except TypeError:
               return stack.enter_context(
                    contextmanager(func)(*args, **kwargs)
               )


class AsyncExitStackTransactionManager(AsyncExitStack):
          
     def transaction(self) -> AsyncExitStackTransaction:
          return AsyncExitStackTransaction(self)
     

     
     
          
     