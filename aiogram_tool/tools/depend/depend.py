from typing import Callable

from aiogram_tool.tools.depend.types.enums import Scope
     


class From:
     
     def __init__(
          self, 
          depend: Callable, 
          scope: Scope | None = None
     ) -> None:
          if not callable(depend):
               raise ValueError(f"object {depend} is not callable")
          
          self.depend = depend
          self.scope = scope
     