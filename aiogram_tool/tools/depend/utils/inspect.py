from collections.abc import Callable
from functools import lru_cache
from inspect import Signature, signature
from typing import Annotated, get_args, get_origin

from aiogram_tool.tools.depend.depend import From
from aiogram_tool.tools.depend.types.schema import InspectArgument
from aiogram_tool.tools.depend.utils.scope_registry import ScopeRegistry


@lru_cache(maxsize=1024)
def get_signature(obj: Callable) -> Signature:
    return signature(obj)


def get_arguments(
    obj: Callable,
    scope_registry: ScopeRegistry,
    dependency_override: dict[Callable, From],
) -> list[InspectArgument]:
    signature = get_signature(obj)

    params = []
    for param_name, param_meta in signature.parameters.items():
        if get_origin(param_meta.annotation) is Annotated:
            annotated_metas = get_args(param_meta.annotation)
            for meta in annotated_metas:
                if isinstance(meta, From):
                    meta = dependency_override.get(meta.depend, meta)
                    params.append(
                        InspectArgument(
                            name=param_name,
                            arg_kind=param_meta.kind,
                            value=scope_registry.get_scope_object(depend=meta),
                        )
                    )
                    break

        elif isinstance(param_meta.default, From):
            default = param_meta.default
            default = dependency_override.get(default.depend, default)
            params.append(
                InspectArgument(
                    name=param_name,
                    arg_kind=param_meta.kind,
                    value=scope_registry.get_scope_object(depend=default),
                )
            )

        else:
            params.append(
                InspectArgument(
                    name=param_name, arg_kind=param_meta.kind, value=param_meta.default
                )
            )
    return params
