"""Connection Parameter Factory Model"""
import pika
from pydantic import BaseModel
from pydantic import Field


MINUTES_1 = 60
HOUR_1 = 3600


class ConnectionParameterFactory(BaseModel):
    """
    Translator for the connection configuration to a pika.ConnectionParameters object.
    >>> from talus.models.connection_parameters import ConnectionParameterFactory
    >>> factory = ConnectionParameterFactory()
    >>> connection_parameters = factory()
    """

    rabbitmq_host: str = Field(
        default="127.0.0.1"
    )  # Host name or IP of the rabbitMQ server. e.g. 127.0.0.1
    rabbitmq_port: int = 5672  # Port the rabbitmq server listens on e.g. 5672
    rabbitmq_user: str = Field(default="guest")  # Username for the rabbitMQ server e.g. guest
    rabbitmq_pass: str = Field(default="guest")  # Password for the rabbitMQ server e.g. guest
    connection_name: str = Field(
        default="default_connection"
    )  # Name of the connection that will be visible in the rabbitmq admin console
    # Controls AMQP heartbeat timeout negotiation
    # during connection tuning. An integer value always overrides the value
    # proposed by broker. Use 0 to deactivate heartbeats and None to always
    # accept the broker's proposal.
    heartbeat: int | None = None

    def __call__(self) -> pika.ConnectionParameters:
        return pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            credentials=pika.credentials.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass),
            heartbeat=self.heartbeat,
            client_properties={"connection_name": self.connection_name},
        )


class ConsumerConnectionParameterFactory(ConnectionParameterFactory):
    """Consumer Connection Parameter Factory Model which defaults to a 1 minute heartbeat."""

    heartbeat: int = MINUTES_1


class ProducerConnectionParameterFactory(ConnectionParameterFactory):
    """Producer Connection Parameter Factory Model which defaults to a 1 hour heartbeat."""

    heartbeat: int = HOUR_1
