### LongCallbackData — длинные callback_data

Telegram ограничивает размер атрибута `callback_data` инлайн-кнопки **64 байтами**.
Если сериализованные данные превышают этот лимит, aiogram выбрасывает ошибку
`ValueError: Resulted callback data is too long!`.

`LongCallbackData` решает эту проблему: слишком «длинные» данные автоматически
сохраняются в хранилище, а в кнопку упаковывается короткий уникальный идентификатор.
Когда пользователь нажимает на кнопку, данные прозрачно восстанавливаются из
хранилища — API остаётся таким же, как у стандартного `CallbackData` в aiogram.


### Как это работает?

Класс `LongCallbackData` наследуется от класса из aiogram `CallbackData` и
добавляет метод `pack_long`, а также переопределяет метод `filter`.

**1. Упаковка — метод `pack_long`**

Метод сначала пытается упаковать данные обычным способом (родительский `pack`).
Если данные помещаются в 64 байта — возвращается обычный результат, и никакой
дополнительной логики не выполняется. Если же перехвачена ошибка
`data is too long!`, то:

- генерируется уникальный идентификатор (класс `_UniqueIDCallbackData`);
- сериализованный экземпляр вашего класса сохраняется в `_storage` под ключом
  `aiot_callback_data@<unique_id>`;
- в атрибут `callback_data` класса `InlineKeyboardButton` упаковывается
  уникальный идентификатор вместо «длинных» данных.

**2. Обработка нажатия — метод `filter`**

Метод `filter` возвращает экземпляр класса `LongCallbackQueryFilter` — наследника
класса из aiogram `CallbackQueryFilter`. В магическом методе `__call__` происходит
следующее:

1. Проверяется, что событие — это `CallbackQuery` и `query.data` не пустое.
2. Данные пытаются распаковаться как `_UniqueIDCallbackData`. Если это не удалось,
   данные распаковываются как обычный `callback_data` (короткие данные работают
   точно так же, как в стандартном aiogram).
3. Если данные оказались `_UniqueIDCallbackData`, проверяется совпадение префикса,
   затем из хранилища `_storage` достаётся сохранённая «длинная» `callback_data`.
4. Если данных в хранилище нет (например, бот был перезапущен), вызывается
   `_answer_callback` (по умолчанию — alert «Button expired»), и фильтр возвращает `False`.
5. Если данные найдены, они распаковываются в экземпляр вашего класса, к нему
   применяется правило `rule` (MagicFilter), и при успехе в обработчик передаётся
   `callback_data` — полноценный экземпляр вашего класса.


### Быстрый старт

```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_tool.tools.callback_data import LongCallbackData

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Определяем класс callback data, наследуясь от LongCallbackData
class MyLongData(LongCallbackData, prefix="mydata"):
    mode: str
    payload: str


@dp.message(CommandStart())
async def start_handler(message: Message):
    # Короткие данные упаковываются как обычно
    short_cb = await MyLongData(mode="short", payload="Hello!").pack_long()

    # «Длинные» данные (больше 64 байт) автоматически сохраняются в хранилище
    long_cb = await MyLongData(mode="long", payload="A" * 200).pack_long()

    await message.answer(
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Короткие данные", callback_data=short_cb)],
            [InlineKeyboardButton(text="Длинные данные", callback_data=long_cb)],
        ]),
    )


# Фильтры работают точно так же, как в стандартном aiogram
@dp.callback_query(MyLongData.filter(F.mode == "long"))
async def process_long_data(query: CallbackQuery, callback_data: MyLongData):
    # Исходные данные доступны полностью, несмотря на лимит Telegram
    await query.answer(text=f"Длина payload: {len(callback_data.payload)}")
```


### Документация

> [!TIP]
> Короткие данные (которые помещаются в 64 байта) упаковываются методом `pack_long`
> как обычно, без обращения к хранилищу. То есть `pack_long` можно использовать
> всегда — накладных расходов на коротких данных не будет.

> [!CAUTION]
> По умолчанию используется `MemoryStorage`. При перезапуске приложения кнопки,
> содержавшие «длинные» данные, перестанут работать: при нажатии пользователь
> получит сообщение «Button expired». Чтобы данные переживали перезапуск,
> используйте `AsyncRedisStorage` или `FileStorage` (см. раздел «Хранилища»).

