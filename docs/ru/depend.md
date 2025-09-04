### Документация


`function: setup_depend_tool`

    arguments: 
        dp: Dispatcher - (required)
        dependency_override: dict[str, Depend] - (default {})
        allowed_updates: list[str] - (default [])

    Данная функция добавляет DependInnerMiddleware каждому событию.


`class: Depend`

    arguments: 
        obj: Callable - (required)

    Данный класс позволяет добавить зависимость в обработчик.


`class: DependExit`

    arguments:
        event: TelegramObject | None - (default None)
        **event_kwargs

    Если зависимость возвращает этот класс, то обработчик не будет вызван. 
    Данный класс имеет метод 'event_answer', который вызывает метод 'answer' у 'event'. 
    **event_kwargs, передаются в виде именовынных аргументов в метод 'answer'. 
    Если не передать аргумент 'event', то пользователь не узнает, почему обработчик не был вызван.


`class: DependHandler`

    arguments:
        *dependencies: Depend - (required)

    Этот класс предоставляет возможность вызывать зависимости до вызова обработчика. 
    Лучшая практика это из зависимости, переданной в 'dependencies', возвращать DependExit, в таком случае обработчик вызван НЕ будет. 
    Обратите внимание! HandlerDepend не даёт возможности передавать зависимости в качестве аргументов в обработчик.


`class: Scope`
    
    arguments:
        null

    Данный класс позволяет добавить scope зависимости.
    APP - результат зависимости кэшируется на всё время работы приложения
    REQUEST - зависимость вызывается каждый раз во время запроса к обработчику


`function: dependency_scope`

    arguments:
        scope: Scope

    Данная функция добавляет scope зависимости.
    По умолчанию каждая зависимость имеет scope REQUEST.


[Со всеми примерами кода можно ознакомиться здесь](https://github.com/shayzi3/aiogram_tool/blob/master/examples/depend/)