from typing import Any

from aiogram.filters import Filter

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.exceptions import InvalidDependencyError
from aiogram_tool.tools.depend.utils.resolver import Resolver

from .exit import DependExit


class DependFilter(Filter):
    """This class allows invoking a dependency at the filter level."""

    def __init__(self, *dependencies: From) -> None:
        for dep in dependencies:
            if not isinstance(dep, From):
                raise InvalidDependencyError(f"Invalid type in dependency {dep}")

        self._dependencies = dependencies

    def get_resolver(self, data: dict[str, Any]) -> Resolver:
        if "resolver" not in data:
            raise ValueError("Resolver not found in data")
        return data["resolver"]

    async def __call__(self, *args, **kwargs) -> bool:
        resolver = self.get_resolver(kwargs)
        for depend in self._dependencies:
            try:
                await resolver.resolve(
                    func=depend.depend, scope=depend.scope, middleware_data=kwargs
                )
            except DependExit:
                return False
        return True
