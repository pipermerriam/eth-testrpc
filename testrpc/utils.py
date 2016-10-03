def normalize_number(value):
    try:
        return int(value, 16)
    except TypeError:
        return int(value)


def normalize_block_number(value):
    try:
        return normalize_number(value)
    except ValueError:
        return value


def noop(value):
    return value


TXN_KWARGS_MAP = {
    'from': '_from',
    'gasPrice': 'gas_price',
}


TXN_FORMATTERS = {
    'value': normalize_number,
    'gas': normalize_number,
    'gasPrice': normalize_number
}


def input_transaction_formatter(transaction):
    return {
        TXN_KWARGS_MAP.get(k, k): TXN_FORMATTERS.get(k, noop)(v)
        for k, v in transaction.items()
    }
