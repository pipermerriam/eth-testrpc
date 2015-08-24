# Adapted from http://github.com/ethereum/pyethapp/
from ethereum.utils import is_string, is_numeric, int_to_big_endian, encode_hex

def decode_number(data):
    """Decode `data` representing a number."""
    if hasattr(data, '__int__'):
        return data
    elif not is_string(data):
        success = False
    elif not data.startswith('0x'):
        success = False  # must start with 0x prefix
    elif len(data) > 3 and data[2] == '0':
        success = False  # must not have leading zeros (except `0x0`)
    else:
        data = data[2:]
        # ensure even length
        if len(data) % 2 == 1:
            data = '0' + data
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
    return '0x' + (encode_hex(data).lstrip('0') or '0')


def encode_address(address):
    assert len(address) in (20, 0)
    return '0x' + encode_hex(address)


def encode_data(data, length=None):
    """Encode unformatted binary `data`.

    If `length` is given, the result will be padded like this: ``quantity_encoder(255, 3) ==
    '0x0000ff'``.
    """
    s = encode_hex(data)
    if length is None:
        return '0x' + s
    else:
        return '0x' + s.rjust(length * 2, '0')


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

