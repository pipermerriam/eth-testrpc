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


def test_new_filter_with_some_events(client, call_emitter_contract):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = call_emitter_contract('logNoArgs(uint8)', [1])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
