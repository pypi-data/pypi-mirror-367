"""Tests for the message processor models."""
from typing import Type

import pika
import pytest

from talus.models.message import ConsumeMessageBase
from talus.models.processor import DEFAULT_DEAD_LETTER_EXCEPTIONS
from talus.models.processor import DLQMessageProcessor
from talus.models.processor import format_dead_letter_exceptions
from talus.models.processor import MessageProcessorBase


@pytest.fixture()
def successful_message_processor(consume_message_cls) -> MessageProcessorBase:
    """
    A message processor that does not raise an exception.
    """

    class SuccessfulMessageProcessor(MessageProcessorBase):
        message_cls: Type[ConsumeMessageBase] = consume_message_cls

        def process_message(self, message: ConsumeMessageBase):
            self._message_was_processed = True

    yield SuccessfulMessageProcessor()


@pytest.fixture()
def consumed_message(
    publish_message_cls,
    producer,
    consumer,
    body,
) -> tuple[pika.spec.Basic.Deliver, pika.spec.BasicProperties, bytes]:
    outbound_message = publish_message_cls(body=body)
    producer.publish(message=outbound_message)
    for m, p, b in consumer.consume_generator(auto_ack=True):
        yield m, p, b  # only the first one
        break


def test_message_processor_success(consumer, consumed_message, successful_message_processor):
    """
    :given: A message processor that does not raise an exception.
    :when: The message processor is called.
    :then: The message processor should process and acknowledge the message.
    """
    # given
    method, properties, body = consumed_message
    # when
    successful_message_processor(
        channel=consumer.channel, method=method, properties=properties, body=body
    )
    # then
    assert successful_message_processor._message_was_processed
    assert not consumer.channel.get_waiting_message_count()  # no messages left in the queue


@pytest.fixture()
def erroring_message_processor(consume_message_cls) -> MessageProcessorBase:
    """
    A message processor that raises a non-dead-letter exception.
    """

    class ErroringMessageProcessor(MessageProcessorBase):
        message_cls: Type[ConsumeMessageBase] = consume_message_cls
        dead_letter_exceptions: Type[Exception] = ValueError

        def process_message(self, message: ConsumeMessageBase):
            raise RuntimeError("A bad message processor raised an exception that is not DLQ'd.")

    yield ErroringMessageProcessor()


def test_message_processor_failure(erroring_message_processor, consumed_message, consumer):
    """
    :given: A message processor that raises an exception.
    :when: The message processor is called.
    :then: Expected exception is raised.
    """
    # given
    method, properties, body = consumed_message
    # when/then
    with pytest.raises(RuntimeError):
        erroring_message_processor(
            channel=consumer.channel, method=method, properties=properties, body=body
        )


@pytest.fixture()
def dlq_message_processor(consume_message_cls) -> DLQMessageProcessor:
    """
    A message processor that raises a non-dead-letter exception.
    """

    class AutoDLQMessageProcessor(DLQMessageProcessor):
        message_cls: Type[ConsumeMessageBase] = consume_message_cls

        def process_message(self, message: ConsumeMessageBase):
            self._process_message_called = True
            super().process_message(message)

    yield AutoDLQMessageProcessor()


def test_dlq_message_processor(dlq_message_processor, consumed_message, consumer):
    """
    :given: A message processor that raises an exception identified as for DLQ.
    :when: The message processor is called.
    :then: The message processor should DLQ the message.
    """
    # given
    method, properties, body = consumed_message
    # when
    dlq_message_processor(channel=consumer.channel, method=method, properties=properties, body=body)
    # then
    assert dlq_message_processor._process_message_called
    assert not consumer.channel.get_waiting_message_count()  # no messages left in the queue


@pytest.fixture()
def message_processor_with_producer(
    producer, queue_bindings, direct_exchange
) -> MessageProcessorBase:
    """
    A message processor that has a producer.
    """
    durable_producer = producer

    class MessageProcessorWithProducer(MessageProcessorBase):
        message_cls: Type[ConsumeMessageBase] = ConsumeMessageBase

        def process_message(self, message: ConsumeMessageBase):
            if self.producer.is_connected:
                self._message_was_processed = True

    return MessageProcessorWithProducer(producer=durable_producer)


def test_message_processor_with_producer_success(
    consumer, consumed_message, message_processor_with_producer
):
    """
    :given: A message processor that does not raise an exception.
    :when: The message processor is called.
    :then: The message processor should process and acknowledge the message.
    """
    # given
    method, properties, body = consumed_message
    # when
    message_processor_with_producer(
        channel=consumer.channel, method=method, properties=properties, body=body
    )
    # then
    assert message_processor_with_producer._message_was_processed
    assert not consumer.channel.get_waiting_message_count()  # no messages left on queue


@pytest.mark.parametrize(
    "exc",
    [
        pytest.param(KeyError, id="single"),
        pytest.param(None, id="none"),
        pytest.param((ValueError, RuntimeError), id="multiple"),
    ],
)
def test_format_dead_letter_exceptions(exc):
    """
    Given: an exception
    When: the exception is formatted
    Then: the default exceptions are added to the formatted exception
    """
    result = format_dead_letter_exceptions(exc)
    assert isinstance(result, tuple)
    for e in DEFAULT_DEAD_LETTER_EXCEPTIONS:
        assert e in result
    if exc is not None:
        if isinstance(exc, tuple):
            for e in exc:
                assert e in result
        else:
            assert exc in result
