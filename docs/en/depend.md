### Documentation


`function: setup_depend_tool`

    arguments:
        dp: Dispatcher - (required)
        dependency_override: dict[str, Depend] - (default {})
        allowed_updates: list[str] - (default [])

    This function adds DependInnerMiddleware to each event.


`class: Depend`

    arguments:
        obj: Callable - (required)

    This class allows you to add a dependency to the handler.


> [!TIP]
> If a dependency has an argument that has a default value, then
> this default value will be passed when calling the dependency.
> Examples:
> `async def dependency(flag: bool = True)` - When calling the dependency, flag will receive the True argument.
> `async def dependency(event: TelegramObject)` - Arguments that do not have a default value receive the value from `middleware_data`.
> It is also possible to pass `Depend` via a default value: `async def func(dep: Any = Depend(some_dep))`.


`class: DependExit`

    arguments:
        event: TelegramObject | None - (default None)
        **event_kwargs

    If the dependency returns this class, the handler will not be called.

    This class has a method 'event_answer', which calls the 'answer' method of 'event'.
    **event_kwargs, passed as named arguments to the 'answer' method.
    If you do not pass the 'event' argument, the user will not know why the handler was not called.


`class: DependHandler`

    arguments:
        *dependencies: Depend - (required)

    This class provides the ability to call dependencies before calling the handler.
    The best practice is to return DependExit from the dependency passed to 'dependencies', in which case the handler will NOT be called.
    Please note! HandlerDepend does not provide the ability to pass dependencies as arguments to the handler.


`class: Scope`

    arguments:
        null

    This class allows you to add a dependency scope.
    APP - the dependency result is cached for the entire duration of the application
    REQUEST - the dependency is called each time during a request to the handler


`function: dependency_scope`

    arguments:
        scope: Scope

    This function adds a dependency scope. By default, each dependency has a scope REQUEST.


[All code examples can be found here](https://github.com/shayzi3/aiogram_tool/blob/master/examples/depend/)