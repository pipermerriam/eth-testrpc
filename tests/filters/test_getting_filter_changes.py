from sha3 import sha3_256

assert sha3_256(b'').hexdigest() == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

from testrpc.client.utils import force_text


def test_filtering_single_topic(rpc_client,
                                call_emitter_method,
                                rpc_emitter_contract_address,
                                LogFunctions,
                                LogTopics,
                                Events):

    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{
            'from_block': 'earliest',
            'to_block': 'latest',
            'address': rpc_emitter_contract_address,
            'topics': [],
        }]
    )

    call_emitter_method(LogFunctions.logNoArgs, [Events.LogNoArguments])

    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )

    assert len(changes) == 1
    log_entry = changes[0]
    assert force_text(LogTopics.LogNoArguments) in log_entry['topics']

    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )
    assert len(changes) == 0

    all_changes = rpc_client(
        method='eth_getFilterLogs',
        params=[filter_id],
    )
    assert len(all_changes) == 1
