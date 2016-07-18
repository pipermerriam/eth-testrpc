from sha3 import sha3_256


assert sha3_256(b'').hexdigest() == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

from eth_tester_client.utils import force_bytes


def test_new_filter_no_events(client, call_emitter_contract):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    changes = client.get_filter_changes(filter_id)

    assert changes == []


class LogFunctions(object):
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


def fn_selector(fn_sig):
    return force_bytes("0x" + sha3_256(force_bytes(fn_sig)).hexdigest())


class LogTopics(object):
    LogAnonymous = fn_selector("LogAnonymous()")
    LogNoArguments = fn_selector("LogNoArguments()")
    LogSingleArg = fn_selector("LogSingleArg(uint256)")
    LogSingleWithIndex = fn_selector("LogSingleWithIndex(uint256)")
    LogDoubleArg = fn_selector("LogDoubleArg(uint256,uint256)")
    LogDoubleWithIndex = fn_selector("LogDoubleWithIndex(uint256,uint256)")
    LogTripleArg = fn_selector("LogTripleArg(uint256,uint256,uint256)")
    LogTripleWithIndex = fn_selector("LogTripleWithIndex(uint256,uint256,uint256)")
    LogQuadrupleArg = fn_selector("LogQuadrupleArg(uint256,uint256,uint256,uint256)")
    LogQuadrupleWithIndex = fn_selector("LogQuadrupleWithIndex(uint256,uint256,uint256,uint256)")

    logNoArgs = fn_selector("logNoArgs(uint8)")
    logSingle = fn_selector("logSingle(uint8,uint256)")
    logDouble = fn_selector("logDouble(uint8,uint256,uint256)")
    logTriple = fn_selector("logTriple(uint8,uint256,uint256,uint256)")
    logQuadruple = fn_selector("logQuadruple(uint8,uint256,uint256,uint256,uint256)")


def test_new_filter_with_single_no_args_event(client, call_emitter_contract):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = call_emitter_contract('logNoArgs(uint8)', [LogFunctions.LogNoArguments])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]
    assert LogTopics.LogNoArguments in log_entry['topics']


def test_new_filter_with_anonymous_event(client, call_emitter_contract):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = call_emitter_contract('logNoArgs(uint8)', [LogFunctions.LogAnonymous])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]
    assert not log_entry['topics']  # anonymous event


def test_new_filter_with_topic_based_filtering(client, call_emitter_contract):
    filter_id = client.new_filter(
        from_block="earliest",
        to_block="latest",
        address=[],
        topics=[[LogTopics.LogSingleArg], [LogTopics.LogNoArguments]],
    )

    call_emitter_contract('logDouble(uint8,uint256,uint256'
    txn_hash = call_emitter_contract('logNoArgs(uint8)', [LogFunctions.LogNoArguments])
    txn_hash = call_emitter_contract('logSingle(uint8,uint256)', [LogFunctions.LogSingleArg, 1234])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 2
    log_entry_a, log_entry_b = changes

    assert LogTopics.LogNoArguments in log_entry_a['topics']
    assert LogTopics.LogSingleArg in log_entry_b['topics']
