"""Tests for the connection parameters factory"""
import pika

from talus.models.connection_parameters import ConnectionParameterFactory


def test_connection_parameters():
    """
    :given: A connection parameter factory
    :when: The factory is called
    :then: A pika.ConnectionParameters object is returned
    """
    connection_parameters = ConnectionParameterFactory()
    assert isinstance(connection_parameters(), pika.ConnectionParameters)
