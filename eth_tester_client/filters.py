"""
def serialize_log(block, txn, txn_index, log, log_index):
    return {
        "type": "mined",
        "logIndex": encode_number(log_index),
        "transactionIndex": encode_number(txn_index),
        "transactionHash": encode_32bytes(txn.hash),
        "blockHash": encode_32bytes(block.hash),
        "blockNumber": encode_number(block.number),
        "address": encode_32bytes(log.address),
        "data": encode_32bytes(log.data),
        "topics": [
            encode_number(topic, 32) for topic in log.topics
            for topic in log.topics
        ],
    }
"""

from .utils import (
    is_string,
    coerce_args_to_bytes,
)


@coerce_args_to_bytes
def check_if_filter_matches_log(log_entry, latest_block, from_block, to_block,
                                addresses, topics):
    #
    # validate `from_block` (left bound)
    #
    if is_string(from_block):
        if from_block == "latest":
            if log_entry.number != latest_block.number:
                return False
        else:
            raise NotImplementedError(
                "Filters not implemented for any block identifier other than 'latest'"
            )
    else:
        if from_block > block.number:
            return False

    #
    # validate `to_block` (left bound)
    #
    if is_string(to_block):
        if to_block == "latest":
            if log_entry.number != latest_block.number:
                return False
        else:
            raise NotImplementedError(
                "Filters not implemented for any block identifier other than 'latest'"
            )
    else:
        if to_block > block.number:
            return False

    #
    # validate `addresses`
    #
    if addresses and log.address not in addresses:
        return False

    #
    # validate `topics`
    if not check_filter_matches_log(filter_topics, log.topics):
        return False

    return True


def is_array(value):
    return isinstance(value, (list, tuple))


def is_empty_array(value):
    return value == [] or value == tuple()


def is_topic_array(value):
    if not is_array(value):
        return False
    return all(is_string(item) or item is None for item in value)


def is_nested_topic_array(value):
    if not is_array(value):
        return False

    return all((is_topic_array(item) for item in value))


def check_filter_topics_validity(filter_topics):
    return any((
        is_empty_array(filter_topics),
        is_topic_array(filter_topics),
        is_nested_topic_array(filter_topics),
    ))


@coerce_args_to_bytes
def check_topic_match(filter_topic, log_topic):
    if filter_topic is None:
        return True
    return filter_topic == log_topic


@coerce_args_to_bytes
def check_filter_matches_log(filter_topics, log_topics):
    if is_empty_array(filter_topics):
        return True
    elif is_topic_array(filter_topics):
        if len(filter_topics) > len(log_topics):
            return False
        return all(
            check_topic_match(filter_topic, log_topic)
            for filter_topic, log_topic
            in zip(filter_topics, log_topics)
        )
    elif is_nested_topic_array(filter_topics):
        return any(
            check_filter_matches_log(sub_topics, log_topics)
            for sub_topics in filter_topics
        )
    else:
        raise ValueError("Invalid filter topics format")


def log_filter(
