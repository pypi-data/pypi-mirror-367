"""
Base wrapper definition shared by both consumer and producer wrappers
"""
import logging
from typing import Callable

import pika
from tenacity import Retrying

from talus.models.connection_parameters import ConnectionParameterFactory
from talus.models.queue import Queue
from talus.models.retryer import ConnectionRetryerFactory

logger = logging.getLogger(__name__)


class DurableConnection:
    """
    RabbitMQ connector that establishes a blocking connection and channel
    """

    def __init__(
        self,
        connection_parameters: pika.ConnectionParameters
        | Callable[[], pika.ConnectionParameters] = ConnectionParameterFactory(),
        connection_retryer: Retrying | Callable[[], Retrying] = ConnectionRetryerFactory(),
    ):
        """
        Constructor for a durable connection to RabbitMQ.
        :param connection_parameters: A pika.ConnectionParameters object or one resulting
            from a callable that returns a ConnectionParameters object.
        :param connection_retryer: A tenacity.Retrying object or one resulting from a callable that returns
            a Retrying object.
        """
        if isinstance(connection_parameters, pika.ConnectionParameters):
            self.connection_parameters = connection_parameters
        else:  # factory
            self.connection_parameters = connection_parameters()
        if isinstance(connection_retryer, Retrying):
            self.connection_retryer = connection_retryer
        else:  # factory
            self.connection_retryer = connection_retryer()
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel | None = None

    def connect(self):
        """
        Connect to the RabbitMQ server retrying errors configured in the connection_retryer.
        """
        if not self.is_connected:
            self.connection_retryer(self._connect)

    def _connect(self):
        """
        Configures and initiates connection to the RabbitMQ server.
        """
        logger.debug(
            f"Attempt to connect to RabbitMQ: connection_params={self.connection_parameters}"
        )
        self.connection = pika.BlockingConnection(self.connection_parameters)
        logger.info(f"Connection Created")
        self.channel = self.connection.channel()
        logger.info("Channel Created")
        logger.info(f"Connected to RabbitMQ: connection={self.connection_parameters}")

    @property
    def is_connected(self):
        """
        Current state of the connection.  Only updated when the connection is used.

        :return: Latest connection state
        """
        if self.connection is not None:
            return self.connection.is_open
        return False

    def disconnect(self):
        """
        Closes connection and related channels to the RabbitMQ Server.
        """

        if self.is_connected:
            self.connection.close()
        logger.info(f"Disconnected from RabbitMQ: " f"connection={self.connection_parameters}")

    def create_queue(self, queue: Queue):
        """
        Create a queue on an already opened connection.
        """
        self.channel.queue_declare(
            queue=queue.name,
            durable=queue.durable,
            passive=queue.passive,
            auto_delete=queue.auto_delete,
            exclusive=queue.exclusive,
            arguments=queue.arguments,
        )
        logger.info(f"Queue Created: queue={queue.name}")

    def __enter__(self):
        """
        Entry for context manager.

        :return: connected instance of self
        """
        self.connect()
        return self

    def __exit__(self, exc_type, value, traceback):
        """
        Exit for context manager which disconnects from rabbitmq
        """
        self.disconnect()

    def __repr__(self):
        """Representation of the DurableConnection object"""
        return f"{self.__class__.__name__}(connection_parameters={self.connection_parameters!r}), connection_retryer={self.connection_retryer!r})"
