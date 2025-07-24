# Documentation for Limit

`Warning!`
`Each handler function name you add a filter to must be unique.`

### sync function: `setup_limit_tool`
*arguments*:

    dispatcher:
        an instance of the Dispatcher class from aiogram

    storage:
        MemoryStorage() by default. 
        There is also RedisStorage support.
        
    answer_callback:
        asynchronous function called at the moment
        when the user has reached the limit to use the command.

        Important! The function takes 3 arguments as input:
            event: TelegramObject
            time: timedelta - restriction on the use of the command
            lost_time: datetime is the time until reuse.

        The names of the arguments can be arbitrary.


#### [Example RedisStorage](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/storage.py)
#### [Example answer_callback](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/answer_callback.py)


### class: `Limit`
*arguments*:

    Time:
        seconds
        minutes
        hours
        days
    
    all_users:
        Sets a team limit for all bot users

    storage:
        Redefining what was set in setup_limit_tool

    answer_callback:
        Redefining what was set in setup_limit_tool