"""Test the Retryer model."""
from tenacity import Retrying

from talus.models.retryer import ConnectionRetryerFactory
from talus.models.retryer import DEFAULT_CONNECTION_EXCEPTIONS
from talus.models.retryer import RetryerFactory


def test_retryer_defaults():
    """
    :given: A retryer factory
    :when: The factory is called
    :then: A Retryer object is returned
    """
    # given
    factory = RetryerFactory()
    # when
    retryer = factory()
    # then
    assert isinstance(retryer, Retrying)


def test_retryer_with_attempts():
    """
    :given: A retryer factory with attempts > 1
    :when: The factory is called
    :then: A Retryer object is returned with a stop_after_attempt object
    """
    # given
    factory = RetryerFactory(attempts=5)
    # when
    retryer = factory()
    # then
    assert isinstance(retryer, Retrying)
    assert retryer.stop is not None


def test_connection_retryer_factory():
    """
    :given: A connection retryer factory
    :when: The factory is called
    :then: A Retrying object is returned
    """
    # given
    factory = ConnectionRetryerFactory()
    # when
    retryer = factory()
    # then
    assert isinstance(retryer, Retrying)
    assert factory.exceptions == DEFAULT_CONNECTION_EXCEPTIONS
