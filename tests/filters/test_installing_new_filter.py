def test_registering_new_filter(rpc_client, call_emitter_method):
    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{}]
    )
    changes = rpc_client(
        method='eth_getFilterChanges',
        params=[filter_id],
    )

    assert not changes
