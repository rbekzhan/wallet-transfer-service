import json

import aio_pika

from app.db_manager.rabbit.rabbit_connection import RabbitMQConnection


async def publish_event(event_type: str, payload: dict):
    channel = await RabbitMQConnection.get_channel()
    exchange = await channel.declare_exchange("wallet_exchange", durable=True)

    message = aio_pika.Message(
        body=json.dumps({"type": event_type, "payload": payload}).encode(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    await exchange.publish(message, routing_key="wallet.events")
