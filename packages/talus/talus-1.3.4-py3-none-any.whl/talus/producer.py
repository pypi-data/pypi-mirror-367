"""
Producer implementation of the base connection wrapper
"""
import logging
from typing import Callable

import pika
from pika.exceptions import NackError
from pika.exceptions import UnroutableError
from tenacity import Retrying

from talus.base import DurableConnection
from talus.models.binding import Binding
from talus.models.connection_parameters import ProducerConnectionParameterFactory
from talus.models.exchange import Exchange
from talus.models.message import PublishMessageBase
from talus.models.retryer import ConnectionRetryerFactory
from talus.models.retryer import RetryerFactory

logger = logging.getLogger(__name__)


class DurableProducer(DurableConnection):
    """
    RabbitMQ Connector for posting to 1 to many queues via an exchange
    """

    def __init__(
        self,
        queue_bindings: list[Binding] | Binding,
        publish_exchange: Exchange,
        connection_parameters: pika.ConnectionParameters
        | Callable[[], pika.ConnectionParameters] = ProducerConnectionParameterFactory(),
        connection_retryer: Retrying | Callable[[], Retrying] = ConnectionRetryerFactory(),
    ):
        """
        Constructor for the producer connector

        :param queue_bindings: Bindings used to map routing key to destination queue for an exchange

        :param publish_exchange: Name of the exchange that the  producer will publish to.

        :param connection_parameters: A pika.ConnectionParameters object or one resulting
            from a callable that returns a ConnectionParameters object.

        :param connection_retryer: A tenacity.Retrying object or one resulting from a callable that returns
            a Retrying object.

        >>> from talus.models.binding import Binding
        >>> from talus.models.exchange import Exchange
        >>> from talus.producer import DurableProducer
        >>> from talus.models.retryer import ConnectionRetryerFactory
        >>> from talus.models.connection_parameters import ProducerConnectionParameterFactory
        >>> from talus.models.queue import Queue
        >>> from talus.models.message import PublishMessageBase
        >>> queue = Queue(name="test_queue")
        >>> exchange = Exchange(name="test_exchange")
        >>> # Bind the queue to the routing key on message.
        >>> queue_bindings = Binding(queue=queue, message=PublishMessageBase)
        >>> with DurableProducer(queue_bindings=queue_bindings, publish_exchange=exchange, connection_parameters=ProducerConnectionParameterFactory(), connection_retryer=ConnectionRetryerFactory()) as producer:
        >>>     producer.publish(PublishMessageBase(body={"test": "test"}))

        """
        super().__init__(
            connection_parameters=connection_parameters, connection_retryer=connection_retryer
        )
        if isinstance(queue_bindings, Binding):
            queue_bindings = [queue_bindings]
        self.queue_bindings = queue_bindings
        self.publish_exchange = publish_exchange

        # Retry posts which are not confirmed by the broker
        publish_retryer_factory = RetryerFactory(
            delay_min=1,
            delay_max=3,
            jitter_min=1,
            jitter_max=3,
            attempts=3,
            exceptions=(UnroutableError, NackError),
        )
        self.publish_retryer = publish_retryer_factory()

    def _connect(self) -> None:
        """
        Configures and initiates producer connection to the RabbitMQ server.
        :return:
        """
        super()._connect()
        self.channel.confirm_delivery()  # ensure persistence prior to message confirmation
        self.channel.exchange_declare(
            exchange=self.publish_exchange.name,
            exchange_type=self.publish_exchange.type,
            passive=self.publish_exchange.passive,
            durable=self.publish_exchange.durable,
            auto_delete=self.publish_exchange.auto_delete,
            internal=self.publish_exchange.internal,
            arguments=self.publish_exchange.arguments,
        )
        for binding in self.queue_bindings:
            self.create_queue(queue=binding.queue)
            self.channel.queue_bind(
                exchange=self.publish_exchange.name,
                queue=binding.queue_name,
                routing_key=binding.routing_key,
            )
            logger.info(
                f"Bindings configured: exchange={self.publish_exchange}, "
                f"queue={binding.queue.name}, "
                f"routing_key={binding.routing_key} "
            )

    def _publish(self, message: PublishMessageBase) -> None:
        """
        Publish message to the exchange configured on the producer

        :param message: Message to publish
        :return: None
        """
        self.connect()
        self.publish_retryer(
            self.channel.basic_publish,
            exchange=self.publish_exchange.name,
            routing_key=message.routing_key,
            body=message.body.model_dump_json(by_alias=True),
            properties=message.properties,
            mandatory=True,  # paired with channel.confirm_delivery() to ensure message persistence
        )

    def publish(self, message: PublishMessageBase) -> None:
        """
        Publish message to the exchange configured on the producer retrying connection errors configured in the connection_retryer.
        :return: None
        """
        self.connection_retryer(self._publish, message=message)

    def __repr__(self):
        """Representation of the DurableProducer instance."""
        return f"{self.__class__.__name__}(queue_bindings={self.queue_bindings !r}, exchange={self.publish_exchange!r}, connection_parameters={self.connection_parameters!r}, connection_retryer={self.connection_retryer!r})"
