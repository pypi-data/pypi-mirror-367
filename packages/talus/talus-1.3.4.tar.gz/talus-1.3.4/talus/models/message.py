"""
Module encapsulating message structure to facilitate use with the Consumer and Producer wrappers
"""
import uuid
from typing import Type

import pika.spec
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class MessageBodyBase(BaseModel):
    """
    Base class for message schemas which can be used to validate message bodies.
    This is a pydantic.BaseModel so each message body schema can be validated.  Extend this class
    to add fields to a new message body schema.  For Example:
    >>> class ObjectBucketBody(MessageBodyBase):
    >>>     objectName: str
    >>>     bucket: str
    """

    model_config = ConfigDict(extra="allow")

    conversationId: str = Field(default_factory=lambda: uuid.uuid4().hex)


class _MessageBase:
    """
    Base class for messages establishing a common interface for use by DurableConnections.
    Not intended for direct use.  Use ConsumeMessageBase or PublishMessageBase instead.
    """

    message_body_cls: Type[MessageBodyBase] = MessageBodyBase

    def __init__(self, routing_key: str, body: bytes | dict | str | MessageBodyBase):
        self.routing_key = routing_key
        if isinstance(body, dict | BaseModel):
            self.body: MessageBodyBase = self.message_body_cls.model_validate(body)
        else:  # str | bytes
            self.body: MessageBodyBase = self.message_body_cls.model_validate_json(body)


class ConsumeMessageBase(_MessageBase):
    """
    Base class for messages consumed from a DurableConsumer MessageProcessor.  Each instance
    correlates with a single consumed message.  The body of the message is validated against the
    message_body_cls class attribute.
    >>> class ObjectBucketBody(MessageBodyBase):
    >>>    objectName: str
    >>>    bucket: str
    >>>
    >>> class InboundMessage(ConsumeMessageBase):
    >>>     message_body_cls: Type[ObjectBucketBody] = ObjectBucketBody  # Validate the body with ObjectBucketBody
    >>>
    >>> queue = Queue(name="my_queue")
    >>> with DurableConsumer(consume_queue=queue) as consumer:
    >>>     consumer.listen(lambda ch, method, properties, body: InboundMessage(method, properties, body))
    """

    def __init__(
        self,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes | dict | str | MessageBodyBase,
    ):
        super().__init__(method.routing_key, body)
        self.method = method
        self.properties = properties

    @property
    def delivery_tag(self):
        return self.method.delivery_tag

    @property
    def headers(self) -> dict | None:
        return self.properties.headers

    def __repr__(self):
        return f"{self.__class__.__name__}(method={self.method!r}, properties={self.properties!r}, body={self.body!r})"


class PublishMessageBase(_MessageBase):
    """
    Base class for messages published to with a DurableProducer.
    Each instance correlates with a single message to publish.  The body of the message is validated
    against the class defined in message_body_cls class attribute.  Additional class attributes for
    routing_key and headers are provided for customizing the message at the class level e.g. all
    instances share a routing_key.

    >>> class OutboundMessage(PublishMessageBase):
    >>>     message_body_cls: Type[ObjectBucketBody] = ObjectBucketBody
    >>>     default_routing_key: str = "outbound.m"
    >>>     headers: dict[str, str] = {"header1": "value1"}
    >>>
    >>>
    >>> queue = Queue(name="test_queue")
    >>> exchange = Exchange(name="test_exchange")
    >>> queue_bindings = Binding(queue=queue, message=OutboundMessage)
    >>> with DurableProducer(queue_bindings=queue_bindings, publish_exchange=exchange) as producer:
    >>>     body = {"objectName": "object", "bucket": "bucket"}
    >>>     producer.publish(OutboundMessage(body))
    """

    default_routing_key: str = "default.m"
    headers: dict[str, str] | None = None

    def __init__(
        self,
        body: bytes | dict | str | MessageBodyBase,
    ):
        super().__init__(self.default_routing_key, body)

    @property
    def properties(self) -> pika.spec.BasicProperties:
        return pika.BasicProperties(
            content_type="text/plain",
            priority=0,
            delivery_mode=pika.DeliveryMode.Persistent,
            content_encoding="UTF-8",
            headers=self.headers,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(body={self.body!r}) # {self.routing_key = }"
