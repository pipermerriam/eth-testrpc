import pytest

from eth_tester_client.utils import str_to_bytes


@pytest.mark.parametrize(
    'arg,expected',
    (
        ('', b''),
        (b'', b''),
        ('abc', b'abc'),
        (b'abc', b'abc'),
        ('\x00', b'\x00'),
        (b'\x00', b'\x00'),
    )
)
def test_str_to_bytes(arg, expected):
    actual = str_to_bytes(arg)
    assert actual == expected