> [!CAUTION]
> Префикс вашего класса не должен быть слишком длинным: помимо префикса в
> `callback_data` упаковывается уникальный идентификатор, которому требуется
> минимум 6 байт (12 hex-символов). При слишком длинном префиксе будет выброшено
> исключение `ValueError`.


`class: LongCallbackData(CallbackData, prefix="?")`

    Класс для работы с «длинными» callback data. Наследуйте его своим классам
    с префиксом, как у обычного CallbackData, — остальное произойдёт автоматически.

    атрибуты класса (ClassVar):

        _storage: BaseStorage - (default MemoryStorage)
            Хранилище, в которое сохраняются «длинные» значения.
            Переопределите, чтобы использовать Redis, файлы и т.д.

        _answer_callback: CallbackDataAnswer - (default CallbackDataAnswer())
            Вызывается, если данные кнопки не найдены в хранилище
            (например, после перезапуска бота).

    методы:

        async pack_long() -> str
            Пытается упаковать данные родительским методом pack. Если данные
            помещаются в 64 байта — возвращается обычный результат. Если перехвачена
            ошибка «data is too long!», данные сохраняются в _storage, а в кнопку
            упаковывается уникальный идентификатор.

        classmethod filter(rule: MagicFilter | None = None) -> LongCallbackQueryFilter
            Возвращает фильтр, совместимый со стандартным CallbackData.filter().
            Аргумент rule — необязательное MagicFilter-правило (например, F.mode == "long").


`class: CallbackDataAnswer`

    arguments:
        null

    Вызывается, когда callback_data кнопки не найдена в хранилище
    («кнопка истекла»). По умолчанию показывает alert с текстом «Button expired».

    Чтобы задать своё поведение, унаследуйте класс и переопределите __call__:

        class MyExpiredAnswer(CallbackDataAnswer):
            async def __call__(self, query: CallbackQuery) -> None:
                await query.message.answer("Кнопка устарела, отправьте /start заново.")
                await query.answer()


`class: LongCallbackQueryFilter(CallbackQueryFilter)`

    arguments:
        callback_data: type[LongCallbackData]
        rule: MagicFilter | None - (default None)

    Фильтр, возвращаемый методом LongCallbackData.filter(). Распаковывает как
    обычные, так и «длинные» callback data, достаёт данные из хранилища,
    применяет правило rule и передаёт экземпляр вашего класса в обработчик
    через аргумент callback_data.


`class: _UniqueIDCallbackData(CallbackData, prefix="UIDPR")` — внутренний

    arguments:
        unique_id: str
        callback_data_prefix: str

    Сериализуется в атрибут callback_data класса InlineKeyboardButton вместо
    «длинных» данных. Уникальный идентификатор генерируется через secrets.token_hex,
    его длина рассчитывается так, чтобы общий размер укладывался в 64 байта.
    Ключ в хранилище: aiot_callback_data@<unique_id>.


### Хранилища

Хранилище задаётся атрибутом класса `_storage` и должно реализовывать интерфейс
`BaseStorage` (методы `set_value` и `get_value`).

| Хранилище | Персистентность | Особенности |
|---|---|---|
| `MemoryStorage` / `MemoryLockStorage` | В памяти | По умолчанию; данные теряются при перезапуске |
| `AsyncRedisStorage` / `AsyncRedisLockStorage` | Redis | Переживают перезапуск; TTL через аргумент `expire` |
| `FileStorage` / `FileLockStorage` | Локальный файл | Данные переживают перезапуск |

Пример с Redis (данные живут 1 час и переживают перезапуск бота):

```python
from redis.asyncio import Redis as AsyncRedis
from aiogram_tool.storage import AsyncRedisLockStorage

redis_storage = AsyncRedisLockStorage(
    redis=AsyncRedis(host="localhost", port=6379, decode_responses=True),
    expire=3600,
)

class PersistentData(LongCallbackData, prefix="redis"):
    _storage = redis_storage

    user_id: int
    big_context: str
```


[Со всеми примерами кода можно ознакомиться здесь](examples/callback_data/)
