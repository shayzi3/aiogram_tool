### How does it work?

The `LongCallbackData` class inherits from the aiogram `CallbackData` class
and overrides two methods of the parent class. The first method is `pack`, it
overrides it in order to catch an error about too many characters.
If there is no error, then the result of the parent `pack` method is returned, if there is,
then a unique identifier is generated, which will be the key, and the value will be
an instance of the class you created, after that the unique identifier will be saved in the `callback_data` attribute of the `InlineKeyboardButton` class. What's next? And then the second
overridden `filter` method comes into play, it returns an instance of the `LongCallbackQueryFilter` class.
Now more details about `LongCallbackQueryFilter`. This class inherits the class
from aiogram `CallbackQueryFilter`. First of all, our class is a filter, which means it has a magic method `__call__`. What happens in it? The condition is checked that `callback_data` contains the identifier key, if so, then an instance of your 'long' `callback_data` is taken from memory storage, and then the filters are checked.


### Documentation


> [!TIP]
> You don't need to inherit `LongCallbackData` in every class, inherit it only in those
> classes in which the number of allowed characters will be exceeded. This will make the code clearer.


> [!TIP]
> When you restart the application, the buttons that contained the serialized class `UniqueIDCallbackData`
> will stop working and when you click on them, the message 'Button expired' will appear.


`class: UniqueIDCallbackData`

     arguments:
          mode: str = "__unique_id_callback"
          unique_id: str

     This class is saved serialized in the callback_data attribute of the InlineKeyboardButton class,
     where initially in the passed class there was an excess of characters. An instance of the original class
     is saved as a value in memory storage, where the key is unique_id.


`class: LongCallbackQueryFilter`

     arguments:
          null

     This class is a filter. Its main task is to check if there is a '__unique_id_callback' string in the callback_data and if it is, then an instance of the class is taken from memory storage on which the specified filters are already checked and, accordingly, this class
     is passed to the callback_data handler argument.


`class: LongCallbackData`

     arguments:
          null

     This class inherits from CallbackData. If you have a class that will exceed 64 characters when serialized, 
     then feel free to inherit the LongCallbackData class.

[All code examples can be found here](https://github.com/shayzi3/aiogram_tool/blob/master/examples/callback_data/)