# Документация для Limit

### sync function: `setup_limit_tool`
*arguments*:

    dispatcher: 
        экземпляр класса Dispacher из aiogram

    storage:
        MemoryStorage() по умолчанию. 
        Также есть поддержка RedisStorage
        
    answer_callback:
        асинхронная функция вызываемая в момент, 
        когда у пользователя кончился лимит 
        на использование команды.

        Важно! На вход функция принимает 3 аргумента:
            message: Message
            time: timedelta - ограничение на использование команды
            lost_time: datetime - время до повторного использования

        Имена аргументов могут быть произвольными.


#### [Example RedisStorage](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/storage.py)
#### [Example answer_callback](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/answer_callback.py)


### class: `Limit`
*arguments*:
    
    Время:
        seconds
        minutes
        hours
        days
    
    all_users: 
        Устанавливает ограничение команды для всех пользователей бота

    storage:
        Переопределение того, что было установлено в setup_limit_tool

    answer_callback:
        Переопределение того, что было установлено в setup_limit_tool