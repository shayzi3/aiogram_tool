### How does it work?

- Does not work through middleware because:

    - Inner middleware. It does not support MiddlewareData transfer between each other. If you have several inner middleware registered, then DependMiddleware must be executed last in order to successfully transfer dependencies to the handler.

    - Outer middleware. The problem here is that the outer middleware call occurs before all filters are processed for the handlers of a certain event. The 'handler' key in the MiddlewareData passed to the outer middleware is not defined, which means that dependency injection will not be possible if there is no handler.

#### Dependency injection via Filter

It sounds strange, but I'll try to explain.

Since using outer middleware would lead to crutches, it was decided to do everything using the Filter class.

To a person who understands aiogram, this will seem strange, because in the method of the class `aiogram.dispatcher.handler.event.HandlerObject` there is a `check` method that checks all filters from the handler. And this method is called in the method of the `aiogram.dispatcher.event.telegram.TelegramEventObserver.trigger` at the time of iteration for all handlers belonging to the received event.

In simple words: an event arrives, then aiogram searches among the handlers belonging to this event for the one that needs to be called. This search is performed by calling filters for each handler.

The problem is that the `DependFilter` class can be called multiple times if used incorrectly. 

#### Solving the problem

The 'setup_depend_tool` function does this, namely, it adds a `DependFilter' filter to each handler in each event. When the method is `aiogram.dispatcher.event.handler.HandlerObject.check`will iterate over all handler filters, then `DependFilter' will be called most recently. This ensures that all filters passed for verification will be executed earlier and, accordingly, the `DependFilter` will be called when the handler is guaranteed to be suitable.


> [!CAUTION]
> Do not add the `DependFilter` class to the handler filters yourself! 
> This can lead to bad consequences if the transmission is incorrect!


### Documentation


`function: setup_depend_tool`

    arguments: 
        dp: Dispatcher - (required)
        dependency_override: dict[str, Depend] - (default {})
        allowed_updates: list[str] - (default [])

    This function adds a DependFilter filter to each event handler.


`class: Depend`

    arguments: 
        obj: Callable - (required)

    This class allows you to add a dependency to the handler.


`class: DependFilter`
    
    arguments:
        null

    This class processes dependencies and passes them to the handler. 


`class: DependExit`

    arguments:
        event: TelegramObject | None - (default None)
        **event_kwargs

    If the dependency returns this class, the handler will not be called. 
    This class has an 'event_answer' method that calls the 'answer' method for 'event'. 
    **event_kwargs, passed as named arguments to the 'answer' method. 
    If the 'event' argument is not passed, the user will not know why the handler was not called.


`class: DependHandler`

    arguments:
        *dependencies: Depend - (required)

    This class provides the ability to invoke dependencies before calling the handler. 
    The best practice is to return DependExit from the dependency passed to 'dependencies', in which case the handler will NOT be called. 
    Please note! HandlerDepend does not allow passing dependencies as arguments to the handler.


[All code examples can be found here](https://github.com/shayzi3/aiogram_tool/blob/master/examples/depend/)