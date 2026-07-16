
from aiogram_tool.tools.depend import (
     Depends,
     ScopeRegistry, 
     DependTool,
     Scope
)
from aiogram_tool.types import _MISSING
from aiogram_tool.tools.depend.utils.resolver import DependResolver
from aiogram_tool.tools.depend.utils.stack_manager import AsyncExitStackTransaction



def test_scope_registry() -> None:
     scopes = ScopeRegistry()
     
     @scopes(Scope.SINGLETON)
     async def func() -> None:
          return None
     
     get_scope = scopes.get_scope(func) 
     assert get_scope == Scope.SINGLETON
     
     
async def test_singleton_scope(
     depend_tool: DependTool,
     stack_transaction: AsyncExitStackTransaction,
     scope_registry: ScopeRegistry
) -> None:
     @scope_registry(Scope.SINGLETON)
     async def singleton_func() -> int:
          return 5
     
     async def handler(integer: int = Depends(singleton_func)) -> int:
          return integer**2
     
     async with depend_tool.registry.transaction() as registry:
          resolver = DependResolver(
               handler_callback=handler,
               registry=registry,
               stack=stack_transaction,
               scope_registry=scope_registry,
               middleware_data={},
               dependency_override={}
          )
          inject = await resolver.resolve_callback_depends()
          assert inject == {"integer": 5}
          handler_result = await handler(**inject)
          assert handler_result == 25
          
          dependency = await registry.storage.get_value(
               key=singleton_func
          )
          assert dependency == _MISSING
     
     dependency = await depend_tool.registry.storage.get_value(
          key=singleton_func
     )
     assert dependency == 5
     
     
async def test_singleton_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry
) -> None:
     @scope_registry(Scope.SINGLETON)
     async def singleton_generator_func():
          yield 15
          
     async def handler(integer: int = Depends(singleton_generator_func)) -> int:
          return integer * 2
     
     async with depend_tool.stack_manager.transaction() as stack:
          async with depend_tool.registry.transaction() as registry:
               resolver = DependResolver(
                    handler_callback=handler,
                    registry=registry,
                    scope_registry=scope_registry,
                    stack=stack,
                    middleware_data={},
                    dependency_override={}
               )
               inject = await resolver.resolve_callback_depends()
               assert inject == {"integer": 15}
               handler_result = await handler(**inject)
               assert handler_result == 30
               
               dependency = await registry.storage.get_value(
                    key=singleton_generator_func
               )
               assert dependency == _MISSING
               assert not getattr(stack.stack, "_exit_callbacks", True)
     
     dependency = await depend_tool.registry.storage.get_value(
          key=singleton_generator_func
     )
     assert dependency == 15
     assert getattr(depend_tool.stack_manager.stack, "_exit_callbacks", False)
               
     
async def test_request_scope(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     stack_transaction: AsyncExitStackTransaction,
) -> None:
     @scope_registry(Scope.REQUEST)
     async def request_func() -> int:
          return 30
     
     async def handler(integer: int = Depends(request_func)) -> int:
          return integer * 2
     
     async with depend_tool.registry.transaction() as registry:
          resolver = DependResolver(
               handler_callback=handler,
               registry=registry,
               stack=stack_transaction,
               scope_registry=scope_registry,
               middleware_data={},
               dependency_override={}
          )
          inject = await resolver.resolve_callback_depends()
          assert inject == {"integer": 30}
          handler_result = await handler(**inject)
          assert handler_result == 60
          
          req_dependency = await registry.storage.get_value(
               key=request_func
          )
          assert req_dependency == 30
          
     clear_req_dependency = await registry.storage.get_value(
          key=request_func
     )
     assert clear_req_dependency == _MISSING
     
     app_dependency = await depend_tool.registry.storage.get_value(
          key=request_func
     )
     assert app_dependency == _MISSING
     
     
async def test_request_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry
) -> None:
     @scope_registry(Scope.REQUEST)
     async def request_generator_func():
          yield 10
          
     async def handler(integer: int = Depends(request_generator_func)) -> int:
          return integer * 2
     
     async with depend_tool.stack_manager.transaction() as stack:
          async with depend_tool.registry.transaction() as registry:
               resolver = DependResolver(
                    handler_callback=handler,
                    registry=registry,
                    scope_registry=scope_registry,
                    stack=stack,
                    middleware_data={},
                    dependency_override={}
               )
               inject = await resolver.resolve_callback_depends()
               assert inject == {"integer": 10}
               handler_result = await handler(**inject)
               assert handler_result == 20
               
               req_dependency = await registry.storage.get_value(
                    key=request_generator_func
               )
               assert req_dependency == 10
               assert getattr(stack.stack, "_exit_callbacks", False)
               
     clear_req_dependency = await registry.storage.get_value(
          key=request_generator_func
     )
     assert clear_req_dependency == _MISSING
     assert not getattr(stack.stack, "_exit_callbacks", True)
     
     app_dependency = await depend_tool.registry.storage.get_value(
          key=request_generator_func
     )
     assert app_dependency == _MISSING
     assert not getattr(depend_tool.stack_manager.stack, "_exit_callbacks", True)
     
     
async def test_transient_scope(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry,
     stack_transaction: AsyncExitStackTransaction,
) -> None:
     @scope_registry(Scope.TRANSIENT)
     async def transient_func() -> int:
          return 12

     async def handler(integer: int = Depends(transient_func)) -> int:
          return integer * 2
     
     async with depend_tool.registry.transaction() as registry:
          resolver = DependResolver(
               handler_callback=handler,
               registry=registry,
               stack=stack_transaction,
               scope_registry=scope_registry,
               middleware_data={},
               dependency_override={}
          )
          inject = await resolver.resolve_callback_depends()
          assert inject == {"integer": 12}
          handler_result = await handler(**inject)
          assert handler_result == 24
          
          tr_dependency = await registry.storage.get_value(
               key=transient_func
          )
          assert tr_dependency == _MISSING
          
     tr_dependency = await registry.storage.get_value(
          key=transient_func
     )
     assert tr_dependency == _MISSING
     
     app_dependency = await depend_tool.registry.storage.get_value(
          key=transient_func
     )
     assert app_dependency == _MISSING
     
     
async def test_transient_scope_generator(
     depend_tool: DependTool,
     scope_registry: ScopeRegistry
) -> None:
     @scope_registry(Scope.TRANSIENT)
     async def transient_generator_func():
          yield 8
          
     async def handler(integer: int = Depends(transient_generator_func)) -> int:
          return integer * 2
     
     async with depend_tool.stack_manager.transaction() as stack:
          async with depend_tool.registry.transaction() as registry:
               resolver = DependResolver(
                    handler_callback=handler,
                    registry=registry,
                    scope_registry=scope_registry,
                    stack=stack,
                    middleware_data={},
                    dependency_override={}
               )
               inject = await resolver.resolve_callback_depends()
               assert inject == {"integer": 8}
               handler_result = await handler(**inject)
               assert handler_result == 16
               
               tr_dependency = await registry.storage.get_value(
                    key=transient_generator_func
               )
               assert tr_dependency == _MISSING
               assert getattr(stack.stack, "_exit_callbacks", False)
               
     tr_dependency = await registry.storage.get_value(
          key=transient_generator_func
     )
     assert tr_dependency == _MISSING
     assert not getattr(stack.stack, "_exit_callbacks", True)
     
     app_dependency = await depend_tool.registry.storage.get_value(
          key=transient_generator_func
     )
     assert app_dependency == _MISSING
     assert not getattr(depend_tool.stack_manager.stack, "_exit_callbacks", True)
          
     
     
     