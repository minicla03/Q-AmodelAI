import os
import redis
import logging
from typing import Optional


class RedisConnectionManager:
    _instance: Optional["RedisConnectionManager"] = None

    def __init__(self):
        if hasattr(self, "client"):
            return

        redis_url = os.getenv("REDIS_URL")

        try:
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=os.getenv("REDIS_PASSWORD", None),
                    db=int(os.getenv("REDIS_DB", 0)),
                    decode_responses=True
                )

            self.client.ping()
            logging.info("Connesso a Redis.")

        except redis.exceptions.ConnectionError as e:
            logging.error(f"Errore critico connessione Redis: {e}")
            raise ConnectionError("Impossibile connettersi a Redis")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance