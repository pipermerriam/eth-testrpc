def test_new_filter_no_events(client, call_emitter_contract):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    changes = client.get_filter_changes(filter_id)

    assert changes == []
