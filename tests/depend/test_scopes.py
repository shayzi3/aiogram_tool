import pytest

from asyncio import gather
from typing_extensions import Self

from aiogram.types import Message

from aiogram_tool.tools.depend import (
     Depends,
     ScopeRegistry, 
     DependTool,
     Scope
)

from .conftest import MyDispatcher, MiddlewareRegistryType


class MyInstance:
          ...
          
class MySession:
     def __init__(self) -> None:
          self.is_alive = None
          
     async def __aenter__(self) -> Self:
          self.is_alive = True
          return self   
     
     async def __aexit__(self, exc_type, exc, tb):
          self.is_alive = False
          return None
          
class InstanceManager:
     def __init__(self):
          self.instances = []
          
     def __call__(self) -> MyInstance:
          instance = MyInstance()
          self.instances.append(instance)
          return instance
               
class SessionManager:
     
     def __init__(self):
          self.sessions: list[MySession] = []
     
     def __call__(self) -> MySession:
          session = MySession()
          self.sessions.append(session)
          return session


@pytest.fixture(scope="function")
def instance_manager() -> InstanceManager:
     return InstanceManager()


@pytest.fixture(scope="function")
def session_manager() -> SessionManager:
     return SessionManager()


def test_scope_registry() -> None:
     scopes = ScopeRegistry()
     
     @scopes(Scope.SINGLETON)
     async def func() -> None:
          return None
     
     get_scope = scopes.get_scope(func) 
     assert get_scope == Scope.SINGLETON
     
     
async def test_singleton_scope(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     instance_manager: InstanceManager
) -> None:
     @scope_registry(Scope.SINGLETON)
     async def get_instance() -> MyInstance:
          return instance_manager()
     
     @my_dispatcher.message()
     async def handle(
          message: Message,
          instance: MyInstance = Depends(get_instance),
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(instance, MyInstance)
          return "handle"
          
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(instance_manager.instances) == 1
     
     
async def test_singleton_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     session_manager: SessionManager
) -> None:
     @scope_registry(scope=Scope.SINGLETON)
     async def get_session():
          async with session_manager() as session:
               yield session
          
     @my_dispatcher.message()
     async def handle(
          message: Message,
          session: MySession = Depends(get_session),
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(session, MySession)
          assert session.is_alive is True
          return "handle"
     
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(session_manager.sessions) == 1
     for session in session_manager.sessions:
          assert session.is_alive is True
     
     
     
async def test_request_scope(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     instance_manager: InstanceManager
) -> None:
     @scope_registry(Scope.REQUEST)
     async def get_instance() -> MyInstance:
          return instance_manager()
          
     async def depend(ins: MyInstance = Depends(get_instance)) -> MyInstance:
          return ins
          
     @my_dispatcher.message()
     async def handle(
          message: Message,
          ins: MyInstance = Depends(get_instance),
          ins_from_depend: MyInstance = Depends(depend)
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(ins, MyInstance)
          assert isinstance(ins_from_depend, MyInstance)
          assert ins is ins_from_depend
          return "handle"
          
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(instance_manager.instances) == 2
     
     
     
async def test_request_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     session_manager: SessionManager
) -> None:
     @scope_registry(Scope.REQUEST)
     async def get_session():
          async with session_manager() as session:
               yield session
     
     async def depend(session: MySession = Depends(get_session)) -> MySession:
          return session
          
     @my_dispatcher.message()
     async def handle(
          message: Message,
          session: MySession = Depends(get_session),
          session_from_depend: MySession = Depends(depend)
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(session, MySession)
          assert isinstance(session_from_depend, MySession)
          assert session is session_from_depend
          assert session.is_alive is True
          return "handle"
          
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(session_manager.sessions) == 2
     for session in session_manager.sessions:
          assert session.is_alive is False
     
     
async def test_transient_scope(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     instance_manager: InstanceManager
) -> None:
     @scope_registry(Scope.TRANSIENT)
     async def get_instance() -> MyInstance:
          return instance_manager()
          
     async def depend(ins: MyInstance = Depends(get_instance)) -> MyInstance:
          return ins
          
     @my_dispatcher.message()
     async def handle(
          message: Message,
          ins: MyInstance = Depends(get_instance),
          ins_from_depend: MyInstance = Depends(depend)
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(ins, MyInstance)
          assert isinstance(ins_from_depend, MyInstance)
          assert ins is not ins_from_depend
          return "handle"
          
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(instance_manager.instances) == 4
     
     
async def test_transient_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     middleware_register: MiddlewareRegistryType,
     my_dispatcher: MyDispatcher,
     session_manager: SessionManager
) -> None:
     @scope_registry(Scope.TRANSIENT)
     async def get_session():
          async with session_manager() as session:
               yield session
     
     async def depend(session: MySession = Depends(get_session)) -> MySession:
          return session
          
     @my_dispatcher.message()
     async def handle(
          message: Message,
          session: MySession = Depends(get_session),
          session_from_depend: MySession = Depends(depend)
     ) -> str:
          assert isinstance(message, Message)
          assert isinstance(session, MySession)
          assert isinstance(session_from_depend, MySession)
          assert session is not session_from_depend
          assert session.is_alive is True
          return "handle"
          
     middleware_register(["message"])
     depend_tool.scope_registry = scope_registry
     handle_result = await gather(
          *[
               my_dispatcher.message_update() for _ in range(2)
          ]
     )
     assert handle_result == ["handle", "handle"]
     assert len(session_manager.sessions) == 4
     for session in session_manager.sessions:
          assert session.is_alive is False
     
     