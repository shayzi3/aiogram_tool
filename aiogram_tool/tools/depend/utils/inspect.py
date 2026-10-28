import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

from aiogram_tool.tools.depend.depend import From


@dataclass(frozen=True)
class InspectArgument:
    name: str
    kind: inspect._ParameterKind
    depend: From | None
    default: Any


def get_arguments(obj: Callable) -> list[InspectArgument]:
    signature = inspect.signature(obj)
    return [
        InspectArgument(
            name=param.name,
            kind=param.kind,
            depend=_find_depend(param),
            default=param.default,
        )
        for param in signature.parameters.values()
    ]


def _find_depend(param: inspect.Parameter) -> From | None:
    if get_origin(param.annotation) is Annotated:
        for meta in get_args(param.annotation)[1:]:
            if isinstance(meta, From):
                return meta
    if isinstance(param.default, From):
        return param.default
    return None
