def test_registering_new_filter_with_no_args(rpc_client, rpc_call_emitter):
    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{}]
    )
    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )

    assert not changes


def test_registering_new_filter_with_no_args(rpc_client, rpc_call_emitter):
    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{
            'fromBlock': 1,
            'toBlock': 10,
            'address': '0xd3cda913deb6f67967b99d67acdfa1712c293601',
            'topics': ['0x000000000000000000000000a94f5374fce5edbc8e2a8697c15331677e6ebf0b'],
        }]
    )
    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )

    assert not changes
