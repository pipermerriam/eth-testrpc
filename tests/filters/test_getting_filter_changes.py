from sha3 import sha3_256


assert sha3_256(b'').hexdigest() == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'


from testrpc.client.utils import (
    force_bytes,
)


class Events(object):
    LogAnonymous = 0
    LogNoArguments = 1
    LogSingleArg = 2
    LogDoubleArg = 3
    LogTripleArg = 4
    LogQuadrupleArg = 5
    LogSingleWithIndex = 6
    LogDoubleWithIndex = 7
    LogTripleWithIndex = 8
    LogQuadrupleWithIndex = 9


def mk_topic(fn_sig):
    return "0x" + sha3_256(force_bytes(fn_sig)).hexdigest()


class Topics(object):
    LogAnonymous = mk_topic("LogAnonymous()")
    LogNoArguments = mk_topic("LogNoArguments()")
    LogSingleArg = mk_topic("LogSingleArg(uint256)")
    LogSingleWithIndex = mk_topic("LogSingleWithIndex(uint256)")
    LogDoubleArg = mk_topic("LogDoubleArg(uint256,uint256)")
    LogDoubleWithIndex = mk_topic("LogDoubleWithIndex(uint256,uint256)")
    LogTripleArg = mk_topic("LogTripleArg(uint256,uint256,uint256)")
    LogTripleWithIndex = mk_topic("LogTripleWithIndex(uint256,uint256,uint256)")
    LogQuadrupleArg = mk_topic("LogQuadrupleArg(uint256,uint256,uint256,uint256)")
    LogQuadrupleWithIndex = mk_topic("LogQuadrupleWithIndex(uint256,uint256,uint256,uint256)")


def test_filtering_single_topic(rpc_client, call_emitter_method, emitter_contract_address):
    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{
            'from_block': 'earliest',
            'to_block': 'latest',
            'address': emitter_contract_address,
            'topics': [],
        }]
    )

    call_emitter_method('logNoArgs(uint8)', [Events.LogNoArguments])

    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )

    assert len(changes) == 1
    log_entry = changes[0]
    assert Topics.LogNoArguments in log_entry['topics']

    assert rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    ) == []

    all_changes = rpc_client(
        method='eth_getFilterLogs',
        params=[filter_id],
    )

    assert len(all_changes) == 1
