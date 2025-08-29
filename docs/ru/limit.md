### Как это работает?   

Сейчас я расскажу основной принцип работы ограничителя запросов для обработчика.

- Вся логика работы сосредочена в классе Limit, наследующийся от Filter.

Когда происходит вызов этого фильтра, то сразу определяется ключ, по которому сохранится время, по истечении которого обработчик станет доступен для вызова. 

- Ключ выглядит так: `user_telegram_id@handler_name` или `users@handler_name`

После определения ключа, происходит получение времени из `AbstractStorage`. Если такого ключа не существовало, то сохраняется время по данному ключу и вызов обработчика разрешается. Если сохранённое время превышает значение текущего времени, то вызов обработчика будет запрещён и будет вызван `answer_callback`(если он был передан в класс `Limit` или в функцию `setup_limit_tool`). В случае если значение текущего времени больше сохранённого времени предыдущего вызовы вызов обработчика будет разрешён и сохранится новое время по заданному ключу.

> [!CAUTION]
> Имя каждого обработчика должно быть уникальным. Ответ на вопрос: 
> "Почему имя должно быть уникальным?" вы найдёте, если прочитаете текст сверху."


> [!CAUTION]
> Если вы запускаете бота через webhook, вам необоходимо при вызове метода `feed_update` из класса `Dispatcher` 
> передать именовынный аргумент `dispatcher=экземпляр класса Dispatcher`.


### Документация

`function: setup_limit_tool`
        
        arguments:
            dispatcher: Dispatcher - (required)
            storage: AbstractStorage - (default MemoryStorage)
            answer_callback: AnswerCallback - (default None)

        Данная функция в экземпляр класса dispatcher сохраняет атрибуты 'storage' и 'answer_callback'. 
        Последующее получение этих атрибутов происходит в магическом методе '__call__' класса 'Limit'.


`class: Limit`

        arguments:
            seconds: float - (default 0)
            minutes: float - (default 0)
            hours: float - (default 0)
            days: float - (default 0)
            all_users: bool - (default False)
            storage: AbstractStorage - (default None)
            answer_callback: AnswerCallback - (default None)

        Этот класс позволяет создавать временные ограничения для вызовы обработчика. 

        Документация аргументов:

        1. При передачи аргумент(а/ов) 'storage' или 'answer_callback'
        переопределяется 'storage' или 'answer_callback', 
        переданный в 'setup_limit_tool'. НЕ глобально, а только во время вызова экземпляра
        класса, переданного в фильтр обработчика. 
        
        2. Атрибут all_users даёт ограничение на
        использование обработчика для ВСЕХ пользователей.


`class: AnswerCallback`

        arguments:
            obj: Callable[[TelegramObject, timedelta, datetime], Any]

        Класс вызывается, когда срабатывает ограничение по времени. Он
        позволяет создать кастомный ответ пользователю. 

        Документация аргументов:

        1. Атрибут 'obj' может быть sync/async func, callable class

        2. Аргументы 'obj':
            TelegramObject - тип события
            timedelta - время, заданное при инициализации класса 'Limit'.
            datetime - время до следующего выполнения обработчика.


`class: RedisStorage`

        arguments:
            redis: Redis

        Класс позволяет хранить данные о ограничении обработчиков в Redis. Атрибут 'redis'
        принимает экземпляр класса из библиотеки 'redis'. 'from redis.asyncio import Redis'


[Со всеми примерами кода можно ознакомиться здесь](https://github.com/shayzi3/aiogram_tool/blob/master/examples/limit/)