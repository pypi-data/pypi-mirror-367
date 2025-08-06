"""
Consumer implementation of the base connection wrapper
"""
import logging
from typing import Any
from typing import Callable
from typing import Generator

import pika.adapters.blocking_connection
from tenacity import Retrying

from talus.base import DurableConnection
from talus.models.connection_parameters import ConsumerConnectionParameterFactory
from talus.models.queue import Queue
from talus.models.retryer import ConnectionRetryerFactory

logger = logging.getLogger(__name__)


LISTEN_CALLBACK_TYPE = Callable[
    [
        pika.adapters.blocking_connection.BlockingChannel,
        pika.spec.Basic.Deliver,
        pika.spec.BasicProperties,
        bytes,
    ],
    Any,
]


class DurableConsumer(DurableConnection):
    """
    RabbitMQ connector for consuming from a single queue in RabbitMQ.
    >>> from talus.models.queue import Queue
    >>> from talus.models.connection_parameters import ConsumerConnectionParameterFactory
    >>> from talus.models.retryer import ConnectionRetryerFactory
    >>> from talus.consumer import DurableConsumer
    >>> from talus.models.processor import MessageProcessorBase
    >>> from talus.models.message import ConsumeMessageBase
    >>> consume_queue = Queue(name="test_queue")
    >>> # Consume with the listen method:
    >>> class MessageProcessor(MessageProcessorBase):
    >>>     message_cls: Type[ConsumeMessageBase] = ConsumeMessageBase
    >>>     def process_message(self, message: ConsumeMessageBase):
    >>>         print(message)
    >>> with DurableConsumer(consume_queue=consume_queue, prefetch_count=1, connection_parameters=ConsumerConnectionParameterFactory(), connection_retryer=ConnectionRetryerFactory()) as consumer:
    >>>     message_processor = MessageProcessor()
    >>>     consumer.listen(message_processor)
    >>> # Or consume with the consume_generator method:
    >>> class ConsumeMessageBody(MessageBodyBase):
    >>>     objectName: str
    >>>     bucket: str
    >>> class ConsumeMessage(ConsumeMessageBase):
    >>>     message_body_cls: Type[ConsumeMessageBody] = ConsumeMessageBody
    >>> with DurableConsumer(consume_queue=consume_queue, prefetch_count=1, connection_parameters=ConsumerConnectionParameterFactory(), connection_retryer=ConnectionRetryerFactory()) as consumer:
    >>>     for method, properties, body in consumer.consume_generator():
    >>>         message = ConsumeMessage(method=method, properties=properties, body=body)
    """

    def __init__(
        self,
        consume_queue: Queue,
        prefetch_count: int = 1,
        connection_parameters: pika.ConnectionParameters
        | Callable[[], pika.ConnectionParameters] = ConsumerConnectionParameterFactory(),
        connection_retryer: Retrying | Callable[[], Retrying] = ConnectionRetryerFactory(),
    ):
        """
        Constructor for the consumer connector

        :param consume_queue: Queue to consume messages from

        :param prefetch_count: Number of un-Acked message delivered at a time

        :param connection_parameters: A pika.ConnectionParameters object or one resulting
            from a callable that returns a ConnectionParameters object.

        :param connection_retryer: A tenacity.Retrying object or one resulting from a callable that returns
            a Retrying object.
        """
        super().__init__(
            connection_parameters=connection_parameters,
            connection_retryer=connection_retryer,
        )
        self.consume_queue = consume_queue
        self.prefetch_count = prefetch_count

    def _connect(self) -> None:
        """
        Configures and initiates consumer connection to the RabbitMQ server which includes
        setting up the queue to consume from and the prefetch count.
        """
        super()._connect()
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.create_queue(queue=self.consume_queue)

    def _listen(self, callback: LISTEN_CALLBACK_TYPE) -> None:
        """
        Listens for messages on the channel configured on the consumer instance

        :param callback: Function to execute when a message is received. with the signature
        (ch, method, properties, body).
        ch: Copy of the channel used to acknowledge receipt (pika.Channel)
        method: Management keys for the delivered message e.g. delivery mode (pika.spec.Basic.Deliver)
        properties: Message properties (pika.spec.BasicProperties)
        body: Message body for a transfer message (bytes)
        """
        self.connect()
        logger.info(f"Starting Listener on Queue: consumer_queue={self.consume_queue}")
        self.channel.basic_consume(queue=self.consume_queue.name, on_message_callback=callback)
        self.channel.start_consuming()

    def listen(self, message_processor: LISTEN_CALLBACK_TYPE) -> None:
        """
        Retries calls to _listen and executes the message_processor callback when a message is received.
        This method is blocking and will not return until the connection is closed.
        :param message_processor: Callable to execute when a message is received. with the signature
        (channel, method, properties, body).
        channel: Copy of the channel used to acknowledge receipt (pika.Channel)
        method: Management keys for the delivered message e.g. delivery mode (pika.spec.Basic.Deliver)
        properties: Message properties (pika.spec.BasicProperties)
        body: Message body for a transfer message (bytes)
        and returns None.
        """
        self.connection_retryer(self._listen, callback=message_processor)

    def consume_generator(self, auto_ack=False, inactivity_timeout: float = 0.1) -> Generator:
        """
        Creates a generator for messages that are on the instance consumer_queue.
        Retry logic is not applied to prevent the resetting of the generator cursor

        :param auto_ack: Automatically acknowledge messages
        :param inactivity_timeout: Number of seconds to wait for a message before returning None

        :return: Generator of (method, properties, body)
        """
        self.connect()
        logger.info(f"Creating consumer generator on Queue: consumer_queue={self.consume_queue}")
        return self.channel.consume(
            queue=self.consume_queue.name, auto_ack=auto_ack, inactivity_timeout=inactivity_timeout
        )

    def cancel_consume_generator(self) -> None:
        """
        Resets the active consume generator
        :return: None
        """
        logger.info(f"Cancelling consumer generator on Queue: consumer_queue={self.consume_queue}")
        self.channel.cancel()

    def acknowledge_message(self, delivery_tag, multiple=False) -> None:
        """
        Record a message as acknowledged.
        Retry logic is not applied since creating a new channel would be unable
        to acknowledge the message received on the now dead channel

        :param delivery_tag: method.delivery_tag

        :param multiple: Acknowledge multiple messages by setting to True and acknowledging the last message

        :return: None
        """
        self.channel.basic_ack(delivery_tag, multiple)

    def reject_message(self, delivery_tag) -> None:
        """
        Record a message as rejected.  Will go to dead letter exchange if configured on the server.
        Retry logic is not applied since creating a new channel would be unable
        to use the delivery tag received on the now dead channel

        :param delivery_tag: method.delivery_tag

        :return: None
        """
        self.channel.basic_reject(delivery_tag=delivery_tag, requeue=False)

    def requeue_message(self, delivery_tag) -> None:
        """
        Return message back to the queue.
        Retry logic is not applied since creating a new channel would be unable
        to use the delivery tag received on the now dead channel

        :param delivery_tag: method.delivery_tag

        :return: None
        """
        self.channel.basic_nack(delivery_tag=delivery_tag, requeue=True)

    def __repr__(self):
        """Representation of the DurableConsumer instance."""
        return f"{self.__class__.__name__}(consume_queue={self.consume_queue !r}, prefetch_count={self.prefetch_count}, connection_parameters={self.connection_parameters!r}, connection_retryer={self.connection_retryer!r})"
