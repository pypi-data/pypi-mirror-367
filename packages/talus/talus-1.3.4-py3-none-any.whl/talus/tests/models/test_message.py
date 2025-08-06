"""Tests for the message models."""
import json
from typing import Any

import pika
import pydantic_core
import pytest

from talus.models.message import ConsumeMessageBase
from talus.models.message import MessageBodyBase
from talus.models.message import PublishMessageBase


def test_consume_message_model_valid(
    method, properties, body, routing_key, headers, delivery_tag, message_data
):
    """
    :given: A ConsumeMessage class
    :when: A new instance is created with default args
    :then: The instance body has a conversationId and other properties are set
    """
    # given/when
    message = ConsumeMessageBase(method=method, properties=properties, body=body)
    # then
    assert message.body.conversationId is not None
    assert message.method == method
    assert message.properties == properties
    assert message.routing_key == routing_key
    assert message.headers == headers
    assert message.delivery_tag == delivery_tag
    assert (
        message.body.model_dump() == {"conversationId": message.body.conversationId} | message_data
    )
    assert repr(message)


class ExampleMessageBody(MessageBodyBase):
    required_str: str
    required_int: int


class ConsumableMessage(ConsumeMessageBase):
    message_body_cls = ExampleMessageBody


@pytest.mark.parametrize(
    "invalid_body",
    [
        pytest.param(
            json.dumps({"required_str": 1, "required_int": "zz"}).encode("utf-8"),
            id="schema_invalid",
        ),
        pytest.param(b"123 abc", id="json_invalid"),
    ],
)
def test_consume_message_model_invalid(method, properties, invalid_body: Any):
    """
    :given: A ConsumeMessage class
    :when: A new instance is created and the body is invalid for the message schema
    :then: A Validation Error is raised
    """
    with pytest.raises(pydantic_core.ValidationError):
        ConsumableMessage(method=method, properties=properties, body=invalid_body)


def test_publish_message_model(routing_key, headers, body, message_data, publish_message_cls):
    """
    :given: A PublishMessage class
    :when: A new instance is created
    :then: The instance body has a conversationId and other properties are set
    """
    # given/when
    message = publish_message_cls(body=body)
    # then
    assert message.body.conversationId is not None
    assert message.routing_key == routing_key
    assert message.headers == headers
    assert isinstance(message.properties, pika.spec.BasicProperties)
    assert message.properties.headers == headers
    assert (
        message.body.model_dump() == {"conversationId": message.body.conversationId} | message_data
    )
    assert repr(message)


class PublishMessage(PublishMessageBase):
    message_body_cls = ExampleMessageBody
    default_routing_key = "test.m"


@pytest.mark.parametrize(
    "invalid_body",
    [
        pytest.param(
            json.dumps({"required_str": 1, "required_int": "zz"}).encode("utf-8"),
            id="schema_invalid",
        ),
        pytest.param(b"123 abc", id="json_invalid"),
    ],
)
def test_publish_message_model_invalid(routing_key, invalid_body):
    """
    :given: A PublishMessage class
    :when: A new instance is created and the body is invalid for the message schema
    :then: A Validation Error is raised
    """
    with pytest.raises(pydantic_core.ValidationError):
        PublishMessage(body=invalid_body)
