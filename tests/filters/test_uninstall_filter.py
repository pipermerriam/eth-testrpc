import pytest


def test_uninstalling_filter(client, client_call_emitter):
    filter_id = client.new_filter(from_block="earliest", to_block="latest", address=[], topics=[])

    changes = client.get_filter_changes(filter_id)

    assert changes == []

    assert client.uninstall_filter(filter_id) is True

    with pytest.raises(ValueError):
        client.get_filter_changes(filter_id)

    assert client.uninstall_filter(filter_id) is False
