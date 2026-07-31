from aiogram.types import Message
from aiogram.dispatcher.event.bases import UNHANDLED

from aiogram_tool.tools.depend import (
     Depends,
     DependFilter,
     DependExit,
     DependTool
)

from .conftest import MyDispatcher, MiddlewareRegistryType



async def test_exit_from_handler_depend(
     depend_tool: DependTool,
     my_dispatcher: MyDispatcher,
     middleware_register: MiddlewareRegistryType
):
     async def depend(context: Message) -> str:
          if context.text is not None and "secret" in context.text:
               return "Top Secret"
          raise DependExit() # in middleware
     
     async def depend_for_filter(context: Message) -> None:
          if context.text == "Skibidi":
               raise DependExit() # in filter
     
     @my_dispatcher.message(DependFilter(Depends(depend_for_filter)))
     async def handle(
          message: Message,
          secret: str = Depends(depend)
     ) -> str:
          assert secret == "Top Secret"
          return "handle"
     
     middleware_register(["message"])
     my_dispatcher.workflow_data["depend_tool"] = depend_tool
     data = ["secret in text", "text", "Skibidi"]
     
     assert [
          await my_dispatcher.message_update(text=text, dispatcher=my_dispatcher) for text in data
     ] == ["handle", None, UNHANDLED]