import logging
from redis import Redis, ConnectionPool
from app.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._pool = None
        self._client = None

    def init_redis(self):
        """Initializes the Redis connection pool."""
        try:
            self._pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
            self._client = Redis(connection_pool=self._pool)
            self._client.ping()
            logger.info("Redis client initialized and connected.")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")

    def set_value(self, key: str, value: str, ttl: int = 3600):
        if not self._client: return
        try:
            self._client.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis set failed for {key}: {e}")

    def get_value(self, key: str) -> str | None:
        if not self._client: return None
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed for {key}: {e}")
            return None

    def delete_value(self, key: str):
        if not self._client: return
        try:
            self._client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete failed for {key}: {e}")

    def check_connection(self) -> bool:
        if not self._client: return False
        try:
            return self._client.ping()
        except Exception:
            return False

# Export instance
redis_client = RedisClient()

def init_redis():
    redis_client.init_redis()
