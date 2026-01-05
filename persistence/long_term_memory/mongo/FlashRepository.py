import logging
from typing import Optional, Dict, List, Union

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from persistence.IxRepository.IRepos import IFlashcardRepository
from persistence.model.Flashcard import Flashcard

logger = logging.getLogger(__name__)


class MongoFlashRepository(IFlashcardRepository):
    COLLECTION_NAME = "flashcards"

    def __init__(self, db):
        super().__init__(db)
        self.collection = self.db[self.COLLECTION_NAME]

    def create_flashcard(self, flashcard: Union[Flashcard, Dict]) -> str:
        try:
            if hasattr(flashcard, "to_dict"):
                data = flashcard.to_dict()
            elif isinstance(flashcard, dict):
                data = flashcard
            else:
                raise ValueError("Il dato passato non è né una Flashcard né un dict.")

            if "notebook_id" in data and isinstance(data["notebook_id"], str):
                data["notebook_id"] = ObjectId(data["notebook_id"])

            if "_id" in data and data["_id"] is None:
                del data["_id"]

            result = self.collection.insert_one(data)
            new_id = str(result.inserted_id)

            logger.info(f"Flashcard creata con ID: {new_id}")
            return new_id

        except PyMongoError as e:
            logger.error(f"Errore DB creando flashcard: {e}")
            raise RuntimeError(f"Errore salvataggio flashcard: {e}")

    def delete_flashcard(self, flashcard_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(flashcard_id)})

            if result.deleted_count > 0:
                logger.info(f"Flashcard {flashcard_id} eliminata.")
                return True
            else:
                logger.warning(f"Nessuna flashcard trovata con ID {flashcard_id} da eliminare.")
                return False

        except InvalidId:
            logger.error(f"ID Flashcard non valido: {flashcard_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Errore DB eliminando flashcard {flashcard_id}: {e}")
            return False

    def get_flashcard_by_user(self, user_id: str) -> List[Dict]:
        try:

            cursor = self.collection.find({"user_id": user_id})

            flashcards = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                if "notebook_id" in doc:
                    doc["notebook_id"] = str(doc["notebook_id"])
                flashcards.append(doc)

            return flashcards

        except PyMongoError as e:
            logger.error(f"Errore recuperando flashcards per user {user_id}: {e}")
            return []

    def get_flashcard_by_notebook(self, notebook_id: str) -> List[Dict]:
        try:
            query = {"notebook_id": ObjectId(notebook_id)}
            cursor = self.collection.find(query)

            flashcards = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["notebook_id"] = str(doc["notebook_id"])
                flashcards.append(doc)

            return flashcards

        except InvalidId:
            logger.error(f"Notebook ID non valido: {notebook_id}")
            return []
        except PyMongoError as e:
            logger.error(f"Errore recuperando flashcards per notebook {notebook_id}: {e}")
            return []