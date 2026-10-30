import inspect
from collections.abc import Callable
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    asynccontextmanager,
)
from typing import Any, TypeVar

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.enums import Scope
from aiogram_tool.tools.depend.types.exceptions import (
    ContextManagerError,
    DependRecursionError,
    InvalidMiddlewareDataArgumentError,
    UnsupportedParameterKindError,
)
from aiogram_tool.tools.depend.utils.container_manager import ContainerTransaction
from aiogram_tool.tools.depend.utils.inspect import get_arguments
from aiogram_tool.types import _MISSING, _MissingType

T = TypeVar("T")

_UNSUPPORTED_KINDS = (
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.VAR_POSITIONAL,
    inspect.Parameter.VAR_KEYWORD,
)


class Resolver:
    def __init__(self, container_transaction: ContainerTransaction) -> None:
        self.container_transaction = container_transaction

    async def resolve_handler(
        self, handler: Callable[..., T], middleware_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return await self.build_kwargs(
            func=handler, only_depend=True, middleware_data=middleware_data
        )

    async def resolve(
        self,
        func: Callable[..., T],
        scope: Scope | _MissingType = _MISSING,
        middleware_data: dict[str, Any] | None = None,
    ) -> T:
        return await self._get_depend(
            depend=From(depend=func, scope=scope),
            chain=(),
            middleware_data=middleware_data,
        )

    async def build_kwargs(
        self,
        func: Callable,
        chain: tuple[Callable, ...] = (),
        only_depend: bool = False,
        middleware_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if middleware_data is None:
            middleware_data = {}

        kwargs: dict[str, Any] = {}
        for argument in get_arguments(func):
            if argument.depend is not None or argument.name in middleware_data:
                if argument.kind in _UNSUPPORTED_KINDS:
                    raise UnsupportedParameterKindError(
                        f"Unsupported parameter kind {argument.kind} in {func},"
                        f" param {argument.name}"
                    )

            if argument.depend is not None:
                kwargs[argument.name] = await self._get_depend(
                    depend=argument.depend,
                    chain=chain,
                    middleware_data=middleware_data,
                )
            elif argument.name in middleware_data and only_depend is False:
                kwargs[argument.name] = middleware_data[argument.name]
            elif argument.default is inspect.Parameter.empty and only_depend is False:
                raise InvalidMiddlewareDataArgumentError(
                    f"Argument {argument.name} of {func} not found in middleware data"
                )
        return kwargs

    async def _get_depend(
        self,
        depend: From,
        chain: tuple[Callable, ...],
        middleware_data: dict[str, Any] | None = None,
    ) -> Any:
        depend = self.container_transaction.manager.dependency_override.get(
            depend.depend, depend
        )
        scope_object = (
            self.container_transaction.manager.scope_registry.get_scope_object(depend)
        )
        if scope_object.depend in chain:
            raise DependRecursionError(f"Recursion detected: {scope_object.depend}")

        kwargs = await self.build_kwargs(
            func=scope_object.depend,
            chain=(*chain, scope_object.depend),
            middleware_data=middleware_data,
        )

        registry = self.container_transaction.registry_transaction
        async with await registry.lock(
            key=scope_object.depend, scope=scope_object.scope
        ):
            cached = await registry.get_value(
                func=scope_object.depend, scope=scope_object.scope
            )
            if cached is not _MISSING:
                return cached

            value = await self._invoke(scope_object.depend, kwargs, scope_object.scope)
            await registry.set_value(
                func=scope_object.depend,
                scope=scope_object.scope,
                depend_result=value,
            )
            return value

    async def _invoke(
        self, func: Callable, kwargs: dict[str, Any], scope: Scope
    ) -> Any:
        stack = self.container_transaction.stack_transaction

        if inspect.isgeneratorfunction(func):
            raise ContextManagerError(
                "Only async dependencies are supported."
                " Use async def or @asynccontextmanager."
            )
        if inspect.isasyncgenfunction(func):
            cm = asynccontextmanager(func)(**kwargs)
            return await stack.enter_async_context(context_manager=cm, scope=scope)

        result = func(**kwargs)
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, AbstractAsyncContextManager):
            return await stack.enter_async_context(context_manager=result, scope=scope)
        if isinstance(result, AbstractContextManager):
            raise ContextManagerError(
                "Only async dependencies are supported."
                " Use async def or @asynccontextmanager."
            )
        return result
