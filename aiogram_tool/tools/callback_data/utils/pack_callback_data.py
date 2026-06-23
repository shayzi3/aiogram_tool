from aiogram.filters.callback_data import CallbackData


def pack_without_errors(callback_data: CallbackData) -> str:
    """From class CallbackData of aiogram without ValueError"""
    result = [callback_data.__prefix__]
    for key, value in callback_data.model_dump(mode="python").items():
        encoded = callback_data._encode_value(key, value)
        result.append(encoded)
        
    return callback_data.__separator__.join(result)