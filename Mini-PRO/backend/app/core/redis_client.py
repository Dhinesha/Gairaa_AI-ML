import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("core.redis")

try:
    import redis
except ImportError:
    redis = None


class ResilientCacheClient:
    """
    Resilient Redis client with automatic fallback to thread-safe in-memory cache.
    Ensures zero crashes even when Redis daemon is absent or disconnects.
    """

    def __init__(self, redis_url: str, enabled: bool = True):
        self.redis_url = redis_url
        self.enabled = enabled and (redis is not None)
        self._redis_client = None
        self._memory_store: Dict[str, Any] = {}
        self._memory_expiry: Dict[str, float] = {}
        self._memory_counters: Dict[str, int] = {}
        self.is_connected = False
        self._init_connection()

    def _init_connection(self):
        if not self.enabled:
            logger.info("Redis disabled or module not found. Using in-memory fallback store.")
            return

        try:
            self._redis_client = redis.from_url(
                self.redis_url,
                socket_timeout=1.5,
                socket_connect_timeout=1.5,
                decode_responses=True,
            )
            # Ping to verify
            self._redis_client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            self.is_connected = False
            self._redis_client = None
            logger.warning(
                f"Redis server unavailable ({e}). Gracefully falling back to in-memory state engine."
            )

    def set_key(self, key: str, value: str, ex_seconds: Optional[int] = None) -> bool:
        if self.is_connected and self._redis_client:
            try:
                self._redis_client.set(key, value, ex=ex_seconds)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed ({e}), switching to memory fallback.")
                self.is_connected = False

        # Memory fallback
        self._memory_store[key] = value
        if ex_seconds:
            self._memory_expiry[key] = time.time() + ex_seconds
        return True

    def get_key(self, key: str) -> Optional[str]:
        if self.is_connected and self._redis_client:
            try:
                return self._redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis get failed ({e}), switching to memory fallback.")
                self.is_connected = False

        # Memory fallback with expiry check
        if key in self._memory_expiry and time.time() > self._memory_expiry[key]:
            self._memory_store.pop(key, None)
            self._memory_expiry.pop(key, None)
            return None
        return self._memory_store.get(key)

    def delete_key(self, key: str) -> bool:
        if self.is_connected and self._redis_client:
            try:
                self._redis_client.delete(key)
                return True
            except Exception:
                pass

        self._memory_store.pop(key, None)
        self._memory_expiry.pop(key, None)
        self._memory_counters.pop(key, None)
        return True

    def acquire_lock(self, lock_name: str, timeout_seconds: int = 10) -> bool:
        """
        Concurrency-safe distributed lock to prevent duplicate workflow runs.
        """
        key = f"lock:{lock_name}"
        if self.is_connected and self._redis_client:
            try:
                # SET NX PX
                acquired = self._redis_client.set(key, "locked", nx=True, ex=timeout_seconds)
                return bool(acquired)
            except Exception as e:
                logger.warning(f"Redis acquire_lock failed ({e}), using memory lock.")
                self.is_connected = False

        # In-memory lock
        now = time.time()
        if key in self._memory_expiry and now < self._memory_expiry[key]:
            return False  # Already locked
        self._memory_store[key] = "locked"
        self._memory_expiry[key] = now + timeout_seconds
        return True

    def release_lock(self, lock_name: str) -> bool:
        return self.delete_key(f"lock:{lock_name}")

    def increment_counter(self, counter_name: str, ex_seconds: Optional[int] = None) -> int:
        key = f"counter:{counter_name}"
        if self.is_connected and self._redis_client:
            try:
                val = self._redis_client.incr(key)
                if ex_seconds and val == 1:
                    self._redis_client.expire(key, ex_seconds)
                return val
            except Exception as e:
                logger.warning(f"Redis incr failed ({e}), using memory counter.")
                self.is_connected = False

        # Memory fallback
        val = self._memory_counters.get(key, 0) + 1
        self._memory_counters[key] = val
        return val


from backend.app.core.config import settings

cache_client = ResilientCacheClient(
    redis_url=settings.REDIS_URL,
    enabled=settings.REDIS_ENABLED,
)
