Documentation for Depend

`Warning!`
`When registering other middleware, it is important to pay attention to this,
so that the latter is executed by DependMiddleware`.

`Example:`
```python

dp.message.middleware(OneMiddleware())
dp.message.middleware(TwoMiddleware())

setup_depend_tool(dispatcher=dp)
```

### sync_function: `setup_limit_tool`
*arguments*:

          dispatcher:
               The class management module from the aiogram

          dependency_override:
               Replacing one dependency with another

          allowed updates:
               A list of observers for adding dependent software

          middleware: 
               using middleware to ensure dependency

- Example [dependency_override](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/override_depend.py)


### class: `Depend`
A class for enabling dependency

*arguments*:

          obj:
               A callable object that receives a lot of information from intermediate data, for example, an event: A Telegram object. 
               There is also class support using the __call__

- Example [dependencies](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/sub_depend.py)
- Example [default usage](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/default.py)
- Example [sync generators](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/sync_generator.py)
- Example [async generators](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/async_generator.py)
- Example [arguments in obj](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/arguments.py)
- Example [callable classes](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/callable_class.py)



### class: `DependFilter`
A class that allows you to skip dependencies using a filter

- Example [dependent filter](https://github.com/shayzi3/aiogram_tool/tree/master/examples/depend/depend_filter.py)