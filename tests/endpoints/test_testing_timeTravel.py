def test_timetravel(rpc_client):
    latest_block = rpc_client('eth_getBlockByNumber', ['pending'])
    latest_block_timestamp = int(
        latest_block['timestamp'],
        16,
    )

    time_travel_timestamp = latest_block_timestamp + 12345

    rpc_client('testing_timeTravel', [time_travel_timestamp])

    block = rpc_client('eth_getBlockByNumber', ['pending'])
    block_timestamp = int(block['timestamp'], 16)

    assert block_timestamp >= time_travel_timestamp
