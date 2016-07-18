def test_registering_new_filter(rpc_client, call_emitter_method):
    assert rpc_client(
        method='eth_uninstallFilter',
        params=['some-filter-id-that-doesnt-exist'],
    ) is False

    filter_id = rpc_client(
        method='eth_newFilter',
        params=[{}]
    )

    assert rpc_client(
        method='eth_uninstallFilter',
        params=[filter_id],
    ) is True

    # already un-installed
    assert rpc_client(
        method='eth_uninstallFilter',
        params=[filter_id],
    ) is False
