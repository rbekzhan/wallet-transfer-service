import aio_pika
from aio_pika.abc import AbstractChannel, AbstractConnection

class RabbitMQConnection:
    _connection: AbstractConnection | None = None
    _channel: AbstractChannel | None = None

    @classmethod
    async def get_channel(cls):
        if cls._channel and not cls._channel.is_closed:
            return cls._channel

        cls._connection = await aio_pika.connect_robust(
            "amqp://guest:guest@localhost:5672"
        )
        cls._channel = await cls._connection.channel()
        return cls._channel
