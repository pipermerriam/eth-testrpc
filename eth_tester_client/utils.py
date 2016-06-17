import sys
import functools

from ethereum import utils as ethereum_utils


if sys.version_info.major == 2:
    str_to_bytes = str

    def is_any_string_type(value):
        return isinstance(value, basestring)

else:
    def str_to_bytes(value):
        if isinstance(value, bytearray):
            value = bytes(value)
        if isinstance(value, bytes):
            return value
        return bytes(value, 'utf-8')

    def is_any_string_type(value):
        return isinstance(value, (bytes, str))


def force_args_to_bytes(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bytes_args = tuple((
            str_to_bytes(arg) if is_any_string_type(arg) else arg
            for arg in args
        ))
        bytes_kwargs = {
            key: str_to_bytes(value) if is_any_string_type(value) else value
            for key, value in kwargs.items()
        }
        return func(*bytes_args, **bytes_kwargs)
    return wrapper


def strip_0x(value):
    if value and value.startswith(b'0x'):
        return value[2:]
    return value


def encode_hex(value):
    return b"0x" + ethereum_utils.encode_hex(value)


def int_to_hex(value):
    if value == 0:
        return hex(0)
    return ethereum_utils.int_to_hex(value)
