### LongCallbackData — long callback_data

Telegram limits the size of the `callback_data` attribute of an inline button to **64 bytes**.
If the serialized data exceeds this limit, aiogram raises the error
`ValueError: Resulted callback data is too long!`.

`LongCallbackData` solves this problem: data that is too "long" is automatically
stored in the storage, and a short unique identifier is packed into the button instead.
When the user presses the button, the data is transparently restored from
the storage — the API remains the same as that of the standard `CallbackData` in aiogram.


### How does it work?

The `LongCallbackData` class inherits from the aiogram `CallbackData` class and
adds the `pack_long` method, as well as overrides the `filter` method.

**1. Packing — the `pack_long` method**

The method first tries to pack the data the usual way (the parent `pack`).
If the data fits into 64 bytes, the regular result is returned and no
additional logic is executed. If the `data is too long!` error is caught, then:

- a unique identifier is generated (the `_UniqueIDCallbackData` class);
- the serialized instance of your class is stored in `_storage` under the key
  `aiot_callback_data@<unique_id>`;
- the unique identifier is packed into the `callback_data` attribute of the
  `InlineKeyboardButton` class instead of the "long" data.

**2. Handling a button press — the `filter` method**

The `filter` method returns an instance of the `LongCallbackQueryFilter` class — a descendant
of the aiogram `CallbackQueryFilter` class. In the `__call__` magic method the
following happens:

1. It is checked that the event is a `CallbackQuery` and `query.data` is not empty.
2. The data is attempted to be unpacked as `_UniqueIDCallbackData`. If that fails,
   the data is unpacked as regular `callback_data` (short data works
   exactly the same as in standard aiogram).
3. If the data turned out to be `_UniqueIDCallbackData`, the prefix match is checked,
   then the saved "long" `callback_data` is retrieved from the `_storage`.
4. If the data is not in the storage (for example, the bot was restarted),
   `_answer_callback` is called (by default — an alert "Button expired"), and the filter returns `False`.
5. If the data is found, it is unpacked into an instance of your class, the `rule` (MagicFilter) is applied to it,
   and upon success `callback_data` — a full-fledged instance of your class — is passed to the handler.


### Quick start

```python
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram_tool.tools.callback_data import LongCallbackData

bot = Bot("YOUR_TOKEN_HERE")
dp = Dispatcher()


# Define the callback data class by inheriting from LongCallbackData
class MyLongData(LongCallbackData, prefix="mydata"):
    mode: str
    payload: str


@dp.message(CommandStart())
async def start_handler(message: Message):
    # Short data is packed as usual
    short_cb = await MyLongData(mode="short", payload="Hello!").pack_long()

    # "Long" data (more than 64 bytes) is automatically stored in the storage
    long_cb = await MyLongData(mode="long", payload="A" * 200).pack_long()

    await message.answer(
        "Choose an action:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Short data", callback_data=short_cb)],
            [InlineKeyboardButton(text="Long data", callback_data=long_cb)],
        ]),
    )


# Filters work exactly the same as in standard aiogram
@dp.callback_query(MyLongData.filter(F.mode == "long"))
async def process_long_data(query: CallbackQuery, callback_data: MyLongData):
    # The original data is fully available despite the Telegram limit
    await query.answer(text=f"Payload length: {len(callback_data.payload)}")
```


### Documentation

> [!TIP]
> Short data (which fits into 64 bytes) is packed by the `pack_long` method
> as usual, without accessing the storage. In other words, `pack_long` can be used
> always — there will be no overhead for short data.

> [!CAUTION]
> `MemoryStorage` is used by default. When the application is restarted, buttons
> that contained "long" data will stop working: when pressed, the user
> will receive the "Button expired" message. To make the data survive a restart,
> use `AsyncRedisStorage` or `FileStorage` (see the "Storages" section).

> [!CAUTION]
> The prefix of your class should not be too long: in addition to the prefix, a
> unique identifier is packed into `callback_data`, which requires
> at least 6 bytes (12 hex characters). If the prefix is too long, a
> `ValueError` exception will be raised.


`class: LongCallbackData(CallbackData, prefix="?")`

    A class for working with "long" callback data. Inherit your classes from it
    with a prefix, just like with a regular CallbackData — everything else will happen automatically.

    class attributes (ClassVar):

        _storage: BaseStorage - (default MemoryStorage)
            The storage where "long" values are saved.
            Override it to use Redis, files, etc.

        _answer_callback: CallbackDataAnswer - (default CallbackDataAnswer())
            Called if the button data is not found in the storage
            (for example, after the bot is restarted).

    methods:

        async pack_long() -> str
            Tries to pack the data with the parent pack method. If the data
            fits into 64 bytes, the regular result is returned. If the
            "data is too long!" error is caught, the data is saved to _storage, and a
            unique identifier is packed into the button.

        classmethod filter(rule: MagicFilter | None = None) -> LongCallbackQueryFilter
            Returns a filter compatible with the standard CallbackData.filter().
            The rule argument is an optional MagicFilter rule (for example, F.mode == "long").


`class: CallbackDataAnswer`

    arguments:
        null

    Called when the button's callback_data is not found in the storage
    ("the button has expired"). By default, it shows an alert with the text "Button expired".

    To define your own behavior, inherit the class and override __call__:

        class MyExpiredAnswer(CallbackDataAnswer):
            async def __call__(self, query: CallbackQuery) -> None:
                await query.message.answer("The button has expired, send /start again.")
                await query.answer()


`class: LongCallbackQueryFilter(CallbackQueryFilter)`

    arguments:
        callback_data: type[LongCallbackData]
        rule: MagicFilter | None - (default None)

    The filter returned by the LongCallbackData.filter() method. It unpacks both
    regular and "long" callback data, retrieves the data from the storage,
    applies the rule, and passes an instance of your class to the handler
    via the callback_data argument.


`class: _UniqueIDCallbackData(CallbackData, prefix="UIDPR")` — internal

    arguments:
        unique_id: str
        callback_data_prefix: str

    Serialized into the callback_data attribute of the InlineKeyboardButton class instead of
    the "long" data. The unique identifier is generated via secrets.token_hex,
    its length is calculated so that the total size fits into 64 bytes.
    The key in the storage: aiot_callback_data@<unique_id>.


### Storages

The storage is set by the `_storage` class attribute and must implement the
`BaseStorage` interface (the `set_value` and `get_value` methods).

| Storage | Persistence | Features |
|---|---|---|
| `MemoryStorage` / `MemoryLockStorage` | In memory | Default; data is lost on restart |
| `AsyncRedisStorage` / `AsyncRedisLockStorage` | Redis | Survives restarts; TTL via the `expire` argument |
| `FileStorage` / `FileLockStorage` | Local file | Data survives restarts |

Example with Redis (the data lives for 1 hour and survives bot restarts):

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


[All code examples can be found here](examples/callback_data)