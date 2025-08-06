"""Tests for the durable consumer module."""
from talus.consumer import DurableConsumer


def test_consumer_listen(consumer, single_message_on_queue, message_data, consume_message_cls):
    """
    :given: A consumer and a message on the queue
    :when: The consumer listens for a message
    :then: The message is consumed
    """

    def verify_message(ch, method, properties, body):  # then
        message = consume_message_cls(method=method, properties=properties, body=body)
        for field_name in message.body.model_fields:
            assert getattr(message.body, field_name) == getattr(
                single_message_on_queue.body, field_name
            )
        ch.basic_ack(method.delivery_tag)
        consumer.disconnect()

    # when
    consumer.listen(verify_message)


def test_consume_generator(consumer, single_message_on_queue, consume_message_cls):
    """
    :given: A consumer and a message on the queue
    :when: The consumer consumes a message via consume_generator
    :then: The expected message is consumed and the generator cancelled
    """
    # when
    for method, properties, body in consumer.consume_generator():
        # then
        message = consume_message_cls(method=method, properties=properties, body=body)
        for field_name in message.body.model_fields:
            assert getattr(message.body, field_name) == getattr(
                single_message_on_queue.body, field_name
            )
        consumer.cancel_consume_generator()


def test_acknowledge_message(consumer, single_message_on_queue, consume_message_cls):
    """
    :given: A consumer and a message on the queue
    :when: The consumer acknowledges a message
    :then: The message is consumed
    """
    # when
    for method, properties, body in consumer.consume_generator():
        message = consume_message_cls(method=method, properties=properties, body=body)
        for field_name in message.body.model_fields:
            assert getattr(message.body, field_name) == getattr(
                single_message_on_queue.body, field_name
            )
        consumer.acknowledge_message(method.delivery_tag)
        break
    # then
    for method, properties, body in consumer.consume_generator():
        assert body is None
        break


def test_reject_message(consumer, single_message_on_queue, consume_message_cls):
    """
    :given: A consumer and a message on the queue
    :when: The consumer rejects a message
    :then: The message is not consumed
    """
    # when
    for method, properties, body in consumer.consume_generator():
        message = consume_message_cls(method=method, properties=properties, body=body)
        for field_name in message.body.model_fields:
            assert getattr(message.body, field_name) == getattr(
                single_message_on_queue.body, field_name
            )
        consumer.reject_message(message.delivery_tag)
        break
    # then
    for method, properties, body in consumer.consume_generator():
        assert body is None
        break


# requeue
def test_requeue_message(consumer, single_message_on_queue, consume_message_cls):
    """
    :given: A consumer and a message on the queue
    :when: The consumer requeues a message
    :then: The message is requeued
    """
    for _ in range(2):
        # when (loop 0) / then(loop 1)
        for method, properties, body in consumer.consume_generator():
            message = consume_message_cls(method=method, properties=properties, body=body)
            for field_name in message.body.model_fields:
                assert getattr(message.body, field_name) == getattr(
                    single_message_on_queue.body, field_name
                )
            consumer.requeue_message(method.delivery_tag)
            break


def test_repr(consumer):
    """
    :given: A consumer
    :when: The consumer is represented as a string
    :then: The string representation is returned
    """
    assert DurableConsumer.__name__ in repr(consumer)
