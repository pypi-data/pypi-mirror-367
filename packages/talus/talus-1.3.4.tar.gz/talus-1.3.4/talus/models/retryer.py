"""Retryer Factory Model."""
import logging

from pika.exceptions import AMQPHeartbeatTimeout
from pika.exceptions import ChannelClosed
from pika.exceptions import ChannelClosedByClient
from pika.exceptions import ChannelError
from pika.exceptions import ChannelWrongStateError
from pika.exceptions import ConnectionBlockedTimeout
from pika.exceptions import ConnectionClosedByClient
from pika.exceptions import ConnectionOpenAborted
from pika.exceptions import ConnectionWrongStateError
from pika.exceptions import InvalidChannelNumber
from pika.exceptions import NoFreeChannels
from pika.exceptions import StreamLostError
from pika.exceptions import UnexpectedFrameError
from pydantic import BaseModel
from tenacity import after_log
from tenacity import before_log
from tenacity import retry_if_exception_type
from tenacity import Retrying
from tenacity import stop_after_attempt
from tenacity import stop_never
from tenacity import wait_exponential_jitter

logger = logging.getLogger(__name__)


class RetryerFactory(BaseModel):
    """
    Translator for the retry configuration to a tenacity.Retrying object.

    >>> from talus.models.retryer import RetryerFactory
    >>> factory = RetryerFactory()
    >>> retryer = factory()
    """

    delay_min: float = 1.0
    delay_max: float = 300.0
    backoff: float = 2.0
    jitter_min: float = 0
    jitter_max: float = 10.0
    attempts: int = -1  # -1 means retry forever
    exceptions: type[Exception] | tuple[type[Exception], ...] = type(
        Exception
    )  # retry any exception

    def __call__(self) -> Retrying:
        """
        Returns a tenacity.Retrying object based on the configuration.
        """
        wait = wait_exponential_jitter(
            initial=self.delay_min,
            max=self.delay_max,
            exp_base=self.backoff,
            jitter=self.jitter_max,
        )

        stop = stop_never
        if self.attempts > -1:
            stop = stop_after_attempt(self.attempts)
        return Retrying(
            retry=retry_if_exception_type(self.exceptions),
            wait=wait,
            stop=stop,
            before=before_log(logger=logger, log_level=logging.DEBUG),
            after=after_log(logger=logger, log_level=logging.DEBUG),
        )


DEFAULT_CONNECTION_EXCEPTIONS = (
    ConnectionOpenAborted,
    StreamLostError,
    NoFreeChannels,
    ConnectionWrongStateError,
    ConnectionClosedByClient,
    ConnectionBlockedTimeout,
    AMQPHeartbeatTimeout,
    ChannelWrongStateError,
    ChannelClosed,
    ChannelClosedByClient,
    InvalidChannelNumber,
    UnexpectedFrameError,
    ChannelError,
)


class ConnectionRetryerFactory(RetryerFactory):
    """Retryer Factory for connection exceptions."""

    exceptions: type[Exception] | tuple[type[Exception], ...] = DEFAULT_CONNECTION_EXCEPTIONS
