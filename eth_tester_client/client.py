"""
Large portions of this implementation were influenced or downright copied from
the `eth-testrpc` project by ConsenSys

https://github.com/ConsenSys/eth-testrpc
"""
import sys
import time
import threading
import uuid

import rlp

from ethereum import transactions
from ethereum import tester as t

from .utils import (
    coerce_args_to_bytes,
    strip_0x,
    encode_32bytes,
    encode_address,
    encode_data,
    normalize_number,
    normalize_address,
    decode_hex,
)
from .serializers import (
    serialize_txn,
    serialize_txn_receipt,
    serialize_block,
)


if sys.version_info.major == 2:
    from Queue import Queue

else:
    from queue import Queue


# Set the gas
DEFAULT_GAS_LIMIT = t.gas_limit = t.GAS_LIMIT = 3141592


class EthTesterClient(object):
    """
    Stand-in replacement for the rpc client that speaks directly to the
    `ethereum.tester` facilities.
    """
    def __init__(self, async=True, async_timeout=10):
        self.snapshots = []

        self.reset_evm()

        self.is_async = async
        self.async_timeout = async_timeout

        if self.is_async:
            self.request_queue = Queue()
            self.results = {}

            self.request_thread = threading.Thread(target=self.process_requests)
            self.request_thread.daemon = True
            self.request_thread.start()

    def reset_evm(self, snapshot_idx=None):
        if snapshot_idx is not None:
            self.revert_evm(snapshot_idx)
        else:
            self.evm = t.state()
            self.evm.block.gas_limit = DEFAULT_GAS_LIMIT

    def snapshot_evm(self):
        self.snapshots.append((self.evm.block.number, self.evm.snapshot()))
        return len(self.snapshots) - 1

    def revert_evm(self, snapshot_idx=None, reset_logs=False):
        if len(self.snapshots) == 0:
            raise ValueError("No snapshots to revert to")

        if snapshot_idx is not None:
            block_number, snapshot = self.snapshots[snapshot_idx]
        else:
            block_number, snapshot = self.snapshots.pop()

        # Remove all blocks after our saved block number.
        del self.evm.blocks[block_number + 1:]

        self.evm.revert(snapshot)

    def process_requests(self):
        while True:
            id, args, kwargs = self.request_queue.get()
            mine = kwargs.pop('_mine', False)
            try:
                self._send_transaction(*args, **kwargs)
                if mine:
                    self.evm.mine()
                response = self.evm.last_tx.hash
            except Exception as e:
                response = e
                if mine:
                    self.evm.mine()
            self.results[id] = response

    def wait_for_block(self, block_number, max_wait=0):
        while self.evm.block.number < block_number:
            self.evm.mine()
        return self.get_block_by_number(self.evm.block.number)

    def wait_for_transaction(self, txn_hash, max_wait=0):
        return self.get_transaction_receipt(txn_hash)

    def get_max_gas(self):
        return t.gas_limit

    #
    # Internal getters for EVM objects
    #
    def _get_transaction_by_hash(self, txn_hash):
        txn_hash = strip_0x(txn_hash)
        if len(txn_hash) == 64:
            txn_hash = decode_hex(txn_hash)
        for block in reversed(self.evm.blocks):
            txn_hashes = block.get_transaction_hashes()

            if txn_hash in txn_hashes:
                txn_index = txn_hashes.index(txn_hash)
                txn = block.transaction_list[txn_index]
                break
        else:
            raise ValueError("Transaction not found")
        return block, txn, txn_index

    def _get_block_by_number(self, block_number="latest"):
        if block_number == "latest":
            return self.evm.block
        elif block_number == "earliest":
            return self.evm.blocks[0]
        elif block_number == "pending":
            raise ValueError("Fetching 'pending' block is unsupported")
        else:
            block_number = normalize_number(block_number)

            if block_number >= len(self.evm.blocks):
                raise ValueError("Invalid block number")
            return self.evm.blocks[block_number]

    def _get_block_by_hash(self, block_hash):
        if len(block_hash) > 32:
            block_hash = decode_hex(strip_0x(block_hash))
        for block in self.evm.blocks:
            if block.hash == block_hash:
                return block
        else:
            raise ValueError("Could not find block for provided hash")

    @coerce_args_to_bytes
    def _send_transaction(self, _from=None, to=None, gas=None, gas_price=None,
                          value=0, data=b''):
        """
        The tester doesn't care about gas so we discard it.
        """
        if _from is None:
            _from = self.get_coinbase()

        _from = normalize_address(_from)

        sender = t.keys[t.accounts.index(_from)]

        if to is None:
            to = b''

        to = normalize_address(to, allow_blank=True)

        if data is None:
            data = b''

        data = decode_hex(data)

        output = self.evm.send(sender=sender, to=to, value=value, evmdata=data)
        return output

    #
    # Public API
    #
    def get_coinbase(self):
        return encode_address(self.evm.block.coinbase)

    def get_accounts(self):
        return [
            encode_address(addr) for addr in t.accounts
        ]

    def get_code(self, address, block_number="latest"):
        block = self._get_block_by_number(block_number)
        return encode_32bytes(block.get_code(strip_0x(address)))

    def send_transaction(self, *args, **kwargs):
        if self.is_async:
            kwargs['_mine'] = True
            request_id = uuid.uuid4()
            self.request_queue.put((request_id, args, kwargs))
            start = time.time()
            while time.time() - start < self.async_timeout:
                if request_id in self.results:
                    result = self.results.pop(request_id)
                    if isinstance(result, Exception):
                        raise result
                    return encode_data(result)
            raise ValueError("Timeout waiting for {0}".format(request_id))
        else:
            self._send_transaction(*args, **kwargs)
            self.evm.mine()
            return encode_32bytes(self.evm.last_tx.hash)

    def send_raw_transaction(self, raw_tx):
        tx = rlp.decode(decode_hex(strip_0x(raw_tx)), transactions.Transaction)

        to = encode_address(tx.to) if tx.to else b''
        _from = encode_address(tx.sender)
        data = encode_data(tx.data)

        return self.send_transaction(
            _from=_from,
            to=to,
            gas=tx.gasprice,
            value=tx.value,
            data=data,
        )

    def get_transaction_receipt(self, txn_hash):
        block, txn, txn_index = self._get_transaction_by_hash(txn_hash)

        return serialize_txn_receipt(block, txn, txn_index)

    def get_transaction_count(self, address, block_number="latest"):
        block = self._get_block_by_number(block_number)
        address = normalize_address(address)

        return block.get_nonce(address)

    def get_block_by_number(self, block_number, full_transactions=True):
        block = self._get_block_by_number(block_number)

        return serialize_block(block, full_transactions)

    def get_block_by_hash(self, block_hash, full_transactions=True):
        block = self._get_block_by_hash(block_hash)

        return serialize_block(block, full_transactions)

    def get_block_number(self):
        return self.evm.block.number

    def get_gas_price(self):
        return t.gas_price

    def get_balance(self, address, block="latest"):
        _block = self._get_block_by_number(block)
        return _block.get_balance(strip_0x(address))

    def call(self, *args, **kwargs):
        if len(args) >= 7 and args[6] != "latest":
            raise ValueError("Using call on any block other than latest is unsupported")
        if kwargs.get('block', 'latest') != "latest":
            raise ValueError("Using call on any block other than latest is unsupported")
        snapshot_idx = self.snapshot_evm()
        output = self._send_transaction(*args, **kwargs)
        self.revert_evm(snapshot_idx)

        return encode_data(output)

    def get_transaction_by_hash(self, txn_hash):
        block, txn, txn_index = self._get_transaction_by_hash(txn_hash)
        return serialize_txn(block, txn, txn_index)
