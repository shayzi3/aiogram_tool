from typing import Annotated

from aiogram_tool.tools.depend import Depends, ScopeRegistry, Scope
from aiogram_tool.tools.depend.utils.resolver import DependResolver



async def test_subdepend_func(
     depend_resolver: DependResolver
) -> None:
     class Test:
          def __init__(self, attr: str) -> None:
               self.attr = attr
          
     async def subdepend() -> Test:
          return Test(attr="Hello")
     
     async def depend(test: Annotated[Test, Depends(subdepend)]) -> Test:
          assert isinstance(test, Test)
          assert test.attr == "Hello"
          return Test(attr=test.attr + " Vlad!")
     
     async def handler(hello: Annotated[Test, Depends(depend)]) -> str:
          assert isinstance(hello, Test)
          assert hello.attr == "Hello Vlad!"
          return hello.attr + " I'm 18"
     
     depend_resolver.handler_callback = handler
     inject = await depend_resolver.resolve_callback_depends()
     handler_result = await handler(**inject)
     assert handler_result == "Hello Vlad! I'm 18"
     
     
async def test_subdepend_func_request_scope(
     depend_resolver: DependResolver,
     scope_registry: ScopeRegistry
) -> None:
     class Test:
          pass
          
     @scope_registry(Scope.REQUEST)
     async def subdepend() -> Test:
          return Test()
     
     async def depend(test: Annotated[Test, Depends(subdepend)]) -> Test:
          return test
     
     async def handler(
          arg: Annotated[Test, Depends(depend)],
          sub_arg: Annotated[Test, Depends(subdepend)]
     ) -> str:
          assert arg == sub_arg
     
     depend_resolver.handler_callback = handler
     depend_resolver.scope_registry = scope_registry
     inject = await depend_resolver.resolve_callback_depends()
     await handler(**inject)
     