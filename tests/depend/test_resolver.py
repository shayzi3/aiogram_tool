from typing import Annotated

from aiogram.types import Message

from aiogram_tool.tools.depend import Depends, DependTool, Scope, ScopeRegistry
from aiogram_tool.tools.depend.utils.resolver import Resolver

from .conftest import MiddlewareRegistryType, MyDispatcher


class MyInstance: ...


class InstanceManager:
    def __init__(self):
        self.instances = []

    def __call__(self) -> MyInstance:
        instance = MyInstance()
        self.instances.append(instance)
        return instance


async def test_resolver_call_in_middleware(
    depend_tool: DependTool,
    scope_registry: ScopeRegistry,
    middleware_register: MiddlewareRegistryType,
    my_dispatcher: MyDispatcher,
) -> None:
    instance_manager = InstanceManager()

    @scope_registry(Scope.REQUEST)
    async def get_instance() -> MyInstance:
        return instance_manager()

    async def user_middleware(handler, event, data):
        resolver: Resolver = data["resolver"]
        data["middleware_instance"] = await resolver.resolve(get_instance)
        return await handler(event, data)

    @my_dispatcher.message()
    async def handle(
        message: Message,
        middleware_instance: MyInstance,
        handler_instance: Annotated[MyInstance, Depends(get_instance)],
    ) -> str:
        assert isinstance(message, Message)
        assert isinstance(middleware_instance, MyInstance)
        assert handler_instance is middleware_instance
        return "handle"

    depend_tool.container_manager.scope_registry = scope_registry
    middleware_register(["message"])
    my_dispatcher.message.outer_middleware(user_middleware)

    assert scope_registry.get_scope(get_instance) is Scope.REQUEST
    assert await my_dispatcher.message_update() == "handle"
    assert await my_dispatcher.message_update() == "handle"
    assert len(instance_manager.instances) == 2
