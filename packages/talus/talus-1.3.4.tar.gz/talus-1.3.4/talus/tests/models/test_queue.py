"""Tests for the queue model."""
from talus.models.queue import Queue


def test_queue():
    """
    :given: A queue name.
    :when: A queue is created.
    :then: The queue name is accessible with expected defaults.
    """
    # given
    queue_name = "foo"
    # when
    queue = Queue(name=queue_name)
    # then
    assert queue.name == queue_name
    assert queue.passive is False
    assert queue.durable is True
    assert queue.auto_delete is False
    assert queue.exclusive is False
    assert queue.arguments is None
