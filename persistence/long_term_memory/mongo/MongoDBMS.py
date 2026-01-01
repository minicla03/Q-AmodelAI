import os
import logging
from typing import Optional
from pymongo import MongoClient

class MongoConnectionManager:
    _instance: Optional["MongoConnectionManager"] = None

    def __init__(self):
        if hasattr(self, "client"):
            return

        self.uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGO_DB", "rag_system")

        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')
            logging.info(f"Connesso a MongoDB: {self.db_name}")
        except Exception as e:
            logging.error(f"Errore connessione MongoDB: {e}")
            raise ConnectionError("Impossibile connettersi a MongoDB")

    @property
    def db(self):
        return self.client[self.db_name]

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def try_connection(self):
        try:
            self._client.admin.command('ping')
            logging.info(f"Connesso a MongoDB ({self.host}:{self.port})")
            return True
        except Exception as e:
            logging.error(f"Errore di connessione a MongoDB: {e}")
            raise ConnectionError("Impossibile connettersi a MongoDB.")


