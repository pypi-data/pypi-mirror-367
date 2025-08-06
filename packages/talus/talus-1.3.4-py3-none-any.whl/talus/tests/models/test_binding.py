"""Tests for the various models in the Talus application."""
from uuid import uuid4

import pytest

from talus.models.binding import Binding
from talus.models.message import ConsumeMessageBase
from talus.models.message import PublishMessageBase
from talus.models.queue import Queue


@pytest.fixture()
def queue_name() -> str:
    return uuid4().hex


@pytest.fixture()
def queue(queue_name) -> Queue:
    return Queue(name=queue_name)


def test_binding_valid(queue, queue_name, publish_message_cls, routing_key):
    """
    :given: A message class and a queue.
    :when: A binding is created.
    :then: the routing key and queue name are accessible.
    """
    # when
    binding = Binding(message=publish_message_cls, queue=queue)
    # then
    assert binding.routing_key == routing_key
    assert binding.queue_name == queue_name


@pytest.fixture()
def consume_message(body, method, properties) -> ConsumeMessageBase:
    return ConsumeMessageBase(method=method, properties=properties, body=body)


class BadPublishMessage(PublishMessageBase):
    default_routing_key = ""


@pytest.mark.parametrize(
    "message, queue",
    [
        pytest.param(
            ConsumeMessageBase,
            Queue(name="foo"),
            id="consume_message",
        ),
        pytest.param(
            BadPublishMessage,
            Queue(name="foo"),
            id="routing_key_empty",
        ),
    ],
)
def test_binding_invalid(message, queue):
    """
    :given: A message without a routing key and a queue.
    :when: A binding is created.
    :then: A Value error is raised
    """
    # when/then
    with pytest.raises(ValueError):
        Binding(message=message, queue=queue)
