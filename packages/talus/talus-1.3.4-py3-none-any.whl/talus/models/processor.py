"""Base Processor for messages consumed from a channel."""
import logging
from abc import ABC
from abc import abstractmethod
from typing import Type

import pika
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import ValidationError

from talus.models.message import ConsumeMessageBase
from talus.producer import DurableProducer

logger = logging.getLogger(__name__)


DEFAULT_DEAD_LETTER_EXCEPTIONS: tuple[type[Exception], ...] = (ValidationError,)


def format_dead_letter_exceptions(
    exceptions: Type[Exception] | tuple[Type[Exception], ...] | None = None,
) -> tuple[Type[Exception], ...]:
    """Append default exceptions to the given exceptions."""
    if exceptions is None:
        return DEFAULT_DEAD_LETTER_EXCEPTIONS
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)
    return exceptions + DEFAULT_DEAD_LETTER_EXCEPTIONS


class MessageProcessorBase(BaseModel, ABC):
    """
    Base Processor for processing messages consumed from a channel.  This is pydantic.BaseModel to enhance
    validation and error handling.
    Implementations should extend this class and implement the process_message method.
    Instances of a processor will be used to process multiple messages when they are run.
    The signature of the of running a message processor instance matches the
    DurableConsumer().consume() method callback.
    :param: message_cls: Validate the message body with this class.
    :param: dead_letter_exceptions: Exceptions that will cause the message to be dead lettered.
    :param: producer: Producer to use for publishing messages as part of inbound message processing if necessary.
    >>> class ObjectBucketBody(MessageBodyBase):
    >>>    objectName: str
    >>>    bucket: str
    >>>
    >>> class InboundMessage(ConsumeMessageBase):
    >>>     message_body_cls: Type[ObjectBucketBody] = ObjectBucketBody  # Validate the body with ObjectBucketBody
    >>>
    >>> class MyMessageProcessor(MessageProcessorBase):
    >>>     message_cls: Type[InboundMessage] = InboundMessage
    >>>     def process_message(self, message: InboundMessage):
    >>>         print(f"Processing message: {message}")
    >>>
    >>> queue = Queue(name="my_queue")
    >>> with DurableConsumer(consume_queue=queue) as consumer:
    >>>     consumer.listen(MyMessageProcessor())
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    message_cls: Type[ConsumeMessageBase] = ConsumeMessageBase
    dead_letter_exceptions: tuple[Type[Exception]] = format_dead_letter_exceptions()
    producer: DurableProducer | None = None

    @abstractmethod
    def process_message(self, message: ConsumeMessageBase):
        pass  # pragma: no cover

    @classmethod
    def dlq_message(
        cls,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        exception: Exception | None = None,
    ) -> None:
        """
        Reject the message but do not requeue it. Depending on exchange policy, this will trigger dead lettering
        https://www.rabbitmq.com/docs/dlx
        """
        logger.warning(f"Dead lettering message:{method=}, {properties=}, {exception=}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @classmethod
    def acknowledge_message(
        cls, channel: pika.adapters.blocking_connection.BlockingChannel, message: ConsumeMessageBase
    ) -> None:
        """Acknowledge the message which removes it from the queue."""
        logger.debug(
            f"Acknowledging message: method={message.method}, properties={message.properties}, {message=}"
        )
        channel.basic_ack(delivery_tag=message.delivery_tag)

    def __call__(
        self,
        channel: pika.adapters.blocking_connection.BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> "MessageProcessorBase":
        """
        Message processors are meant to be called from the DurableConsumer.consume() method.
        Calling a message processor instance first validates the message body using the instance
        message_cls.  If the message body is valid, the process_message method is called with the
        validated model, otherwise the error is evaluated for dead lettering.  The default is to
        dead letter messages that fail validation but other exceptions can be added to the instance.
        Exceptions that are raised but not dead lettered will be re-raised while dead lettered
        exceptions will be logged but effectively be consumed.
        """
        try:
            message = self.message_cls(method=method, properties=properties, body=body)
            self.process_message(message)
            self.acknowledge_message(channel=channel, message=message)
        except self.dead_letter_exceptions as e:
            self.dlq_message(channel=channel, method=method, properties=properties, exception=e)
        return self


class DLQMessageProcessor(MessageProcessorBase):
    """
    A message processor that dead letters all messages it processes.  This is useful for testing and
    fall through cases where a message processor is not found for a message.
    """

    message_cls: Type[ConsumeMessageBase] = ConsumeMessageBase
    dead_letter_exceptions: tuple[Type[Exception]] = format_dead_letter_exceptions(ValueError)

    def process_message(self, message: ConsumeMessageBase):
        raise ValueError(f"DLQMessageProcessor auto fails processing: {message=}")
