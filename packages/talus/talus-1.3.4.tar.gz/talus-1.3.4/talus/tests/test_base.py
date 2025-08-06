"""Test the durable connection base module."""
import logging

import pika
import pytest
from tenacity import after_log
from tenacity import retry_if_exception_type
from tenacity import Retrying
from tenacity import stop_after_attempt
from tenacity import wait_exponential
from tenacity import wait_random

from talus.base import DurableConnection
from talus.models.connection_parameters import ConnectionParameterFactory
from talus.models.retryer import ConnectionRetryerFactory
from talus.models.retryer import DEFAULT_CONNECTION_EXCEPTIONS


logger = logging.getLogger(__name__)


@pytest.fixture(params=["pika.ConnectionParameters", "ConnectionParameterFactory"])
def connection_parameters(request):
    match request.param:
        case "pika.ConnectionParameters":
            return pika.ConnectionParameters(
                host="localhost",
                port=5672,
                credentials=pika.PlainCredentials("guest", "guest"),
            )
        case "ConnectionParameterFactory":
            return ConnectionParameterFactory()
        case _:
            raise NotImplementedError("Fixture parameter not implemented.")


@pytest.fixture(params=["Retrying", "RetryerFactory"])
def connection_retryer(request):
    match request.param:
        case "Retrying":
            return Retrying(
                retry=retry_if_exception_type(DEFAULT_CONNECTION_EXCEPTIONS),
                wait=wait_exponential(
                    multiplier=1,
                    min=1,
                    max=3,
                )
                + wait_random(1, 3),
                stop=stop_after_attempt(2),
                after=after_log(logger=logger, log_level=logging.INFO),
            )
        case "RetryerFactory":
            return ConnectionRetryerFactory(
                delay_min=1,
                delay_max=3,
                jitter_min=1,
                jitter_max=3,
                attempts=2,
                exceptions=DEFAULT_CONNECTION_EXCEPTIONS,
            )
        case _:
            raise NotImplementedError("Fixture parameter not implemented.")


def test_durable_connection(connection_parameters, connection_retryer):
    """
    :given: Connection Parameters and Retryer
    :when: DurableConnection is instantiated
    :then: Connection can be established.
    """
    # when
    with DurableConnection(
        connection_parameters=connection_parameters, connection_retryer=connection_retryer
    ) as durable_connection:
        # then
        durable_connection.connect()
        assert durable_connection.is_connected
    assert not durable_connection.is_connected


@pytest.fixture()
def durable_connection(connection_parameters, connection_retryer):
    with DurableConnection(
        connection_parameters=connection_parameters, connection_retryer=connection_retryer
    ) as durable_connection:
        yield durable_connection


def test_create_queue(durable_connection, test_queue):
    """
    :given: Connection to RabbitMQ
    :when: Queue is created
    :then: Queue is created
    """
    # given
    durable_connection.connect()
    # when
    durable_connection.create_queue(test_queue)
    # then
    test_queue.passive = True  # Only check if queue exists and raise `ChannelClosed` if it doesn't
    durable_connection.create_queue(test_queue)


def test_repr(durable_connection):
    """
    :given: Connection to RabbitMQ
    :when: Connection is represented as a string
    :then: String representation is returned
    """
    # when
    assert DurableConnection.__name__ in repr(durable_connection)
