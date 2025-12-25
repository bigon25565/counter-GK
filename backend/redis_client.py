import os
import time
from redis import Redis, RedisError

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') or None

def get_redis_client(retries=5, wait=1):
    for i in range(retries):
        try:
            client = Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
            client.ping()
            return client
        except RedisError:
            if i == retries - 1:
                raise
            time.sleep(wait)
    raise RedisError("Cannot connect to Redis")