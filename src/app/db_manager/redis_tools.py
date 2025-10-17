import redis
from app.config import REDIS_SERVICE_PORT, REDIS_SERVICE_HOST, REDIS_SERVICE_DB


class RedisConnection:
    def __init__(self):
        redis_host = REDIS_SERVICE_HOST
        redis_port = REDIS_SERVICE_PORT
        redis_db = REDIS_SERVICE_DB

        self._redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    def __enter__(self):
        return self._redis_client.client()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._redis_client.close()
