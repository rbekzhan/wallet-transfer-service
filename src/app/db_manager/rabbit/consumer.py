import json
from aio_pika import connect_robust

async def consume_events():
    connection = await connect_robust("amqp://guest:guest@localhost:5672")
    channel = await connection.channel()
    queue = await channel.declare_queue("wallet_notifications", durable=True)
    await queue.bind("wallet_exchange", routing_key="wallet.events")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                print(f"Получено событие: {data}")

