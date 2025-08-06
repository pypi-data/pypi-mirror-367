talus
=========

|codecov|

talus (noun) - ta·​lus | ˈtā-ləs: a slope formed especially by an accumulation of rock debris; Occasional habitat of the pika.

A wrapper for connecting to RabbitMQ which constrains clients to a single purpose channel (producer or consumer) with healing for intermittent connectivity.

Features
--------

- Guided separation of connections for producers and consumers

- Re-establish connections to the server when lost

- Constrained interface to support simple produce / consume use cases for direct exchanges

Installation
------------

.. code:: bash

   pip install talus

Examples
--------

**Creating a consumer which listens on a queue, processes valid messages and publishes as part of processing**

Uses default connection parameters and connection retryer expecting a rabbitmq server running in its default configuration.

.. code:: python

    from talus import DurableConsumer
    from talus import DurableProducer
    from talus import ConnectionRetryerFactory
    from talus import ConsumerConnectionParameterFactory, ProducerConnectionParameterFactory
    from talus import MessageProcessorBase
    from talus import ConsumeMessageBase, PublishMessageBase, MessageBodyBase
    from talus import Queue
    from talus import Exchange
    from talus import Binding
    from typing import Type

    ##########################
    # Consumer Configurations#
    ##########################
    # Configure messages that will be consumed
    class ConsumeMessageBody(MessageBodyBase):
        objectName: str
        bucket: str

    class ConsumeMessage(ConsumeMessageBase):
        message_body_cls: Type[ConsumeMessageBody] = ConsumeMessageBody

    # Configure the queue the messages should be consumed from
    inbound_queue = Queue(name="inbound.q")


    ###########################
    # Producer Configurations #
    ###########################
    # Configure messages that will be produced
    class ProducerMessageBody(MessageBodyBase):
        key: str
        code: str

    class PublishMessage(PublishMessageBase):
        message_body_cls: Type[ProducerMessageBody] = ProducerMessageBody
        default_routing_key: str = "outbound.message.m"

    # Configure the queues the message should be routed to
    outbound_queue_one = Queue(name="outbound.one.q")
    outbound_queue_two = Queue(name="outbound.two.q")


    # Configure the exchange and queue bindings for publishing (Publish Message -> Outbound Queues)
    publish_exchange = Exchange(name="outbound.exchange") # Direct exchange by default
    bindings = [Binding(queue=outbound_queue_one, message=PublishMessage),
                Binding(queue=outbound_queue_two, message=PublishMessage)] # publishing PublishMessage will route to both queues.


    ############################
    # Processor Configurations #
    ############################

    # Configure a message processor to handle the consumed messages
    class MessageProcessor(MessageProcessorBase):
        def process_message(self, message: ConsumeMessage):
            print(message)
            outbound_message = PublishMessage(
                body=ProducerMessageBody(
                    key=message.body.objectName,
                    code="newBucket",
                    conversationId=message.body.conversationId,
                )
            )  # crosswalk the values from the consumed message to the produced message
            self.producer.publish(outbound_message)
            print(outbound_message)


    # Actually Connect and run the consumer
    def main():
        """Starts a listener which will consume messages from the inbound queue and publish messages to the outbound queues."""
        with DurableProducer(
            queue_bindings=bindings,
            publish_exchange=publish_exchange,
            connection_parameters=ProducerConnectionParameterFactory(),
            connection_retryer=ConnectionRetryerFactory(),
        ) as producer:
            with DurableConsumer(
                consume_queue=inbound_queue,
                connection_parameters=ConsumerConnectionParameterFactory(),
                connection_retryer=ConnectionRetryerFactory(),
            ) as consumer:
                message_processor = MessageProcessor(message_cls=ConsumeMessage, producer=producer)
                consumer.listen(message_processor)


    if __name__ == "__main__":
        # First message to consume
        class InitialMessage(PublishMessageBase):
            message_body_cls: Type[
                ConsumeMessageBody] = ConsumeMessageBody
            default_routing_key: str = "inbound.message.m"

        initial_message_bindings = [Binding(queue=inbound_queue, message=InitialMessage)]

        with DurableProducer(
                queue_bindings=initial_message_bindings,
                publish_exchange=publish_exchange,
                connection_parameters=ProducerConnectionParameterFactory(),
                connection_retryer=ConnectionRetryerFactory(),
        ) as producer:
            producer.publish(InitialMessage(body={"objectName": "object", "bucket": "bucket"}))
        # Consume the message and process it
        main()

.. |codecov| image:: https://codecov.io/bb/dkistdc/interservice-bus-adapter/branch/master/graph/badge.svg
   :target: https://codecov.io/bb/dkistdc/interservice-bus-adapter
