from testrpc.client.utils import (
    force_bytes,
    encode_number,
)


def test_new_filter_no_events(client):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    changes = client.get_filter_changes(filter_id)

    assert changes == []


def test_new_filter_with_single_no_args_event(client, client_call_emitter,
                                              Events, LogFunctions, LogTopics):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = client_call_emitter(LogFunctions.logNoArgs, [Events.LogNoArguments])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]
    assert LogTopics.LogNoArguments in log_entry['topics']


def test_new_filter_block_numbers_hex(client, client_call_emitter,
                                      Events, LogFunctions, LogTopics):
    filter_id = client.new_filter(from_block="0x0", to_block="0x1", address=[], topics=[])

    txn_hash = client_call_emitter(LogFunctions.logNoArgs, [Events.LogNoArguments])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]
    assert LogTopics.LogNoArguments in log_entry['topics']


def test_new_filter_with_anonymous_event(client, client_call_emitter,
                                         LogFunctions, Events):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = client_call_emitter(LogFunctions.logNoArgs, [Events.LogAnonymous])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]
    assert not log_entry['topics']  # anonymous event


def test_new_filter_with_topic_based_filtering(client,
                                               client_call_emitter,
                                               LogFunctions,
                                               LogTopics,
                                               Events):
    filter_id = client.new_filter(
        from_block="earliest",
        to_block="latest",
        address=[],
        topics=[[LogTopics.LogSingleArg], [LogTopics.LogNoArguments]],
    )

    client_call_emitter(LogFunctions.logDouble, [Events.LogDoubleWithIndex, 1234, 4321])
    txn_hash = client_call_emitter(LogFunctions.logNoArgs, [Events.LogNoArguments])
    txn_hash = client_call_emitter(LogFunctions.logSingle, [Events.LogSingleArg, 1234])
    client_call_emitter(LogFunctions.logDouble, [Events.LogDoubleWithIndex, 5678, 8765])

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 2
    log_entry_a, log_entry_b = changes

    assert LogTopics.LogNoArguments in log_entry_a['topics']
    assert LogTopics.LogSingleArg in log_entry_b['topics']


def test_new_filter_with_topic_filter_on_indexed_arg(client,
                                                     client_call_emitter,
                                                     Events,
                                                     LogFunctions,
                                                     LogTopics):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    txn_hash = client_call_emitter(
        LogFunctions.logSingle,
        [Events.LogSingleWithIndex, 1234567890],
    )

    changes = client.get_filter_changes(filter_id)

    assert len(changes) == 1
    log_entry = changes[0]

    assert LogTopics.LogSingleWithIndex in log_entry['topics']
    assert force_bytes(encode_number(1234567890, 32)) in log_entry['topics']
