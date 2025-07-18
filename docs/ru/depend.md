Документация ддля Depend

### sync_function: `setup_limit_tool`
*arguments*:

        dispatcher:
            экземпляр класса Dispacher из aiogram

        dependency_override:
            Замена одной зависимости на другую

        allowed_updates:
            Список observers для добавления DependMiddleware

        middleware: 
            Использование middleware для пробрасывания зависимостей

- Example [dependency_override](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/override_depend.py)


### class: `Depend`
Класс для подключения зависимости

*arguments*:

        obj:
            callable объект, принимающий только аргументы из MiddlewareData, а также event: TelegramObject. 
            Также имеется поддержка классов с методом __call__

- Example [sub dependencies](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/sub_depend.py)
- Example [default usage](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/default.py)
- Example [sync generators](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/sync_generator.py)
- Example [async generators](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/async_generator.py)
- Example [arguments in obj](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/arguments.py)
- Example [callable classes](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/callable_class.py)



### class: `DependFilter`
Класс позволяющий пробрасывать зависимости при помощи фильтра

- Example [depend filter](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/depend_filter.py)
