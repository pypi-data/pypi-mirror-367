"""Tests for the durable producer module."""
from talus.producer import DurableProducer


def test_publish(producer, publish_message_cls, message_data, consumer, consume_message_cls):
    """
    :given: A producer and message data
    :when: The producer publishes a message
    :then: The message is published
    """
    # when
    publish_message = publish_message_cls(message_data)
    producer.publish(publish_message)
    # then
    for method, properties, body in consumer.consume_generator(auto_ack=True):
        message = consume_message_cls(method=method, properties=properties, body=body)
        for field_name in message.body.model_fields:
            assert getattr(message.body, field_name) == getattr(publish_message.body, field_name)
        break


def test_repr(producer):
    """
    :given: A producer
    :when: The producer is represented as a string
    :then: The string representation is as expected
    """
    assert DurableProducer.__name__ in repr(producer)
