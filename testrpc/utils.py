import sys
import functools

from rlp.utils import (
    int_to_big_endian,
    encode_hex,
)
from ethereum.utils import (
    is_string,
    is_numeric,
)


if sys.version_info.major == 2:
    str_to_bytes = str

    def is_any_string_type(value):
        return isinstance(value, basestring)  # NOQA  py3 doesn't have basestr
else:
    def str_to_bytes(value):
        if isinstance(value, bytearray):
            value = bytes(value)
        if isinstance(value, bytes):
            return value
        return bytes(value, 'utf-8')

    def is_any_string_type(value):
        return isinstance(value, (bytes, str))


def decode_number(data):
    """Decode `data` representing a number."""
    if hasattr(data, '__int__'):
        return data
    elif not is_string(data):
        success = False
    elif not data.startswith('0x'):
        success = False  # must start with 0x prefix
    elif len(data) > 3 and data[2] == b'0':
        success = False  # must not have leading zeros (except `0x0`)
    else:
        data = data[2:]
        # ensure even length
        if len(data) % 2 == 1:
            data = b'0' + data
        try:
            return int(data, 16)
        except ValueError:
            success = False
    assert not success
    raise Exception('Invalid number encoding: %s' % data)


def encode_number(i):
    """Encode interger quantity `data`."""
    assert is_numeric(i)
    data = int_to_big_endian(i)
    return b'0x' + (encode_hex(data).lstrip(b'0') or b'0')


def encode_address(address):
    assert len(address) in (20, 0)
    return b'0x' + encode_hex(address)


def encode_data(data, length=None):
    """Encode unformatted binary `data`.

    If `length` is given, the result will be padded like this: ``quantity_encoder(255, 3) ==
    '0x0000ff'``.
    """
    s = encode_hex(data)
    if length is None:
        return b'0x' + s
    else:
        return b'0x' + s.rjust(length * 2, '0')


def encode_loglist(loglist):
    """Encode a list of log"""
    # l = []
    # if len(loglist) > 0 and loglist[0] is None:
    #     assert all(element is None for element in l)
    #     return l
    result = []
    for l in loglist:
        result.append({
            'logIndex': encode_number(l['log_idx']),
            'transactionIndex': encode_number(l['tx_idx']),
            'transactionHash': encode_data(l['txhash']),
            'blockHash': encode_data(l['block'].hash),
            'blockNumber': encode_number(l['block'].number),
            'address': encode_address(l['log'].address),
            'data': encode_data(l['log'].data),
            'topics': [encode_data(int_to_big_endian(topic), 32) for topic in l['log'].topics],
            'type': 'pending' if l['pending'] else 'mined'
        })
    return result


def strip_0x(value):
    if value and value.startswith(b'0x'):
        return value[2:]
    return value


def force_obj_to_bytes(obj, skip_unsupported=False):
    if is_any_string_type(obj):
        return str_to_bytes(obj)
    elif isinstance(obj, dict):
        return {
            k: force_obj_to_bytes(v) for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple)):
        return type(obj)(force_obj_to_bytes(v) for v in obj)
    elif not skip_unsupported:
        raise ValueError("Unsupported type: {0}".format(type(obj)))


def coerce_args_to_bytes(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        bytes_args = force_obj_to_bytes(args)
        bytes_kwargs = force_obj_to_bytes(kwargs)
        return fn(*bytes_args, **bytes_kwargs)
    return inner
