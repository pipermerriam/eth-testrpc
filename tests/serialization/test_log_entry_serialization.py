import pytest


@pytest.mark.parametrize(
    'contract_fn,event_name,call_args,exp_topic_length,exp_data_length',
    (
        ('logNoArgs', 'LogNoArguments', [], 1, 0),
        ('logNoArgs', 'LogAnonymous', [], 0, 0),
        ('logSingle', 'LogSingleArg', [12345], 1, 1),
        ('logSingle', 'LogSingleAnonymous', [12345], 1, 0),
        ('logSingle', 'LogSingleWithIndex', [12345], 2, 0),
        ('logDouble', 'LogDoubleArg', [12345, 54321], 1, 2),
        ('logDouble', 'LogDoubleAnonymous', [12345, 54321], 1, 1),
        ('logDouble', 'LogDoubleWithIndex', [12345, 54321], 2, 1),
        ('logTriple', 'LogTripleArg', [12345, 54321, 1], 1, 3),
        ('logTriple', 'LogTripleWithIndex', [12345, 54321, 1], 3, 1),
        ('logQuadruple', 'LogQuadrupleArg', [12345, 54321, 1, 2], 1, 4),
        ('logQuadruple', 'LogQuadrupleWithIndex', [12345, 54321, 1, 2], 3, 2),
    )
)
def test_log_topic_serialization(client,
                                 call_emitter_contract,
                                 LogFunctions,
                                 LogTopics,
                                 Events,
                                 contract_fn,
                                 event_name,
                                 call_args,
                                 exp_topic_length,
                                 exp_data_length):
    contract_fn_sig = getattr(LogFunctions, contract_fn)
    event_id = getattr(Events, event_name)
    txn_hash = call_emitter_contract(contract_fn_sig, [event_id] + call_args)
    txn_receipt = client.get_transaction_receipt(txn_hash)

    assert len(txn_receipt['logs']) == 1

    log_entry = txn_receipt['logs'][0]

    event_topic = getattr(LogTopics, event_name)

    if 'Anonymous' in event_name:
        assert event_topic not in log_entry['topics']
    else:
        assert event_topic in log_entry['topics']
    assert len(log_entry['topics']) == exp_topic_length
    assert len(log_entry['data']) == exp_data_length * 64 + 2
