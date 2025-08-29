### How does it work?   

Now I will tell you the basic principle of operation of the request limiter for the handler.

- All the logic of the work is concentrated in the Limit class, inherited from Filter.

When this filter is called, the key is immediately determined, which will save the time after which the handler will become available for the call. 

- The key looks like this: `user_telegram_id@handler_name` or `users@handler_name`

After the key is determined, the time is obtained from the `AbstractStorage`. If such a key did not exist, then the time for this key is saved and the handler call is allowed. If the saved time exceeds the value of the current time, then calling the handler will be prohibited and `answer_callback` will be called (if it was passed to the `Limit` class or to the 'setup_limit_tool` function). If the value of the current time is greater than the saved time of the previous call, the handler call will be resolved and the new time will be saved using the specified key.

> [!CAUTION]
> The name of each handler must be unique. The answer to the question: 
> "Why should the name be unique?" you will find it if you read the text at the top."


> [!CAUTION]
> If you are launching a bot via a webhook, you do not need to call the `feed_update` method from the `Dispatcher` class 
> pass the named argument `dispatcher=instance of the Dispatcher class'.


### Documentation

`function: setup_limit_tool`
        
        arguments:
            dispatcher: Dispatcher - (required)
            storage: AbstractStorage - (default MemoryStorage)
            answer_callback: AnswerCallback - (default None)

        This function stores the 'storage' and 'answer_callback' attributes in an instance of the dispatcher class. 
        The subsequent acquisition of these attributes takes place in the magic method '__call__' of the 'Limit' class.


`class: Limit`

        arguments:
            seconds: float - (default 0)
            minutes: float - (default 0)
            hours: float - (default 0)
            days: float - (default 0)
            all_users: bool - (default False)
            storage: AbstractStorage - (default None)
            answer_callback: AnswerCallback - (default None)

        This class allows you to create time limits for handler calls. 

        Documentation of arguments:

        1. When transmitting the argument(s) 'storage' or 'answer_callback'
        the 'storage' or 'answer_callback'
        passed to 'setup_limit_tool' is redefined. NOT globally, but only during instance invocation
        the class passed to the handler filter. 
        
        2. The all_users attribute restricts
        using a handler for ALL users.


`class: AnswerCallback`

        arguments:
            obj: Callable[[TelegramObject, timedelta, datetime], Any]

        The class is called when the time limit is triggered. It
        allows you to create a custom response to the user. 

        Documentation of arguments:

        1. The 'obj' attribute can be sync/async func, callable class

        2. Arguments of 'obj':
            TelegramObject - event type
            timedelta is the time set during initialization of the 'Limit' class.
            datetime is the time until the next handler execution.


`class: RedisStorage`

        arguments:
            redis: Redis

        This class allows you to store handler restriction data in Redis. The 'redis' attribute
        accepts an instance of the class from the 'redis' library. 'from redis.asyncio import Redis'


[All code examples can be found here](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/)