from typing_extensions import Self

from aiogram.types import Message

from aiogram_tool.tools.depend import (
     Depends,
     ScopeRegistry, 
     DependTool,
     Scope,
     DependFilter
)

from .conftest import MyDispatcher, MiddlewareRegistryType



async def test_depend_filter(
     depend_tool: DependTool,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     scope_registry: ScopeRegistry
):
     class Session:
          def __init__(self):
               self.storage = {}
               
          async def __aenter__(self) -> Self:
               return self
          
          async def __aexit__(self, exc_type, exc, tb):
               self.storage.clear()
               
     @scope_registry(Scope.REQUEST)
     async def get_session():
          async with Session() as s:
               yield s
     
     @scope_registry(Scope.TRANSIENT)
     async def depend_for_filter(
          context: Message, 
          session: Session = Depends(get_session)
     ):
          session.storage["text"] = context.text
     
     @my_dispatcher.message(DependFilter(Depends(depend_for_filter)))
     async def handle(
          message: Message,
          session: Session = Depends(get_session)
     ) -> str:
          text = session.storage.get("text")
          assert text == "Hello"
          return "handle"
     
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     my_dispatcher.workflow_data["depend_tool"] = depend_tool
     handle_result = await my_dispatcher.message_update(text="Hello", dispatcher=my_dispatcher)
     
     assert handle_result == "handle"