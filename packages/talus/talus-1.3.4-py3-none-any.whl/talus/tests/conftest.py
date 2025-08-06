"""Common test fixtures for the talus package."""
import json
from typing import Type
from uuid import uuid4

import pika
import pytest
from pydantic import Field

from talus.consumer import DurableConsumer
from talus.models.binding import Binding
from talus.models.connection_parameters import ConsumerConnectionParameterFactory
from talus.models.connection_parameters import ProducerConnectionParameterFactory
from talus.models.exchange import Exchange
from talus.models.message import ConsumeMessageBase
from talus.models.message import MessageBodyBase
from talus.models.message import PublishMessageBase
from talus.models.queue import Queue
from talus.models.retryer import ConnectionRetryerFactory
from talus.producer import DurableProducer


@pytest.fixture()
def message_data_schema_cls() -> Type[MessageBodyBase]:
    class MessageDataBody(MessageBodyBase):
        key: str = Field(default="value")

    return MessageDataBody


@pytest.fixture(params=["no-conversation-id", "conversation-id"])
def message_data(request, message_data_schema_cls) -> dict[str, str]:
    result = message_data_schema_cls(key=uuid4().hex).model_dump()
    match request.param:
        case "no-conversation-id":
            result.pop("conversationId")
            return result
        case "conversation-id":
            return result
        case _:
            raise NotImplementedError("message data parameter not implemented")


@pytest.fixture(params=["bytes-body", "python-body", "json-body"])
def body(message_data, request) -> bytes:
    match request.param:
        case "bytes-body":
            return json.dumps(message_data).encode("utf-8")
        case "python-body":
            return message_data
        case "json-body":
            return json.dumps(message_data)
        case _:
            raise NotImplementedError("body type not implemented")


@pytest.fixture(params=["no-headers", "headers"])
def headers(request) -> dict[str, str] | None:
    match request.param:
        case "no-headers":
            return None
        case "headers":
            return {"header1": "value1"}
        case _:
            raise NotImplementedError("headers parameter not implemented")


@pytest.fixture()
def properties(headers) -> pika.spec.BasicProperties:
    return pika.spec.BasicProperties(headers=headers)


@pytest.fixture()
def routing_key() -> str:
    return uuid4().hex


@pytest.fixture()
def delivery_tag() -> str:
    return uuid4().hex


@pytest.fixture()
def method(routing_key, delivery_tag) -> pika.spec.Basic.Deliver:
    return pika.spec.Basic.Deliver(routing_key=routing_key, delivery_tag=delivery_tag)


@pytest.fixture
def test_queue(request) -> Queue:
    """A queue name for consume tests."""
    prefix = request.node.name
    return Queue(name=f"queue_{prefix}_{uuid4().hex[:6]}", auto_delete=True)


@pytest.fixture
def consumer(test_queue) -> DurableConsumer:
    """A test consumer."""
    with DurableConsumer(
        consume_queue=test_queue,
        prefetch_count=1,
        connection_parameters=ConsumerConnectionParameterFactory(),
        connection_retryer=ConnectionRetryerFactory(attempts=2, wait=0),
    ) as consumer:
        yield consumer


@pytest.fixture()
def consume_message_cls(message_data_schema_cls) -> Type[ConsumeMessageBase]:
    """A test consume message class."""

    class ConsumeMessage(ConsumeMessageBase):
        message_body_cls = message_data_schema_cls

    return ConsumeMessage


@pytest.fixture
def publish_message_cls(routing_key, headers) -> Type[PublishMessageBase]:
    """A test publish message class."""
    rk = routing_key
    h = headers

    class PublishMessage(PublishMessageBase):
        default_routing_key: str = rk
        headers: dict[str, str] = h

    return PublishMessage


@pytest.fixture()
def direct_exchange() -> Exchange:
    return Exchange(
        name=f"direct_{uuid4().hex[:6]}",
        auto_delete=True,
    )


@pytest.fixture()
def queue_bindings(test_queue, publish_message_cls) -> Binding:
    """A list of routing key -> queue bindings"""
    return Binding(
        message=publish_message_cls,
        queue=test_queue,
    )


@pytest.fixture
def producer(queue_bindings, direct_exchange) -> DurableProducer:
    """A test producer."""

    with DurableProducer(
        queue_bindings=queue_bindings,
        publish_exchange=direct_exchange,
        connection_parameters=ProducerConnectionParameterFactory(),
        connection_retryer=ConnectionRetryerFactory(attempts=2, wait=0),
    ) as producer:
        yield producer


@pytest.fixture
def single_message_on_queue(producer, test_queue, publish_message_cls, body) -> PublishMessageBase:
    """
    Fixture that produces a single message to an empty test queue
    """
    publish_message = publish_message_cls(body=body)
    producer.publish(publish_message)
    return publish_message
